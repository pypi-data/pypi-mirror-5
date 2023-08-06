#include "Python.h"

static PyObject* escape_content(PyObject* self, PyObject* args) {
	PyObject* text;

	if(!PyArg_ParseTuple(args, "O", &text)) {
		return NULL;
	}

	if(!PyUnicode_CheckExact(text)) {
		PyErr_SetString(PyExc_TypeError, "escape_content()’s argument must be a string");
		return NULL;
	}

	if(PyUnicode_READY(text)) {
		return NULL;
	}

	const int kind = PyUnicode_KIND(text);
	const void* data = PyUnicode_DATA(text);
	const Py_ssize_t original_length = PyUnicode_GET_LENGTH(text);
	Py_ssize_t additional = 0;
	Py_ssize_t i;

	for(i = 0; i < original_length; i++) {
		Py_UCS4 c = PyUnicode_READ(kind, data, i);

		switch(c) {
			case '&':
				additional += 4;
				break;
			case '<':
			case '>':
				additional += 3;
				break;
		}
	}

	if(!additional) {
		Py_INCREF(text);
		return text;
	}

	const void* escaped_data = malloc(kind * (original_length + additional));
	Py_ssize_t escaped_index = 0;

	for(i = 0; i < original_length; i++) {
		Py_UCS4 c = PyUnicode_READ(kind, data, i);

		switch(c) {
			case '&':
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, '&');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'a');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'm');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'p');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, ';');
				break;
			case '<':
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, '&');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'l');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 't');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, ';');
				break;
			case '>':
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, '&');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'g');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 't');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, ';');
				break;
			default:
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, c);
		}
	}

	return PyUnicode_FromKindAndData(kind, escaped_data, original_length + additional);
}

static PyObject* escape_attribute_value(PyObject* self, PyObject* args) {
	PyObject* text;

	if(!PyArg_ParseTuple(args, "O", &text)) {
		return NULL;
	}

	if(!PyUnicode_CheckExact(text)) {
		PyErr_SetString(PyExc_TypeError, "escape_attribute_value()’s argument must be a string");
		return NULL;
	}

	if(PyUnicode_READY(text)) {
		return NULL;
	}

	const int kind = PyUnicode_KIND(text);
	const void* data = PyUnicode_DATA(text);
	const Py_ssize_t original_length = PyUnicode_GET_LENGTH(text);
	Py_ssize_t additional = 0;
	Py_ssize_t i;

	for(i = 0; i < original_length; i++) {
		Py_UCS4 c = PyUnicode_READ(kind, data, i);

		switch(c) {
			case '&':
				additional += 4;
				break;
			case '"':
				additional += 5;
				break;
		}
	}

	if(!additional) {
		Py_INCREF(text);
		return text;
	}

	const void* escaped_data = malloc(kind * (original_length + additional));
	Py_ssize_t escaped_index = 0;

	for(i = 0; i < original_length; i++) {
		Py_UCS4 c = PyUnicode_READ(kind, data, i);

		switch(c) {
			case '&':
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, '&');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'a');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'm');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'p');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, ';');
				break;
			case '"':
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, '&');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'q');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'u');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 'o');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, 't');
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, ';');
				break;
			default:
				PyUnicode_WRITE(kind, escaped_data, escaped_index++, c);
		}
	}

	return PyUnicode_FromKindAndData(kind, escaped_data, original_length + additional);
}

static PyMethodDef EscapeMethods[] = {
	{"escape_content", escape_content, METH_VARARGS, "Escapes text for use as content in HTML."},
	{"escape_attribute_value", escape_attribute_value, METH_VARARGS, "Escapes text for use as part of an attribute value in HTML."},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef escape = {
	PyModuleDef_HEAD_INIT,
	"leafblade_escape",
	NULL,
	-1,
	EscapeMethods
};

PyMODINIT_FUNC PyInit_leafblade_escape(void) {
	return PyModule_Create(&escape);
}
