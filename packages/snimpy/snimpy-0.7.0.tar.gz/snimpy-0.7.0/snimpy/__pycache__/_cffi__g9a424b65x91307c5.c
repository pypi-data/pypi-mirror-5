
#include <stdio.h>
#include <stddef.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>   /* XXX for ssize_t on some platforms */

#ifdef _WIN32
#  include <Windows.h>
#  define snprintf _snprintf
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef SSIZE_T ssize_t;
typedef unsigned char _Bool;
#else
#  include <stdint.h>
#endif


#include <smi.h>

int _cffi_const_SMI_BASETYPE_INTEGER32(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_INTEGER32);
  return (SMI_BASETYPE_INTEGER32) <= 0;
}

int _cffi_const_SMI_BASETYPE_OCTETSTRING(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_OCTETSTRING);
  return (SMI_BASETYPE_OCTETSTRING) <= 0;
}

int _cffi_const_SMI_BASETYPE_OBJECTIDENTIFIER(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_OBJECTIDENTIFIER);
  return (SMI_BASETYPE_OBJECTIDENTIFIER) <= 0;
}

int _cffi_const_SMI_BASETYPE_UNSIGNED32(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_UNSIGNED32);
  return (SMI_BASETYPE_UNSIGNED32) <= 0;
}

int _cffi_const_SMI_BASETYPE_INTEGER64(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_INTEGER64);
  return (SMI_BASETYPE_INTEGER64) <= 0;
}

int _cffi_const_SMI_BASETYPE_UNSIGNED64(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_UNSIGNED64);
  return (SMI_BASETYPE_UNSIGNED64) <= 0;
}

int _cffi_const_SMI_BASETYPE_ENUM(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_ENUM);
  return (SMI_BASETYPE_ENUM) <= 0;
}

int _cffi_const_SMI_BASETYPE_BITS(long long *out_value)
{
  *out_value = (long long)(SMI_BASETYPE_BITS);
  return (SMI_BASETYPE_BITS) <= 0;
}

int _cffi_const_SMI_INDEX_INDEX(long long *out_value)
{
  *out_value = (long long)(SMI_INDEX_INDEX);
  return (SMI_INDEX_INDEX) <= 0;
}

int _cffi_const_SMI_INDEX_AUGMENT(long long *out_value)
{
  *out_value = (long long)(SMI_INDEX_AUGMENT);
  return (SMI_INDEX_AUGMENT) <= 0;
}

void _cffi_f_smiExit(void)
{
  smiExit();
}

SmiNode * _cffi_f_smiGetElementNode(SmiElement * x0)
{
  return smiGetElementNode(x0);
}

SmiNode * _cffi_f_smiGetFirstChildNode(SmiNode * x0)
{
  return smiGetFirstChildNode(x0);
}

SmiElement * _cffi_f_smiGetFirstElement(SmiNode * x0)
{
  return smiGetFirstElement(x0);
}

SmiNamedNumber * _cffi_f_smiGetFirstNamedNumber(SmiType * x0)
{
  return smiGetFirstNamedNumber(x0);
}

SmiNode * _cffi_f_smiGetFirstNode(SmiModule * x0, unsigned int x1)
{
  return smiGetFirstNode(x0, x1);
}

SmiRange * _cffi_f_smiGetFirstRange(SmiType * x0)
{
  return smiGetFirstRange(x0);
}

SmiModule * _cffi_f_smiGetModule(char const * x0)
{
  return smiGetModule(x0);
}

SmiNode * _cffi_f_smiGetNextChildNode(SmiNode * x0)
{
  return smiGetNextChildNode(x0);
}

SmiElement * _cffi_f_smiGetNextElement(SmiElement * x0)
{
  return smiGetNextElement(x0);
}

SmiNamedNumber * _cffi_f_smiGetNextNamedNumber(SmiNamedNumber * x0)
{
  return smiGetNextNamedNumber(x0);
}

SmiNode * _cffi_f_smiGetNextNode(SmiNode * x0, unsigned int x1)
{
  return smiGetNextNode(x0, x1);
}

SmiRange * _cffi_f_smiGetNextRange(SmiRange * x0)
{
  return smiGetNextRange(x0);
}

SmiNode * _cffi_f_smiGetNode(SmiModule * x0, char const * x1)
{
  return smiGetNode(x0, x1);
}

SmiModule * _cffi_f_smiGetNodeModule(SmiNode * x0)
{
  return smiGetNodeModule(x0);
}

SmiType * _cffi_f_smiGetNodeType(SmiNode * x0)
{
  return smiGetNodeType(x0);
}

SmiNode * _cffi_f_smiGetParentNode(SmiNode * x0)
{
  return smiGetParentNode(x0);
}

SmiNode * _cffi_f_smiGetRelatedNode(SmiNode * x0)
{
  return smiGetRelatedNode(x0);
}

int _cffi_f_smiInit(char const * x0)
{
  return smiInit(x0);
}

char * _cffi_f_smiLoadModule(char const * x0)
{
  return smiLoadModule(x0);
}

char * _cffi_f_smiRenderNode(SmiNode * x0, int x1)
{
  return smiRenderNode(x0, x1);
}

