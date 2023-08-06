#ifndef __PYX_HAVE__axon___loader
#define __PYX_HAVE__axon___loader

struct SimpleBuilder;

/* "axon/_loader.pxd":144
 * 
 * 
 * cdef public class SimpleBuilder[type SimpleBuilderType, object SimpleBuilder]:             # <<<<<<<<<<<<<<
 *     cdef object (*create_int)(unicode)
 *     cdef object (*create_float)(unicode)
 */
struct SimpleBuilder {
  PyObject_HEAD
  PyObject *(*create_int)(PyObject *);
  PyObject *(*create_float)(PyObject *);
  PyObject *(*create_decimal)(PyObject *);
  PyObject *(*create_time)(int, int, int, int, PyObject *);
  PyObject *(*create_date)(int, int, int);
  PyObject *(*create_datetime)(int, int, int, int, int, int, int, PyObject *);
  PyObject *(*create_tzinfo)(int);
  PyObject *(*create_inf)(void);
  PyObject *(*create_ninf)(void);
  PyObject *(*create_nan)(void);
};

#ifndef __PYX_HAVE_API__axon___loader

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) SimpleBuilderType;

#endif /* !__PYX_HAVE_API__axon___loader */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_loader(void);
#else
PyMODINIT_FUNC PyInit__loader(void);
#endif

#endif /* !__PYX_HAVE__axon___loader */
