/* jpegoptim module */

/*******************************************************************
 * JPEGoptim
 * Copyright (c) Timo Kokkonen, 1996-2013.
 * All Rights Reserved.
 *
 * requires libjpeg.a (from JPEG Group's JPEG software
 *                     release 6a or later...)
 *
 * $Id: 1b6e87f5200058417582befc170780ce7206c1e5 $
 */

#include "Python.h"
#include <jpeglib.h>
#include <stddef.h>
#include <structmember.h>

#ifdef	bool
#undef	bool
#endif
#define	bool		int

#ifdef	false
#undef	false
#endif
#define	false		0

#ifdef	true
#undef	true
#endif
#define	true		1

#ifndef MAXPATHLEN
#define MAXPATHLEN 1024
#endif

#define EXIF_JPEG_MARKER   JPEG_APP0+1
#define EXIF_IDENT_STRING  "Exif\000\000"
#define EXIF_IDENT_STRING_SIZE 6

#define IPTC_JPEG_MARKER   JPEG_APP0+13

#define ICC_JPEG_MARKER   JPEG_APP0+2
#define ICC_IDENT_STRING  "ICC_PROFILE\0"
#define ICC_IDENT_STRING_SIZE 12


typedef struct {
    PyObject_HEAD
    char *filename;
    bool strip_exif;
    bool strip_iptc;
    bool strip_com;
    bool strip_icc;
    int quality;
} JpegOptimObject;

static PyTypeObject JpegOptimType;

/* Methods */

void
jpegoptim_close(JpegOptimObject* self)
{
    if (self->filename) {
        PyMem_Free(self->filename);
        self->filename = NULL;
    }
}

static void
jpegoptim_dealloc(JpegOptimObject* self)
{
    if(self != NULL ){
        jpegoptim_close(self);
        PyObject_Del(self);
    }
}

static PyObject *
jpegoptim__close(register JpegOptimObject *dp, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":close"))
        return NULL;
    jpegoptim_close(dp);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
