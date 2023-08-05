#include <Python.h>
#include <structmember.h>
#include <db.h>

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

#define WT_READ 0
#define WT_WRITE 1

#define WT_UINT 0 
#define WT_INT 1 
#define WT_FLOAT 2
#define WT_CHAR 3

#define WT_VAR_1 0 
#define MAX_NUM_ELEMENTS 255
#define MAX_ROW_SIZE 65536

#define MODULE_DOC \
"Low level Berkeley DB interface for wormtable"

static PyObject *WormtableError;

/* TODO:
 * 1) We need much better error reporting for the parsers. These should have a
 * top level variadic function that takes arguments and set the Python exception
 * appropriately.
 * 3) The numerical types need a little cleaning up and thought put into. We
 * now have single and double floating point sizes and should export constants
 * to tell what they are. There should also be some constants telling range
 * of integers and so on.
 */

typedef struct Column_t {
    PyObject_HEAD
    PyObject *name;
    PyObject *description;
    PyObject *min_element;
    PyObject *max_element;
    int position;
    int element_type;
    int element_size;
    int num_elements;
    int fixed_region_offset;
    void **input_elements; /* pointer to each elements in input format */
    void *element_buffer; /* parsed input elements in native CPU format */
    int num_buffered_elements;
    int (*string_to_native)(struct Column_t*, char *);  /* DEPRECATED */
    int (*python_to_native)(struct Column_t*, PyObject *);
    int (*verify_elements)(struct Column_t*);
    int (*truncate_elements)(struct Column_t*, double);
    int (*pack_elements)(struct Column_t*, void *);
    int (*unpack_elements)(struct Column_t*, void *);
    PyObject *(*native_to_python)(struct Column_t *, int);
} Column;


typedef struct {
    PyObject_HEAD
    DB *db;
    PyObject *filename;
    Column **columns;
    Py_ssize_t cache_size;
    u_int32_t num_columns;
    u_int32_t fixed_region_size;
    void *row_buffer;
    u_int32_t row_buffer_size;     /* max size */
    u_int32_t current_row_size;    /* current size */
    u_int64_t current_row_id;      
} Table;


typedef struct {
    PyObject_HEAD
    Table *table;
    DB *db;
    PyObject *filename;
    Py_ssize_t cache_size;
    u_int32_t *columns;
    u_int32_t num_columns;
    void *key_buffer;
    u_int32_t key_buffer_size;
    /* this buffer isn't really necessary - we should just use the table's
     * row buffer.
     */
    void *row_buffer;
    u_int32_t row_buffer_size;
    double *bin_widths;
} Index;

typedef struct {
    PyObject_HEAD
    Index *index;
    DBC *cursor;
    u_int32_t *read_columns;
    u_int32_t num_read_columns; 
    void *min_key;
    u_int32_t min_key_size;
    void *max_key;
    u_int32_t max_key_size;
} IndexRowIterator;


typedef struct {
    PyObject_HEAD
    Table *table;
    DBC *cursor;
    u_int32_t *read_columns;
    u_int32_t num_read_columns; 
    void *min_key;
    u_int32_t min_key_size;
    void *max_key;
    u_int32_t max_key_size;
} TableRowIterator;


typedef struct {
    PyObject_HEAD
    Index *index;
    DBC *cursor;
} DistinctValueIterator;


static void 
handle_bdb_error(int err)
{
    PyErr_SetString(WormtableError, db_strerror(err));
}

#ifndef WORDS_BIGENDIAN
/* 
 * Copies n bytes of source into destination, swapping the order of the 
 * bytes.
 */
static void
byteswap_copy(void* dest, void *source, size_t n)
{
    size_t j = 0;
    unsigned char *dest_c = (unsigned char *) dest;
    unsigned char *source_c = (unsigned char *) source;
    for (j = 0; j < n; j++) {
        dest_c[j] = source_c[n - j - 1];
    }
}
#endif

/* 
 * Returns the missing value for a k byte integer.
 */
static int64_t 
missing_int(u_int32_t k) 
{
    int64_t v = (-1) * (1ll << (8 * k - 1));
    return v;
}

/* 
 * Returns the minimum value for a k byte integer.
 */
static int64_t 
min_int(u_int32_t k) 
{
    int64_t v = (-1) * (1ll << (8 * k - 1)) + 1;
    return v;
}

/* 
 * Returns the maximum value for a k byte integer.
 */
static int64_t 
max_int(u_int32_t k) 
{
    int64_t v = (1ll << (8 * k - 1)) - 1;
    return v;
}

/* 
 * Returns the missing value for a k byte unsigned integer.
 */
static u_int64_t 
missing_uint(u_int32_t k) 
{
    return (u_int64_t) -1ll;
}

/* 
 * Returns the maximum value for a k byte unsigned integer.
 */
static u_int64_t 
max_uint(u_int32_t k) 
{
    u_int64_t v = (u_int64_t) -1ll;
    if (k < 8) {
        v = (1ll << (8 * k)) - 1;
    } 
    return v - 1;
}

/* 
 * Returns the minumum value for a k byte unsigned integer.
 */
static u_int64_t 
min_uint(u_int32_t k) 
{
    u_int64_t v = 0ll;
    return v;
}


/* 
 * Returns the missing value for a k byte float.
 *
 */
static double 
missing_float(u_int32_t k) 
{
    double v;
    u_int64_t u = 0xffffffffffffffffLL;
    memcpy(&v, &u, sizeof(double));
    return v;
}


/*==========================================================
 * Column object 
 *==========================================================
 */

/**************************************
 *
 * Native values to Python conversion. 
 *
 *************************************/

static PyObject *
Column_native_to_python_uint(Column *self, int index)
{
    PyObject *ret = NULL;
    u_int64_t *elements = (u_int64_t *) self->element_buffer;
    u_int64_t missing_value = missing_uint(self->element_size); 
    if (elements[index] == missing_value) {
        Py_INCREF(Py_None);
        ret = Py_None;
    } else {
        ret = PyLong_FromUnsignedLongLong((unsigned long long) elements[index]);
        if (ret == NULL) {
            PyErr_NoMemory();
        }
    }
    return ret;
}

static PyObject *
Column_native_to_python_int(Column *self, int index)
{
    PyObject *ret = NULL;
    int64_t *elements = (int64_t *) self->element_buffer;
    int64_t missing_value = missing_int(self->element_size); 
    if (elements[index] == missing_value) {
        Py_INCREF(Py_None);
        ret = Py_None;
    } else {
        ret = PyLong_FromLongLong((long long) elements[index]);
        if (ret == NULL) {
            PyErr_NoMemory();
        }
    }
    return ret;
}

static PyObject *
Column_native_to_python_float(Column *self, int index)
{
    PyObject *ret = NULL;
    double *elements = (double *) self->element_buffer;
    /* We cannot compare directly to missing value here because NaN is not 
     * equal to itself. Therefore we test against NaN and assume that 
     * this is equal to the missing value. This may cause problems!
     */
    if (isnan(elements[index])) {
        Py_INCREF(Py_None);
        ret = Py_None;
    } else {
        ret = PyFloat_FromDouble(elements[index]);
        if (ret == NULL) {
            PyErr_NoMemory();
        }
    }
    return ret;
}

static PyObject *
Column_native_to_python_char(Column *self, int index)
{
    PyObject *ret = NULL;
    int j = self->num_buffered_elements - 1;
    char *str = (char *) self->element_buffer;
    if (self->num_elements != WT_VAR_1) {
        /* check for shortened fixed-length strings, which will be padded 
         * with NULLs */
        while (str[j] == '\0' && j >= 0) {
            j--;
        }
    }
    ret = PyBytes_FromStringAndSize(str, j + 1); 
    if (ret == NULL) {
        PyErr_NoMemory();
    }
    return ret;
}

/**************************************
 *
 * Floating point packing and unpacking. This is based on the implementation 
 * of SortedFloat and SortedDouble from Berkeley DB Java edition. See 
 * com.sleepycat.bind.tuple.TupleInput for the source of the bit
 * manipulations below.
 *
 *************************************/

static void 
pack_float(float value, void *dest)
{
    int32_t float_bits;
    memcpy(&float_bits, &value, sizeof(float));
    float_bits ^= (float_bits < 0) ? 0xffffffff: 0x80000000;
#ifdef WORDS_BIGENDIAN
    memcpy(dest, &float_bits, sizeof(float)); 
#else    
    byteswap_copy(dest, &float_bits, sizeof(float)); 
#endif
}

static double  
unpack_float(void *src)
{
    int32_t float_bits;
    float value;
#ifdef WORDS_BIGENDIAN
    memcpy(&float_bits, src, sizeof(float));
#else
    byteswap_copy(&float_bits, src, sizeof(float));
#endif
    float_bits ^= (float_bits < 0) ? 0x80000000: 0xffffffff;
    memcpy(&value, &float_bits, sizeof(float));
    return (double) value;
}

static void 
pack_double(double value, void *dest)
{
    int64_t double_bits;
    memcpy(&double_bits, &value, sizeof(double));
    double_bits ^= (double_bits < 0) ? 0xffffffffffffffffLL: 0x8000000000000000LL;
#ifdef WORDS_BIGENDIAN
    memcpy(dest, &double_bits, sizeof(double)); 
#else
    byteswap_copy(dest, &double_bits, sizeof(double)); 
#endif
}

static double  
unpack_double(void *src)
{
    int64_t double_bits;
    double value;
#ifdef WORDS_BIGENDIAN
    memcpy(&double_bits, src, sizeof(double));
#else
    byteswap_copy(&double_bits, src, sizeof(double));
#endif
    double_bits ^= (double_bits < 0) ? 0x8000000000000000LL: 0xffffffffffffffffLL;
    memcpy(&value, &double_bits, sizeof(double));
    return value;
}


/**************************************
 *
 * Unpacking from a row to the element buffer. 
 *
 *************************************/

static u_int64_t
unpack_uint(void *src, u_int8_t size) 
{
    u_int64_t dest = 0;
    void *v = &dest;
#ifdef WORDS_BIGENDIAN
    memcpy(v + 8 - size, src, size);
#else
    byteswap_copy(v, src, size);
#endif
    /* decrement and return */
    dest -= 1;
    return dest; 
}


static int 
Column_unpack_elements_uint(Column *self, void *source)
{
    int j;
    int ret = -1;
    u_int64_t *elements = (u_int64_t *) self->element_buffer;
    int size = self->element_size; 
    for (j = 0; j < self->num_buffered_elements; j++) {
        elements[j] = unpack_uint(source + j * size, size); 
    }
    ret = 0;
    return ret; 
}

static int64_t
unpack_int(void *src, u_int8_t size) 
{
    int64_t dest = 0;
    void *v = &dest;
    const int64_t m = 1LL << (size * 8 - 1);
#ifdef WORDS_BIGENDIAN
    memcpy(v + 8 - size, src, size);
#else
    byteswap_copy(v, src, size);
#endif
    /* flip the sign bit */
    dest ^= m;
    /* sign extend and return */
    dest = (dest ^ m) - m;
    return dest; 
}


static int 
Column_unpack_elements_int(Column *self, void *source)
{
    int j;
    int ret = -1;
    int64_t *elements = (int64_t *) self->element_buffer;
    int size = self->element_size; 
    for (j = 0; j < self->num_buffered_elements; j++) {
        elements[j] = unpack_int(source + j * size, size); 
    }
    ret = 0;
    return ret; 
}

static int 
Column_unpack_elements_float(Column *self, void *source)
{
    int j;
    int ret = -1;
    void *v = source;
    double *elements = (double *) self->element_buffer;
    /* TODO Tidy this up and make it consistent with the pack definition */
    for (j = 0; j < self->num_buffered_elements; j++) {
        if (self->element_size == 4) {
            elements[j] = unpack_float(v); 
        } else {
            elements[j] = unpack_double(v); 
        }
        v += self->element_size;
    }
    ret = 0;
    return ret; 
}

static int 
Column_unpack_elements_char(Column *self, void *source)
{
    /*
    char v[1024];
    memcpy(v, source, self->num_buffered_elements); 
    v[self->num_buffered_elements] = 0;
    printf("unpacked: '%s': %d\n", v, self->num_buffered_elements);
    */
    memcpy(self->element_buffer, source, self->num_buffered_elements); 
    return  0; 
}




/**************************************
 *
 * Packing native values from the element_buffer to a row.
 *
 *************************************/

static int 
Column_pack_elements_uint(Column *self, void *dest)
{
    int j;
    int ret = -1;
    void *v = dest;
    void *src;
    u_int64_t *elements = (u_int64_t *) self->element_buffer;
    u_int64_t u;
    for (j = 0; j < self->num_buffered_elements; j++) {
        u = elements[j];
        /* increment before storing */
        u += 1; 
        src = &u;
#ifdef WORDS_BIGENDIAN
        memcpy(v, src + (8 - self->element_size), self->element_size);
#else
        byteswap_copy(v, src, self->element_size);
#endif
        v += self->element_size;
    }
    ret = 0;
    return ret; 
}

