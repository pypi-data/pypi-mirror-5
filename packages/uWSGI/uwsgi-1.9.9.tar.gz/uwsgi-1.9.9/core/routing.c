#ifdef UWSGI_ROUTING
#include <uwsgi.h>

extern struct uwsgi_server uwsgi;

struct uwsgi_route_var *uwsgi_register_route_var(char *name, char *(*func)(struct wsgi_request *, char *, uint16_t, uint16_t *)) {

	struct uwsgi_route_var *old_urv = NULL,*urv = uwsgi.route_vars;
        while(urv) {
                if (!strcmp(urv->name, name)) {
                        return urv;
                }
                old_urv = urv;
                urv = urv->next;
        }

        urv = uwsgi_calloc(sizeof(struct uwsgi_route_var));
        urv->name = name;
	urv->name_len = strlen(name);
        urv->func = func;

        if (old_urv) {
                old_urv->next = urv;
        }
        else {
                uwsgi.route_vars = urv;
        }

        return urv;
}

struct uwsgi_route_var *uwsgi_get_route_var(char *name, uint16_t name_len) {
	struct uwsgi_route_var *urv = uwsgi.route_vars;
	while(urv) {
		if (!uwsgi_strncmp(urv->name, urv->name_len, name, name_len)) {
			return urv;
		}
		urv = urv->next;
	}
	return NULL;
}

struct uwsgi_buffer *uwsgi_routing_translate(struct wsgi_request *wsgi_req, struct uwsgi_route *ur, char *subject, uint16_t subject_len, char *data, size_t data_len) {

	char *pass1 = data;
	size_t pass1_len = data_len;

	if (ur->condition_ub[wsgi_req->async_id] && ur->ovn[wsgi_req->async_id] > 0) {
		pass1 = uwsgi_regexp_apply_ovec(ur->condition_ub[wsgi_req->async_id]->buf, ur->condition_ub[wsgi_req->async_id]->pos, data, data_len, ur->ovector[wsgi_req->async_id], ur->ovn[wsgi_req->async_id]);
		pass1_len = strlen(pass1);
	}
	// cannot fail
	else if (subject) {
		pass1 = uwsgi_regexp_apply_ovec(subject, subject_len, data, data_len, ur->ovector[wsgi_req->async_id], ur->ovn[wsgi_req->async_id]);
		pass1_len = strlen(pass1);
	}

	struct uwsgi_buffer *ub = uwsgi_buffer_new(pass1_len);
	size_t i;
	int status = 0;
	char *key = NULL;
	size_t keylen = 0;
	for(i=0;i<pass1_len;i++) {
		switch(status) {
			case 0:
				if (pass1[i] == '$') {
					status = 1;
					break;
				}
				if (uwsgi_buffer_append(ub, pass1 + i, 1)) goto error;
				break;
			case 1:
				if (pass1[i] == '{') {
					status = 2;
					key = pass1+i+1;
					keylen = 0;
					break;
				}
				status = 0;
				key = NULL;
				keylen = 0;
				if (uwsgi_buffer_append(ub, "$", 1)) goto error;
				if (uwsgi_buffer_append(ub, pass1 + i, 1)) goto error;
				break;
			case 2:
				if (pass1[i] == '}') {
					uint16_t vallen = 0;
					int need_free = 0;
					char *value = NULL;
					char *bracket = memchr(key, '[', keylen);
					if (bracket && keylen > 0 && key[keylen-1] == ']') {
						struct uwsgi_route_var *urv = uwsgi_get_route_var(key, bracket - key);
						if (urv) {
							need_free = urv->need_free;
							value = urv->func(wsgi_req, bracket + 1, keylen - (urv->name_len+2), &vallen); 
						}
						else {
							value = uwsgi_get_var(wsgi_req, key, keylen, &vallen);
						}
					}
					else {
						value = uwsgi_get_var(wsgi_req, key, keylen, &vallen);
					}
					if (value) {
						if (uwsgi_buffer_append(ub, value, vallen)) {
							if (need_free) {
								free(value);
							}
							goto error;
						}
						if (need_free) {
							free(value);
						}
					}
                                        status = 0;
					key = NULL;
					keylen = 0;
                                        break;
                                }
				keylen++;
				break;
			default:
				break;
		}
	}

	// fix the buffer
	if (status == 1) {
		if (uwsgi_buffer_append(ub, "$", 1)) goto error;
	}
	else if (status == 2) {
		if (uwsgi_buffer_append(ub, "${", 2)) goto error;
		if (keylen > 0) {
			if (uwsgi_buffer_append(ub, key, keylen)) goto error;
		}
	}

	// add the final NULL byte (to simplify plugin work)
	if (uwsgi_buffer_append(ub, "\0", 1)) goto error;
	// .. but came back of 1 position to avoid accounting it
	ub->pos--;

	if (pass1 != data) {
		free(pass1);
	}
	return ub;

error:
	uwsgi_buffer_destroy(ub);
	return NULL;
}

static void uwsgi_routing_reset_memory(struct wsgi_request *wsgi_req, struct uwsgi_route *routes) {
	// free dynamic memory structures
	if (routes->if_func) {
                        routes->ovn[wsgi_req->async_id] = 0;
                        if (routes->ovector[wsgi_req->async_id]) {
                                free(routes->ovector[wsgi_req->async_id]);
                                routes->ovector[wsgi_req->async_id] = NULL;
                        }
                        if (routes->condition_ub[wsgi_req->async_id]) {
                                uwsgi_buffer_destroy(routes->condition_ub[wsgi_req->async_id]);
                                routes->condition_ub[wsgi_req->async_id] = NULL;
                        }
	}

}