jpegoptim__save(register JpegOptimObject *dp, PyObject *args)
{
    PyObject                *filename;
    FILE                    *infile;
    FILE                    *outfile;
    int                     j;
    struct                  jpeg_decompress_struct dinfo;
    struct                  jpeg_compress_struct cinfo;
    JSAMPARRAY              buf = NULL;
    jvirt_barray_ptr        *coef_arrays = NULL;
    jpeg_saved_marker_ptr   mrk;
    struct jpeg_error_mgr   derr;
    struct jpeg_error_mgr   cerr;

    if (!PyArg_ParseTuple(args, "O:save", &filename))
        return NULL;

    infile = fopen(dp->filename, "rb");

    if( infile == NULL ){
        PyErr_SetString(PyExc_ValueError, "I/O operation on closed file.");
        return NULL;
    }

    jpeg_create_decompress(&dinfo);
    dinfo.err = jpeg_std_error(&derr);

    if (!dp->strip_com){
        jpeg_save_markers(&dinfo, JPEG_COM, 0xffff);
    }

    if (!dp->strip_iptc){
        jpeg_save_markers(&dinfo, IPTC_JPEG_MARKER, 0xffff);
    }

    if (!dp->strip_exif){
        jpeg_save_markers(&dinfo, EXIF_JPEG_MARKER, 0xffff);
    }

    if (!dp->strip_icc){
        jpeg_save_markers(&dinfo, ICC_JPEG_MARKER, 0xffff);
    }

    jpeg_stdio_src(&dinfo, infile);
    jpeg_read_header(&dinfo, true);

    if(dp->quality > 0){
        jpeg_start_decompress(&dinfo);

        buf = PyMem_Malloc(sizeof(JSAMPROW)*dinfo.output_height);

        if (buf == NULL){
            jpeg_abort_decompress(&dinfo);
            return PyErr_NoMemory();
        }

        for (j = 0;j < dinfo.output_height; j++) {
            buf[j] = PyMem_Malloc(sizeof(JSAMPLE)*dinfo.output_width * dinfo.out_color_components);
            if (!buf[j]){
                jpeg_abort_decompress(&dinfo);
                fclose(infile);
                PyErr_SetString(PyExc_ValueError, "not enough memory.");
                return NULL;
            }
        }

        while (dinfo.output_scanline < dinfo.output_height) {
            jpeg_read_scanlines(&dinfo,&buf[dinfo.output_scanline],
                                dinfo.output_height-dinfo.output_scanline);
        }
    } else {
        coef_arrays = jpeg_read_coefficients(&dinfo);
    }

    outfile = fopen(PyString_AsString(filename), "wb");

    jpeg_create_compress(&cinfo);
    cinfo.err = jpeg_std_error(&cerr);
    jpeg_stdio_dest(&cinfo, outfile);

    if(dp->quality > 0){

        cinfo.in_color_space = dinfo.out_color_space;
        cinfo.input_components = dinfo.output_components;
        cinfo.image_width = dinfo.image_width;
        cinfo.image_height = dinfo.image_height;

        jpeg_set_defaults(&cinfo);
        jpeg_set_quality(&cinfo, dp->quality, true);

        if (dinfo.progressive_mode){
            jpeg_simple_progression(&cinfo);
        }

        cinfo.optimize_coding = true;
        jpeg_start_compress(&cinfo, true);

    }else{
        jpeg_copy_critical_parameters(&dinfo, &cinfo);

        if (dinfo.progressive_mode){
            jpeg_simple_progression(&cinfo);
        }

        cinfo.optimize_coding = true;
        jpeg_write_coefficients(&cinfo, coef_arrays);
    }

    mrk = (&dinfo)->marker_list;
    while (mrk) {
        if (!dp->strip_com && mrk->marker == JPEG_COM)
            jpeg_write_marker(&cinfo, JPEG_COM, mrk->data,mrk->data_length);

        if (!dp->strip_iptc && mrk->marker == IPTC_JPEG_MARKER)
            jpeg_write_marker(&cinfo, IPTC_JPEG_MARKER, mrk->data,mrk->data_length);

        if (!dp->strip_exif && mrk->marker == EXIF_JPEG_MARKER) {
            if (!memcmp(mrk->data, EXIF_IDENT_STRING, EXIF_IDENT_STRING_SIZE)) {
                jpeg_write_marker(&cinfo, EXIF_JPEG_MARKER, mrk->data,mrk->data_length);
            }
        }

        if (!dp->strip_icc && mrk->marker == ICC_JPEG_MARKER) {
            if (!memcmp(mrk->data,ICC_IDENT_STRING,ICC_IDENT_STRING_SIZE)) {
                jpeg_write_marker(&cinfo,ICC_JPEG_MARKER,mrk->data,mrk->data_length);
            }
        }

        mrk = mrk->next;
    }

    if(dp->quality > 0){
        while (cinfo.next_scanline < cinfo.image_height) {
            jpeg_write_scanlines(&cinfo,&buf[cinfo.next_scanline],
                                 dinfo.output_height);
        }
    }

    jpeg_finish_compress(&cinfo);

    if (buf) {
        for (j = 0; j < dinfo.output_height; j++){
            PyMem_Free(buf[j]);
        }
        PyMem_Free(buf);
        buf=NULL;
    }

    jpeg_finish_decompress(&dinfo);

    fclose(infile);
    fclose(outfile);

    jpeg_destroy_decompress(&dinfo);
    jpeg_destroy_compress(&cinfo);

    Py_INCREF(Py_True);
    return Py_True;
}

static PyMethodDef jpegoptim_methods[] = {
    {"close", (PyCFunction)jpegoptim__close, METH_VARARGS,
     "close()\nClose the handler."},
    {"save", (PyCFunction)jpegoptim__save, METH_VARARGS,
     "save(filename) -> value\n"
     "Return bool."},
    {NULL, NULL} /* sentinel */
};

