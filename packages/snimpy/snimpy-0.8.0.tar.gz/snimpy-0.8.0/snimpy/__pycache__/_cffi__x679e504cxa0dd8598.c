
#include <Python.h>
#include <stddef.h>

#ifdef MS_WIN32
#include <malloc.h>   /* for alloca() */
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef unsigned char _Bool;
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_CheckExact
# undef PyCapsule_GetPointer
# define PyCapsule_CheckExact(capsule) (PyCObject_Check(capsule))
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_ulong PyLong_FromUnsignedLong
#define _cffi_from_c_longlong PyLong_FromLongLong
#define _cffi_from_c_ulonglong PyLong_FromUnsignedLongLong

#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_from_c_SIGNED(x, type)                                     \
    (sizeof(type) <= sizeof(long) ? PyInt_FromLong(x) :                  \
                                    PyLong_FromLongLong(x))
#define _cffi_from_c_UNSIGNED(x, type)                                   \
    (sizeof(type) < sizeof(long) ? PyInt_FromLong(x) :                   \
     sizeof(type) == sizeof(long) ? PyLong_FromUnsignedLong(x) :         \
                                    PyLong_FromUnsignedLongLong(x))

#define _cffi_to_c_SIGNED(o, type)                                       \
    (sizeof(type) == 1 ? _cffi_to_c_i8(o) :                              \
     sizeof(type) == 2 ? _cffi_to_c_i16(o) :                             \
     sizeof(type) == 4 ? _cffi_to_c_i32(o) :                             \
     sizeof(type) == 8 ? _cffi_to_c_i64(o) :                             \
     (Py_FatalError("unsupported size for type " #type), 0))
#define _cffi_to_c_UNSIGNED(o, type)                                     \
    (sizeof(type) == 1 ? _cffi_to_c_u8(o) :                              \
     sizeof(type) == 2 ? _cffi_to_c_u16(o) :                             \
     sizeof(type) == 4 ? _cffi_to_c_u32(o) :                             \
     sizeof(type) == 8 ? _cffi_to_c_u64(o) :                             \
     (Py_FatalError("unsupported size for type " #type), 0))

#define _cffi_to_c_i8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_u8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_i16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_u16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[4])
#define _cffi_to_c_i32                                                   \
                 ((int(*)(PyObject *))_cffi_exports[5])
#define _cffi_to_c_u32                                                   \
                 ((unsigned int(*)(PyObject *))_cffi_exports[6])
#define _cffi_to_c_i64                                                   \
                 ((long long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_u64                                                   \
                 ((unsigned long long(*)(PyObject *))_cffi_exports[8])
#define _cffi_to_c_char                                                  \
                 ((int(*)(PyObject *))_cffi_exports[9])
#define _cffi_from_c_pointer                                             \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[10])
#define _cffi_to_c_pointer                                               \
    ((char *(*)(PyObject *, CTypeDescrObject *))_cffi_exports[11])
#define _cffi_get_struct_layout                                          \
    ((PyObject *(*)(Py_ssize_t[]))_cffi_exports[12])
#define _cffi_restore_errno                                              \
    ((void(*)(void))_cffi_exports[13])
#define _cffi_save_errno                                                 \
    ((void(*)(void))_cffi_exports[14])
#define _cffi_from_c_char                                                \
    ((PyObject *(*)(char))_cffi_exports[15])
#define _cffi_from_c_deref                                               \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[16])
#define _cffi_to_c                                                       \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[17])
#define _cffi_from_c_struct                                              \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[18])
#define _cffi_to_c_wchar_t                                               \
    ((wchar_t(*)(PyObject *))_cffi_exports[19])
#define _cffi_from_c_wchar_t                                             \
    ((PyObject *(*)(wchar_t))_cffi_exports[20])
#define _cffi_to_c_long_double                                           \
    ((long double(*)(PyObject *))_cffi_exports[21])
#define _cffi_to_c__Bool                                                 \
    ((_Bool(*)(PyObject *))_cffi_exports[22])
#define _cffi_prepare_pointer_call_argument                              \
    ((Py_ssize_t(*)(CTypeDescrObject *, PyObject *, char **))_cffi_exports[23])
#define _cffi_convert_array_from_object                                  \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[24])
#define _CFFI_NUM_EXPORTS 25

typedef struct _ctypedescr CTypeDescrObject;

static void *_cffi_exports[_CFFI_NUM_EXPORTS];
static PyObject *_cffi_types, *_cffi_VerificationError;

static PyObject *_cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    return _cffi_setup_custom(library);
}

static void _cffi_init(void)
{
    PyObject *module = PyImport_ImportModule("_cffi_backend");
    PyObject *c_api_object;

    if (module == NULL)
        return;

    c_api_object = PyObject_GetAttrString(module, "_C_API");
    if (c_api_object == NULL)
        return;
    if (!PyCapsule_CheckExact(c_api_object)) {
        PyErr_SetNone(PyExc_ImportError);
        return;
    }
    memcpy(_cffi_exports, PyCapsule_GetPointer(c_api_object, "cffi"),
           _CFFI_NUM_EXPORTS * sizeof(void *));
}

#define _cffi_type(num) ((CTypeDescrObject *)PyList_GET_ITEM(_cffi_types, num))

/**********/



#include <smi.h>


static int _cffi_const_SMI_BASETYPE_INTEGER32(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_INTEGER32) && (SMI_BASETYPE_INTEGER32) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_INTEGER32));
  else if ((SMI_BASETYPE_INTEGER32) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_INTEGER32));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_INTEGER32));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_INTEGER32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_SMI_BASETYPE_OCTETSTRING(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_OCTETSTRING) && (SMI_BASETYPE_OCTETSTRING) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_OCTETSTRING));
  else if ((SMI_BASETYPE_OCTETSTRING) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_OCTETSTRING));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_OCTETSTRING));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_OCTETSTRING", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_INTEGER32(lib);
}