int uwsgi_apply_routes_do(struct wsgi_request *wsgi_req, char *subject, uint16_t subject_len) {

	struct uwsgi_route *routes = uwsgi.routes;
	int n = -1;

	char *orig_subject = subject;
	uint16_t orig_subject_len = subject_len;

	while (routes) {

		if (routes->label) goto next;

		if (wsgi_req->route_goto > 0 && wsgi_req->route_pc < wsgi_req->route_goto) {
			goto next;
		}

		wsgi_req->route_goto = 0;

		if (!routes->if_func) {
			// could be a "run"
			if (!routes->subject) {
				n = 0;
				goto run;
			}
			if (!subject) {
				char **subject2 = (char **) (((char *) (wsgi_req)) + routes->subject);
				uint16_t *subject_len2 = (uint16_t *) (((char *) (wsgi_req)) + routes->subject_len);
				subject = *subject2 ;
				subject_len = *subject_len2;
			}
			n = uwsgi_regexp_match_ovec(routes->pattern, routes->pattern_extra, subject, subject_len, routes->ovector[wsgi_req->async_id], routes->ovn[wsgi_req->async_id]);
		}
		else {
			int ret = routes->if_func(wsgi_req, routes);
			// error
			if (ret < 0) {
				uwsgi_routing_reset_memory(wsgi_req, routes);
				return UWSGI_ROUTE_BREAK;
			}
			// true
			if (!routes->if_negate) {
				if (ret == 0) {
					uwsgi_routing_reset_memory(wsgi_req, routes);
					goto next;	
				}
				n = ret;
			}
			else {
				if (ret > 0) {
					uwsgi_routing_reset_memory(wsgi_req, routes);
					goto next;	
				}
				n = 1;
			}
		}

run:
		if (n >= 0) {
			wsgi_req->is_routing = 1;
			int ret = routes->func(wsgi_req, routes);
			uwsgi_routing_reset_memory(wsgi_req, routes);
			wsgi_req->is_routing = 0;
			if (ret == UWSGI_ROUTE_BREAK) {
				uwsgi.workers[uwsgi.mywid].cores[wsgi_req->async_id].routed_requests++;
				return ret;
			}
			if (ret == UWSGI_ROUTE_CONTINUE) {
				return ret;
			}
			
			if (ret == -1) {
				return UWSGI_ROUTE_BREAK;
			}
		}
next:
		subject = orig_subject;
		subject_len = orig_subject_len;
		routes = routes->next;
		if (routes) wsgi_req->route_pc++;
	}

	return UWSGI_ROUTE_CONTINUE;
}

int uwsgi_apply_routes(struct wsgi_request *wsgi_req) {

	if (!uwsgi.routes)
		return UWSGI_ROUTE_CONTINUE;

	// avoid loops
	if (wsgi_req->is_routing)
		return UWSGI_ROUTE_CONTINUE;

	if (uwsgi_parse_vars(wsgi_req)) {
		return UWSGI_ROUTE_BREAK;
	}

	// in case of static files serving previous rules could be applied
	if (wsgi_req->routes_applied) {
		return UWSGI_ROUTE_CONTINUE;
	}

	return uwsgi_apply_routes_do(wsgi_req, NULL, 0);
}

static void *uwsgi_route_get_condition_func(char *name) {
	struct uwsgi_route_condition *urc = uwsgi.route_conditions;
	while(urc) {
		if (!strcmp(urc->name, name)) {
			return urc->func;
		}
		urc = urc->next;
	}
	return NULL;
}

void uwsgi_opt_add_route(char *opt, char *value, void *foobar) {

	char *space = NULL;
	char *command = NULL;
	struct uwsgi_route *old_ur = NULL,*ur = uwsgi.routes;
	uint64_t pos = 0;
	while(ur) {
		old_ur = ur;
		ur = ur->next;
		pos++;
	}
	ur = uwsgi_calloc(sizeof(struct uwsgi_route));
	if (old_ur) {
		old_ur->next = ur;
	}
	else {
		uwsgi.routes = ur;
	}

	ur->pos = pos;

	// is it a label ?
	if (foobar == NULL) {
		ur->label = value;
		ur->label_len = strlen(value);
		return;
	}

	ur->orig_route = uwsgi_str(value);

	if (!strcmp(foobar, "run")) {
		command = ur->orig_route;	
		goto done;
	}

	space = strchr(ur->orig_route, ' ');
	if (!space) {
		uwsgi_log("invalid route syntax\n");
		exit(1);
	}

	*space = 0;

	if (!strcmp(foobar, "if") || !strcmp(foobar, "if-not")) {
		char *colon = strchr(ur->orig_route, ':');
		if (!colon) {
			uwsgi_log("invalid route condition syntax\n");
                	exit(1);
		}
		*colon = 0;

		if (!strcmp(foobar, "if-not")) {
			ur->if_negate = 1;
		}

		foobar = colon+1;
		ur->if_func = uwsgi_route_get_condition_func(ur->orig_route);
		if (!ur->if_func) {
			uwsgi_log("unable to find \"%s\" route condition\n", ur->orig_route);
			exit(1);
		}
	}

	else if (!strcmp(foobar, "http_host")) {
		ur->subject = offsetof(struct wsgi_request, host);
		ur->subject_len = offsetof(struct wsgi_request, host_len);
	}
	else if (!strcmp(foobar, "request_uri")) {
		ur->subject = offsetof(struct wsgi_request, uri);
		ur->subject_len = offsetof(struct wsgi_request, uri_len);
	}
	else if (!strcmp(foobar, "query_string")) {
		ur->subject = offsetof(struct wsgi_request, query_string);
		ur->subject_len = offsetof(struct wsgi_request, query_string_len);
	}
	else if (!strcmp(foobar, "remote_addr")) {
		ur->subject = offsetof(struct wsgi_request, remote_addr);
		ur->subject_len = offsetof(struct wsgi_request, remote_addr_len);
	}
	else if (!strcmp(foobar, "user_agent")) {
		ur->subject = offsetof(struct wsgi_request, user_agent);
		ur->subject_len = offsetof(struct wsgi_request, user_agent_len);
	}
	else if (!strcmp(foobar, "referer")) {
		ur->subject = offsetof(struct wsgi_request, referer);
		ur->subject_len = offsetof(struct wsgi_request, referer_len);
	}
	else if (!strcmp(foobar, "remote_user")) {
		ur->subject = offsetof(struct wsgi_request, remote_user);
		ur->subject_len = offsetof(struct wsgi_request, remote_user_len);
	}
	else {
		ur->subject = offsetof(struct wsgi_request, path_info);
		ur->subject_len = offsetof(struct wsgi_request, path_info_len);
	}

	ur->subject_str = foobar;
	ur->subject_str_len = strlen(ur->subject_str);
	ur->regexp = ur->orig_route;

	command = space + 1;
done:
	ur->action = uwsgi_str(command);

	char *colon = strchr(command, ':');
	if (!colon) {
		uwsgi_log("invalid route syntax\n");
		exit(1);
	}

	*colon = 0;

	struct uwsgi_router *r = uwsgi.routers;
	while (r) {
		if (!strcmp(r->name, command)) {
			if (r->func(ur, colon + 1) == 0) {
				return;
			}
			break;
		}
		r = r->next;
	}

	uwsgi_log("unable to register route \"%s\"\n", value);
	exit(1);
}