static int 
Column_pack_elements_int(Column *self, void *dest)
{
    int j;
    int ret = -1;
    void *v = dest;
    void *src;
    int64_t *elements = (int64_t *) self->element_buffer;
    int64_t u;
    for (j = 0; j < self->num_buffered_elements; j++) {
        //printf("\npacking :%ld\n", elements[j]); 
        u = elements[j];
        /* flip the sign bit */
        u ^= 1LL << (self->element_size * 8 - 1);
        src = &u;
#ifdef WORDS_BIGENDIAN
        memcpy(v, src + (8 - self->element_size), self->element_size);
#else
        byteswap_copy(v, src, self->element_size);
#endif
        v += self->element_size;
    }
    ret = 0;
    return ret; 
}

static int 
Column_pack_elements_float(Column *self, void *dest)
{
    int j;
    int ret = -1;
    void *v = dest;
    double *elements = (double *) self->element_buffer;
    /* TODO tidy this up */
    for (j = 0; j < self->num_buffered_elements; j++) {
        if (self->element_size == 4) {
            pack_float((float) elements[j], v);
        } else if (self->element_size == 8) {
            pack_double(elements[j], v);
        } else {
            assert(0);
        }
        
        
        v += self->element_size;
    }
    ret = 0;
    return ret; 
}

static int 
Column_pack_elements_char(Column *self, void *dest)
{
    int ret = -1;
    /*
    char v[1024];
    memcpy(v, self->element_buffer, self->num_buffered_elements); 
    v[self->num_buffered_elements] = 0;
    printf("packed: '%s': %d\n", v, self->num_buffered_elements);
    */
    memcpy(dest, self->element_buffer, self->num_buffered_elements); 
    ret = 0;
    return ret; 
}



/**************************************
 *
 * Verify elements in the buffer. 
 *
 *************************************/

/* This doesn't really have any useful function any more, as we were forced
 * to put the range checking functionality into the native_to_python_int
 * function. This is was because there was no way to exclude the user 
 * from using the missing_value as an input parameter, and this would 
 * have led to very annoying bugs. This doesn't do any harm here though,
 * so let's leave it in for now.
 */
static int 
Column_verify_elements_uint(Column *self)
{
    int j;
    int ret = -1;
    u_int64_t *elements = (u_int64_t *) self->element_buffer;
    u_int64_t min_value = min_uint(self->element_size); 
    u_int64_t max_value = max_uint(self->element_size); 
    u_int64_t missing_value = missing_uint(self->element_size); 
    for (j = 0; j < self->num_buffered_elements; j++) {
        if (elements[j] != missing_value && 
                (elements[j] < min_value || elements[j] > max_value)) {
            PyErr_Format(PyExc_OverflowError, 
                    "Values for column '%s' must be between %lld and %lld",
                    PyBytes_AsString(self->name), (long long) min_value, 
                    (long long) max_value);
            goto out;
        }
    }
    ret = 0;
out:
    return ret; 

}
    
static int 
Column_verify_elements_int(Column *self)
{
    int j;
    int ret = -1;
    int64_t *elements = (int64_t *) self->element_buffer;
    int64_t min_value = min_int(self->element_size); 
    int64_t max_value = max_int(self->element_size); 
    int64_t missing_value = missing_int(self->element_size); 
    for (j = 0; j < self->num_buffered_elements; j++) {
        if (elements[j] != missing_value && 
                (elements[j] < min_value || elements[j] > max_value)) {
            PyErr_Format(PyExc_OverflowError, 
                    "Values for column '%s' must be between %lld and %lld",
                    PyBytes_AsString(self->name), (long long) min_value, 
                    (long long) max_value);
            goto out;
        }
    }
    ret = 0;
out:
    return ret; 

}

static int 
Column_verify_elements_float(Column *self)
{
    return 0; 
}

static int 
Column_verify_elements_char(Column *self)
{
    return 0; 
}

/**************************************
 *
 * Truncate elements in the buffer. 
 *
 *************************************/
static int 
Column_truncate_elements_uint(Column *self, double bin_width)
{
    int ret = 0;
    unsigned int j;
    u_int64_t w = (u_int64_t) bin_width; 
    u_int64_t *elements = (u_int64_t *) self->element_buffer;
    u_int64_t missing_value = missing_uint(self->element_size); 
    u_int64_t u; 
    if (bin_width <= 0.0) {
        PyErr_Format(PyExc_SystemError, "bin_width for column '%s' must > 0",
                PyBytes_AsString(self->name));
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        u = elements[j];
        if (u != missing_value) {
            elements[j] = u - (u % w);
        }
    }
    ret = 0;
out:
    return ret;
}


    
static int 
Column_truncate_elements_int(Column *self, double bin_width)
{
    int ret = 0;
    unsigned int j;
    int64_t w = (int64_t) bin_width; 
    int64_t *elements = (int64_t *) self->element_buffer;
    int64_t missing_value = missing_int(self->element_size); 
    int64_t u; 
    if (bin_width <= 0.0) {
        PyErr_Format(PyExc_SystemError, "bin_width for column '%s' must > 0",
                PyBytes_AsString(self->name));
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        u = elements[j];
        if (u != missing_value) {
            elements[j] = u - (u % w);
        }
    }
    ret = 0;
out:
    return ret;
}

static int 
Column_truncate_elements_float(Column *self, double bin_width)
{
    int ret = -1;
    unsigned int j;
    double missing_value = missing_float(self->element_size);
    double *elements = (double *) self->element_buffer;
    double u; 
    if (bin_width <= 0.0) {
        PyErr_Format(PyExc_SystemError, "bin_width for column '%s' must > 0",
                PyBytes_AsString(self->name));
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        u = elements[j];
        if (u != missing_value) {
            elements[j] = u - fmod(u, bin_width); 
        }
        //printf("truncating :%f by %f = %f\n", u, bin_width, elements[j]);    
    }
    ret = 0;
out:
    return ret;
    
}

static int 
Column_truncate_elements_char(Column *self, double bin_width)
{
    return 0; 
}


/**************************************
 *
 * Python input element parsing.
 *
 *************************************/


/*
 * Takes a Python sequence and places pointers to the Python 
 * elements into the input_elements list. Checks for various 
 * errors in the format of this sequence.
 */
static int 
Column_parse_python_sequence(Column *self, PyObject *elements)
{
    int ret = -1;
    int j, num_elements;
    PyObject *seq = NULL;
    PyObject *v;
    self->num_buffered_elements = 0;
    if (self->num_elements == 1) {
        self->input_elements[0] = elements;
        num_elements = 1;
    } else {
        seq = PySequence_Fast(elements, "Sequence required");
        if (seq == NULL) {
            goto out;
        }
        num_elements = PySequence_Fast_GET_SIZE(seq);
        if (self->num_elements == WT_VAR_1) {
            if (num_elements > MAX_NUM_ELEMENTS) {
                PyErr_Format(PyExc_ValueError, 
                        "too many elements for column '%s'",
                        PyBytes_AsString(self->name));
                goto out;
            }
        } else {    
            if (num_elements != self->num_elements) {
                PyErr_Format(PyExc_ValueError, 
                        "incorrect number of elements for column '%s'",
                        PyBytes_AsString(self->name));
                goto out;
            }
        }
        for (j = 0; j < num_elements; j++) {
            v = PySequence_Fast_GET_ITEM(seq, j);
            self->input_elements[j] = v; 
        }
    }
    if (self->num_elements != WT_VAR_1) {
        if (num_elements != self->num_elements) {
            PyErr_Format(PyExc_ValueError, 
                    "incorrect number of elements for column '%s'",
                    PyBytes_AsString(self->name));
            goto out;
        }
    }
    self->num_buffered_elements = num_elements;
    ret = 0;
out:
    Py_XDECREF(seq);
    return ret;
}

static int 
Column_python_to_native_uint(Column *self, PyObject *elements)
{
    int ret = -1;
    u_int64_t *native= (u_int64_t *) self->element_buffer; 
    u_int64_t missing_value = missing_uint(self->element_size); 
    u_int64_t min_value = min_uint(self->element_size);  
    u_int64_t max_value = max_uint(self->element_size); 
    PyObject *v;
    int j;
    if (Column_parse_python_sequence(self, elements) < 0) {
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        v = (PyObject *) self->input_elements[j];
        if (v == Py_None) {
            native[j] = missing_value;
        } else { 
            if (!PyNumber_Check(v)) {
                PyErr_Format(PyExc_TypeError, 
                        "Values for column '%s' must be numeric",
                        PyBytes_AsString(self->name));
                goto out;
            }
#ifdef IS_PY3K
            native[j] = (u_int64_t) PyLong_AsUnsignedLongLong(v);
#else
            /* there's a problem with Python 2 in which we have to convert to 
             * long first.
             */
            v = PyNumber_Long(v);
            if (v == NULL) {
                goto out;
            }
            native[j] = (u_int64_t) PyLong_AsUnsignedLongLong(v);
            Py_DECREF(v);
#endif
            if (native[j] == -1) {
                /* PyLong_AsUnsignedLongLong return -1 and raises OverFlowError
                 * if the value cannot be represented as an unsigned long long 
                 */
                if (PyErr_Occurred()) {
                    goto out;
                }
            }
            /* check if the values are in the right range for the column */
            if (native[j] < min_value || native[j] > max_value) {
                PyErr_Format(PyExc_OverflowError, 
                        "Values for column '%s' must be between %lld and %lld",
                        PyBytes_AsString(self->name), (long long) min_value, 
                        (long long) max_value);
                goto out;
            }
        }
    }
    ret = 0;
out:
    return ret;
}


static int 
Column_python_to_native_int(Column *self, PyObject *elements)
{
    int ret = -1;
    int64_t *native= (int64_t *) self->element_buffer; 
    int64_t missing_value = missing_int(self->element_size); 
    int64_t min_value = min_int(self->element_size); 
    int64_t max_value = max_int(self->element_size); 
    PyObject *v;
    int j;
    if (Column_parse_python_sequence(self, elements) < 0) {
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        v = (PyObject *) self->input_elements[j];
        if (v == Py_None) {
            native[j] = missing_value;
        } else { 
            if (!PyNumber_Check(v)) {
                PyErr_Format(PyExc_TypeError, 
                        "Values for column '%s' must be numeric",
                        PyBytes_AsString(self->name));
                goto out;
            }
            native[j] = (int64_t) PyLong_AsLongLong(v);
            if (native[j] == -1) {
                /* PyLong_AsLongLong return -1 and raises OverFlowError if 
                 * the value cannot be represented as a long long 
                 */
                if (PyErr_Occurred()) {
                    goto out;
                }
            }
            /* check if the values are in the right range for the column */
            if (native[j] < min_value || native[j] > max_value) {
                PyErr_Format(PyExc_OverflowError, 
                        "Values for column '%s' must be between %lld and %lld",
                        PyBytes_AsString(self->name), (long long) min_value, 
                        (long long) max_value);
                goto out;
            }
        }
    }
    ret = 0;
out:
    return ret;
}

static int 
Column_python_to_native_float(Column *self, PyObject *elements)
{
    int ret = -1;
    double *native = (double *) self->element_buffer; 
    double missing_value = missing_float(self->element_size);
    PyObject *v;
    int j;
    if (Column_parse_python_sequence(self, elements) < 0) {
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        v = (PyObject *) self->input_elements[j];
        if (v == Py_None) {
            native[j] = missing_value;
        } else {
            if (!PyNumber_Check(v)) {
                PyErr_Format(PyExc_TypeError, 
                        "Values for column '%s' must be numeric",
                        PyBytes_AsString(self->name));
                goto out;
            }
            native[j] = (double) PyFloat_AsDouble(v);
        }
    }
    ret = 0;
out:
    return ret;
}

static int 
Column_python_to_native_char(Column *self, PyObject *elements)
{
    int ret = -1;
    char *s;
    Py_ssize_t max_length = self->num_elements == WT_VAR_1?
            MAX_NUM_ELEMENTS: self->num_elements;
    Py_ssize_t length;
    /* Elements must be a single Python bytes object */
    if (!PyBytes_Check(elements)) {
        PyErr_Format(PyExc_TypeError, 
                "Values for column '%s' must be bytes",
                PyBytes_AsString(self->name));
        goto out;
    }
    if (PyBytes_AsStringAndSize(elements, &s, &length) < 0) {
        PyErr_Format(PyExc_ValueError, 
                "String conversion failed for column '%s'",
                PyBytes_AsString(self->name));
        goto out;
    }
    if (length > max_length) {
        PyErr_Format(PyExc_ValueError, 
                "String too long for column '%s'",
                PyBytes_AsString(self->name));
        goto out;
    }
    memcpy(self->element_buffer, s, length);
    self->num_buffered_elements = length;
    if (self->num_elements != WT_VAR_1) {
        /* Pad out the remaining space with zeros */
        while (self->num_buffered_elements != self->num_elements) {
            ((char *) self->element_buffer)[self->num_buffered_elements] = '\0';
            self->num_buffered_elements++;
        }
    }
    ret = 0; 
out:
    return ret;
}



