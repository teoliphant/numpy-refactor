#ifndef _NUMPY_API_H_
#define _NUMPY_API_H_

#include "numpy/arrayobject.h"

typedef PyObject NpyObject;                             /* An object opaque to core but understood by the interface layer */
typedef PyArrayObject NpyArray;
typedef struct PyArrayIterObject_tag NpyArrayIter;
typedef PyArrayMultiIterObject NpyArrayMultiIter;
typedef PyArray_Descr NpyArray_Descr;

typedef PyArray_Dims NpyArray_Dims;

typedef PyArray_CopySwapFunc NpyArray_CopySwapFunc;
typedef PyArray_ArrFuncs NpyArray_ArrFuncs;
typedef PyArray_ArgFunc NpyArray_ArgFunc;
typedef PyArray_VectorUnaryFunc NpyArray_VectorUnaryFunc;


#define NpyTypeObject PyTypeObject
#define NpyArray_Type PyArray_Type

#define NpyArray_UCS4 npy_ucs4

#define Npy_TYPE(a) Py_TYPE(a)
#define NpyArray_SIZE(a) PyArray_SIZE(a)
#define NpyArray_ITEMSIZE(a) PyArray_ITEMSIZE(a)
#define NpyArray_NDIM(a) PyArray_NDIM(a)
#define NpyArray_DIM(a, i) PyArray_DIM(a, i)
#define NpyArray_STRIDES(a) PyArray_STRIDES(a)
#define NpyArray_STRIDE(obj, n) PyArray_STRIDE(obj,n)
#define NpyArray_DESCR(a) PyArray_DESCR(a)
#define NpyArray_FLAGS(a) PyArray_FLAGS(a)
#define NpyArray_BASE(a) PyArray_BASE(a)
#define NpyArray_BYTES(obj) PyArray_BYTES(obj) 
#define NpyArray_NBYTES(m) (NpyArray_ITEMSIZE(m) * NpyArray_SIZE(m))
#define NpyDimMem_NEW(size) PyDimMem_NEW(size)
#define NpyArray_CHKFLAGS(a, flags) PyArray_CHKFLAGS(a, flags)
#define NpyArray_ISFORTRAN(a) PyArray_ISFORTRAN(a)
#define NpyArray_ISCONTIGUOUS(a) PyArray_ISCONTIGUOUS(a)
#define NpyArray_ISONESEGMENT(a) PyArray_ISONESEGMENT(a)
#define NpyArray_ISFLEXIBLE(obj) PyTypeNum_ISFLEXIBLE(PyArray_TYPE(obj))
#define NpyArray_ISUNSIGNED(obj) PyArray_ISUNSIGNED(obj)
#define NpyArray_ISWRITEABLE(a) PyArray_ISWRITEABLE(a)
#define NpyArray_SAMESHAPE(a1, a2) PyArray_SAMESHAPE(a1,a2)

#define NpyDataType_FLAGCHK(dtype, flag)                                   \
        (((dtype)->flags & (flag)) == (flag))

#define NpyArray_DESCR_REPLACE(descr) PyArray_DESCR_REPLACE(descr)
#define NpyArray_ISNBO(arg) ((arg) != NPY_OPPBYTE)
#define NpyArray_IsNativeByteOrder NpyArray_ISNBO
#define NpyArray_ISNOTSWAPPED(m) NpyArray_ISNBO(PyArray_DESCR(m)->byteorder)
#define NpyArray_ISBYTESWAPPED(m) (!NpyArray_ISNOTSWAPPED(m))

#define NpyArray_FLAGSWAP(m, flags) (NpyArray_CHKFLAGS(m, flags) &&       \
        NpyArray_ISNOTSWAPPED(m))


#define NpyArray_SAFEALIGNEDCOPY(obj) PyArray_SAFEALIGNEDCOPY(obj)
#define NpyArray_ISCARRAY(m) PyArray_FLAGSWAP(m, NPY_CARRAY)
#define NpyArray_ISCARRAY_RO(m) PyArray_FLAGSWAP(m, NPY_CARRAY_RO)
#define NpyArray_ISFARRAY(m) PyArray_FLAGSWAP(m, NPY_FARRAY)
#define NpyArray_ISFARRAY_RO(m) PyArray_FLAGSWAP(m, NPY_FARRAY_RO)
#define NpyArray_ISBEHAVED(m) PyArray_FLAGSWAP(m, NPY_BEHAVED)
#define NpyArray_ISBEHAVED_RO(m) PyArray_FLAGSWAP(m, NPY_ALIGNED)
#define NpyArray_ISALIGNED(m) PyArray_ISALIGNED(m)