void uwsgi_fixup_routes() {
	struct uwsgi_route *ur = uwsgi.routes;
	while(ur) {
		// prepare the main pointers
		ur->ovn = uwsgi_calloc(sizeof(int) * uwsgi.cores);
		ur->ovector = uwsgi_calloc(sizeof(int *) * uwsgi.cores);
		ur->condition_ub = uwsgi_calloc( sizeof(struct uwsgi_buffer *) * uwsgi.cores);

		// fill them if needed... (this is an optimization for route with a static subject)
		if (ur->subject && ur->subject_len) {
                	if (uwsgi_regexp_build(ur->orig_route, &ur->pattern, &ur->pattern_extra)) {
                        	exit(1);
                	}

			int i;
			for(i=0;i<uwsgi.cores;i++) {
                		ur->ovn[i] = uwsgi_regexp_ovector(ur->pattern, ur->pattern_extra);
                		if (ur->ovn[i] > 0) {
                        		ur->ovector[i] = uwsgi_calloc(sizeof(int) * (3 * (ur->ovn[i] + 1)));
                		}
			}
		}
		ur = ur->next;
        }
}

int uwsgi_route_api_func(struct wsgi_request *wsgi_req, char *router, char *args) {
	struct uwsgi_route *ur = NULL;
	struct uwsgi_router *r = uwsgi.routers;
	while(r) {
		if (!strcmp(router, r->name)) {
			goto found;
		}
		r = r->next;
	}
	free(args);
	return -1;
found:
	ur = uwsgi_calloc(sizeof(struct uwsgi_route));
	// initialize the virtual route
	if (r->func(ur, args)) {
		free(ur);
		free(args);
		return -1;
	}
	// call it
	int ret = ur->func(wsgi_req, ur);
	if (ur->free) {
		ur->free(ur);
	}
	free(ur);
	free(args);
	return ret;
}

// continue/last route

static int uwsgi_router_continue_func(struct wsgi_request *wsgi_req, struct uwsgi_route *route) {
	return UWSGI_ROUTE_CONTINUE;	
}

static int uwsgi_router_continue(struct uwsgi_route *ur, char *arg) {
	ur->func = uwsgi_router_continue_func;
	return 0;
}

// break route

static int uwsgi_router_break_func(struct wsgi_request *wsgi_req, struct uwsgi_route *route) {
	if (route->data_len >= 3) {
		if (uwsgi_response_prepare_headers(wsgi_req, route->data, route->data_len)) goto end;
		if (uwsgi_response_add_connection_close(wsgi_req)) goto end;
		if (uwsgi_response_add_content_type(wsgi_req, "text/plain", 10)) goto end;
		// no need to check for return value
		uwsgi_response_write_headers_do(wsgi_req);
	}
end:
	return UWSGI_ROUTE_BREAK;	
}

static int uwsgi_router_break(struct uwsgi_route *ur, char *arg) {
	ur->func = uwsgi_router_break_func;
	ur->data = arg;
        ur->data_len = strlen(arg);
	return 0;
}

// flush response
static int transform_flush(struct wsgi_request *wsgi_req, struct uwsgi_transformation *ut) {
	// avoid loops !!!
	if (ut->chunk->pos == 0) return 0;
	wsgi_req->transformed_chunk = ut->chunk->buf;
	wsgi_req->transformed_chunk_len = ut->chunk->pos;
	int ret = uwsgi_response_write_body_do(wsgi_req, ut->chunk->buf, ut->chunk->pos);
	wsgi_req->transformed_chunk = NULL;
	wsgi_req->transformed_chunk_len = 0;
	ut->flushed = 1;
	return ret;
}
static int uwsgi_router_flush_func(struct wsgi_request *wsgi_req, struct uwsgi_route *route) {
	struct uwsgi_transformation *ut = uwsgi_add_transformation(wsgi_req, transform_flush, NULL);
	ut->can_stream = 1;
	return UWSGI_ROUTE_NEXT;	
}
static int uwsgi_router_flush(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_flush_func;
        return 0;
}

