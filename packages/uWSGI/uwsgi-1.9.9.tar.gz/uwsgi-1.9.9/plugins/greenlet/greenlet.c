#include "../python/uwsgi_python.h"
#include <greenlet/greenlet.h>

extern struct uwsgi_server uwsgi;
extern struct uwsgi_python up;

struct ugreenlet {
	int enabled;
	PyObject *callable;
	PyGreenlet *main;
	PyGreenlet **gl;
} ugl;

static struct uwsgi_option greenlet_options[] = {
	{"greenlet", no_argument, 0, "enable greenlet as suspend engine", uwsgi_opt_true, &ugl.enabled, 0},
	{ 0, 0, 0, 0, 0, 0, 0 }
};

static void gil_greenlet_get() {
        pthread_setspecific(up.upt_gil_key, (void *) PyGILState_Ensure());
}

static void gil_greenlet_release() {
        PyGILState_Release((PyGILState_STATE) pthread_getspecific(up.upt_gil_key));
}

static PyObject *py_uwsgi_greenlet_request(PyObject * self, PyObject *args) {

	async_schedule_to_req_green();

	Py_DECREF(ugl.gl[uwsgi.wsgi_req->async_id]);

	Py_INCREF(Py_None);
	return Py_None;
}

PyMethodDef uwsgi_greenlet_request_method[] = {{"uwsgi_greenlet_request", py_uwsgi_greenlet_request, METH_VARARGS, ""}};

static void greenlet_schedule_to_req() {

	int id = uwsgi.wsgi_req->async_id;
	uint8_t modifier1 = uwsgi.wsgi_req->uh->modifier1;

        // ensure gil
        UWSGI_GET_GIL

	if (!uwsgi.wsgi_req->suspended) {
		ugl.gl[id] = PyGreenlet_New(ugl.callable, NULL);
		uwsgi.wsgi_req->suspended = 1;
	}

	// call it in the main core
        if (uwsgi.p[modifier1]->suspend) {
                uwsgi.p[modifier1]->suspend(NULL);
        }

	PyGreenlet_Switch(ugl.gl[id], NULL, NULL);

	if (uwsgi.p[modifier1]->resume) {
                uwsgi.p[modifier1]->resume(NULL);
        }


}

static void greenlet_schedule_to_main(struct wsgi_request *wsgi_req) {

	// ensure gil
        UWSGI_GET_GIL

        if (uwsgi.p[wsgi_req->uh->modifier1]->suspend) {
                uwsgi.p[wsgi_req->uh->modifier1]->suspend(wsgi_req);
        }
	PyGreenlet_Switch(ugl.main, NULL, NULL);
        if (uwsgi.p[wsgi_req->uh->modifier1]->resume) {
                uwsgi.p[wsgi_req->uh->modifier1]->resume(wsgi_req);
        }
	uwsgi.wsgi_req = wsgi_req;
}


static void greenlet_init_apps(void) {

	if (!ugl.enabled) return;

	if (uwsgi.async <= 1) {
                uwsgi_log("the greenlet suspend engine requires async mode\n");
                exit(1);
        }

	if (uwsgi.has_threads) {
                up.gil_get = gil_greenlet_get;
                up.gil_release = gil_greenlet_release;
        }

        // blindy call it as the stackless gil engine is already set
        UWSGI_GET_GIL


	PyGreenlet_Import();

	ugl.gl = uwsgi_malloc( sizeof(PyGreenlet *) * uwsgi.async );
	ugl.main = PyGreenlet_GetCurrent();
	ugl.callable = PyCFunction_New(uwsgi_greenlet_request_method, NULL);
	uwsgi_log("enabled greenlet engine\n");

	uwsgi.schedule_to_main = greenlet_schedule_to_main;
	uwsgi.schedule_to_req = greenlet_schedule_to_req;
}

struct uwsgi_plugin greenlet_plugin = {

	.name = "greenlet",
	.init_apps = greenlet_init_apps,
	.options = greenlet_options,
};