/**************************************
 *
 * String input element parsing.
 *
 *************************************/

/*
 * Takes a string sequence and places pointers to the start
 * of each individual element into the input_elements list.
 * Checks for various errors in the format of this sequence.
 */
static int 
Column_parse_string_sequence(Column *self, char *s)
{
    int ret = -1;
    int j, num_elements, delimiter;
    self->num_buffered_elements = 0;
    if (self->num_elements == 1) {
        self->input_elements[0] = s;
        num_elements = 1;
    } else {
        j = 0;
        num_elements = 0;
        delimiter = -1;
        if (s[0] == '\0') {
            PyErr_SetString(PyExc_ValueError, "Empty value");
            goto out;
        }
        /* TODO this needs lots of error checking! */
        while (s[j] != '\0') {
            if (s[j] == ',' || s[j] == ';') {
                delimiter = j; 
            }
            if (j == delimiter + 1) {
                /* this is the start of a new element */
                self->input_elements[num_elements] = &s[j];
                num_elements++;
            }
            j++;
        }
    }
    if (self->num_elements != WT_VAR_1) {
        if (num_elements != self->num_elements) {
            PyErr_SetString(PyExc_ValueError, "incorrect number of elements");
            goto out;
        }
    }
    self->num_buffered_elements = num_elements;
    ret = 0;
out:
    return ret;
}

static int 
Column_string_to_native_uint(Column *self, char *string)
{
    int ret = -1;
    u_int64_t *native= (u_int64_t *) self->element_buffer; 
    char *v, *tail;
    int j;
    if (Column_parse_string_sequence(self, string) < 0) {
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        v = (char *) self->input_elements[j];
        errno = 0;
        native[j] = (u_int64_t) strtoull(v, &tail, 0);
        if (errno) {
            PyErr_SetString(PyExc_ValueError, "Element overflow");
            goto out;
        }
        if (v == tail) {
            PyErr_SetString(PyExc_ValueError, "Element parse error");
            goto out;
        }
        if (*tail != '\0') {
            if (!(isspace(*tail) || *tail == ',' || *tail == ';')) {
                PyErr_SetString(PyExc_ValueError, "Element parse error");
                goto out;
            }
        }
    }
    ret = 0;
out:
    return ret;
}


static int 
Column_string_to_native_int(Column *self, char *string)
{
    int ret = -1;
    int64_t *native= (int64_t *) self->element_buffer; 
    char *v, *tail;
    int j;
    if (Column_parse_string_sequence(self, string) < 0) {
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        v = (char *) self->input_elements[j];
        errno = 0;
        native[j] = (int64_t) strtoll(v, &tail, 0);
        if (errno) {
            PyErr_SetString(PyExc_ValueError, "Element overflow");
            goto out;
        }
        if (v == tail) {
            PyErr_SetString(PyExc_ValueError, "Element parse error");
            goto out;
        }
        if (*tail != '\0') {
            if (!(isspace(*tail) || *tail == ',' || *tail == ';')) {
                PyErr_SetString(PyExc_ValueError, "Element parse error");
                goto out;
            }
        }
    }
    ret = 0;
out:
    return ret;
}


static int 
Column_string_to_native_float(Column *self, char *string)
{
    int ret = -1;
    double *native= (double *) self->element_buffer; 
    char *v, *tail;
    int j;
    if (Column_parse_string_sequence(self, string) < 0) {
        goto out;
    }
    for (j = 0; j < self->num_buffered_elements; j++) {
        v = (char *) self->input_elements[j];
        errno = 0;
        native[j] = (double) strtod(v, &tail);
        if (errno) {
            PyErr_SetString(PyExc_ValueError, "Element overflow");
            goto out;
        }
        if (v == tail) {
            PyErr_SetString(PyExc_ValueError, "Element parse error");
            goto out;
        }
        if (*tail != '\0') {
            if (!(isspace(*tail) || *tail == ',' || *tail == ';')) {
                PyErr_SetString(PyExc_ValueError, "Element parse error");
                goto out;
            }
        }
    }
    ret = 0;
out:
    return ret;
}
 
static int 
Column_string_to_native_char(Column *self, char *string)
{
    int ret = -1;
    size_t n = strlen(string);
    Py_ssize_t max_length = self->num_elements == WT_VAR_1?
            MAX_NUM_ELEMENTS: self->num_elements;
    if (n > max_length) {
        PyErr_Format(PyExc_ValueError, 
                "String too long for column '%s'",
                PyBytes_AsString(self->name));
        goto out;
    }
    memcpy(self->element_buffer, string, n); 
    self->num_buffered_elements = n;
    ret = 0;
out:
    return ret;
}


/*
 * Packs the address and number of elements in a variable length column at the
 * specified pointer.
 * 
 */
static int 
Column_pack_variable_elements_address(Column *self, void *dest, 
        uint32_t offset, uint32_t num_elements)
{
    int ret = -1;
    uint16_t off = (uint16_t) offset;
    uint8_t n = (uint8_t) num_elements;
    void *v = dest;
    if (offset >= MAX_ROW_SIZE) {
        PyErr_SetString(PyExc_SystemError, "Row overflow");
        goto out;
    }
    if (num_elements > MAX_NUM_ELEMENTS) {
        PyErr_SetString(PyExc_SystemError, "too many elements");
        goto out;
    }
#if WORDS_BIGENDIAN
    memcpy(v, &off, sizeof(off)); 
    memcpy(v + sizeof(off), &n, sizeof(n)); 
#else
    byteswap_copy(v, &off, sizeof(off)); 
    byteswap_copy(v + sizeof(off), &n, sizeof(n)); 
#endif
    ret = 0;
out:
    return ret;
}   

/*
 * Unpacks the address and number of elements in a variable length column at the
 * specified pointer.
 */
static int 
Column_unpack_variable_elements_address(Column *self, void *src, 
        uint32_t *offset, uint32_t *num_elements)
{
    int ret = -1;
    void *v = src;
    uint16_t off = 0;
    uint8_t n = 0;
#if WORDS_BIGENDIAN
    memcpy(&off, v, sizeof(off)); 
    memcpy(&n, v + sizeof(off), sizeof(n)); 
#else
    byteswap_copy(&off, v, sizeof(off)); 
    byteswap_copy(&n, v + sizeof(off), sizeof(n)); 
#endif
    /* this is actually always false now, but will be important in future */
    if (((u_int32_t) off) >= MAX_ROW_SIZE) {
        PyErr_SetString(PyExc_SystemError, "Row overflow");
        goto out;
    }
    if (n > MAX_NUM_ELEMENTS) {
        PyErr_SetString(PyExc_SystemError, "too many elements");
        goto out;
    }
    *offset = (uint32_t) off;
    *num_elements = (uint32_t) n;
    ret = 0;
out: 
    return ret;
}   


/*
 * Inserts the values in the element buffer into the specified row which 
 * is currently of the specified size, and return the number of bytes 
 * used in the variable region. Returns -1 in the case of an error with 
 * the appropriate Python exception set.
 */
static int 
Column_update_row(Column *self, void *row, uint32_t row_size)
{
    int ret = -1;
    void *dest;
    int bytes_added = 0;
    uint32_t num_elements = (uint32_t) self->num_buffered_elements;
    int data_size = num_elements * self->element_size;
    if (self->verify_elements(self) < 0) {
        goto out;
    }
    dest = row + self->fixed_region_offset; 
    if (self->num_elements == WT_VAR_1) {
        bytes_added = data_size;
        if (row_size + bytes_added > MAX_ROW_SIZE) {
            PyErr_SetString(PyExc_ValueError, "Row overflow");
            goto out;
        }
        if (Column_pack_variable_elements_address(self, dest, row_size, 
                num_elements) < 0) {
            goto out;
        }
        //printf("set to offset %d, with %d bytes\n", row_size, num_elements);
        dest = row + row_size; 
    }
    self->pack_elements(self, dest);
    ret = bytes_added;
out:
    return ret;
}

/*
 * Extracts elements from the specified row and inserts them into the 
 * element buffer. 
 */
static int 
Column_extract_elements(Column *self, void *row)
{
    int ret = -1;
    void *src;
    uint32_t offset, num_elements;
    src = row + self->fixed_region_offset; 
    num_elements = self->num_elements;
    if (self->num_elements == WT_VAR_1) {
        if (Column_unpack_variable_elements_address(self, src, &offset, 
                &num_elements) < 0) {
            goto out;
        }
        src = row + offset;
    }
    self->num_buffered_elements = num_elements;
    ret = self->unpack_elements(self, src);
out:
    return ret;
}

/* Copies the data values from the specified source to the specified 
 * destination
 */
static int
Column_copy_row_values(Column *self, void *dest, void *src)
{
    int ret = -1;
    uint32_t len, num_elements, offset;
    void *v = src + self->fixed_region_offset;
    offset = 0;
    num_elements = self->num_elements;
    if (self->num_elements == WT_VAR_1) {
        if (Column_unpack_variable_elements_address(self, v, &offset, 
                &num_elements) < 0) {
            goto out;
        }
        v = src + offset;
    }
    len = self->element_size * num_elements;
    memcpy(dest, v, len); 
    ret = len;
out:
    return ret;
}
/* Copies the data values from the specified source to the specified 
 * destination by first reading them back and then truncating then 
 * according to the specified bin_width.
 */
static int
Column_truncate_values(Column *self, double bin_width, void *dest, void *src)
{
    int ret = -1;
    if (Column_extract_elements(self, src) < 0) {
        goto out;
    }
    if (self->truncate_elements(self, bin_width) < 0) {
        goto out;
    }
    if (self->pack_elements(self, dest) < 0) {
        goto out;
    }
    ret = self->num_buffered_elements * self->element_size;
out:
    return ret;
}

/*
 * Converts the native values in the element buffer to the appropriate 
 * Python types, and returns the result.
 */
static PyObject *
Column_get_python_elements(Column *self)
{
    PyObject *ret = NULL;
    PyObject *u, *t;
    Py_ssize_t j;
    /* TODO Missing value handling is a mess FIXME!!! */
    if (self->element_type == WT_CHAR) {
        ret = self->native_to_python(self, 0);
        if (ret == NULL) {
            goto out;
        }
    } else {
        if (self->num_buffered_elements == 0) {
            /* this is the missing value case. If we have a 
             * variable number of elements, we return an empty
             * tuple, otherwise it's None.
             */
            if (self->num_elements == WT_VAR_1) {
                t = PyTuple_New(0);
                if (t == NULL) {
                    PyErr_NoMemory();
                    goto out;
                }
                ret = t;
            } else {
                Py_INCREF(Py_None);
                ret = Py_None;
            }
        } else {
            if (self->num_elements == 1) {
                ret = self->native_to_python(self, 0);
                if (ret == NULL) {
                    goto out;
                }
            } else {
                t = PyTuple_New(self->num_buffered_elements);
                if (t == NULL) {
                    PyErr_NoMemory();
                    goto out;
                }
                for (j = 0; j < self->num_buffered_elements; j++) {
                    u = self->native_to_python(self, j);
                    if (u == NULL) {
                        Py_DECREF(t);
                        PyErr_NoMemory();
                        goto out;
                    }
                    PyTuple_SET_ITEM(t, j, u);
                }
                ret = t;
            }
        }
    }
out:
    return ret;
}



/* 
 * Returns the number of bytes that this column occupies in the 
 * fixed region of records.
 */  
static int 
Column_get_fixed_region_size(Column *self) 
{
    int ret = self->element_size * self->num_elements;
    if (self->num_elements == WT_VAR_1) {
        /* two byte offset + one byte count */
        ret = 3;
    }
    return ret;
}

/**************************************
 *
 * Special methods for the row_id column 
 *
 *************************************/

static int 
Column_get_row_id(Column *self, u_int64_t *key) 
{
    int ret = -1; 
    u_int64_t *native = (u_int64_t *) self->element_buffer;
    if (self->num_buffered_elements != 1) {
        PyErr_Format(PyExc_SystemError, "key retrieval error."); 
        goto out;
    }
    *key = native[0];
    ret = 0; 
out:
    return ret;
}

static int 
Column_set_row_id(Column *self, u_int64_t key) 
{
    int ret = -1;
    u_int64_t *native = (u_int64_t *) self->element_buffer;
    native[0] = key;
    self->num_buffered_elements = 1;
    ret = 0;
    return ret;
}

static void
Column_dealloc(Column* self)
{
    Py_XDECREF(self->name); 
    Py_XDECREF(self->description); 
    Py_XDECREF(self->min_element); 
    Py_XDECREF(self->max_element); 
    PyMem_Free(self->element_buffer);
    PyMem_Free(self->input_elements);
    Py_TYPE(self)->tp_free((PyObject*)self);
}