static int _cffi_const_SMI_BASETYPE_OBJECTIDENTIFIER(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_OBJECTIDENTIFIER) && (SMI_BASETYPE_OBJECTIDENTIFIER) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_OBJECTIDENTIFIER));
  else if ((SMI_BASETYPE_OBJECTIDENTIFIER) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_OBJECTIDENTIFIER));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_OBJECTIDENTIFIER));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_OBJECTIDENTIFIER", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_OCTETSTRING(lib);
}

static int _cffi_const_SMI_BASETYPE_UNSIGNED32(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_UNSIGNED32) && (SMI_BASETYPE_UNSIGNED32) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_UNSIGNED32));
  else if ((SMI_BASETYPE_UNSIGNED32) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_UNSIGNED32));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_UNSIGNED32));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_UNSIGNED32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_OBJECTIDENTIFIER(lib);
}

static int _cffi_const_SMI_BASETYPE_INTEGER64(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_INTEGER64) && (SMI_BASETYPE_INTEGER64) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_INTEGER64));
  else if ((SMI_BASETYPE_INTEGER64) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_INTEGER64));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_INTEGER64));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_INTEGER64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_UNSIGNED32(lib);
}

static int _cffi_const_SMI_BASETYPE_UNSIGNED64(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_UNSIGNED64) && (SMI_BASETYPE_UNSIGNED64) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_UNSIGNED64));
  else if ((SMI_BASETYPE_UNSIGNED64) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_UNSIGNED64));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_UNSIGNED64));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_UNSIGNED64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_INTEGER64(lib);
}

static int _cffi_const_SMI_BASETYPE_ENUM(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_ENUM) && (SMI_BASETYPE_ENUM) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_ENUM));
  else if ((SMI_BASETYPE_ENUM) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_ENUM));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_ENUM));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_ENUM", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_UNSIGNED64(lib);
}

static int _cffi_const_SMI_BASETYPE_BITS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_BASETYPE_BITS) && (SMI_BASETYPE_BITS) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_BASETYPE_BITS));
  else if ((SMI_BASETYPE_BITS) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_BASETYPE_BITS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_BASETYPE_BITS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_BASETYPE_BITS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_ENUM(lib);
}

static int _cffi_const_SMI_INDEX_INDEX(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_INDEX_INDEX) && (SMI_INDEX_INDEX) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_INDEX_INDEX));
  else if ((SMI_INDEX_INDEX) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_INDEX_INDEX));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_INDEX_INDEX));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_INDEX_INDEX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_BASETYPE_BITS(lib);
}

static int _cffi_const_SMI_INDEX_AUGMENT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_INDEX_AUGMENT) && (SMI_INDEX_AUGMENT) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_INDEX_AUGMENT));
  else if ((SMI_INDEX_AUGMENT) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_INDEX_AUGMENT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_INDEX_AUGMENT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_INDEX_AUGMENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_INDEX_INDEX(lib);
}

