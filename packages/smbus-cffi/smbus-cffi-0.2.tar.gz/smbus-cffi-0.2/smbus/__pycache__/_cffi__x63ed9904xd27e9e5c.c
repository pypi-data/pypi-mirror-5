
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



#include <sys/types.h>
#include <linux/i2c-dev.h>


static PyObject *
_cffi_f_i2c_smbus_access(PyObject *self, PyObject *args)
{
  int x0;
  char x1;
  unsigned char x2;
  int x3;
  union i2c_smbus_data * x4;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:i2c_smbus_access", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_char(arg1);
  if (x1 == (char)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned char);
  if (x2 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_SIGNED(arg3, int);
  if (x3 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(0), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_access(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_process_call(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  unsigned short x2;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:i2c_smbus_process_call", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned short);
  if (x2 == (unsigned short)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_process_call(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_read_byte(PyObject *self, PyObject *arg0)
{
  int x0;
  int32_t result;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_read_byte(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_read_byte_data(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:i2c_smbus_read_byte_data", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_read_byte_data(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_read_word_data(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:i2c_smbus_read_word_data", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_read_word_data(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_write_byte(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:i2c_smbus_write_byte", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_write_byte(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_write_byte_data(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  unsigned char x2;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:i2c_smbus_write_byte_data", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned char);
  if (x2 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_write_byte_data(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_write_quick(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:i2c_smbus_write_quick", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_write_quick(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_i2c_smbus_write_word_data(PyObject *self, PyObject *args)
{
  int x0;
  unsigned char x1;
  unsigned short x2;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:i2c_smbus_write_word_data", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned char);
  if (x1 == (unsigned char)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned short);
  if (x2 == (unsigned short)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = i2c_smbus_write_word_data(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static int _cffi_const_I2C_PEC(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_PEC) && (I2C_PEC) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_PEC));
  else if ((I2C_PEC) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_PEC));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_PEC));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_PEC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_I2C_SLAVE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SLAVE) && (I2C_SLAVE) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SLAVE));
  else if ((I2C_SLAVE) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SLAVE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SLAVE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SLAVE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_PEC(lib);
}

static int _cffi_const_I2C_SMBUS_BLOCK_DATA(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_BLOCK_DATA) && (I2C_SMBUS_BLOCK_DATA) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_BLOCK_DATA));
  else if ((I2C_SMBUS_BLOCK_DATA) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_BLOCK_DATA));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_BLOCK_DATA));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_BLOCK_DATA", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SLAVE(lib);
}

static int _cffi_const_I2C_SMBUS_BLOCK_MAX(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_BLOCK_MAX) && (I2C_SMBUS_BLOCK_MAX) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_BLOCK_MAX));
  else if ((I2C_SMBUS_BLOCK_MAX) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_BLOCK_MAX));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_BLOCK_MAX));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_BLOCK_MAX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_BLOCK_DATA(lib);
}

static int _cffi_const_I2C_SMBUS_BLOCK_PROC_CALL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_BLOCK_PROC_CALL) && (I2C_SMBUS_BLOCK_PROC_CALL) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_BLOCK_PROC_CALL));
  else if ((I2C_SMBUS_BLOCK_PROC_CALL) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_BLOCK_PROC_CALL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_BLOCK_PROC_CALL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_BLOCK_PROC_CALL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_BLOCK_MAX(lib);
}

static int _cffi_const_I2C_SMBUS_BYTE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_BYTE) && (I2C_SMBUS_BYTE) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_BYTE));
  else if ((I2C_SMBUS_BYTE) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_BYTE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_BYTE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_BYTE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_BLOCK_PROC_CALL(lib);
}

static int _cffi_const_I2C_SMBUS_BYTE_DATA(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_BYTE_DATA) && (I2C_SMBUS_BYTE_DATA) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_BYTE_DATA));
  else if ((I2C_SMBUS_BYTE_DATA) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_BYTE_DATA));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_BYTE_DATA));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_BYTE_DATA", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_BYTE(lib);
}

static int _cffi_const_I2C_SMBUS_I2C_BLOCK_BROKEN(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_I2C_BLOCK_BROKEN) && (I2C_SMBUS_I2C_BLOCK_BROKEN) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_I2C_BLOCK_BROKEN));
  else if ((I2C_SMBUS_I2C_BLOCK_BROKEN) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_I2C_BLOCK_BROKEN));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_I2C_BLOCK_BROKEN));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_I2C_BLOCK_BROKEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_BYTE_DATA(lib);
}