static int
Column_init(Column *self, PyObject *args, PyObject *kwds)
{
    int ret = -1;
    static char *kwlist[] = {"name", "description",  "element_type", 
        "element_size", "num_elements", NULL};
    Py_ssize_t max_num_elements; 
    Py_ssize_t native_element_size;
    PyObject *name = NULL;
    PyObject *description = NULL;
    self->position = -1;
    self->min_element = NULL;
    self->max_element = NULL;
    self->element_buffer = NULL;
    self->input_elements = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!iii", kwlist, 
            &PyBytes_Type, &name, 
            &PyBytes_Type, &description, 
            &self->element_type, &self->element_size, 
            &self->num_elements)) {  
        goto out;
    }
    self->name = name;
    self->description = description;
    Py_INCREF(self->name);
    Py_INCREF(self->description);
    if (self->element_type == WT_UINT) {
        if (self->element_size < 1 || self->element_size > 8) {
            PyErr_SetString(PyExc_ValueError, "bad element size");
            goto out;
        }
        self->python_to_native = Column_python_to_native_uint;
        self->string_to_native = Column_string_to_native_uint;
        self->verify_elements = Column_verify_elements_uint;
        self->truncate_elements = Column_truncate_elements_uint;
        self->pack_elements = Column_pack_elements_uint;
        self->unpack_elements = Column_unpack_elements_uint;
        self->native_to_python = Column_native_to_python_uint; 
        native_element_size = sizeof(u_int64_t);
        self->min_element = PyLong_FromUnsignedLongLong(
                min_uint(self->element_size));
        self->max_element = PyLong_FromUnsignedLongLong(
                max_uint(self->element_size));
        if (self->min_element == NULL || self->max_element == NULL) {
            PyErr_NoMemory();
            goto out;
        }
    } else if (self->element_type == WT_INT) {
        if (self->element_size < 1 || self->element_size > 8) {
            PyErr_SetString(PyExc_ValueError, "bad element size");
            goto out;
        }
        self->python_to_native = Column_python_to_native_int;
        self->string_to_native = Column_string_to_native_int;
        self->verify_elements = Column_verify_elements_int;
        self->truncate_elements = Column_truncate_elements_int;
        self->pack_elements = Column_pack_elements_int;
        self->unpack_elements = Column_unpack_elements_int;
        self->native_to_python = Column_native_to_python_int; 
        native_element_size = sizeof(int64_t);
        self->min_element = PyLong_FromLongLong(min_int(self->element_size));
        self->max_element = PyLong_FromLongLong(max_int(self->element_size));
        if (self->min_element == NULL || self->max_element == NULL) {
            PyErr_NoMemory();
            goto out;
        }
    } else if (self->element_type == WT_FLOAT) {
        if (self->element_size != sizeof(float)
                && self->element_size != sizeof(double)) {
            PyErr_SetString(PyExc_ValueError, "bad element size");
            goto out;
        }
        self->python_to_native = Column_python_to_native_float;
        self->string_to_native = Column_string_to_native_float;
        self->verify_elements = Column_verify_elements_float;
        self->truncate_elements = Column_truncate_elements_float;
        self->pack_elements = Column_pack_elements_float;
        self->unpack_elements = Column_unpack_elements_float;
        self->native_to_python = Column_native_to_python_float; 
        native_element_size = sizeof(double);
        self->min_element = Py_None; 
        self->max_element = Py_None; 
        Py_INCREF(self->min_element);
        Py_INCREF(self->max_element);
    } else if (self->element_type == WT_CHAR) {
        if (self->element_size != 1) {
            PyErr_SetString(PyExc_ValueError, "bad element size");
            goto out;
        }
        self->python_to_native = Column_python_to_native_char;
        self->string_to_native = Column_string_to_native_char;
        self->verify_elements = Column_verify_elements_char;
        self->truncate_elements = Column_truncate_elements_char;
        self->pack_elements = Column_pack_elements_char;
        self->unpack_elements = Column_unpack_elements_char;
        self->native_to_python = Column_native_to_python_char; 
        native_element_size = sizeof(char);
        self->min_element = Py_None; 
        self->max_element = Py_None; 
        Py_INCREF(self->min_element);
        Py_INCREF(self->max_element);
    } else {    
        PyErr_SetString(PyExc_ValueError, "Unknown element type");
        goto out;
    }
    if (self->num_elements > MAX_NUM_ELEMENTS) {
        PyErr_SetString(PyExc_ValueError, "Too many elements");
        goto out;
    }
    if (self->num_elements < 0) {
        PyErr_SetString(PyExc_ValueError, "negative num elements");
        goto out;
    }
    max_num_elements = self->num_elements;
    if (self->num_elements == WT_VAR_1) {
        max_num_elements = MAX_NUM_ELEMENTS;    
    }
    self->element_buffer = PyMem_Malloc(max_num_elements 
            * native_element_size);
    if (self->element_buffer == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    self->input_elements = PyMem_Malloc(max_num_elements * sizeof(void *));
    if (self->input_elements == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    ret = 0;
out:
    return ret;
}

static PyMemberDef Column_members[] = {
    {"name", T_OBJECT_EX, offsetof(Column, name), READONLY, "name"},
    {"description", T_OBJECT_EX, offsetof(Column, description), READONLY, "description"},
    {"position", T_INT, offsetof(Column, position), READONLY, "position"},
    {"element_type", T_INT, offsetof(Column, element_type), READONLY, "element_type"},
    {"element_size", T_INT, offsetof(Column, element_size), READONLY, "element_size"},
    {"num_elements", T_INT, offsetof(Column, num_elements), READONLY, "num_elements"},
    {"fixed_region_offset", T_INT, offsetof(Column, fixed_region_offset), 
        READONLY, "fixed_region_offset"},
    {"min_element", T_OBJECT_EX, offsetof(Column, min_element), READONLY, "minimum element"},
    {"max_element", T_OBJECT_EX, offsetof(Column, max_element), READONLY, "maximum element"},
    {NULL}  /* Sentinel */
};

static PyMethodDef Column_methods[] = {
    {NULL}  /* Sentinel */
};

static PyTypeObject ColumnType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_wormtable.Column",             /* tp_name */
    sizeof(Column),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)Column_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "Column objects",           /* tp_doc */
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    0,                     /* tp_iter */
    0,                     /* tp_iternext */
    Column_methods,             /* tp_methods */
    Column_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Column_init,      /* tp_init */
};
   

/*==========================================================
 * Table object 
 *==========================================================
 */

static void
Table_dealloc(Table* self)
{
    u_int32_t j;
    Py_XDECREF(self->filename);
    /* make sure that the DB handles are closed. We can ignore errors here. */ 
    if (self->db != NULL) {
        self->db->close(self->db, 0);
    }
    if (self->row_buffer != NULL) {
        PyMem_Free(self->row_buffer);
    }
    if (self->columns != NULL) {
        /* columns must be decref'd but may be null */
        for (j = 0; j < self->num_columns; j++) {
            Py_XDECREF(self->columns[j]);   
        }
        PyMem_Free(self->columns);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

/*
 * Checks the columns to ensure sanity.
 */
static int 
Table_verify_columns(Table *self)
{
    int ret = -1;
    Column *col;
    u_int32_t j, k;
    char *cj, *ck;
    if (self->num_columns < 2) {
        PyErr_SetString(PyExc_ValueError, "Two or more columns required");
        goto out;
    }
    for (j = 0; j < self->num_columns; j++) {
        if (!PyObject_TypeCheck(self->columns[j], &ColumnType)) {
            PyErr_SetString(PyExc_TypeError, "Must be Column objects");
            goto out;
        }
    }
    /* check the row_id column */
    col = self->columns[0];
    if (col->element_type != WT_UINT || col->num_elements != 1) {
        PyErr_SetString(PyExc_ValueError, 
                "row_id column must be 1 element uint");
        goto out;
    }
    /* check for duplicate columns */
    /* TODO this is very slow for large numbers of columns - we should use a 
     * python dictionary to check instead
     */
    for (j = 0; j < self->num_columns; j++) {
        cj = PyBytes_AsString(self->columns[j]->name);
        for (k = j + 1; k < self->num_columns; k++) {
            ck = PyBytes_AsString(self->columns[k]->name);
            if (self->columns[j] == self->columns[k]) {
                PyErr_SetString(PyExc_ValueError, 
                        "Duplicate columns not permitted");
                goto out;
            }
            /* check for duplicate names */
            if (strcmp(cj, ck) == 0) {
                PyErr_SetString(PyExc_ValueError, 
                        "Duplicate column names not permitted");
                goto out;
            }
        }
    }
    ret = 0; 
out:
    return ret;
}

static int
Table_init(Table *self, PyObject *args, PyObject *kwds)
{
    int ret = -1;
    static char *kwlist[] = {"filename", "columns", "cache_size", NULL}; 
    Column *col;
    PyObject *filename = NULL;
    PyObject *columns = NULL;
    u_int32_t j;
    self->db = NULL;
    self->row_buffer = NULL; 
    self->columns = NULL;
    self->filename = NULL;
    self->cache_size = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!n", kwlist, 
            &PyBytes_Type, &filename, 
            &PyList_Type,  &columns, 
            &self->cache_size)) {
        goto out;
    }
    self->filename = filename;
    Py_INCREF(self->filename);
    self->num_columns = PyList_GET_SIZE(columns);
    self->columns = PyMem_Malloc(self->num_columns * sizeof(Column *));
    for (j = 0; j < self->num_columns; j++) {
        col = (Column *) PyList_GET_ITEM(columns, j);
        Py_INCREF(col);
        self->columns[j] = col; 
    }
    if (Table_verify_columns(self) != 0) {
        goto out;
    }
    self->row_buffer = PyMem_Malloc(MAX_ROW_SIZE);
    if (self->row_buffer == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    self->row_buffer_size = MAX_ROW_SIZE;
    memset(self->row_buffer, 0, self->row_buffer_size);
    self->fixed_region_size = 0;
    for (j = 0; j < self->num_columns; j++) {
        col = self->columns[j]; 
        col->position = j;
        col->fixed_region_offset = self->fixed_region_size;
        self->fixed_region_size += Column_get_fixed_region_size(col);
        if (self->fixed_region_size > MAX_ROW_SIZE) {
            PyErr_SetString(WormtableError, "Columns exceed max row size");
            goto out;
        }
    }
    self->current_row_size = self->fixed_region_size;
    self->current_row_id = 0; 
    ret = 0;
out:
    return ret;
}

static PyMemberDef Table_members[] = {
    {"filename", T_OBJECT_EX, offsetof(Table, filename), READONLY, "filename"},
    {"cache_size", T_PYSSIZET, offsetof(Table, cache_size), READONLY, "cache_size"},
    {"fixed_region_size", T_INT, offsetof(Table, fixed_region_size), READONLY, 
            "fixed_region_size"},
    {NULL}  /* Sentinel */
};


/* 
 * Returns 0 if the column is value. Otherwise 
 * -1 is returned with the appropriate Python exception set.
 */
static int 
Table_check_column_index(Table *self, int col_index)
{
    int ret = -1;
    if (col_index < 0 || col_index >= self->num_columns) {
        PyErr_Format(WormtableError, "Column index out of range."); 
        goto out;
    }
    ret = 0;
out:
    return ret;
}

/* 
 * Returns 0 if the table is opened in write mode. Otherwise 
 * -1 is returned with the appropriate Python exception set.
 */
static int 
Table_check_write_mode(Table *self)
{
    int ret = -1;
    int db_ret;
    u_int32_t flags;
    if (self->db == NULL) {
        PyErr_Format(WormtableError, "Table closed."); 
        goto out;
    }
    db_ret = self->db->get_open_flags(self->db, &flags);
    if (db_ret != 0) {
        handle_bdb_error(flags);
        goto out;
    }
    if ((flags & DB_RDONLY) != 0) {
        PyErr_Format(WormtableError, "Table must be opened WT_WRITE."); 
        goto out;
    }
    ret = 0;
out:
    return ret;
}


/* 
 * Returns 0 if the table is opened in read mode. Otherwise 
 * -1 is returned with the appropriate Python exception set.
 */
static int 
Table_check_read_mode(Table *self)
{
    int ret = -1;
    int db_ret;
    u_int32_t flags;
    if (self == NULL) {
        PyErr_Format(PyExc_SystemError, "Null table."); 
        goto out;
    }
    if (self->db == NULL) {
        PyErr_Format(WormtableError, "Table closed."); 
        goto out;
    }
    db_ret = self->db->get_open_flags(self->db, &flags);
    if (db_ret != 0) {
        handle_bdb_error(flags);
        goto out;
    }
    if ((flags & DB_RDONLY) == 0) {
        PyErr_Format(WormtableError, "Table must be opened WT_READ."); 
        goto out;
    }
    ret = 0;
out:
    return ret;
}

/*
 * Sets up the specified DBTs so that the underlying memory for each points
 * to the complete row_buffer. 
 */
static int 
Table_init_dbts(Table *self, DBT *primary_key, DBT *primary_data)
{
    Column *id_col = self->columns[0];
    u_int32_t primary_key_size = id_col->element_size;
    memset(primary_key, 0, sizeof(DBT));
    memset(primary_data, 0, sizeof(DBT));
    primary_key->data = self->row_buffer;
    primary_key->ulen = primary_key_size; 
    primary_key->size = primary_key_size;
    primary_key->flags = DB_DBT_USERMEM;
    primary_data->data = self->row_buffer + primary_key_size;
    primary_data->ulen = self->row_buffer_size - primary_key_size; 
    primary_data->flags = DB_DBT_USERMEM;
    return 0;
}



static PyObject *
Table_open(Table* self, PyObject *args)
{
    PyObject *ret = NULL;
    char *db_name = NULL;
    u_int32_t flags = 0; 
    Py_ssize_t gigabyte = 1024 * 1024 * 1024;
    u_int32_t gigs, bytes;
    int db_ret, mode;
    if (!PyArg_ParseTuple(args, "i", &mode)) { 
        goto out;
    }
    if (mode == WT_WRITE) {
        flags = DB_CREATE|DB_TRUNCATE;
    } else if (mode == WT_READ) {
        flags = DB_RDONLY|DB_NOMMAP;
    } else {
        PyErr_Format(PyExc_ValueError, "mode must be WT_READ or WT_WRITE."); 
        goto out;
    }
    if (self->db != NULL) {
        PyErr_Format(WormtableError, "Table already open."); 
        goto out;
    }
    db_name = PyBytes_AsString(self->filename);
    if (db_name == NULL) {
        goto out;
    }
    /* Now we create the DB handle */
    db_ret = db_create(&self->db, NULL, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    gigs = (u_int32_t) (self->cache_size / gigabyte);
    bytes = (u_int32_t) (self->cache_size % gigabyte);
    db_ret = self->db->set_cachesize(self->db, gigs, bytes, 1); 
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    /* Disable DB error messages */
    self->db->set_errcall(self->db, NULL);
    db_ret = self->db->open(self->db, NULL, db_name, NULL, DB_BTREE, flags, 0);         
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        self->db->close(self->db, 0);
        self->db = NULL;
        goto out;    
    }
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret;
}


static PyObject *
Table_close(Table* self)
{
    PyObject *ret = NULL;
    int db_ret;
    DB *db = self->db;
    if (db == NULL) {
        PyErr_SetString(WormtableError, "table closed");
        goto out;
    }
    db_ret = db->close(db, 0); 
    self->db = NULL;
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret; 
}


static PyObject *
Table_insert_elements(Table* self, PyObject *args)
{
    PyObject *ret = NULL;
    Column *column = NULL;
    PyObject *elements = NULL;
    int m, col_index;
    if (!PyArg_ParseTuple(args, "iO", &col_index, &elements)) { 
        goto out;
    }
    if (Table_check_column_index(self, col_index) != 0) {
        goto out;
    }
    if (col_index == 0) {
        PyErr_Format(WormtableError, "Cannot update ID column."); 
        goto out;
    }
    if (Table_check_write_mode(self) != 0) {
        goto out;
    }
    column = self->columns[col_index];
    if (column->python_to_native(column, elements) < 0) {
        goto out;   
    }
    m = Column_update_row(column, self->row_buffer, self->current_row_size); 
    if (m < 0) {
        goto out;
    }
    self->current_row_size += m;
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret; 
}

static PyObject *
Table_insert_encoded_elements(Table* self, PyObject *args)
{
    PyObject *ret = NULL;
    Column *column = NULL;
    PyBytesObject *value = NULL;
    char *v;
    int  m, col_index;
    if (!PyArg_ParseTuple(args, "iO!", &col_index, &PyBytes_Type,
            &value)) {
        goto out;
    }
    if (Table_check_column_index(self, col_index) != 0) {
        goto out;
    }
    if (col_index == 0) {
        PyErr_Format(WormtableError, "Cannot update ID column."); 
        goto out;
    }
    if (Table_check_write_mode(self) != 0) {
        goto out;
    }
    column = self->columns[col_index];
    v = PyBytes_AsString((PyObject *) value);
    if (column->string_to_native(column, v) < 0) {
        goto out;   
    }
    m = Column_update_row(column, self->row_buffer, self->current_row_size); 
    if (m < 0) {
        goto out;
    }
    self->current_row_size += m;
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret; 
}



static PyObject *
Table_commit_row(Table* self)
{
    PyObject *ret = NULL;
    int db_ret;
    DBT key, data;
    Column *id_col = self->columns[0];
    u_int32_t key_size = id_col->element_size; 
    if (Table_check_write_mode(self) != 0) {
        goto out;
    }
    if (Column_set_row_id(id_col, self->current_row_id) != 0) {
        goto out;
    }
    if (Column_update_row(id_col, self->row_buffer, self->current_row_size) 
            != 0) {
        goto out;
    }
    memset(&key, 0, sizeof(DBT));
    memset(&data, 0, sizeof(DBT));
    key.data = self->row_buffer;
    key.size = key_size;
    data.data = self->row_buffer + key_size;
    data.size = self->current_row_size - key_size;
    db_ret = self->db->put(self->db, NULL, &key, &data, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret); 
        goto out;
    } 
    memset(self->row_buffer, 0, self->current_row_size); 
    self->current_row_size = self->fixed_region_size;
    self->current_row_id++;
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret; 
}