static PyObject *
_cffi_f_smiExit(PyObject *self, PyObject *no_arg)
{

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { smiExit(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_smiGetElementNode(PyObject *self, PyObject *arg0)
{
  SmiElement * x0;
  Py_ssize_t datasize;
  SmiNode * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetElementNode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetFirstChildNode(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiNode * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetFirstChildNode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetFirstElement(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiElement * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetFirstElement(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(1));
}

static PyObject *
_cffi_f_smiGetFirstNamedNumber(PyObject *self, PyObject *arg0)
{
  SmiType * x0;
  Py_ssize_t datasize;
  SmiNamedNumber * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetFirstNamedNumber(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_smiGetFirstNode(PyObject *self, PyObject *args)
{
  SmiModule * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  SmiNode * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:smiGetFirstNode", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(5), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetFirstNode(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetFirstRange(PyObject *self, PyObject *arg0)
{
  SmiType * x0;
  Py_ssize_t datasize;
  SmiRange * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetFirstRange(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(6));
}

static PyObject *
_cffi_f_smiGetModule(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  SmiModule * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetModule(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_smiGetNextChildNode(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiNode * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNextChildNode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetNextElement(PyObject *self, PyObject *arg0)
{
  SmiElement * x0;
  Py_ssize_t datasize;
  SmiElement * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNextElement(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(1));
}

static PyObject *
_cffi_f_smiGetNextNamedNumber(PyObject *self, PyObject *arg0)
{
  SmiNamedNumber * x0;
  Py_ssize_t datasize;
  SmiNamedNumber * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNextNamedNumber(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_smiGetNextNode(PyObject *self, PyObject *args)
{
  SmiNode * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  SmiNode * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:smiGetNextNode", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNextNode(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetNextRange(PyObject *self, PyObject *arg0)
{
  SmiRange * x0;
  Py_ssize_t datasize;
  SmiRange * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(6), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNextRange(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(6));
}

static PyObject *
_cffi_f_smiGetNode(PyObject *self, PyObject *args)
{
  SmiModule * x0;
  char const * x1;
  Py_ssize_t datasize;
  SmiNode * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:smiGetNode", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(5), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNode(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetNodeModule(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiModule * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNodeModule(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_smiGetNodeType(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiType * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetNodeType(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_smiGetParentNode(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiNode * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetParentNode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiGetParentType(PyObject *self, PyObject *arg0)
{
  SmiType * x0;
  Py_ssize_t datasize;
  SmiType * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetParentType(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_smiGetRelatedNode(PyObject *self, PyObject *arg0)
{
  SmiNode * x0;
  Py_ssize_t datasize;
  SmiNode * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiGetRelatedNode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_smiInit(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiInit(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_smiLoadModule(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  char * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiLoadModule(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(8));
}

static PyObject *
_cffi_f_smiRenderNode(PyObject *self, PyObject *args)
{
  SmiNode * x0;
  int x1;
  Py_ssize_t datasize;
  char * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:smiRenderNode", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = smiRenderNode(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(8));
}

static PyObject *
_cffi_f_smiSetErrorLevel(PyObject *self, PyObject *arg0)
{
  int x0;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { smiSetErrorLevel(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_smiSetFlags(PyObject *self, PyObject *arg0)
{
  int x0;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { smiSetFlags(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static int _cffi_const_SMI_FLAG_ERRORS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_FLAG_ERRORS) && (SMI_FLAG_ERRORS) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_FLAG_ERRORS));
  else if ((SMI_FLAG_ERRORS) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_FLAG_ERRORS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_FLAG_ERRORS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_FLAG_ERRORS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_SMI_FLAG_RECURSIVE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_FLAG_RECURSIVE) && (SMI_FLAG_RECURSIVE) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_FLAG_RECURSIVE));
  else if ((SMI_FLAG_RECURSIVE) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_FLAG_RECURSIVE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_FLAG_RECURSIVE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_FLAG_RECURSIVE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_FLAG_ERRORS(lib);
}

static int _cffi_const_SMI_NODEKIND_COLUMN(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_NODEKIND_COLUMN) && (SMI_NODEKIND_COLUMN) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_NODEKIND_COLUMN));
  else if ((SMI_NODEKIND_COLUMN) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_NODEKIND_COLUMN));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_NODEKIND_COLUMN));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_NODEKIND_COLUMN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_FLAG_RECURSIVE(lib);
}

static int _cffi_const_SMI_NODEKIND_NODE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_NODEKIND_NODE) && (SMI_NODEKIND_NODE) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_NODEKIND_NODE));
  else if ((SMI_NODEKIND_NODE) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_NODEKIND_NODE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_NODEKIND_NODE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_NODEKIND_NODE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_NODEKIND_COLUMN(lib);
}

static int _cffi_const_SMI_NODEKIND_ROW(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_NODEKIND_ROW) && (SMI_NODEKIND_ROW) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_NODEKIND_ROW));
  else if ((SMI_NODEKIND_ROW) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_NODEKIND_ROW));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_NODEKIND_ROW));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_NODEKIND_ROW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_NODEKIND_NODE(lib);
}

static int _cffi_const_SMI_NODEKIND_SCALAR(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_NODEKIND_SCALAR) && (SMI_NODEKIND_SCALAR) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_NODEKIND_SCALAR));
  else if ((SMI_NODEKIND_SCALAR) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_NODEKIND_SCALAR));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_NODEKIND_SCALAR));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_NODEKIND_SCALAR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_NODEKIND_ROW(lib);
}