static int _cffi_const_I2C_SMBUS_I2C_BLOCK_DATA(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_I2C_BLOCK_DATA) && (I2C_SMBUS_I2C_BLOCK_DATA) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_I2C_BLOCK_DATA));
  else if ((I2C_SMBUS_I2C_BLOCK_DATA) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_I2C_BLOCK_DATA));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_I2C_BLOCK_DATA));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_I2C_BLOCK_DATA", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_I2C_BLOCK_BROKEN(lib);
}

static int _cffi_const_I2C_SMBUS_PROC_CALL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_PROC_CALL) && (I2C_SMBUS_PROC_CALL) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_PROC_CALL));
  else if ((I2C_SMBUS_PROC_CALL) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_PROC_CALL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_PROC_CALL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_PROC_CALL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_I2C_BLOCK_DATA(lib);
}

static int _cffi_const_I2C_SMBUS_QUICK(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_QUICK) && (I2C_SMBUS_QUICK) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_QUICK));
  else if ((I2C_SMBUS_QUICK) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_QUICK));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_QUICK));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_QUICK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_PROC_CALL(lib);
}

static int _cffi_const_I2C_SMBUS_READ(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_READ) && (I2C_SMBUS_READ) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_READ));
  else if ((I2C_SMBUS_READ) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_READ));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_READ));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_READ", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_QUICK(lib);
}

static int _cffi_const_I2C_SMBUS_WORD_DATA(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_WORD_DATA) && (I2C_SMBUS_WORD_DATA) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_WORD_DATA));
  else if ((I2C_SMBUS_WORD_DATA) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_WORD_DATA));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_WORD_DATA));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_WORD_DATA", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_READ(lib);
}

static int _cffi_const_I2C_SMBUS_WRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (I2C_SMBUS_WRITE) && (I2C_SMBUS_WRITE) <= LONG_MAX)
    o = PyInt_FromLong((long)(I2C_SMBUS_WRITE));
  else if ((I2C_SMBUS_WRITE) <= 0)
    o = PyLong_FromLongLong((long long)(I2C_SMBUS_WRITE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(I2C_SMBUS_WRITE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "I2C_SMBUS_WRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_I2C_SMBUS_WORD_DATA(lib);
}

static void _cffi_check_union_i2c_smbus_data(union i2c_smbus_data *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->byte) << 1);
  (void)((p->word) << 1);
  { unsigned char(*tmp)[34] = &p->block; (void)tmp; }
}
static PyObject *
_cffi_layout_union_i2c_smbus_data(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; union i2c_smbus_data y; };
  static Py_ssize_t nums[] = {
    sizeof(union i2c_smbus_data),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(union i2c_smbus_data, byte),
    sizeof(((union i2c_smbus_data *)0)->byte),
    offsetof(union i2c_smbus_data, word),
    sizeof(((union i2c_smbus_data *)0)->word),
    offsetof(union i2c_smbus_data, block),
    sizeof(((union i2c_smbus_data *)0)->block),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_union_i2c_smbus_data(0);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_I2C_SMBUS_WRITE(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"i2c_smbus_access", _cffi_f_i2c_smbus_access, METH_VARARGS},
  {"i2c_smbus_process_call", _cffi_f_i2c_smbus_process_call, METH_VARARGS},
  {"i2c_smbus_read_byte", _cffi_f_i2c_smbus_read_byte, METH_O},
  {"i2c_smbus_read_byte_data", _cffi_f_i2c_smbus_read_byte_data, METH_VARARGS},
  {"i2c_smbus_read_word_data", _cffi_f_i2c_smbus_read_word_data, METH_VARARGS},
  {"i2c_smbus_write_byte", _cffi_f_i2c_smbus_write_byte, METH_VARARGS},
  {"i2c_smbus_write_byte_data", _cffi_f_i2c_smbus_write_byte_data, METH_VARARGS},
  {"i2c_smbus_write_quick", _cffi_f_i2c_smbus_write_quick, METH_VARARGS},
  {"i2c_smbus_write_word_data", _cffi_f_i2c_smbus_write_word_data, METH_VARARGS},
  {"_cffi_layout_union_i2c_smbus_data", _cffi_layout_union_i2c_smbus_data, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi__x63ed9904xd27e9e5c(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x63ed9904xd27e9e5c", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