static PyObject *
Table_get_num_rows(Table* self)
{
    int db_ret;
    Column *id_col = self->columns[0];
    u_int64_t max_key = 0;
    PyObject *ret = NULL;
    DBC *cursor = NULL;
    DBT key, data;
    if (Table_check_read_mode(self) != 0) {
        goto out;
    }
    db_ret = self->db->cursor(self->db, NULL, &cursor, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    /* retrieve the last key from the DB */
    memset(&key, 0, sizeof(DBT));
    memset(&data, 0, sizeof(DBT));  
    db_ret = cursor->get(cursor, &key, &data, DB_LAST);
    if (db_ret == 0) {
        if (key.size != id_col->element_size) {
            PyErr_Format(PyExc_SystemError, "key size mismatch");
            goto out;
        }
        if (Column_extract_elements(id_col, key.data) < 0) {
            goto out;
        } 
        if (Column_get_row_id(id_col, &max_key) != 0) {
            goto out;
        }
        max_key++;
    } else if (db_ret != DB_NOTFOUND) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    /* Free the cursor */
    db_ret = cursor->close(cursor);
    cursor = NULL;
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    ret = PyLong_FromUnsignedLongLong(max_key);
out:
    if (cursor != NULL) {
        cursor->close(cursor);
    }
    return ret; 
}
static PyObject *
Table_get_row(Table* self, PyObject *args)
{
    PyObject *ret = NULL;
    int db_ret;
    PyObject *t = NULL;
    Column *col = NULL;
    Column *id_col = self->columns[0];
    PyObject *value = NULL;
    unsigned long long row_id = 0;
    u_int32_t j;
    DBT key, data;
    if (!PyArg_ParseTuple(args, "K", &row_id)) {
        goto out;
    }
    if (Table_check_read_mode(self) != 0) {
        goto out;
    }
    Table_init_dbts(self, &key, &data); 
    if (Column_set_row_id(id_col, row_id) != 0) {
        goto out;
    }
    if (Column_update_row(id_col, self->row_buffer, 0) != 0) {
        goto out;
    }
    db_ret = self->db->get(self->db, NULL, &key, &data, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    t = PyTuple_New(self->num_columns);
    if (t == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    for (j = 0; j < self->num_columns; j++) {
        col = self->columns[j]; 
        if (Column_extract_elements(col, self->row_buffer) < 0) {
            Py_DECREF(t);
            goto out;
        }
        value = Column_get_python_elements(col); 
        if (value == NULL) {
            Py_DECREF(t);
            goto out;
        }
        PyTuple_SET_ITEM(t, j, value);
    }
    ret = t;
out:
    return ret; 
}




static PyMethodDef Table_methods[] = {
    {"get_num_rows", (PyCFunction) Table_get_num_rows, METH_NOARGS, 
            "Returns the number of rows in the table" },
    {"get_row", (PyCFunction) Table_get_row, METH_VARARGS, 
            "Return the jth row as a tuple" },
    {"open", (PyCFunction) Table_open, METH_VARARGS, "Open the table" },
    {"close", (PyCFunction) Table_close, METH_NOARGS, "Close the table" },
    {"commit_row", (PyCFunction) Table_commit_row, METH_NOARGS, 
            "Commit a row to the table in write mode." },
    {"insert_elements", (PyCFunction) Table_insert_elements, METH_VARARGS, 
            "insert element values encoded as native Python objects." },
    {"insert_encoded_elements", (PyCFunction) Table_insert_encoded_elements, 
            METH_VARARGS, 
            "insert element values encoded as comma seperated byte values." },
    {NULL}  /* Sentinel */
};

static PyTypeObject TableType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_wormtable.Table",             /* tp_name */
    sizeof(Table),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)Table_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    "Table objects",           /* tp_doc */
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    0,                     /* tp_iter */
    0,                     /* tp_iternext */
    Table_methods,             /* tp_methods */
    Table_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Table_init,      /* tp_init */
};
 



/*==========================================================
 * Index object 
 *==========================================================
 */

static void
Index_dealloc(Index* self)
{
    Py_XDECREF(self->table);
    Py_XDECREF(self->filename);
    /* make sure that the DB handles are closed. We can ignore errors here. */ 
    if (self->db != NULL) {
        self->db->close(self->db, 0);
    }
    if (self->columns != NULL) {
        PyMem_Free(self->columns);
    }
    if (self->bin_widths != NULL) {
        PyMem_Free(self->bin_widths);
    }
    if (self->key_buffer != NULL) {
        PyMem_Free(self->key_buffer);
    }
    if (self->row_buffer != NULL) {
        PyMem_Free(self->row_buffer);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
Index_init(Index *self, PyObject *args, PyObject *kwds)
{
    int j;
    long k;
    int ret = -1;
    static char *kwlist[] = {"table", "filename", "columns", "cache_size", NULL}; 
    PyObject *v;
    Column *col;
    PyObject *filename = NULL;
    PyObject *columns = NULL;
    Table *table = NULL;
    self->db = NULL;
    self->table = NULL;
    self->filename = NULL;
    self->bin_widths = NULL; 
    self->key_buffer = NULL; 
    self->row_buffer = NULL; 
    self->columns = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!O!n", kwlist, 
            &TableType, &table, 
            &PyBytes_Type, &filename, 
            &PyList_Type,  &columns, 
            &self->cache_size)) {
        goto out;
    }
    self->table = table;
    Py_INCREF(self->table);
    self->filename = filename;
    Py_INCREF(self->filename);
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    self->num_columns = PyList_GET_SIZE(columns);
    if (self->num_columns < 1) {
        PyErr_SetString(PyExc_ValueError, "Must be 1 or more columns index.");
        goto out; 
    }
    self->columns = PyMem_Malloc(self->num_columns * sizeof(u_int32_t));
    if (self->columns == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    self->bin_widths = PyMem_Malloc(self->num_columns * sizeof(double));
    if (self->bin_widths == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    memset(self->bin_widths, 0, self->num_columns * sizeof(double));
    self->key_buffer_size = 0;
    for (j = 0; j < self->num_columns; j++) {
        v = PyList_GET_ITEM(columns, j);
        if (!PyNumber_Check(v)) {
            PyErr_SetString(PyExc_ValueError, "Column indexes must be int");
            goto out;
        }
        k = PyLong_AsLong(v);
        if (k < 0 || k >= self->table->num_columns) {
            PyErr_SetString(PyExc_ValueError, "Column indexes out of bounds");
            goto out;
        }
        self->columns[j] = (u_int32_t) k;
        col = self->table->columns[k];
        if (col->num_elements == WT_VAR_1) {
            self->key_buffer_size += MAX_NUM_ELEMENTS * col->element_size;
        } else {
            self->key_buffer_size += col->num_elements * col->element_size;
        }
    }
    self->key_buffer = PyMem_Malloc(self->key_buffer_size);
    self->row_buffer_size = MAX_ROW_SIZE; 
    self->row_buffer = PyMem_Malloc(self->row_buffer_size);
    if (self->key_buffer == NULL || self->row_buffer == NULL) {
        PyErr_NoMemory();
        goto out;
    }

        
    ret = 0;
out:

    return ret;
}


static PyMemberDef Index_members[] = {
    {"table", T_OBJECT_EX, offsetof(Index, table), READONLY, "table"},
    {"filename", T_OBJECT_EX, offsetof(Index, filename), READONLY, "filename"},
    {"cache_size", T_PYSSIZET, offsetof(Index, cache_size), READONLY, "cache_size"},
    {NULL}  /* Sentinel */
};


/* 
 * Returns 0 if the table is opened in write mode. Otherwise 
 * -1 is returned with the appropriate Python exception set.
 */
static int 
Index_check_write_mode(Index *self)
{
    int ret = -1;
    int db_ret;
    u_int32_t flags;
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    if (self->db == NULL) {
        PyErr_Format(WormtableError, "Index closed."); 
        goto out;
    }
    db_ret = self->db->get_open_flags(self->db, &flags);
    if (db_ret != 0) {
        handle_bdb_error(flags);
        goto out;
    }
    if ((flags & DB_RDONLY) != 0) {
        PyErr_Format(WormtableError, "Index must be opened WT_WRITE."); 
        goto out;
    }
    ret = 0;
out:
    return ret;
}


/* 
 * Returns 0 if the table is opened in read mode. Otherwise 
 * -1 is returned with the appropriate Python exception set.
 */
static int 
Index_check_read_mode(Index *self)
{
    int ret = -1;
    int db_ret;
    u_int32_t flags;
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    if (self->db == NULL) {
        PyErr_Format(WormtableError, "Index closed."); 
        goto out;
    }
    db_ret = self->db->get_open_flags(self->db, &flags);
    if (db_ret != 0) {
        handle_bdb_error(flags);
        goto out;
    }
    if ((flags & DB_RDONLY) == 0) {
        PyErr_Format(WormtableError, "Index must be opened WT_READ."); 
        goto out;
    }
    ret = 0;
out:
    return ret;
}

/*
 * Sets up the specified DBTs so that the underlying memory for each points
 * to the complete row_buffer. 
 */
static int 
Index_init_dbts(Index *self, DBT *primary_key, DBT *primary_data)
{
    Column *id_col = self->table->columns[0];
    u_int32_t primary_key_size = id_col->element_size;
    memset(primary_key, 0, sizeof(DBT));
    memset(primary_data, 0, sizeof(DBT));
    primary_key->data = self->row_buffer;
    primary_key->ulen = primary_key_size; 
    primary_key->flags = DB_DBT_USERMEM;
    primary_data->data = self->row_buffer + primary_key_size;
    primary_data->ulen = self->row_buffer_size - primary_key_size; 
    primary_data->flags = DB_DBT_USERMEM;
    return 0;
}

/* extract values from the specified row and push them into the specified 
 * secondary key. This has valid memory associated with it.
 */
static int 
Index_fill_key(Index *self, void *row, DBT *skey)
{
    int ret = -1;
    Column *col;
    uint32_t j;
    int len;
    void *v = skey->data;
    skey->size = 0;
    for (j = 0; j < self->num_columns; j++) {
        col = self->table->columns[self->columns[j]]; 
        len = 0;
        if (self->bin_widths[j] == 0.0) {
            /* we can just copy the values directly here */
            len = Column_copy_row_values(col, v, row);
        } else {
            /* we must bin the values correctly here */
            len = Column_truncate_values(col, self->bin_widths[j], v, row);
        }
        if (len < 0) {
            goto out;
        }
        skey->size += len;
        v += len;
    }
    ret = 0;
out: 
    return ret;
}

/* 
 * Reads the arguments and sets a key in the specified buffer, returning 
 * its length.
 */
static int 
Index_set_key(Index *self, PyObject *args, void *buffer)
{
    int ret = -1;
    int j, m;
    int size = 0;
    Py_ssize_t n;
    Column *col = NULL;
    PyObject *elements = NULL;
    PyObject *v = NULL;
    void *dest = buffer; 
    if (!PyArg_ParseTuple(args, "O!", &PyTuple_Type, &elements)) { 
        goto out;
    }
    if (Index_check_read_mode(self) != 0) {
        goto out;
    }
    n = PyTuple_GET_SIZE(elements);
    if (n > self->num_columns) {
        PyErr_Format(PyExc_ValueError, "More key values than columns."); 
        goto out;
    }
    for (j = 0; j < n; j++) {
        col = self->table->columns[self->columns[j]]; 
        v = PyTuple_GetItem(elements, j);
        if (v == NULL) {
            goto out;
        }
        if (col->python_to_native(col, v) < 0) {
            goto out;   
        }
        if (col->verify_elements(col) < 0) {
            goto out;
        }
        m = col->num_buffered_elements * col->element_size;
        if (size + m > self->key_buffer_size) {
            PyErr_Format(PyExc_SystemError, "Max key size exceeded."); 
            goto out;
        }
        col->pack_elements(col, dest);
        dest += m;
        size += m;
    }
    ret = size;
out:
    return ret;
}

/*
 * Unpacks value for the columns in this index in the row pointed to in the 
 * specified DBT, truncates them as necessary, and then generates Python 
 * values from the buffer, returning a tuple.
 */
static PyObject *
Index_row_to_python(Index *self, void *row) {
    PyObject *ret = NULL;
    PyObject *value;
    unsigned int j;
    Column *col;
    PyObject *t = PyTuple_New(self->num_columns);
    if (t == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    if (Index_check_read_mode(self) != 0) {
        goto out;
    }
    for (j = 0; j < self->num_columns; j++) {
        col = self->table->columns[self->columns[j]]; 
        if (Column_extract_elements(col, row) < 0) {
            Py_DECREF(t);
            goto out;
        }
        if (self->bin_widths[j] > 0.0) {
            if (col->truncate_elements(col, self->bin_widths[j]) < 0) {
                Py_DECREF(t);
                goto out;
            }
        }
        value = Column_get_python_elements(col); 
        if (value == NULL) {
            Py_DECREF(t);
            goto out;
        }
        PyTuple_SET_ITEM(t, j, value);
    }
    ret = t;
out:
    return ret;
}

static PyObject *
Index_get_num_rows(Index *self, PyObject *args)
{
    PyObject *ret = NULL;
    int db_ret, key_size;
    db_recno_t count = 0;
    DB *db = NULL;
    DBC *cursor = NULL;
    DBT key, data;
    key_size = Index_set_key(self, args, self->key_buffer);
    if (key_size < 0) {
        goto out;
    }
    if (Index_check_read_mode(self) != 0) {
        goto out;
    }
    memset(&key, 0, sizeof(DBT));
    memset(&data, 0, sizeof(DBT));
    db = self->db;
    if (db == NULL) {
        PyErr_SetString(WormtableError, "table closed");
        goto out;
    }
    db_ret = db->cursor(db, NULL, &cursor, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    key.data = self->key_buffer;
    key.size = (u_int32_t) key_size; 
    db_ret = cursor->get(cursor, &key, &data, DB_SET);
    if (db_ret == 0) {
        db_ret = cursor->count(cursor, &count, 0); 
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
    } else if (db_ret != DB_NOTFOUND) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    ret = PyLong_FromUnsignedLongLong((unsigned long long) count);
out:
    if (cursor != NULL) {
        cursor->close(cursor);
    }

    return ret;
}

static PyObject *
Index_get_min(Index* self, PyObject *args)
{
    PyObject *ret = NULL;
    int db_ret;
    DBC *cursor = NULL;
    DBT primary_key, primary_data, secondary_key;
    int key_size = Index_set_key(self, args, self->key_buffer);
    if (key_size < 0) {
        goto out;
    }
    if (Index_check_read_mode(self) != 0) {
        goto out;
    }
    Index_init_dbts(self, &primary_key, &primary_data);
    memset(&secondary_key, 0, sizeof(DBT));
    db_ret = self->db->cursor(self->db, NULL, &cursor, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    secondary_key.data = self->key_buffer;
    secondary_key.size = (u_int32_t) key_size; 
    db_ret = cursor->pget(cursor, &secondary_key, &primary_key, &primary_data, 
            DB_SET_RANGE);
    if (db_ret == 0) {
        ret = Index_row_to_python(self, self->row_buffer);
        if (ret == NULL) {
            goto out;
        }
    } else if (db_ret == DB_NOTFOUND) {
        PyErr_SetObject(PyExc_KeyError, args); 
        goto out;
    } else {
        handle_bdb_error(db_ret);
        goto out;    
    }
out:
    if (cursor != NULL) {
        cursor->close(cursor);
    }
   
    return ret;
}

static PyObject *
Index_get_max(Index* self, PyObject *args)
{
    PyObject *ret = NULL;
    u_int32_t j;
    u_int32_t flags;
    int db_ret;
    DBC *cursor = NULL;
    DBT primary_key, primary_data, secondary_key;
    int key_size = Index_set_key(self, args, self->key_buffer);
    unsigned char *key_buffer = self->key_buffer;
    if (key_size < 0) {
        goto out;
    }
    if (Index_check_read_mode(self) != 0) {
        goto out;
    }
    Index_init_dbts(self, &primary_key, &primary_data);
    memset(&secondary_key, 0, sizeof(DBT));
    db_ret = self->db->cursor(self->db, NULL, &cursor, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    secondary_key.data = key_buffer;
    secondary_key.size = (u_int32_t) key_size; 
    if (key_size == 0) {
        /* An empty list has been passed so we want the last value */
        db_ret = cursor->pget(cursor, &secondary_key, &primary_key, 
                &primary_data, DB_LAST);
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
    } else {
        /* find the last non-zero value in the key buffer and increment it */
        j = secondary_key.size - 1;
        while (j > 0 && key_buffer[j] == 0) {
            j--;
        }
        /* add one to the buffer, making sure to carry base 256 */
        while (j > 0 && key_buffer[j] == 255) {
            key_buffer[j] = 0;
            j--;
        }
        key_buffer[j] += 1;
        /* Seek to the first record >= to this */
        db_ret = cursor->pget(cursor, &secondary_key, &primary_key, 
                &primary_data, DB_SET_RANGE);
        /* If this is not found, we want the last record in the 
         * index; otherwise, we want the record immediately before
         */
        flags = DB_PREV;
        if (db_ret == DB_NOTFOUND) {
            flags = DB_LAST;
        } else if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
        db_ret = cursor->pget(cursor, &secondary_key, &primary_key, 
                &primary_data, flags);
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
    }
    /* data points to the correct row */
    ret = Index_row_to_python(self, self->row_buffer);
out:
    if (cursor != NULL) {
        cursor->close(cursor);
    }
   
    return ret;
}

static PyObject *
Index_set_bin_widths(Index* self, PyObject *args)
{
    Column* col = NULL;
    PyObject *ret = NULL;
    PyObject *w = NULL;
    unsigned int j;
    PyObject *bin_widths = NULL;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &bin_widths)) {
        goto out;
    }
    if (Table_check_read_mode(self->table) != 0) {
        goto out; 
    }
    if (self->db != NULL) {
        PyErr_Format(WormtableError, "Cannot set bin_widths after open()"); 
        goto out;
    }
    if (PyList_GET_SIZE(bin_widths) != self->num_columns) {
        PyErr_Format(PyExc_ValueError, 
                "Number of bins must equal to the number of columns"); 
        goto out;
    }
    for (j = 0; j < PyList_GET_SIZE(bin_widths); j++) {
        w = PyList_GET_ITEM(bin_widths, j);
        col = self->table->columns[self->columns[j]];
        if (!PyNumber_Check(w)) {
            PyErr_Format(PyExc_TypeError, 
                    "Bad bin width for '%s': bin widths must be numeric",
                    PyBytes_AsString(col->name));
            goto out;
        }
        self->bin_widths[j] = PyFloat_AsDouble(w);
        if (PyErr_Occurred()) {
            goto out;
        }
        if (self->bin_widths[j] < 0.0) {
            PyErr_Format(PyExc_ValueError, 
                    "Bad bin width for '%s': bin widths must be nonnegative",
                    PyBytes_AsString(col->name));
            goto out;
        }
        if (col->element_type == WT_CHAR 
                && self->bin_widths[j] != 0.0) {
            PyErr_Format(PyExc_ValueError, 
                    "Bad bin width for '%s': char columns do not support bins",
                    PyBytes_AsString(col->name));
            goto out;
        }
        if (col->element_type == WT_INT) {
            if (fmod(self->bin_widths[j], 1.0) != 0.0) {
                PyErr_Format(PyExc_ValueError, 
                        "Bad bin width for '%s': "
                        "integer column bins must be integers",
                        PyBytes_AsString(col->name));
                goto out;
            }
        }
    }
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret;
}

static PyObject *
Index_build(Index* self, PyObject *args)
{
    int db_ret;
    PyObject *ret = NULL;
    PyObject *arglist, *result;
    PyObject *progress_callback = NULL;
    Column *id_col;
    u_int32_t primary_key_size;
    DBC *cursor = NULL;
    DB *pdb = NULL;
    DB *sdb = NULL;
    DBT pkey, pdata, skey, sdata;
    u_int32_t truncate_count;
    uint64_t callback_interval = 1000;
    uint64_t records_processed = 0;
    if (!PyArg_ParseTuple(args, "|OK", &progress_callback, 
            &callback_interval)) { 
        progress_callback = NULL;
        goto out;
    }
    Py_XINCREF(progress_callback);
    if (Index_check_write_mode(self) != 0) {
        goto out;
    }
    if (progress_callback != NULL) {
        if (!PyCallable_Check(progress_callback)) {
            PyErr_SetString(PyExc_TypeError, "progress_callback must be callable");
            goto out;
        }
    }
    if (callback_interval == 0) {
        PyErr_SetString(PyExc_ValueError, "callback interval cannot be 0");
        goto out;
    }
    id_col = self->table->columns[0];
    primary_key_size = id_col->element_size; 
    pdb = self->table->db;
    sdb = self->db;
    db_ret = pdb->cursor(pdb, NULL, &cursor, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        cursor = NULL;
        goto out;    
    }
    memset(&pkey, 0, sizeof(DBT));
    memset(&pdata, 0, sizeof(DBT));
    memset(&skey, 0, sizeof(DBT));
    memset(&sdata, 0, sizeof(DBT));
    pkey.data = self->row_buffer;
    pkey.ulen = primary_key_size; 
    pkey.flags = DB_DBT_USERMEM;
    pdata.data = self->row_buffer + primary_key_size;
    pdata.ulen = MAX_ROW_SIZE - primary_key_size; 
    pdata.flags = DB_DBT_USERMEM;
    skey.data = self->key_buffer;
    sdata.data = self->row_buffer;
    sdata.size = primary_key_size;
    while ((db_ret = cursor->get(cursor, &pkey, &pdata, DB_NEXT)) == 0) {
        if (Index_fill_key(self, self->row_buffer, &skey) < 0 ) {
            goto out;
        }
        db_ret = sdb->put(sdb, NULL, &skey, &sdata, 0);
        if (db_ret != 0) {
            handle_bdb_error(db_ret); 
            goto out;
        } 
        /* Invoke the callback if necessary */
        records_processed++;
        if (records_processed % callback_interval == 0) {
            if (progress_callback != NULL) {
                arglist = Py_BuildValue("(K)", records_processed);
                if (arglist == NULL) {
                    goto out;
                }
                result = PyObject_CallObject(progress_callback, arglist);
                Py_DECREF(arglist);
                if (result == NULL) {
                    goto out;
                }
                Py_DECREF(result);
                /* Anything might have happened in the mean time, so 
                 * check the state of the DBs again!
                 */
                if (Index_check_write_mode(self) != 0) {
                    goto out;
                }
            }
        }
    }
    if (db_ret != DB_NOTFOUND) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    db_ret = cursor->close(cursor);
    cursor = NULL;
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    Py_XDECREF(progress_callback);
    if (cursor != NULL) {
        /* ignore errors in this case, as we're already handling one */
        if (self->table != NULL) {
            if (self->table->db != NULL) {
                cursor->close(cursor);
            }
        }   
        if (self->db != NULL) {
            sdb = self->db; 
            db_ret = sdb->truncate(sdb, NULL, &truncate_count, 0); 
        }
    }
    return ret;
}

static PyObject *
Index_open(Index* self, PyObject *args)
{
    PyObject *ret = NULL;
    char *db_name = NULL;
    u_int32_t flags = 0; 
    Py_ssize_t gigabyte = 1024 * 1024 * 1024;
    u_int32_t gigs, bytes;
    int db_ret, mode;
    DB *pdb;
    if (!PyArg_ParseTuple(args, "i", &mode)) { 
        goto out;
    }
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    pdb = self->table->db;
    if (mode == WT_WRITE) {
        flags = DB_CREATE|DB_TRUNCATE;
    } else if (mode == WT_READ) {
        flags = DB_RDONLY|DB_NOMMAP;
    } else {
        PyErr_Format(PyExc_ValueError, "mode must be WT_READ or WT_WRITE."); 
        goto out;
    }
    if (self->db != NULL) {
        PyErr_Format(WormtableError, "Index already open."); 
        goto out;
    }
    db_name = PyBytes_AsString(self->filename);
    if (db_name == NULL) {
        goto out;
    }
    /* Now we create the DB handle */
    db_ret = db_create(&self->db, NULL, 0);
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    gigs = (u_int32_t) (self->cache_size / gigabyte);
    bytes = (u_int32_t) (self->cache_size % gigabyte);
    db_ret = self->db->set_cachesize(self->db, gigs, bytes, 1); 
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    db_ret = self->db->set_flags(self->db, DB_DUPSORT); 
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    db_ret = self->db->set_bt_compress(self->db, NULL, NULL); 
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    /* Disable DB error messages */
    self->db->set_errcall(self->db, NULL);
    db_ret = self->db->open(self->db, NULL, db_name, NULL, DB_BTREE, flags, 0);         
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        self->db->close(self->db, 0);
        self->db = NULL;
        goto out;    
    }
    if (mode == WT_READ) {
        db_ret = pdb->associate(pdb, NULL, self->db, NULL, 0);
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
    }
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret;
}

static PyObject *
Index_close(Index* self)
{
    PyObject *ret = NULL;
    int db_ret;
    DB *db = self->db;
    if (db == NULL) {
        PyErr_SetString(WormtableError, "index closed");
        goto out;
    }
    db_ret = db->close(db, 0); 
    self->db = NULL;
    if (db_ret != 0) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    Py_INCREF(Py_None);
    ret = Py_None;
out:
    return ret; 
}


static PyMethodDef Index_methods[] = {
    {"build", (PyCFunction) Index_build, METH_VARARGS, "Build the index" },
    {"set_bin_widths", (PyCFunction) Index_set_bin_widths, METH_VARARGS, 
        "Sets the bin widths for the columns" },
    {"get_min", (PyCFunction) Index_get_min, METH_VARARGS, 
        "Returns the minumum key value in this index" },
    {"get_max", (PyCFunction) Index_get_max, METH_VARARGS, 
        "Returns the maxumum key value in this index" },
    {"get_num_rows", (PyCFunction) Index_get_num_rows, METH_VARARGS, 
        "Returns the number of rows in the index with the specified key." },
    {"open", (PyCFunction) Index_open, METH_VARARGS, "Open the index" },
    {"close", (PyCFunction) Index_close, METH_NOARGS, "Close the index" },
    {NULL}  /* Sentinel */
};


static PyTypeObject IndexType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_wormtable.Index",             /* tp_name */
    sizeof(Index),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)Index_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    "Index objects",           /* tp_doc */
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    0,                     /* tp_iter */
    0,                     /* tp_iternext */
    Index_methods,             /* tp_methods */
    Index_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Index_init,      /* tp_init */
};
   



/*==========================================================
 * TableRowIterator object 
 *==========================================================
 */

static void
TableRowIterator_dealloc(TableRowIterator* self)
{
    if (self->cursor != NULL) {
        if (self->table != NULL) {
            if (self->table->db != NULL) {
                self->cursor->close(self->cursor);
            }
        }
    }
    Py_XDECREF(self->table);
    if (self->min_key != NULL) {
        PyMem_Free(self->min_key);
    }
    if (self->max_key != NULL) {
        PyMem_Free(self->max_key);
    }
    if (self->read_columns != NULL) {
        PyMem_Free(self->read_columns);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
TableRowIterator_init(TableRowIterator *self, PyObject *args, PyObject *kwds)
{
    int j;
    int ret = -1;
    long k;
    static char *kwlist[] = {"table", "columns", NULL}; 
    PyObject *v = NULL; 
    PyObject *columns = NULL;
    Table *table = NULL;
    Column *id_col = NULL;
    self->read_columns = NULL;
    self->table = NULL;
    self->min_key = NULL;
    self->max_key = NULL;
    self->cursor = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!", kwlist, 
            &TableType, &table,
            &PyList_Type, &columns)) {
        goto out;
    }
    self->table = table;
    Py_INCREF(self->table);
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    self->num_read_columns = PyList_GET_SIZE(columns);
    if (self->num_read_columns < 1) {
        PyErr_SetString(PyExc_ValueError, "At least one read column required");
        goto out;
    }
    self->read_columns = PyMem_Malloc(self->num_read_columns 
            * sizeof(u_int32_t));
    if (self->read_columns == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    for (j = 0; j < self->num_read_columns; j++) {
        v = PyList_GET_ITEM(columns, j);
        if (!PyNumber_Check(v)) {
            PyErr_SetString(PyExc_ValueError, "Column positions must be int");
            goto out;
        }
        k = PyLong_AsLong(v);
        if (k < 0 || k >= self->table->num_columns) {
            PyErr_SetString(PyExc_ValueError, "Column positions out of bounds");
            goto out;
        }
        self->read_columns[j] = (u_int32_t) k;
    }
    id_col = self->table->columns[0];
    self->min_key = PyMem_Malloc(id_col->element_size);
    self->max_key = PyMem_Malloc(id_col->element_size);
    if (self->min_key == NULL || self->max_key == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    ret = 0;
out:

    return ret;
}



static PyMemberDef TableRowIterator_members[] = {
    {NULL}  /* Sentinel */
};


static PyObject *
TableRowIterator_next(TableRowIterator *self)
{
    PyObject *ret = NULL;
    PyObject *t = NULL;
    PyObject *value;
    Column *col;
    int db_ret, j;
    DB *db;
    DBT key, data;
    uint32_t flags;
    int max_exceeded = 0;
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    Table_init_dbts(self->table, &key, &data);
    flags = DB_NEXT;
    if (self->cursor == NULL) {
        /* it's the first time through the loop, so set up the cursor */
        db = self->table->db;
        db_ret = db->cursor(db, NULL, &self->cursor, 0);
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
        if (self->min_key_size != 0) {
            if (key.size != self->min_key_size) {
                PyErr_Format(PyExc_SystemError, "key size mismatch."); 
                goto out;
            }
            memcpy(key.data, self->min_key, self->min_key_size);
            flags = DB_SET_RANGE;
        }
    } 
    db_ret = self->cursor->get(self->cursor, &key, &data, flags);
    if (db_ret == 0) {
        /* Now, check if we've hit or gone past max_key */ 
        if (self->max_key_size > 0) {
            if (key.size != self->max_key_size) {
                PyErr_Format(PyExc_SystemError, "key size mismatch."); 
                goto out;
            }
            max_exceeded = memcmp(self->max_key, key.data, key.size) <= 0;
        }
        if (!max_exceeded) { 
            t = PyTuple_New(self->num_read_columns);
            if (t == NULL) {
                PyErr_NoMemory();
                goto out;
            }
            for (j = 0; j < self->num_read_columns; j++) {
                col = self->table->columns[self->read_columns[j]]; 
                if (Column_extract_elements(col, self->table->row_buffer) < 0) {
                    Py_DECREF(t);
                    goto out;
                }
                value = Column_get_python_elements(col); 
                if (value == NULL) {
                    Py_DECREF(t);
                    goto out;
                }
                PyTuple_SET_ITEM(t, j, value);
            }
            ret = t;
        }
    } else if (db_ret != DB_NOTFOUND) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    if (ret == NULL) {
        /* Iteration is finished - free the cursor */
        self->cursor->close(self->cursor);
        self->cursor = NULL;
    }
out:
    return ret;
}


static PyObject *
TableRowIterator_set_min(TableRowIterator *self, PyObject *args)
{
    PyObject *ret = NULL;
    Column *id_col = NULL; 
    unsigned PY_LONG_LONG row_id = 0;
    /* TODO: This is unsatisfactory as it doesn't check for overflow;
     * -1 is accepted as a valid index value.
     */
    if (!PyArg_ParseTuple(args, "K", &row_id)) {
        goto out;
    }
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    id_col = self->table->columns[0];
    if (Column_set_row_id(id_col, (u_int64_t) row_id) != 0) {
        goto out;
    }
    /* this is safe because this column must be at offset 0 */
    if (Column_update_row(id_col, self->min_key, 0) != 0) {
        goto out;
    }
    self->min_key_size = id_col->element_size;
    Py_INCREF(Py_None);
    ret = Py_None; 
out:
    return ret;
}

static PyObject *
TableRowIterator_set_max(TableRowIterator *self, PyObject *args)
{
    PyObject *ret = NULL;
    Column *id_col = NULL; 
    unsigned PY_LONG_LONG row_id = 0;
    /* TODO: This is unsatisfactory as it doesn't check for overflow;
     * -1 is accepted as a valid index value.
     */
    if (!PyArg_ParseTuple(args, "K", &row_id)) {
        goto out;
    }
    if (Table_check_read_mode(self->table) != 0) {
        goto out;
    }
    id_col = self->table->columns[0];
    if (Column_set_row_id(id_col, (u_int64_t) row_id) != 0) {
        goto out;
    }
    /* this is safe because this column must be at offset 0 */
    if (Column_update_row(id_col, self->max_key, 0) != 0) {
        goto out;
    }
    self->max_key_size = id_col->element_size;
    Py_INCREF(Py_None);
    ret = Py_None; 
out:
    return ret;
}


static PyMethodDef TableRowIterator_methods[] = {
    {"set_min", (PyCFunction) TableRowIterator_set_min, METH_VARARGS, "Set the minimum key" },
    {"set_max", (PyCFunction) TableRowIterator_set_max, METH_VARARGS, "Set the maximum key" },
    {NULL}  /* Sentinel */
};


static PyTypeObject TableRowIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_wormtable.TableRowIterator",             /* tp_name */
    sizeof(TableRowIterator),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)TableRowIterator_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    "TableRowIterator objects",           /* tp_doc */
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    PyObject_SelfIter,               /* tp_iter */
    (iternextfunc) TableRowIterator_next, /* tp_iternext */
    TableRowIterator_methods,             /* tp_methods */
    TableRowIterator_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)TableRowIterator_init,      /* tp_init */
};



/*==========================================================
 * IndexRowIterator object 
 *==========================================================
 */

static void
IndexRowIterator_dealloc(IndexRowIterator* self)
{
    if (self->cursor != NULL) {
        if (self->index != NULL) {
            if (self->index->db != NULL) {
                self->cursor->close(self->cursor);
            }
        }
    }
    Py_XDECREF(self->index);
    if (self->min_key != NULL) {
        PyMem_Free(self->min_key);
    }
    if (self->max_key != NULL) {
        PyMem_Free(self->max_key);
    }
    if (self->read_columns != NULL) {
        PyMem_Free(self->read_columns);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);

}

static int
IndexRowIterator_init(IndexRowIterator *self, PyObject *args, PyObject *kwds)
{
    int j;
    int ret = -1;
    long k;
    static char *kwlist[] = {"index", "columns", NULL}; 
    PyObject *v = NULL; 
    PyObject *columns = NULL;
    Index *index = NULL;
    self->read_columns = NULL;
    self->index = NULL;
    self->cursor = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!", kwlist, 
            &IndexType, &index,
            &PyList_Type, &columns)) {
        goto out;
    }
    self->index = index;
    Py_INCREF(self->index);
    if (Index_check_read_mode(self->index) != 0) {
        goto out;
    }
    self->num_read_columns = PyList_GET_SIZE(columns);
    if (self->num_read_columns < 1) {
        PyErr_SetString(PyExc_ValueError, "At least one read column required");
        goto out;
    }
    self->read_columns = PyMem_Malloc(self->num_read_columns 
            * sizeof(u_int32_t));
    if (self->read_columns == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    for (j = 0; j < self->num_read_columns; j++) {
        v = PyList_GET_ITEM(columns, j);
        if (!PyNumber_Check(v)) {
            PyErr_SetString(PyExc_ValueError, "Column indexes must be int");
            goto out;
        }
        k = PyLong_AsLong(v);
        if (k < 0 || k >= self->index->table->num_columns) {
            PyErr_SetString(PyExc_ValueError, "Column indexes out of bounds");
            goto out;
        }
        self->read_columns[j] = (u_int32_t) k;
    }
    self->min_key = PyMem_Malloc(self->index->key_buffer_size);
    self->max_key = PyMem_Malloc(self->index->key_buffer_size);
    if (self->min_key == NULL || self->max_key == NULL) {
        PyErr_NoMemory();
        goto out;
    }
    self->min_key_size = 0;
    self->max_key_size = 0;
    ret = 0;
out:

    return ret;
}