// fix content length
static int transform_fixcl(struct wsgi_request *wsgi_req, struct uwsgi_transformation *ut) {
	char buf[sizeof(UMAX64_STR)+1];
        int ret = snprintf(buf, sizeof(UMAX64_STR)+1, "%llu", (unsigned long long) ut->chunk->pos);
        if (ret <= 0 || ret > (int) (sizeof(UMAX64_STR)+1)) {
                wsgi_req->write_errors++;
                return -1;
        }
	// do not check for errors !!!
        uwsgi_response_add_header(wsgi_req, "Content-Length", 14, buf, ret);
	return 0;
}
static int uwsgi_router_fixcl_func(struct wsgi_request *wsgi_req, struct uwsgi_route *route) {
        uwsgi_add_transformation(wsgi_req, transform_fixcl, NULL);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_fixcl(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_fixcl_func;
        return 0;
}


// log route
static int uwsgi_router_log_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {

	char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
	if (!ub) return UWSGI_ROUTE_BREAK;

	uwsgi_log("%.*s\n", ub->pos, ub->buf);
	uwsgi_buffer_destroy(ub);
	return UWSGI_ROUTE_NEXT;	
}

static int uwsgi_router_log(struct uwsgi_route *ur, char *arg) {
	ur->func = uwsgi_router_log_func;
	ur->data = arg;
	ur->data_len = strlen(arg);
	return 0;
}

// do not log !!!
static int uwsgi_router_donotlog_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
	wsgi_req->do_not_log = 1;
	return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_donotlog(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_donotlog_func;
        return 0;
}

// logvar route
static int uwsgi_router_logvar_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {

        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data2, ur->data2_len);
	if (!ub) return UWSGI_ROUTE_BREAK;
	uwsgi_logvar_add(wsgi_req, ur->data, ur->data_len, ub->buf, ub->pos);
	uwsgi_buffer_destroy(ub);

        return UWSGI_ROUTE_NEXT;
}

static int uwsgi_router_logvar(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_logvar_func;
	char *equal = strchr(arg, '=');
	if (!equal) {
		uwsgi_log("invalid logvar syntax, must be key=value\n");
		exit(1);
	}
        ur->data = arg;
        ur->data_len = equal-arg;
	ur->data2 = equal+1;
	ur->data2_len = strlen(ur->data2);
        return 0;
}


// goto route 

static int uwsgi_router_goto_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
	// build the label (if needed)
	char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;

	// find the label
	struct uwsgi_route *routes = uwsgi.routes;
	while(routes) {
		if (!routes->label) goto next;
		if (!uwsgi_strncmp(routes->label, routes->label_len, ub->buf, ub->pos)) {
			wsgi_req->route_goto = routes->pos;
			goto found;
		}
next:
		routes = routes->next;
	}

	wsgi_req->route_goto = ur->custom;
	
found:
	uwsgi_buffer_destroy(ub);
	if (wsgi_req->route_goto <= wsgi_req->route_pc) {
		wsgi_req->route_goto = 0;
		uwsgi_log("[uwsgi-route] ERROR \"goto\" instruction can only jump forward (check your label !!!)\n");
		return UWSGI_ROUTE_BREAK;
	}
	return UWSGI_ROUTE_NEXT;	
}

static int uwsgi_router_goto(struct uwsgi_route *ur, char *arg) {
	ur->func = uwsgi_router_goto_func;
	ur->data = arg;
	ur->data_len = strlen(arg);
	ur->custom = atoi(arg);
        return 0;
}

// addvar route
static int uwsgi_router_addvar_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {

        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data2, ur->data2_len);
        if (!ub) return UWSGI_ROUTE_BREAK;

	if (!uwsgi_req_append(wsgi_req, ur->data, ur->data_len, ub->buf, ub->pos)) {
		uwsgi_buffer_destroy(ub);
        	return UWSGI_ROUTE_BREAK;
	}
	uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}


static int uwsgi_router_addvar(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_addvar_func;
	char *equal = strchr(arg, '=');
	if (!equal) {
		uwsgi_log("[uwsgi-route] invalid addvar syntax, must be KEY=VAL\n");
		exit(1);
	}
	ur->data = arg;
	ur->data_len = equal-arg;
	ur->data2 = equal+1;
	ur->data2_len = strlen(ur->data2);
        return 0;
}


// addheader route
static int uwsgi_router_addheader_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {

        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
	uwsgi_additional_header_add(wsgi_req, ub->buf, ub->pos);
	uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}


static int uwsgi_router_addheader(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_addheader_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}

// remheader route
static int uwsgi_router_remheader_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {

        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
        uwsgi_remove_header(wsgi_req, ub->buf, ub->pos);
	uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}


static int uwsgi_router_remheader(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_remheader_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}