static struct PyMemberDef jpegoptim_members[] = {
    {"filename", T_STRING, offsetof(JpegOptimObject, filename), 0, "filename"},
    {"strip_exif", T_BOOL, offsetof(JpegOptimObject, strip_exif), 0, "strip_exif"},
    {"strip_iptc", T_BOOL, offsetof(JpegOptimObject, strip_iptc), 0, "strip_iptc"},
    {"strip_icc", T_BOOL, offsetof(JpegOptimObject, strip_icc), 0, "strip_icc"},
    {"quality", T_INT, offsetof(JpegOptimObject, quality), 0, "quality"},
    {NULL}  /* Sentinel */
};

static PyTypeObject JpegOptimType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "jpegoptim.JpegOptim",
    sizeof(JpegOptimObject),
    0,
    (destructor)jpegoptim_dealloc,      /*tp_dealloc*/
    0,                                  /*tp_print*/
    0,                                  /*tp_getattr*/
    0,                                  /*tp_setattr*/
    0,                                  /*tp_compare*/
    0,                                  /*tp_repr*/
    0,                                  /*tp_as_number*/
    0,                                  /*tp_as_sequence*/
    0,                                  /*tp_as_mapping*/
    0,                                  /*tp_hash  */
    0,                                  /*tp_call */
    0,                                  /*tp_str */
    PyObject_GenericGetAttr,            /*tp_getattro */
    PyObject_GenericSetAttr,            /*tp_setattro */
    0,                                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    "jpegoptim.JpegOptim",              /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    jpegoptim_methods,                  /* tp_methods */
    jpegoptim_members,                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    0,                                  /* tp_new */
    PyObject_Del,                       /* tp_free */
    0,                                  /* tp_is_gc */
};


/* ----------------------------------------------------------------- */
/* jpegoptim module                                                      */
/* ----------------------------------------------------------------- */

static PyObject *
jpegoptim_new(PyObject* self, PyObject* args, PyObject* kwargs)
{
    JpegOptimObject *dp;

    static char *kwlist[] = {
            "filename",
            "strip_exif",
            "strip_iptc",
            "strip_com",
            "strip_icc",
            "quality", NULL};

    dp = PyObject_New(JpegOptimObject, &JpegOptimType);

    if (dp == NULL)
        return NULL;

    dp->filename = NULL;
    dp->strip_exif = true;
    dp->strip_iptc = true;
    dp->strip_com = true;
    dp->strip_icc = true;
    dp->quality = 80;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s|iiiii", kwlist,
            &dp->filename, &dp->strip_exif, &dp->strip_iptc,
            &dp->strip_com, &dp->strip_icc, &dp->quality
        ))
    {
        return NULL;
    }

    if(!dp->filename){
        PyErr_SetString(PyExc_IOError, "Cannot open jpeg file.");
        return NULL;
    }

    if (dp->quality < 0){
        dp->quality = 0;
    }else if (dp->quality > 100){
        dp->quality=100;
    }

    return (PyObject *)dp;
}

static PyMethodDef jpegoptimmodule_methods[] = {
    { "JpegOptim", (PyCFunction)jpegoptim_new, METH_VARARGS | METH_KEYWORDS,
      "JpegOptim(filename, strip_com=True, strip_iptc=True,\n"
      "          strip_exif=True, strip_icc=True, quality=80)\n"
      "Return a jpegoptim object."},
    { 0, 0 },
};

PyMODINIT_FUNC
initjpegoptim(void) {
    PyObject *m, *d, *s;

    JpegOptimType.ob_type = &PyType_Type;

    m = Py_InitModule("jpegoptim", jpegoptimmodule_methods);
    if (m == NULL)
        return;

    d = PyModule_GetDict(m);
    s = PyString_FromString("JpegOptim");
    if (s != NULL) {
        PyDict_SetItemString(d, "__doc__", s);
        Py_DECREF(s);
    }

    s = PyString_FromString("0.1");
    if (s != NULL) {
        PyDict_SetItemString(d, "__version__", s);
        Py_DECREF(s);
    }

}