static int _cffi_const_SMI_NODEKIND_TABLE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_NODEKIND_TABLE) && (SMI_NODEKIND_TABLE) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_NODEKIND_TABLE));
  else if ((SMI_NODEKIND_TABLE) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_NODEKIND_TABLE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_NODEKIND_TABLE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_NODEKIND_TABLE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_NODEKIND_SCALAR(lib);
}

static int _cffi_const_SMI_RENDER_ALL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (SMI_RENDER_ALL) && (SMI_RENDER_ALL) <= LONG_MAX)
    o = PyInt_FromLong((long)(SMI_RENDER_ALL));
  else if ((SMI_RENDER_ALL) <= 0)
    o = PyLong_FromLongLong((long long)(SMI_RENDER_ALL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(SMI_RENDER_ALL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SMI_RENDER_ALL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SMI_NODEKIND_TABLE(lib);
}

static void _cffi_check_struct_SmiElement(struct SmiElement *p)
{
  /* only to generate compile-time warnings or errors */
}
static PyObject *
_cffi_layout_struct_SmiElement(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiElement y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiElement),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiElement(0);
}

static void _cffi_check_struct_SmiModule(struct SmiModule *p)
{
  /* only to generate compile-time warnings or errors */
  { char * *tmp = &p->name; (void)tmp; }
  (void)((p->conformance) << 1);
}
static PyObject *
_cffi_layout_struct_SmiModule(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiModule y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiModule),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiModule, name),
    sizeof(((struct SmiModule *)0)->name),
    offsetof(struct SmiModule, conformance),
    sizeof(((struct SmiModule *)0)->conformance),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiModule(0);
}

static void _cffi_check_struct_SmiNamedNumber(struct SmiNamedNumber *p)
{
  /* only to generate compile-time warnings or errors */
  { char * *tmp = &p->name; (void)tmp; }
  { SmiValue *tmp = &p->value; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_SmiNamedNumber(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiNamedNumber y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiNamedNumber),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiNamedNumber, name),
    sizeof(((struct SmiNamedNumber *)0)->name),
    offsetof(struct SmiNamedNumber, value),
    sizeof(((struct SmiNamedNumber *)0)->value),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiNamedNumber(0);
}

static void _cffi_check_struct_SmiNode(struct SmiNode *p)
{
  /* only to generate compile-time warnings or errors */
  { char * *tmp = &p->name; (void)tmp; }
  (void)((p->oidlen) << 1);
  { unsigned int * *tmp = &p->oid; (void)tmp; }
  { char * *tmp = &p->format; (void)tmp; }
  { SmiIndexkind *tmp = &p->indexkind; (void)tmp; }
  (void)((p->implied) << 1);
  (void)((p->nodekind) << 1);
}
static PyObject *
_cffi_layout_struct_SmiNode(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiNode y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiNode),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiNode, name),
    sizeof(((struct SmiNode *)0)->name),
    offsetof(struct SmiNode, oidlen),
    sizeof(((struct SmiNode *)0)->oidlen),
    offsetof(struct SmiNode, oid),
    sizeof(((struct SmiNode *)0)->oid),
    offsetof(struct SmiNode, format),
    sizeof(((struct SmiNode *)0)->format),
    offsetof(struct SmiNode, indexkind),
    sizeof(((struct SmiNode *)0)->indexkind),
    offsetof(struct SmiNode, implied),
    sizeof(((struct SmiNode *)0)->implied),
    offsetof(struct SmiNode, nodekind),
    sizeof(((struct SmiNode *)0)->nodekind),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiNode(0);
}

static void _cffi_check_struct_SmiRange(struct SmiRange *p)
{
  /* only to generate compile-time warnings or errors */
  { SmiValue *tmp = &p->minValue; (void)tmp; }
  { SmiValue *tmp = &p->maxValue; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_SmiRange(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiRange y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiRange),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiRange, minValue),
    sizeof(((struct SmiRange *)0)->minValue),
    offsetof(struct SmiRange, maxValue),
    sizeof(((struct SmiRange *)0)->maxValue),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiRange(0);
}