// signal route
static int uwsgi_router_signal_func(struct wsgi_request *wsgi_req, struct uwsgi_route *route) {
	uwsgi_signal_send(uwsgi.signal_socket, route->custom);	
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_signal(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_signal_func;
	ur->custom = atoi(arg);
        return 0;
}

// chdir route
static int uwsgi_router_chdir_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
	char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
	if (!ub) return UWSGI_ROUTE_BREAK;
	if (chdir(ub->buf)) {
		uwsgi_error("uwsgi_router_chdir_func()/chdir()");
		uwsgi_buffer_destroy(ub);
		return UWSGI_ROUTE_BREAK;
	}
	uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_chdir(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_chdir_func;
        ur->data = arg;
	ur->data_len = strlen(arg);
        return 0;
}

// setapp route
static int uwsgi_router_setapp_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
	char *ptr = uwsgi_req_append(wsgi_req, "UWSGI_APPID", 11, ub->buf, ub->pos);
	if (!ptr) {
                uwsgi_buffer_destroy(ub);
                return UWSGI_ROUTE_BREAK;
        }
	wsgi_req->appid = ptr;
	wsgi_req->appid_len = ub->pos;
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_setapp(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_setapp_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}

// setscriptname route
static int uwsgi_router_setscriptname_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
        char *ptr = uwsgi_req_append(wsgi_req, "SCRIPT_NAME", 11, ub->buf, ub->pos);
        if (!ptr) {
                uwsgi_buffer_destroy(ub);
                return UWSGI_ROUTE_BREAK;
        }
        wsgi_req->script_name = ptr;
        wsgi_req->script_name_len = ub->pos;
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_setscriptname(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_setscriptname_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}


// setuser route
static int uwsgi_router_setuser_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
	uint16_t user_len = ub->pos;
	// stop at the first colon (useful for various tricks)
	char *colon = memchr(ub->buf, ':', ub->pos);
	if (colon) {
		user_len = colon - ub->buf;
	}
        char *ptr = uwsgi_req_append(wsgi_req, "REMOTE_USER", 11, ub->buf, user_len);
        if (!ptr) {
                uwsgi_buffer_destroy(ub);
                return UWSGI_ROUTE_BREAK;
        }
        wsgi_req->remote_user = ptr;
        wsgi_req->remote_user_len = ub->pos;
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_setuser(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_setuser_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}


// sethome route
static int uwsgi_router_sethome_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
        char *ptr = uwsgi_req_append(wsgi_req, "UWSGI_HOME", 10, ub->buf, ub->pos);
        if (!ptr) {
                uwsgi_buffer_destroy(ub);
                return UWSGI_ROUTE_BREAK;
        }
        wsgi_req->home = ptr;
        wsgi_req->home_len = ub->pos;
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_sethome(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_sethome_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}

// setfile route
static int uwsgi_router_setfile_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
        char *ptr = uwsgi_req_append(wsgi_req, "UWSGI_HOME", 10, ub->buf, ub->pos);
        if (!ptr) {
                uwsgi_buffer_destroy(ub);
                return UWSGI_ROUTE_BREAK;
        }
        wsgi_req->file = ptr;
        wsgi_req->file_len = ub->pos;
	wsgi_req->dynamic = 1;
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_setfile(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_setfile_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}


// setprocname route
static int uwsgi_router_setprocname_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub) return UWSGI_ROUTE_BREAK;
	uwsgi_set_processname(ub->buf);
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_setprocname(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_setprocname_func;
        ur->data = arg;
        ur->data_len = strlen(arg);
        return 0;
}

// alarm route
static int uwsgi_router_alarm_func(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char **subject = (char **) (((char *)(wsgi_req))+ur->subject);
        uint16_t *subject_len = (uint16_t *)  (((char *)(wsgi_req))+ur->subject_len);

        struct uwsgi_buffer *ub_alarm = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data, ur->data_len);
        if (!ub_alarm) return UWSGI_ROUTE_BREAK;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, *subject, *subject_len, ur->data2, ur->data2_len);
        if (!ub) {
		uwsgi_buffer_destroy(ub_alarm);
		return UWSGI_ROUTE_BREAK;
	}
	uwsgi_alarm_trigger(ub_alarm->buf, ub->buf, ub->pos);	
        uwsgi_buffer_destroy(ub_alarm);
        uwsgi_buffer_destroy(ub);
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_alarm(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_alarm_func;
	char *space = strchr(arg, ' ');
	if (!space) {
		return -1;
	}
	*space = 0;
        ur->data = arg;
        ur->data_len = strlen(arg);
        ur->data2 = space+1;
        ur->data2_len = strlen(ur->data2);
        return 0;
}



// send route
static int uwsgi_router_send_func(struct wsgi_request *wsgi_req, struct uwsgi_route *route) {
	uwsgi_response_write_body_do(wsgi_req, route->data, route->data_len);
	if (route->custom) {
		uwsgi_response_write_body_do(wsgi_req, "\r\n", 2);
	}
        return UWSGI_ROUTE_NEXT;
}
static int uwsgi_router_send(struct uwsgi_route *ur, char *arg) {
        ur->func = uwsgi_router_send_func;
	ur->data = arg;
	ur->data_len = strlen(arg);
        return 0;
}
static int uwsgi_router_send_crnl(struct uwsgi_route *ur, char *arg) {
	uwsgi_router_send(ur, arg);
        ur->custom = 1;
        return 0;
}

static int uwsgi_route_condition_exists(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
	if (!ub) return -1;
	if (uwsgi_file_exists(ub->buf)) {
		uwsgi_buffer_destroy(ub);
		return 1;
	}
	uwsgi_buffer_destroy(ub);
	return 0;
}