#define NpyArray_TYPE(obj) PyArray_TYPE(obj)
#define NpyArray_NOTYPE PyArray_NOTYPE
#define NpyArray_NTYPES PyArray_NTYPES
#define NpyArray_NSORTS PyArray_NSORTS
#define NpyArray_USERDEF PyArray_USERDEF
#define NpyTypeNum_ISUSERDEF(a) PyTypeNum_ISUSERDEF(a)
#define NpyArray_BOOL PyArray_BOOL
#define NpyArray_GENBOOLLTR PyArray_GENBOOLLTR
#define NpyArray_SIGNEDLTR PyArray_SIGNEDLTR
#define NpyArray_INT8 PyArray_INT8
#define NpyArray_INT16 PyArray_INT16
#define NpyArray_INT32 PyArray_INT32
#define NpyArray_INT64 PyArray_INT64
#define NpyArray_UNSIGNEDLTR PyArray_UNSIGNEDLTR
#define NpyArray_UINT8 PyArray_UINT8
#define NpyArray_UINT16 PyArray_UINT16
#define NpyArray_UINT32 PyArray_UINT32
#define NpyArray_UINT64 PyArray_UINT64
#define NpyArray_FLOATINGLTR PyArray_FLOATINGLTR
#define NpyArray_FLOAT32 PyArray_FLOAT32
#define NpyArray_FLOAT64 PyArray_FLOAT64
#define NpyArray_FLOAT128 PyArray_FLOAT128
#define NpyArray_COMPLEXLTR PyArray_COMPLEXLTR
#define NpyArray_COMPLEX64 PyArray_COMPLEX64
#define NpyArray_COMPLEX128 PyArray_COMPLEX128
#define NpyArray_COMPLEX256 PyArray_COMPLEX256

#define NpyArray_NOSCALAR PyArray_NOSCALAR
#define NpyArray_NSCALARKINDS PyArray_NSCALARKINDS
#define NpyArray_FORTRANORDER NPY_FORTRANORDER

#define NpyArray_ITER_NEXT(it) PyArray_ITER_NEXT(it)
#define NpyArray_MultiIter_RESET(multi) PyArray_MultiIter_RESET(multi)
#define NpyArray_MultiIter_NEXT(multi) PyArray_MultiIter_NEXT(multi)
#define NpyArray_MultiIter_GOTO(multi, dest) PyArray_MultiIter_GOTO(multi, dest) 
#define NpyArray_MultiIter_GOTO1D(multi, ind) PyArray_MultiIter_GOTO1D(multi, ind)
#define NpyArray_MultiIter_DATA(multi, i) PyArray_MultiIter_DATA(multi, i)    
#define NpyArray_NEXTi(multi, i) PyArray_MultiIter_NEXTi(multi, i)   
#define NpyArray_NOTDONE(multi) PyArray_MultiIter_NOTDONE(multi)

#define NpyDataType_ISSTRING(obj) PyDataType_ISSTRING(obj)
#define NpyArray_CheckExact(op) PyArray_CheckExact(op)
#define NpyDataMem_NEW(size) PyDataMem_NEW(size)

/* 
 * Functions we need to convert.
 */

#define NpyArray_DescrFromType(type) \
        PyArray_DescrFromType(type)

/* convert_datatype.c */
#define NpyArray_CanCastTo(a, b) PyArray_CanCastTo(a, b)
#define NpyArray_CastTo(a, b) PyArray_CastTo(a, b)
#define NpyArray_CastAnyTo(a, b) PyArray_CastAnyTo(a, b)


/* ctors.c */
#define NpyArray_EnsureAnyArray(op)  (PyObject *)PyArray_EnsureAnyArray(op)


/* iterators.c */
#define NpyArray_IterAllButAxis(a1, a2) PyArray_IterAllButAxis(a1, a2)
#define NpyArray_MultiIterNew PyArray_MultiIterNew
#define NpyArray_RemoveSmallest(multi) PyArray_RemoveSmallest(multi)
#define NpyArray_IterNew(obj) PyArray_IterNew(obj)


/* multiarraymodule.c */
#define NpyArray_EquivTypes(a1, a2) PyArray_EquivTypes(a1, a2)


/* number.c */
#define NpyArray_GenericReduceFunction(m1, op, axis, rtype, out) \
        PyArray_GenericReduceFunction(m1, op, axis, rtype, out)


/* Already exists as a macro */
#define NpyArray_ContiguousFromAny(op, type, min_depth, max_depth)             \
        PyArray_FromAny(op, NpyArray_DescrFromType(type), min_depth,           \
        max_depth, NPY_DEFAULT, NULL)

