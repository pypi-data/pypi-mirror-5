#ifndef __PYX_HAVE__axon___loader
#define __PYX_HAVE__axon___loader

struct SimpleBuilder;

/* "axon/_loader.pxd":146
 * cdef dict tz_dict = {}
 * 
 * cdef public class SimpleBuilder[type SimpleBuilderType, object SimpleBuilder]:             # <<<<<<<<<<<<<<
 * #     cdef object (*create_int)(unicode)
 * #     cdef object (*create_float)(unicode)
 */
struct SimpleBuilder {
  PyObject_HEAD
  struct __pyx_vtabstruct_4axon_7_loader_SimpleBuilder *__pyx_vtab;
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
