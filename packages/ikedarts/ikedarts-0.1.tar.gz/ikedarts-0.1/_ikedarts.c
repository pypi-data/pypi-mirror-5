#include "ikedarts.h"
#include <Python.h>
#include <assert.h>

static char module_docstring[]="darts interface";

/****
no need to export this since python's dtr calls this.
extern void ikedarts_finish(struct ikedarts *ikd);

consider exporting these:
extern int ikedarts_match(struct ikedarts *ikd, const char *text, visit_t);
extern int ikedarts_markup(const char *index_path);
extern int ikedarts_main(int argc, char **argv) ;
****/

static int _dump_match(const char* text, 
		       unsigned int off, 
		       unsigned int length, 
		       int value, 
		       void *data) 
{
	PyObject *cb_po=(PyObject*)data;
	// char *tok=strndup(text, length);

	if (!PyCallable_Check(cb_po)) {
		PyErr_SetString(PyExc_TypeError, "visit must be callable");
		return -1;	/* todo: abort result traversal. return error status from search. */
        }

	PyObject *cb_args=Py_BuildValue("(siii)", text, off, length, value);
	PyObject *result=PyEval_CallObject(cb_po, cb_args);
				/* forward result */
	if (PyBool_Check(result) && Py_True==result) {
		return 1;	/* todo: implement 1=>stop in search */
	}

	return 0;
}

void _ikd_dtr(void*ikd) 
{
	// debug("_IKD_DTR:\n");
	assert(ikd);
	ikedarts_finish(ikd);
	free(ikd);
}

/* 
 * struct ikedarts *ikedarts_init(struct ikedarts *ikd);
 */
static char ikedarts_init_docstring[]="attach the darts index file";
static PyObject *_ikedarts_init(PyObject *self, PyObject *args)
{
	struct ikedarts *ikd;

	ikd=ikedarts_init(NULL);
	if (!ikd) {
		PyErr_SetString(PyExc_TypeError, "ikedarts_init failed.");
		return NULL;
        }

	//2.7 return PyCapsule_New(ikd, NULL,); 
	return PyCObject_FromVoidPtr(ikd, _ikd_dtr);
	/* do I have to incref? */
}

/* 
 * extern int ikedarts_open(struct ikedarts *ikd, const char *index_path);
 */
static char ikedarts_open_docstring[]="attach the darts index file";
static PyObject *_ikedarts_open(PyObject *self, PyObject *args)
{
	PyObject *ikd_po, *index_path_po;
				/* unpack */
	if (!PyArg_ParseTuple(args, "OO", &ikd_po, &index_path_po)) {
		PyErr_SetString(PyExc_TypeError, "arg error");
		return NULL;
	}

	const char *index_path=PyString_AsString(PyObject_Str(index_path_po));
				/* check */
	if (!PyCObject_Check(ikd_po)) {
		PyErr_SetString(PyExc_TypeError, "expected a PyCObject");
		return NULL;
	}
				/* cast */
	struct ikedarts *ikd=(struct ikedarts *)PyCObject_AsVoidPtr(ikd_po);

	if (ikedarts_open(ikd, index_path)!=0) {
		PyErr_SetString(PyExc_TypeError, "open failed");
		return NULL;
	}

	/* xxx return something sensible for success.. */
	Py_INCREF(Py_None);
	return Py_None;
}

/* 
 * extern int ikedarts_search(struct ikedarts *ikd, const char *text, visit_t);
 */
static char ikedarts_search_docstring[]="search world";
static PyObject *_ikedarts_search(PyObject *self, PyObject *args)
{
	PyObject *ikd_po, *text_po, *cb_po;

	if (!PyArg_ParseTuple(args, "OOO", &ikd_po, &text_po, &cb_po)) {
		PyErr_SetString(PyExc_TypeError, "arg error");
		return NULL;
	}

	if (!PyCObject_Check(ikd_po)) {
		PyErr_SetString(PyExc_TypeError, "expected an object..");
		return NULL;
	}
	struct ikedarts *ikd=(struct ikedarts *)PyCObject_AsVoidPtr(ikd_po);

	/* xxx check string */
	if (!PyCallable_Check(cb_po)) {
		PyErr_SetString(PyExc_TypeError, "visit must be callable");
		return NULL;
        }

	const char *text=PyString_AsString(PyObject_Str(text_po));

	// xx map this over
	ikedarts_search(ikd, text, _dump_match, cb_po);

	Py_INCREF(Py_None);
	return Py_None;
}

static char ikedarts_hello_docstring[]="hello world";
static PyObject *_ikedarts_hello(PyObject *self, PyObject *args)
{
	PyObject *result;
	PyObject *cb_args;
	PyObject *fun;

				/* unpack args */
	if (!PyArg_ParseTuple(args, "O", &fun)) {
		PyErr_SetString(PyExc_TypeError, "arg error");
		return NULL;
	}
				/* ensure callable */
	if (!PyCallable_Check(fun)) {
		PyErr_SetString(PyExc_TypeError, "parameter must be callable");
		return NULL;
        }
				/* create args */
	cb_args=Py_BuildValue("(i)", 42);
				/* call */
	result = PyEval_CallObject(fun, cb_args);
				/* cleanup */
	Py_DECREF(cb_args);
				/* supposedly the cannonical approach to returning None */
	Py_INCREF(Py_None);
	return Py_None;
}

////////////////
static PyMethodDef module_methods[] = {
	{"ikedarts_init", _ikedarts_init, METH_VARARGS, ikedarts_init_docstring},
	{"ikedarts_open", _ikedarts_open, METH_VARARGS, ikedarts_open_docstring},
	{"ikedarts_search", _ikedarts_search, METH_VARARGS, ikedarts_search_docstring},
	{"ikedarts_hello", _ikedarts_hello, METH_VARARGS, ikedarts_hello_docstring},
	{NULL, NULL, 0, NULL}
};

/*
 *  module initialization (not instance ctor)
 */
PyMODINIT_FUNC init_ikedarts(void)
{
    PyObject *m = Py_InitModule3("_ikedarts", module_methods, module_docstring);
    if (m == NULL)
        return;
    /* ... */
}
