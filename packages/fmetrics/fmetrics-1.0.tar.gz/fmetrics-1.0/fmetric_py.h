/*
 * Python module
 */


#include<Python.h>


typedef struct {
    PyObject* results;
    int error_code;
} resourcesStruct, Resources;

void precision(Image target, Image source, int radius, PyObject* list, int i) {
    float precision = dist_match(target, source, radius);
    PyList_SetItem(list, i, Py_BuildValue("f", precision));
}

void recall(Image target, Image source, int radius, PyObject* list, int i) {
    float recall = dist_match(source, target, radius);
    PyList_SetItem(list, i, Py_BuildValue("f", recall));
}

void fmeasure(Image target, Image source, int radius, PyObject* list, int i) {
    float precision = dist_match(target, source, radius);
    float recall = dist_match(source, target, radius);
    float fmeasure = 2 * precision * recall / (precision + recall);
    
    PyList_SetItem(list, i, Py_BuildValue("[f,f,f]", precision, recall, fmeasure));
}

Resources apply_function(PyObject* self, PyObject* args, void (*function)(Image target, Image source, int radius, PyObject* list, int i)) {
    PyObject* s_filesnames;
    PyObject* radii;
    PyObject* results;
    PyObject* source_i;

    Resources resources;

    char* t_filename;
    Image source;
    Image target;
    
    int error_code = 0;

    if (!PyArg_ParseTuple(args, "sOO", &t_filename, &s_filesnames, &radii)) {
        error_code = 9;
        goto done;
    }

    target = read_image(t_filename);
    if (isnull(target)) {
        PyErr_SetString(PyExc_IOError, "Unable to read target image.");
        error_code = 1;
        goto done;
    }
    
    //Get the sequence of sources file name.
    s_filesnames = PySequence_Fast(s_filesnames, "Argument must be iterable");
    if (!s_filesnames) {
        error_code = 2;
        goto done;
    }
    int n_sources = PySequence_Fast_GET_SIZE(s_filesnames);

    //Get the sequence of radii.
    radii = PySequence_Fast(radii, "Argument must be iterable");
    if (!radii) {
        error_code = 3;
        goto done;
    }
    int n_radii = PySequence_Fast_GET_SIZE(radii); 

    char* s_filename;
    results = PyList_New(n_sources);
    for (int i = 0; i < n_sources; i++) {
        //Get element from python sequence and converts it to string.        
        PyObject* s_filesnames_el = PySequence_Fast_GET_ITEM(s_filesnames, i);
        if (!s_filesnames_el) {
            PyErr_SetString(PyExc_StandardError, "Unable to get element from sequence of sources file name.");
            error_code = 4;
            goto done;
        }
        if (!(s_filename = PyString_AsString(s_filesnames_el))) {
            PyErr_SetString(PyExc_TypeError, "Sources files name must be of type string.");
            error_code = 5;
            goto done;
        } 

        source = read_image(s_filename);
        if (isnull( source )) {
            //sprintf(errormsg, "Unable to read source image %s.", s_filename);
            PyErr_SetString(PyExc_IOError, "Unable to read source image.");
            error_code = 6;
            goto done;
        }

        source_i = PyList_New(n_radii);
        int r;
        for (int j = 0; j < n_radii; j++) {
            //Get element from python sequence and converts it to an integer.        
            PyObject* radii_el = PySequence_Fast_GET_ITEM(radii, j);
            if (!radii_el) {
                PyErr_SetString(PyExc_StandardError, "Unable to get element from sequence of radii.");
                error_code = 7;
                goto done;
            }
            if (!(r = PyInt_AsLong(radii_el))) {
                PyErr_SetString(PyExc_TypeError, "Radii must be of type int.");
                error_code = 8;
                goto done;
            }

            if (r < 1 || r > 100) {
                PyErr_SetString(PyExc_StandardError, "The radii must be in the range [1,100].");
                error_code = 10;
                goto done;
            }

            function(target, source, r, source_i, j);
        }
        PyList_SetItem(results, i, Py_BuildValue("O", source_i));
        img_free(source);
    }

    done:

    if (!isnull(target)) img_free(target);
    //if (!isnull(source)) img_free(source);

    Py_DECREF(s_filesnames);
    Py_DECREF(radii);
    Py_DECREF(source_i);

    resources.results = results;
    resources.error_code = error_code;

    if (error_code != 0) {
        Py_DECREF(results);
        resources.results = Py_None;
    }

    return resources;
}

static PyObject* fmetrics_precision(PyObject* self, PyObject* args) {
   Resources resources = apply_function(self, args, precision);
    if (resources.error_code != 0) {
        return NULL;
    }

    return resources.results;
}

static PyObject* fmetrics_recall(PyObject* self, PyObject* args) {
    Resources resources = apply_function(self, args, recall);
    if (resources.error_code != 0) {
        return NULL;
    }

    return resources.results;
}

static PyObject* fmetrics_fmeasure(PyObject* self, PyObject* args) {
  Resources resources = apply_function(self, args, fmeasure);
    if (resources.error_code != 0) {
        return NULL;
    }

    return resources.results;
}

static PyMethodDef fmetrics_methods[] = {
    {"precision", fmetrics_precision, METH_VARARGS, "Calculates precison metric."},
    {"recall", fmetrics_recall, METH_VARARGS, "Calculates recall metric."},
    {"fmeasure", fmetrics_fmeasure, METH_VARARGS, "Calculates f-measure metric. Returns the tuple (fmeasure, precision, recall)."},
    {NULL, NULL}
};

void initfmetrics() {
    Py_InitModule("fmetrics", fmetrics_methods);
}