static void _cffi_check_struct_SmiType(struct SmiType *p)
{
  /* only to generate compile-time warnings or errors */
  { char * *tmp = &p->name; (void)tmp; }
  { SmiBasetype *tmp = &p->basetype; (void)tmp; }
  { char * *tmp = &p->format; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_SmiType(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiType y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiType),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiType, name),
    sizeof(((struct SmiType *)0)->name),
    offsetof(struct SmiType, basetype),
    sizeof(((struct SmiType *)0)->basetype),
    offsetof(struct SmiType, format),
    sizeof(((struct SmiType *)0)->format),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiType(0);
}

static void _cffi_check_struct_SmiValue(struct SmiValue *p)
{
  /* only to generate compile-time warnings or errors */
  { SmiBasetype *tmp = &p->basetype; (void)tmp; }
  /* cannot generate 'union $1' in field 'value': unknown type name */
}
static PyObject *
_cffi_layout_struct_SmiValue(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct SmiValue y; };
  static Py_ssize_t nums[] = {
    sizeof(struct SmiValue),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiValue, basetype),
    sizeof(((struct SmiValue *)0)->basetype),
    offsetof(struct SmiValue, value),
    sizeof(((struct SmiValue *)0)->value),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiValue(0);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_SMI_RENDER_ALL(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"smiExit", _cffi_f_smiExit, METH_NOARGS},
  {"smiGetElementNode", _cffi_f_smiGetElementNode, METH_O},
  {"smiGetFirstChildNode", _cffi_f_smiGetFirstChildNode, METH_O},
  {"smiGetFirstElement", _cffi_f_smiGetFirstElement, METH_O},
  {"smiGetFirstNamedNumber", _cffi_f_smiGetFirstNamedNumber, METH_O},
  {"smiGetFirstNode", _cffi_f_smiGetFirstNode, METH_VARARGS},
  {"smiGetFirstRange", _cffi_f_smiGetFirstRange, METH_O},
  {"smiGetModule", _cffi_f_smiGetModule, METH_O},
  {"smiGetNextChildNode", _cffi_f_smiGetNextChildNode, METH_O},
  {"smiGetNextElement", _cffi_f_smiGetNextElement, METH_O},
  {"smiGetNextNamedNumber", _cffi_f_smiGetNextNamedNumber, METH_O},
  {"smiGetNextNode", _cffi_f_smiGetNextNode, METH_VARARGS},
  {"smiGetNextRange", _cffi_f_smiGetNextRange, METH_O},
  {"smiGetNode", _cffi_f_smiGetNode, METH_VARARGS},
  {"smiGetNodeModule", _cffi_f_smiGetNodeModule, METH_O},
  {"smiGetNodeType", _cffi_f_smiGetNodeType, METH_O},
  {"smiGetParentNode", _cffi_f_smiGetParentNode, METH_O},
  {"smiGetParentType", _cffi_f_smiGetParentType, METH_O},
  {"smiGetRelatedNode", _cffi_f_smiGetRelatedNode, METH_O},
  {"smiInit", _cffi_f_smiInit, METH_O},
  {"smiLoadModule", _cffi_f_smiLoadModule, METH_O},
  {"smiRenderNode", _cffi_f_smiRenderNode, METH_VARARGS},
  {"smiSetErrorLevel", _cffi_f_smiSetErrorLevel, METH_O},
  {"smiSetFlags", _cffi_f_smiSetFlags, METH_O},
  {"_cffi_layout_struct_SmiElement", _cffi_layout_struct_SmiElement, METH_NOARGS},
  {"_cffi_layout_struct_SmiModule", _cffi_layout_struct_SmiModule, METH_NOARGS},
  {"_cffi_layout_struct_SmiNamedNumber", _cffi_layout_struct_SmiNamedNumber, METH_NOARGS},
  {"_cffi_layout_struct_SmiNode", _cffi_layout_struct_SmiNode, METH_NOARGS},
  {"_cffi_layout_struct_SmiRange", _cffi_layout_struct_SmiRange, METH_NOARGS},
  {"_cffi_layout_struct_SmiType", _cffi_layout_struct_SmiType, METH_NOARGS},
  {"_cffi_layout_struct_SmiValue", _cffi_layout_struct_SmiValue, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi__x679e504cxa0dd8598(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x679e504cxa0dd8598", _cffi_methods);
  if (lib == NULL || _cffi_const_SMI_INDEX_AUGMENT(lib) < 0)
    return;
  _cffi_init();
  return;
}