void _cffi_f_smiSetErrorLevel(int x0)
{
  smiSetErrorLevel(x0);
}

void _cffi_f_smiSetFlags(int x0)
{
  smiSetFlags(x0);
}

int _cffi_const_SMI_FLAG_ERRORS(long long *out_value)
{
  *out_value = (long long)(SMI_FLAG_ERRORS);
  return (SMI_FLAG_ERRORS) <= 0;
}

int _cffi_const_SMI_FLAG_RECURSIVE(long long *out_value)
{
  *out_value = (long long)(SMI_FLAG_RECURSIVE);
  return (SMI_FLAG_RECURSIVE) <= 0;
}

int _cffi_const_SMI_NODEKIND_COLUMN(long long *out_value)
{
  *out_value = (long long)(SMI_NODEKIND_COLUMN);
  return (SMI_NODEKIND_COLUMN) <= 0;
}

int _cffi_const_SMI_NODEKIND_NODE(long long *out_value)
{
  *out_value = (long long)(SMI_NODEKIND_NODE);
  return (SMI_NODEKIND_NODE) <= 0;
}

int _cffi_const_SMI_NODEKIND_ROW(long long *out_value)
{
  *out_value = (long long)(SMI_NODEKIND_ROW);
  return (SMI_NODEKIND_ROW) <= 0;
}

int _cffi_const_SMI_NODEKIND_SCALAR(long long *out_value)
{
  *out_value = (long long)(SMI_NODEKIND_SCALAR);
  return (SMI_NODEKIND_SCALAR) <= 0;
}

int _cffi_const_SMI_NODEKIND_TABLE(long long *out_value)
{
  *out_value = (long long)(SMI_NODEKIND_TABLE);
  return (SMI_NODEKIND_TABLE) <= 0;
}

int _cffi_const_SMI_RENDER_ALL(long long *out_value)
{
  *out_value = (long long)(SMI_RENDER_ALL);
  return (SMI_RENDER_ALL) <= 0;
}

static void _cffi_check_struct_SmiElement(struct SmiElement *p)
{
  /* only to generate compile-time warnings or errors */
}
ssize_t _cffi_layout_struct_SmiElement(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiElement y; };
  static ssize_t nums[] = {
    sizeof(struct SmiElement),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiElement(0);
}

static void _cffi_check_struct_SmiModule(struct SmiModule *p)
{
  /* only to generate compile-time warnings or errors */
  { char * *tmp = &p->name; (void)tmp; }
  (void)((p->conformance) << 1);
}
ssize_t _cffi_layout_struct_SmiModule(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiModule y; };
  static ssize_t nums[] = {
    sizeof(struct SmiModule),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiModule, name),
    sizeof(((struct SmiModule *)0)->name),
    offsetof(struct SmiModule, conformance),
    sizeof(((struct SmiModule *)0)->conformance),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiModule(0);
}

static void _cffi_check_struct_SmiNamedNumber(struct SmiNamedNumber *p)
{
  /* only to generate compile-time warnings or errors */
  { char * *tmp = &p->name; (void)tmp; }
  { SmiValue *tmp = &p->value; (void)tmp; }
}
ssize_t _cffi_layout_struct_SmiNamedNumber(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiNamedNumber y; };
  static ssize_t nums[] = {
    sizeof(struct SmiNamedNumber),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiNamedNumber, name),
    sizeof(((struct SmiNamedNumber *)0)->name),
    offsetof(struct SmiNamedNumber, value),
    sizeof(((struct SmiNamedNumber *)0)->value),
    -1
  };
  return nums[i];
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
ssize_t _cffi_layout_struct_SmiNode(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiNode y; };
  static ssize_t nums[] = {
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
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiNode(0);
}

static void _cffi_check_struct_SmiRange(struct SmiRange *p)
{
  /* only to generate compile-time warnings or errors */
  { SmiValue *tmp = &p->minValue; (void)tmp; }
  { SmiValue *tmp = &p->maxValue; (void)tmp; }
}
ssize_t _cffi_layout_struct_SmiRange(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiRange y; };
  static ssize_t nums[] = {
    sizeof(struct SmiRange),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiRange, minValue),
    sizeof(((struct SmiRange *)0)->minValue),
    offsetof(struct SmiRange, maxValue),
    sizeof(((struct SmiRange *)0)->maxValue),
    -1
  };
  return nums[i];
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
ssize_t _cffi_layout_struct_SmiType(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiType y; };
  static ssize_t nums[] = {
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
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiType(0);
}

static void _cffi_check_struct_SmiValue(struct SmiValue *p)
{
  /* only to generate compile-time warnings or errors */
  { SmiBasetype *tmp = &p->basetype; (void)tmp; }
  /* cannot generate 'union $1' in field 'value': unknown type name */
}
ssize_t _cffi_layout_struct_SmiValue(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct SmiValue y; };
  static ssize_t nums[] = {
    sizeof(struct SmiValue),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct SmiValue, basetype),
    sizeof(((struct SmiValue *)0)->basetype),
    offsetof(struct SmiValue, value),
    sizeof(((struct SmiValue *)0)->value),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_SmiValue(0);
}