#define NpyArray_EquivArrTypes(a1, a2)                                         \
        NpyArray_EquivTypes(NpyArray_DESCR(a1), NpyArray_DESCR(a2))


/*
 * API functions.
 */
npy_intp NpyArray_Size(NpyArray *op);
NpyArray *NpyArray_ArgMax(NpyArray *op, int axis, NpyArray *out);
NpyArray *NpyArray_CheckAxis(NpyArray *arr, int *axis, int flags);
int NpyArray_CompareUCS4(npy_ucs4 *s1, npy_ucs4 *s2, size_t len);
int NpyArray_CompareString(char *s1, char *s2, size_t len);
int NpyArray_ElementStrides(NpyArray *arr);
npy_bool NpyArray_CheckStrides(int elsize, int nd, npy_intp numbytes,
                               npy_intp offset,
                               npy_intp *dims, npy_intp *newstrides);
NpyArray *NpyArray_FromArray(NpyArray *arr, NpyArray_Descr *newtype, int flags);

int NpyArray_MoveInto(NpyArray *dest, NpyArray *src);

NpyArray* NpyArray_Newshape(NpyArray* self, NpyArray_Dims *newdims,
                            NPY_ORDER fortran);
NpyArray* NpyArray_Squeeze(NpyArray *self);
NpyArray* NpyArray_SwapAxes(NpyArray *ap, int a1, int a2);
NpyArray* NpyArray_Transpose(NpyArray *ap, NpyArray_Dims *permute);
int NpyArray_TypestrConvert(int itemsize, int gentype);
NpyArray* NpyArray_Ravel(NpyArray *a, NPY_ORDER fortran);
NpyArray* NpyArray_Flatten(NpyArray *a, NPY_ORDER order);

void NpyArray_InitArrFuncs(NpyArray_ArrFuncs *f);
int NpyArray_RegisterDataType(NpyArray_Descr *descr);
int NpyArray_RegisterCastFunc(NpyArray_Descr *descr, int totype,
                              NpyArray_VectorUnaryFunc *castfunc);
int NpyArray_RegisterCanCast(NpyArray_Descr *descr, int totype,
                             NPY_SCALARKIND scalar);
int NpyArray_TypeNumFromName(char *str);
int NpyArray_TypeNumFromTypeObj(void* typeobj);
NpyArray_Descr* NpyArray_UserDescrFromTypeNum(int typenum);

NpyArray *NpyArray_NewFromDescr(NpyTypeObject *subtype, 
                                NpyArray_Descr *descr, int nd,
                                npy_intp *dims, npy_intp *strides, void *data,
                                int flags, NpyObject *obj);
NpyArray *NpyArray_New(NpyTypeObject *subtype, int nd, npy_intp *dims, int type_num,
                       npy_intp *strides, void *data, int itemsize, int flags,
                       NpyObject *obj);
int NpyArray_CopyInto(NpyArray *dest, NpyArray *src);
int NpyArray_CopyAnyInfo(NpyArray *dest, NpyArray *src);

/*
 * Reference counting.
 */

#define Npy_INCREF(a) Py_INCREF(a)
#define Npy_DECREF(a) Py_DECREF(a)
#define Npy_XDECREF(a) Py_XDECREF(a)
#define NpyArray_REFCOUNT(a) PyArray_REFCOUNT(a)
#define NpyArray_INCREF(a) PyArray_INCREF(a)
#define NpyArray_DECREF(a) PyArray_DECREF(a)
#define NpyArray_XDECREF(a) PyArray_XDECREF(a)


/*
 * Memory
 */
#define NpyDataMem_RENEW(p, sz) PyDataMem_RENEW(p, sz)

#define NpyDimMem_RENEW(p, sz) PyDimMem_RENEW(p, sz)

/*
 * Error handling.
 */
#define NpyErr_SetString(exc, str) PyErr_SetString(exc, str)
#define NpyErr_NoMemory() PyErr_NoMemory()
#define NpyExc_ValueError PyExc_ValueError
#define NpyExc_MemoryError PyExc_MemoryError
#define NpyExc_TypeError PyExc_TypeError
#define NpyErr_Format PyErr_Format
#define NpyExc_RuntimeError PyExc_RuntimeError



/*
 * TMP
 */
#define NpyArray_MultiplyList(a, b) PyArray_MultiplyList(a, b)
#define NpyArray_View(a, b, c) ((NpyArray*) PyArray_View(a,b,c))
#define NpyArray_NewCopy(a, order) ((NpyArray*) PyArray_NewCopy(a, order))
#define NpyArray_UpdateFlags(a, flags) PyArray_UpdateFlags(a, flags)

extern int _flat_copyinto(NpyArray *dst, NpyArray *src, NPY_ORDER order);

#endif