static PyMemberDef IndexRowIterator_members[] = {
    {NULL}  /* Sentinel */
};


static PyObject *
IndexRowIterator_next(IndexRowIterator *self)
{
    PyObject *ret = NULL;
    PyObject *t = NULL;
    PyObject *value;
    Column *col;
    int db_ret, j, cmp;
    DB *db;
    DBT primary_key, primary_data, secondary_key;
    uint32_t flags, cmp_size;
    int max_exceeded = 0;
    if (Index_check_read_mode(self->index) != 0) {
        goto out;
    }
    Index_init_dbts(self->index, &primary_key, &primary_data);
    memset(&secondary_key, 0, sizeof(DBT));
    flags = DB_NEXT;
    if (self->cursor == NULL) {
        /* it's the first time through the loop, so set up the cursor */
        db = self->index->db;
        db_ret = db->cursor(db, NULL, &self->cursor, 0);
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
        if (self->min_key_size != 0) {
            secondary_key.data = self->min_key;
            secondary_key.size = self->min_key_size;
            flags = DB_SET_RANGE;
        }
    } 
    db_ret = self->cursor->pget(self->cursor, &secondary_key, &primary_key, 
            &primary_data, flags);
    if (db_ret == 0) {
        /* Now, check if we've hit or gone past max_key */
        if (self->max_key_size > 0) {
            cmp_size = self->max_key_size;
            if (secondary_key.size < cmp_size) {
                cmp_size = secondary_key.size;
            }
            cmp = memcmp(self->max_key, secondary_key.data, cmp_size);
            max_exceeded = cmp <= 0;
            if (secondary_key.size < self->max_key_size) {
                max_exceeded = cmp < 0;
            }
            
        }
        if (!max_exceeded) { 
            t = PyTuple_New(self->num_read_columns);
            if (t == NULL) {
                PyErr_NoMemory();
                goto out;
            }
            for (j = 0; j < self->num_read_columns; j++) {
                col = self->index->table->columns[self->read_columns[j]]; 
                if (Column_extract_elements(col, self->index->row_buffer) < 0) {
                    Py_DECREF(t);
                    goto out;
                }
                value = Column_get_python_elements(col); 
                if (value == NULL) {
                    Py_DECREF(t);
                    goto out;
                }
                PyTuple_SET_ITEM(t, j, value);
            }
            ret = t;
        }
    } else if (db_ret != DB_NOTFOUND) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    if (ret == NULL) {
        /* Iteration is finished - free the cursor */
        self->cursor->close(self->cursor);
        self->cursor = NULL;
    }
out:
    return ret;
}