static int uwsgi_route_condition_isfile(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
        if (!ub) return -1;
        if (uwsgi_is_file(ub->buf)) {
                uwsgi_buffer_destroy(ub);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        return 0;
}

static int uwsgi_route_condition_regexp(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;

        ur->condition_ub[wsgi_req->async_id] = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ur->condition_ub[wsgi_req->async_id]) return -1;

	pcre *pattern;
	pcre_extra *pattern_extra;
	char *re = uwsgi_concat2n(semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str), "", 0);
	if (uwsgi_regexp_build(re, &pattern, &pattern_extra)) {
		free(re);
		return -1;
	}
	free(re);

	// a condition has no initialized vectors, let's create them
	ur->ovn[wsgi_req->async_id] = uwsgi_regexp_ovector(pattern, pattern_extra);
        if (ur->ovn[wsgi_req->async_id] > 0) {
        	ur->ovector[wsgi_req->async_id] = uwsgi_calloc(sizeof(int) * (3 * (ur->ovn[wsgi_req->async_id] + 1)));
        }

	if (uwsgi_regexp_match_ovec(pattern, pattern_extra, ur->condition_ub[wsgi_req->async_id]->buf, ur->condition_ub[wsgi_req->async_id]->pos, ur->ovector[wsgi_req->async_id], ur->ovn[wsgi_req->async_id] ) >= 0) {
		pcre_free(pattern);
#ifdef PCRE_STUDY_JIT_COMPILE
		pcre_free_study(pattern_extra);
#else
		pcre_free(pattern_extra);
#endif
		return 1;
	}

	pcre_free(pattern);
#ifdef PCRE_STUDY_JIT_COMPILE
	pcre_free_study(pattern_extra);
#else
	pcre_free(pattern_extra);
#endif
        return 0;
}

static int uwsgi_route_condition_empty(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
        if (!ub) return -1;

	if (ub->pos == 0) {
        	uwsgi_buffer_destroy(ub);
        	return 1;
	}

        uwsgi_buffer_destroy(ub);
        return 0;
}


static int uwsgi_route_condition_equal(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
	char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
	if (!semicolon) return 0;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

	struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
		uwsgi_buffer_destroy(ub);
		return -1;
	}

	if(!uwsgi_strncmp(ub->buf, ub->pos, ub2->buf, ub2->pos)) {
		uwsgi_buffer_destroy(ub);
		uwsgi_buffer_destroy(ub2);
		return 1;
	}
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}

static int uwsgi_route_condition_higher(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

	long num1 = strtol(ub->buf, NULL, 10);
	long num2 = strtol(ub2->buf, NULL, 10);
        if(num1 > num2) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}

static int uwsgi_route_condition_higherequal(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

        long num1 = strtol(ub->buf, NULL, 10);
        long num2 = strtol(ub2->buf, NULL, 10);
        if(num1 >= num2) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}


static int uwsgi_route_condition_lower(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;
        
        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

        long num1 = strtol(ub->buf, NULL, 10);
        long num2 = strtol(ub2->buf, NULL, 10);
        if(num1 < num2) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}

static int uwsgi_route_condition_lowerequal(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;
        
        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

        long num1 = strtol(ub->buf, NULL, 10);
        long num2 = strtol(ub2->buf, NULL, 10);
        if(num1 <= num2) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}

#ifdef UWSGI_SSL
static int uwsgi_route_condition_lord(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
	struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
        if (!ub) return -1;
        int ret = uwsgi_legion_i_am_the_lord(ub->buf);
        uwsgi_buffer_destroy(ub);
        return ret;
}
#endif



static int uwsgi_route_condition_startswith(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

        if(!uwsgi_starts_with(ub->buf, ub->pos, ub2->buf, ub2->pos)) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}

static int uwsgi_route_condition_contains(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

        if(uwsgi_contains_n(ub->buf, ub->pos, ub2->buf, ub2->pos)) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}

static int uwsgi_route_condition_endswith(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        char *semicolon = memchr(ur->subject_str, ';', ur->subject_str_len);
        if (!semicolon) return 0;

        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, semicolon - ur->subject_str);
        if (!ub) return -1;

        struct uwsgi_buffer *ub2 = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, semicolon+1, ur->subject_str_len - ((semicolon+1) - ur->subject_str));
        if (!ub2) {
                uwsgi_buffer_destroy(ub);
                return -1;
        }

	if (ub2->pos > ub->pos) goto zero;
        if(!uwsgi_strncmp(ub->buf + (ub->pos - ub2->pos), ub2->pos, ub2->buf, ub2->pos)) {
                uwsgi_buffer_destroy(ub);
                uwsgi_buffer_destroy(ub2);
                return 1;
        }

zero:
        uwsgi_buffer_destroy(ub);
        uwsgi_buffer_destroy(ub2);
        return 0;
}