static PyObject *
IndexRowIterator_set_min(IndexRowIterator *self, PyObject *args)
{
    PyObject *ret = NULL;
    int size = Index_set_key(self->index, args, self->min_key);
    if (size < 0) {
        goto out;
    }
    self->min_key_size = size;
    ret = Py_BuildValue("");
out:
    return ret;
}

static PyObject *
IndexRowIterator_set_max(IndexRowIterator *self, PyObject *args)
{
    PyObject *ret = NULL;
    int size = Index_set_key(self->index, args, self->max_key);
    if (size < 0) {
        goto out;
    }
    self->max_key_size = size;
    ret = Py_BuildValue("");
out:
    return ret;
}


static PyMethodDef IndexRowIterator_methods[] = {
    {"set_min", (PyCFunction) IndexRowIterator_set_min, METH_VARARGS, "Set the minimum key" },
    {"set_max", (PyCFunction) IndexRowIterator_set_max, METH_VARARGS, "Set the maximum key" },
    {NULL}  /* Sentinel */
};


static PyTypeObject IndexRowIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_wormtable.IndexRowIterator",             /* tp_name */
    sizeof(IndexRowIterator),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)IndexRowIterator_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    "IndexRowIterator objects",           /* tp_doc */
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    PyObject_SelfIter,               /* tp_iter */
    (iternextfunc) IndexRowIterator_next, /* tp_iternext */
    IndexRowIterator_methods,             /* tp_methods */
    IndexRowIterator_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)IndexRowIterator_init,      /* tp_init */
};

/*==========================================================
 * DistinctValueIterator object 
 *==========================================================
 */

static void
DistinctValueIterator_dealloc(DistinctValueIterator* self)
{
    if (self->cursor != NULL) {
        if (self->index != NULL) {
            if (self->index->db != NULL) {
                self->cursor->close(self->cursor);
            }
        }
    }
    Py_XDECREF(self->index);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
DistinctValueIterator_init(DistinctValueIterator *self, PyObject *args, PyObject *kwds)
{
    int ret = -1;
    static char *kwlist[] = {"index", NULL}; 
    Index *index = NULL;
    self->index = NULL;
    self->cursor = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist, 
            &IndexType, &index)) {
        goto out;
    }
    self->index = index;
    Py_INCREF(self->index);
    if (Index_check_read_mode(self->index) != 0) {
        goto out;
    }
    ret = 0;
out:
    return ret;
}

static PyMemberDef DistinctValueIterator_members[] = {
    {NULL}  /* Sentinel */
};


static PyObject *
DistinctValueIterator_next(DistinctValueIterator *self)
{
    PyObject *ret = NULL;
    int db_ret;
    DB *db;
    DBT primary_key, primary_data, secondary_key;
    if (Index_check_read_mode(self->index) != 0) {
        goto out;
    }
    Index_init_dbts(self->index, &primary_key, &primary_data);
    memset(&secondary_key, 0, sizeof(DBT));
    if (self->cursor == NULL) {
        /* it's the first time through the loop, so set up the cursor */
        db = self->index->db;
        db_ret = db->cursor(db, NULL, &self->cursor, 0);
        if (db_ret != 0) {
            handle_bdb_error(db_ret);
            goto out;    
        }
    }
    db_ret = self->cursor->pget(self->cursor, &secondary_key, &primary_key, 
            &primary_data, DB_NEXT_NODUP);
    if (db_ret == 0) {
        ret = Index_row_to_python(self->index, self->index->row_buffer);
        if (ret == NULL) {
            goto out;
        }
    } else if (db_ret != DB_NOTFOUND) {
        handle_bdb_error(db_ret);
        goto out;    
    }
    if (ret == NULL) {
        /* Iteration is finished - free the cursor */
        self->cursor->close(self->cursor);
        self->cursor = NULL;
    }
out:
    return ret;
}

static PyMethodDef DistinctValueIterator_methods[] = {
    {NULL}  /* Sentinel */
};


static PyTypeObject DistinctValueIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_wormtable.DistinctValueIterator",             /* tp_name */
    sizeof(DistinctValueIterator),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)DistinctValueIterator_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    "DistinctValueIterator objects",           /* tp_doc */
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    PyObject_SelfIter,               /* tp_iter */
    (iternextfunc) DistinctValueIterator_next, /* tp_iternext */
    DistinctValueIterator_methods,             /* tp_methods */
    DistinctValueIterator_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)DistinctValueIterator_init,      /* tp_init */
};



/* Initialisation code supports Python 2.x and 3.x. The framework uses the 
 * recommended structure from http://docs.python.org/howto/cporting.html. 
 * I've ignored the point about storing state in globals, as the examples 
 * from the Python documentation still use this idiom. 
 */

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef wormtablemodule = {
    PyModuleDef_HEAD_INIT,
    "_wormtable",   /* name of module */
    MODULE_DOC, /* module documentation, may be NULL */
    -1,    
    NULL, NULL, NULL, NULL, NULL 
};

#define INITERROR return NULL

PyObject * 
PyInit__wormtable(void)

#else
#define INITERROR return

void
init_wormtable(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&wormtablemodule);
#else
    PyObject *module = Py_InitModule3("_wormtable", NULL, MODULE_DOC);
#endif
    if (module == NULL) {
        INITERROR;
    }
    /* Column */
    ColumnType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ColumnType) < 0) {
        INITERROR;
    }
    Py_INCREF(&ColumnType);
    PyModule_AddObject(module, "Column", (PyObject *) &ColumnType);
    /* Table */
    TableType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TableType) < 0) {
        INITERROR;
    }
    Py_INCREF(&TableType);
    PyModule_AddObject(module, "Table", (PyObject *) &TableType);
    /* Index */
    IndexType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexType) < 0) {
        INITERROR;
    }
    Py_INCREF(&IndexType);
    PyModule_AddObject(module, "Index", (PyObject *) &IndexType);
    /* TableRowIterator */
    TableRowIteratorType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TableRowIteratorType) < 0) {
        INITERROR;
    }
    Py_INCREF(&TableRowIteratorType);
    PyModule_AddObject(module, "TableRowIterator", (PyObject *) &TableRowIteratorType);
    /* TableRowIterator */
    IndexRowIteratorType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexRowIteratorType) < 0) {
        INITERROR;
    }
    Py_INCREF(&IndexRowIteratorType);
    PyModule_AddObject(module, "IndexRowIterator", (PyObject *) &IndexRowIteratorType);
    /* DistinctValueIterator */
    DistinctValueIteratorType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&DistinctValueIteratorType) < 0) {
        INITERROR;
    }
    Py_INCREF(&DistinctValueIteratorType);
    PyModule_AddObject(module, "DistinctValueIterator", 
            (PyObject *) &DistinctValueIteratorType);
    
    WormtableError = PyErr_NewException("_wormtable.WormtableError", 
            NULL, NULL);
    Py_INCREF(WormtableError);
    PyModule_AddObject(module, "WormtableError", WormtableError);
    
    PyModule_AddIntConstant(module, "WT_VAR_1", WT_VAR_1);
    PyModule_AddIntConstant(module, "WT_CHAR", WT_CHAR);
    PyModule_AddIntConstant(module, "WT_UINT", WT_UINT);
    PyModule_AddIntConstant(module, "WT_INT", WT_INT);
    PyModule_AddIntConstant(module, "WT_FLOAT", WT_FLOAT);
    
    PyModule_AddIntConstant(module, "WT_READ", WT_READ);
    PyModule_AddIntConstant(module, "WT_WRITE", WT_WRITE);
    
    PyModule_AddIntConstant(module, "MAX_ROW_SIZE", MAX_ROW_SIZE);
    PyModule_AddIntConstant(module, "MAX_NUM_ELEMENTS", MAX_NUM_ELEMENTS);

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}