static int uwsgi_route_condition_isdir(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
        if (!ub) return -1;
        if (uwsgi_is_dir(ub->buf)) {
                uwsgi_buffer_destroy(ub);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        return 0;
}

static int uwsgi_route_condition_islink(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
        if (!ub) return -1;
        if (uwsgi_is_link(ub->buf)) {
                uwsgi_buffer_destroy(ub);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        return 0;
}


static int uwsgi_route_condition_isexec(struct wsgi_request *wsgi_req, struct uwsgi_route *ur) {
        struct uwsgi_buffer *ub = uwsgi_routing_translate(wsgi_req, ur, NULL, 0, ur->subject_str, ur->subject_str_len);
        if (!ub) return -1;
        if (!access(ub->buf, X_OK)) {
                uwsgi_buffer_destroy(ub);
                return 1;
        }
        uwsgi_buffer_destroy(ub);
        return 0;
}

static char *uwsgi_route_var_uwsgi(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
	char *ret = NULL;
	if (!uwsgi_strncmp(key, keylen, "wid", 3)) {
		ret = uwsgi_num2str(uwsgi.mywid);
		*vallen = strlen(ret);
	}
	else if (!uwsgi_strncmp(key, keylen, "pid", 3)) {
		ret = uwsgi_num2str(uwsgi.mypid);
		*vallen = strlen(ret);
	}
	else if (!uwsgi_strncmp(key, keylen, "uuid", 4)) {
		ret = uwsgi_malloc(37);
		uwsgi_uuid(ret);
		*vallen = 36;
	}

	return ret;
}

static char *uwsgi_route_var_mime(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
	char *ret = NULL;
        uint16_t var_vallen = 0;
        char *var_value = uwsgi_get_var(wsgi_req, key, keylen, &var_vallen);
        if (var_value) {
		size_t mime_type_len = 0;
		char *ret = uwsgi_get_mime_type(key, keylen, &mime_type_len);
		if (ret) *vallen = mime_type_len;
        }
        return ret;
}

static char *uwsgi_route_var_httptime(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
        // 30+1
        char *ht = uwsgi_calloc(31);
	size_t t = uwsgi_str_num(key, keylen);
        int len = uwsgi_http_date(uwsgi_now() + t, ht);
	if (len == 0) {
		free(ht);
		return NULL;
	}
	*vallen = len;
        return ht;
}


static char *uwsgi_route_var_time(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
        char *ret = NULL;
        if (!uwsgi_strncmp(key, keylen, "unix", 4)) {
                ret = uwsgi_num2str(uwsgi_now());
                *vallen = strlen(ret);
        }
        return ret;
}

static char *uwsgi_route_var_base64(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
	char *ret = NULL;
	uint16_t var_vallen = 0;
        char *var_value = uwsgi_get_var(wsgi_req, key, keylen, &var_vallen);
	if (var_value) {
		size_t b64_len = 0;
		ret = uwsgi_base64_encode(var_value, var_vallen, &b64_len);
		*vallen = b64_len;
	}
        return ret;
}

static char *uwsgi_route_var_hex(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
        char *ret = NULL;
        uint16_t var_vallen = 0;
        char *var_value = uwsgi_get_var(wsgi_req, key, keylen, &var_vallen);
        if (var_value) {
                ret = uwsgi_str_to_hex(var_value, var_vallen);
                *vallen = var_vallen*2;
        }
        return ret;
}

#ifdef UWSGI_MATHEVAL
static char *uwsgi_route_var_math(struct wsgi_request *wsgi_req, char *key, uint16_t keylen, uint16_t *vallen) {
	char *ret = NULL;
	// avoid crash	
	if (!wsgi_req->var_cnt) return NULL;
	// we make a bit of fun here, we do a copy of the vars buffer (+1 byte for final zero) and zeor-pad all of the strings
	char *vars_buf = uwsgi_malloc(wsgi_req->uh->pktsize + keylen + 1);
	char **names = uwsgi_malloc(sizeof(char *) * (wsgi_req->var_cnt/2));
	double *values = uwsgi_calloc(sizeof(double) * (wsgi_req->var_cnt/2));
	int i,j = 0;
	char *ptr = vars_buf;
	for (i = wsgi_req->var_cnt-1; i > 0; i -= 2) {
		memcpy(ptr, wsgi_req->hvec[i-1].iov_base, wsgi_req->hvec[i-1].iov_len);	
		names[j] = ptr;
		ptr += wsgi_req->hvec[i-1].iov_len;
		*ptr++=0;
		char *num = ptr;
		memcpy(ptr, wsgi_req->hvec[i].iov_base, wsgi_req->hvec[i].iov_len);
		ptr += wsgi_req->hvec[i].iov_len;
                *ptr++=0;
		values[j] = strtod(num, NULL);
		j++;
        }

	char *expr = ptr;
	memcpy(ptr, key, keylen); ptr += keylen;
	*ptr++=0;

	void *e = evaluator_create(expr);
        if (!e) goto end;
        double n = evaluator_evaluate(e, j, names, values);
        evaluator_destroy(e);
	ret = uwsgi_num2str((int)n);
	*vallen = strlen(ret);
end:
	free(vars_buf);
	free(names);
	free(values);
	return ret;
}
#endif

// register embedded routers
void uwsgi_register_embedded_routers() {
	uwsgi_register_router("continue", uwsgi_router_continue);
        uwsgi_register_router("last", uwsgi_router_continue);
        uwsgi_register_router("break", uwsgi_router_break);
        uwsgi_register_router("log", uwsgi_router_log);
        uwsgi_register_router("donotlog", uwsgi_router_donotlog);
        uwsgi_register_router("logvar", uwsgi_router_logvar);
        uwsgi_register_router("goto", uwsgi_router_goto);
        uwsgi_register_router("addvar", uwsgi_router_addvar);
        uwsgi_register_router("addheader", uwsgi_router_addheader);
        uwsgi_register_router("delheader", uwsgi_router_remheader);
        uwsgi_register_router("remheader", uwsgi_router_remheader);
        uwsgi_register_router("signal", uwsgi_router_signal);
        uwsgi_register_router("send", uwsgi_router_send);
        uwsgi_register_router("send-crnl", uwsgi_router_send_crnl);
        uwsgi_register_router("chdir", uwsgi_router_chdir);
        uwsgi_register_router("setapp", uwsgi_router_setapp);
        uwsgi_register_router("setuser", uwsgi_router_setuser);
        uwsgi_register_router("sethome", uwsgi_router_sethome);
        uwsgi_register_router("setfile", uwsgi_router_setfile);
        uwsgi_register_router("setscriptname", uwsgi_router_setscriptname);
        uwsgi_register_router("setprocname", uwsgi_router_setprocname);
        uwsgi_register_router("alarm", uwsgi_router_alarm);

        uwsgi_register_router("flush", uwsgi_router_flush);
        uwsgi_register_router("fixcl", uwsgi_router_fixcl);

        uwsgi_register_route_condition("exists", uwsgi_route_condition_exists);
        uwsgi_register_route_condition("isfile", uwsgi_route_condition_isfile);
        uwsgi_register_route_condition("isdir", uwsgi_route_condition_isdir);
        uwsgi_register_route_condition("islink", uwsgi_route_condition_islink);
        uwsgi_register_route_condition("isexec", uwsgi_route_condition_isexec);
        uwsgi_register_route_condition("equal", uwsgi_route_condition_equal);
        uwsgi_register_route_condition("isequal", uwsgi_route_condition_equal);
        uwsgi_register_route_condition("eq", uwsgi_route_condition_equal);
        uwsgi_register_route_condition("==", uwsgi_route_condition_equal);
        uwsgi_register_route_condition("startswith", uwsgi_route_condition_startswith);
        uwsgi_register_route_condition("endswith", uwsgi_route_condition_endswith);
        uwsgi_register_route_condition("regexp", uwsgi_route_condition_regexp);
        uwsgi_register_route_condition("re", uwsgi_route_condition_regexp);
        uwsgi_register_route_condition("ishigher", uwsgi_route_condition_higher);
        uwsgi_register_route_condition(">", uwsgi_route_condition_higher);
        uwsgi_register_route_condition("islower", uwsgi_route_condition_lower);
        uwsgi_register_route_condition("<", uwsgi_route_condition_lower);
        uwsgi_register_route_condition("ishigherequal", uwsgi_route_condition_higherequal);
        uwsgi_register_route_condition(">=", uwsgi_route_condition_higherequal);
        uwsgi_register_route_condition("islowerequal", uwsgi_route_condition_lowerequal);
        uwsgi_register_route_condition("<=", uwsgi_route_condition_lowerequal);
        uwsgi_register_route_condition("contains", uwsgi_route_condition_contains);
        uwsgi_register_route_condition("contain", uwsgi_route_condition_contains);
#ifdef UWSGI_SSL
        uwsgi_register_route_condition("lord", uwsgi_route_condition_lord);
#endif

        uwsgi_register_route_condition("empty", uwsgi_route_condition_empty);

        uwsgi_register_route_var("cookie", uwsgi_get_cookie);
        uwsgi_register_route_var("qs", uwsgi_get_qs);
        uwsgi_register_route_var("mime", uwsgi_route_var_mime);
        struct uwsgi_route_var *urv = uwsgi_register_route_var("uwsgi", uwsgi_route_var_uwsgi);
	urv->need_free = 1;
        urv = uwsgi_register_route_var("time", uwsgi_route_var_time);
	urv->need_free = 1;
        urv = uwsgi_register_route_var("httptime", uwsgi_route_var_httptime);
	urv->need_free = 1;
#ifdef UWSGI_MATHEVAL
        urv = uwsgi_register_route_var("math", uwsgi_route_var_math);
	urv->need_free = 1;
#endif
        urv = uwsgi_register_route_var("base64", uwsgi_route_var_base64);
	urv->need_free = 1;

        urv = uwsgi_register_route_var("hex", uwsgi_route_var_hex);
	urv->need_free = 1;
}

struct uwsgi_router *uwsgi_register_router(char *name, int (*func) (struct uwsgi_route *, char *)) {

	struct uwsgi_router *ur = uwsgi.routers;
	if (!ur) {
		uwsgi.routers = uwsgi_calloc(sizeof(struct uwsgi_router));
		uwsgi.routers->name = name;
		uwsgi.routers->func = func;
		return uwsgi.routers;
	}

	while (ur) {
		if (!ur->next) {
			ur->next = uwsgi_calloc(sizeof(struct uwsgi_router));
			ur->next->name = name;
			ur->next->func = func;
			return ur->next;
		}
		ur = ur->next;
	}

	return NULL;

}

struct uwsgi_route_condition *uwsgi_register_route_condition(char *name, int (*func) (struct wsgi_request *, struct uwsgi_route *)) {
	struct uwsgi_route_condition *old_urc = NULL,*urc = uwsgi.route_conditions;
	while(urc) {
		if (!strcmp(urc->name, name)) {
			return urc;
		}
		old_urc = urc;
		urc = urc->next;
	}

	urc = uwsgi_calloc(sizeof(struct uwsgi_route_condition));
	urc->name = name;
	urc->func = func;

	if (old_urc) {
		old_urc->next = urc;
	}
	else {
		uwsgi.route_conditions = urc;
	}

	return urc;
}

void uwsgi_routing_dump() {
	struct uwsgi_route *routes = uwsgi.routes;
	if (!routes) return;
	uwsgi_log("*** dumping internal routing table ***\n");
	while(routes) {
		if (routes->label) {
			uwsgi_log("[rule: %llu] label: %s\n", (unsigned long long ) routes->pos, routes->label);
		}
		else if (!routes->subject_str && !routes->if_func) {
			uwsgi_log("[rule: %llu] action: %s\n", (unsigned long long ) routes->pos, routes->action);
		}
		else {
			uwsgi_log("[rule: %llu] subject: %s %s: %s%s action: %s\n", (unsigned long long ) routes->pos, routes->subject_str, routes->if_func ? "func" : "regexp", routes->if_negate ? "!" : "", routes->regexp, routes->action);
		}
		routes = routes->next;
	}
	uwsgi_log("*** end of the internal routing table ***\n");
}
#endif
