/*
Distance - Utilities for comparing sequences
Copyright (C) 2013 Michaël Meyer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
*/


#include "Python.h"


#define WE_GOT_A_PROBLEM -2

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)))

PyDoc_STRVAR(hamming_doc,
"hamming(seq1, seq2, normalized=False)\n\
\n\
Compute the Hamming distance between the two sequences `seq1` and `seq2`.\n\
The Hamming distance is the number of differing items in two ordered sequences\n\
of the same length. If the sequences submitted do not have the same length,\n\
an error will be raised.\n\
\n\
If `normalized` evaluates to `False`, the return value will be an integer between\n\
0 and the length of the sequences provided, edge values included; otherwise, it\n\
will be a float between 0 and 1 included, where 0 means equal, and 1 totally different.\n\
Normalized hamming distance is computed as:\n\
\n\
    0.0                         if len(seq1) == 0\n\
    hamming_dist / len(seq1)    otherwise\
");

PyDoc_STRVAR(levenshtein_doc,
"levenshtein(seq1, seq2, normalized=False, max_dist=2)\n\
\n\
Compute the Levenshtein distance between the two sequences `seq1` and `seq2`.\n\
The Levenshtein distance is the minimum number of edit operations necessary for\n\
transforming one sequence into the other. The edit operations allowed are:\n\
\n\
    * deletion:     ABC -> BC, AC, AB\n\
    * insertion:    ABC -> ABCD, EABC, AEBC..\n\
    * substitution: ABC -> ABE, ADC, FBC..\n\
\n\
If `normalized` evaluates to `False`, the return value will be an integer between\n\
0 and the length of the sequences provided, edge values included; otherwise, it\n\
will be a float between 0 and 1 included, where 0 means equal, and 1 totally\n\
different. Normalized levenshtein distance is computed as:\n\
\n\
    0.0                                   if len(seq1) == len(seq2) == 0\n\
    lev_dist / max(len(seq1), len(seq2))  otherwise\n\
\n\
The `max_dist` parameter controls at which moment we should stop computing the\n\
distance between the provided sequences. If it is a negative int, the distance\n\
will be computed until the sequences are exhausted; otherwise, the computation\n\
will stop at the moment the calculated distance is higher than `max_dist`, and\n\
then return -1. For example:\n\
\n\
    >>> levenshtein(\"abc\", \"abcd\", max_dist=1)  # dist=1\n\
    1\n\
    >>> levenshtein(\"abc\", \"abcde\", max_dist=1) # dist=2\n\
    -1\n\
\n\
This can be a time saver if you're not interested in absolute distance.\
");

PyDoc_STRVAR(fast_comp_doc,
"fast_comp(str1, str2, transpositions=False)\n\
\n\
Compute the distance between the two strings `str1` and `str2` up to a maximum\n\
of 2 included, and return it. If the edit distance between the two strings is higher\n\
than that, -1 is returned.\n\
\n\
`str1` and `str2` are expected to be unicode strings. If `transpositions` is `True`,\n\
transpositions will be taken into account when computing the distance between the\n\
submitted strings. This can make a difference, e.g.:\n\
\n\
    >>> fast_comp(\"abc\", \"bac\", transpositions=False)\n\
    2\n\
    >>> fast_comp(\"abc\", \"bac\", transpositions=True)\n\
    1\n\
\n\
The algorithm comes from `http://writingarchives.sakura.ne.jp/fastcomp`. I've added\n\
transpositions support to the original code, and rewritten it in C.\
");

PyDoc_STRVAR(ifast_comp_doc,
"ifast_comp(str1, strs, transpositions=False)\n\
\n\
Return an iterator over all the strings in `strs` which distance from `str1`\n\
is lower or equal to 2. The strings which distance from the reference string\n\
is higher than that are dropped.\n\
\n\
    `str1`: the reference unicode string.\n\
    `strs`: an iterable of unicode strings (can be a generator).\n\
    `transpositions` has the same sense than in `fast_comp`.\n\
\n\
The return value is a series of pairs (distance, string).\n\
\n\
This is faster than `levensthein` by an order of magnitude, so use this if you're\n\
only interested in strings which are below distance 2 from the reference string.\n\
If you need a different threshold than distance 2, see the `max_dist` parameter\n\
in `levenshtein`.\n\
\n\
You might want to call `sorted()` on the iterator to get the results in a\n\
significant order:\n\
\n\
    >>> g = ifast_comp(\"foo\", [\"fo\", \"bar\", \"foob\", \"foo\", \"foobaz\"])\n\
    >>> sorted(g)\n\
    [(0, 'foo'), (1, 'fo'), (1, 'foob')]\
");



/* Hamming */

static Py_ssize_t
uni_hamming(PyObject *str1, PyObject *str2, Py_ssize_t len)
{
	Py_ssize_t i, dist = 0;
	
	void *ptr1 = PyUnicode_DATA(str1);
	void *ptr2 = PyUnicode_DATA(str2);
	int kind1 = PyUnicode_KIND(str1);
	int kind2 = PyUnicode_KIND(str2);
    
	for (i = 0; i < len; i++) {
		if (PyUnicode_READ(kind1, ptr1, i) != PyUnicode_READ(kind2, ptr2, i))
			dist++;
	}

	return dist;
}


static Py_ssize_t
rich_hamming(PyObject *seq1, PyObject *seq2, Py_ssize_t len)
{
	Py_ssize_t i, comp, dist = 0;
	
	for (i = 0; i < len; i++) {
		comp = PyObject_RichCompareBool(
			PySequence_Fast_GET_ITEM(seq1, i),
			PySequence_Fast_GET_ITEM(seq2, i),
			Py_EQ);
		if (comp == -1) {
			Py_DECREF(seq1);
			Py_DECREF(seq2);
			PyErr_SetString(PyExc_RuntimeError, "failed to compare objects");
			return WE_GOT_A_PROBLEM;
		}
		if (!comp)
			dist++;
	}
	
	Py_DECREF(seq1);
	Py_DECREF(seq2);

	return dist;
}


static PyObject *
hamming(PyObject *self, PyObject *args, PyObject *kwargs)
{
	PyObject *arg1, *arg2;
	Py_ssize_t len1, len2, dist;
	int do_normalize = 0;
	static char *keywords[] = {"arg1", "arg2", "normalized", NULL};
	
	if (!PyArg_ParseTupleAndKeywords(args, kwargs,
		"OO|p:hamming", keywords, &arg1, &arg2, &do_normalize))
		return NULL;
	
	if (PyUnicode_Check(arg1) && PyUnicode_Check(arg2)) {
	
		if (PyUnicode_READY(arg1) == -1)
			return NULL;
		if (PyUnicode_READY(arg2) == -1)
			return NULL;
		len1 = PyUnicode_GET_LENGTH(arg1);
		len2 = PyUnicode_GET_LENGTH(arg2);
		if (len1 != len2) {
			PyErr_SetString(PyExc_ValueError, "expected two objects of the same length");
			return NULL;
		}
		dist = uni_hamming(arg1, arg2, len1);
	}
	
	else if (PySequence_Check(arg1) && PySequence_Check(arg2)) {
	
		PyObject *seq1 = PySequence_Fast(arg1, "");
		PyObject *seq2 = PySequence_Fast(arg2, "");
	
		if (seq1 == NULL || seq2 == NULL) {
			Py_XDECREF(seq1);
			Py_XDECREF(seq2);
			PyErr_SetString(PyExc_RuntimeError, "failed to get objects as tuples");
			return NULL;
		}
	
		len1 = PySequence_Fast_GET_SIZE(seq1);
		len2 = PySequence_Fast_GET_SIZE(seq2);
		if (len1 == -1 || len2 == -1) {
			Py_DECREF(seq1);
			Py_DECREF(seq2);
			PyErr_SetString(PyExc_RuntimeError, "failed to get len of objects");
			return NULL;
		}
		if (len1 != len2) {
			Py_DECREF(seq1);
			Py_DECREF(seq2);
			PyErr_SetString(PyExc_ValueError, "expected two objects of the same len");
			return NULL;
		}
		dist = rich_hamming(seq1, seq2, len1);
	}
	
	else {
		PyErr_SetString(PyExc_TypeError, "expected two sequence objects");
		return NULL;
	}
	
	if (dist == WE_GOT_A_PROBLEM)
		return NULL;
	
	if (do_normalize) {
		if (len1 == 0 && len2 == 0)
			return Py_BuildValue("f", 0.0);  /* identical */
		double normalized = dist / (double)len1;
		return Py_BuildValue("d", normalized);
	}
	return Py_BuildValue("n", dist);
}



/* Levenshtein */


#define OUT_OF_BOUND -1

static Py_ssize_t
minimum(Py_ssize_t *column, Py_ssize_t len)
{
	Py_ssize_t i;
	/* column should not be empty, we already checked this */
	Py_ssize_t min = column[0];
	
	for (i = 1; i < len; i++) {
		if (column[i] < min)
			min = column[i];
	}
	return min;
}


static Py_ssize_t
uni_levenshtein(PyObject *str1, PyObject *str2,
	Py_ssize_t len1, Py_ssize_t len2, Py_ssize_t max_dist)
{
	Py_ssize_t x, y, last, old;
	Py_ssize_t *column;
	int kind1, kind2;
	void *ptr1, *ptr2;
	unsigned short cost;

	if (max_dist >= 0 && (len1 - len2) > max_dist)
		return OUT_OF_BOUND;
	else {
		if (len1 == 0)
			return len2;
		if (len2 == 0)
			return len1;
	}

	ptr1 = PyUnicode_DATA(str1);
	ptr2 = PyUnicode_DATA(str2);
	kind1 = PyUnicode_KIND(str1);
	kind2 = PyUnicode_KIND(str2);

	column = (Py_ssize_t*) malloc((len2 + 1) * sizeof(Py_ssize_t));
	if (column == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "no memory");
		return WE_GOT_A_PROBLEM;
	}

	for (y = 1 ; y <= len2; y++)
		column[y] = y;
	for (x = 1 ; x <= len1; x++) {
		column[0] = x;
		for (y = 1, last = x - 1; y <= len2; y++) {
			old = column[y];
			cost = (PyUnicode_READ(kind1, ptr1, x - 1) != PyUnicode_READ(kind2, ptr2, y - 1));
			column[y] = MIN3(column[y] + 1, column[y - 1] + 1, last + cost);
			last = old;
		}
		if (max_dist >= 0 && minimum(column, len2 + 1) > max_dist) {
			free(column);
			return OUT_OF_BOUND;
		}
	}

	free(column);
	
	if (max_dist >= 0 && column[len2] > max_dist)
		return OUT_OF_BOUND;
	return column[len2];
}


static Py_ssize_t
rich_levenshtein(PyObject *seq1, PyObject *seq2,
	Py_ssize_t len1, Py_ssize_t len2, Py_ssize_t max_dist)
{
	Py_ssize_t *column;
	Py_ssize_t x, y, last, old;
	int comp;

	if (max_dist >= 0 && (len1 - len2) > max_dist)
		return OUT_OF_BOUND;
	else {
		if (len1 == 0)
			return len2;
		if (len2 == 0)
			return len1;
	}
	
	column = (Py_ssize_t*) malloc((len2 + 1) * sizeof(Py_ssize_t));
	if (column == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "no memory");
		return WE_GOT_A_PROBLEM;
	}

	for (y = 1; y <= len2; y++)
		column[y] = y;
	for (x = 1; x <= len1; x++) {
		column[0] = x;
		for (y = 1, last = x - 1; y <= len2; y++) {
			old = column[y];
			comp = PyObject_RichCompareBool(
				PySequence_Fast_GET_ITEM(seq1, x - 1),
				PySequence_Fast_GET_ITEM(seq2, y - 1),
				Py_EQ);
			if (comp == -1) {
				free(column);
				PyErr_SetString(PyExc_RuntimeError, "failed to compare objects");
				return WE_GOT_A_PROBLEM;
			}
			column[y] = MIN3(column[y] + 1, column[y - 1] + 1, last + (comp != 1));
			last = old;
		}
		if (max_dist >= 0 && minimum(column, len2 + 1) > max_dist) {
			free(column);
			return OUT_OF_BOUND;
		}
	}
	
	free(column);
	
	if (max_dist >= 0 && column[len2] > max_dist)
		return OUT_OF_BOUND;
	return column[len2];
}


static PyObject *
levenshtein(PyObject *self, PyObject *args, PyObject *kwargs)
{
	PyObject *arg1, *arg2;
	Py_ssize_t len1, len2, dist=-1;
	int do_normalize = 0;
	Py_ssize_t max_dist = -1;
	static char *keywords[] = {"arg1", "arg2", "normalized", "max_dist", NULL};
	
	if (!PyArg_ParseTupleAndKeywords(args, kwargs,
		"OO|pn:levenshtein", keywords, &arg1, &arg2, &do_normalize, &max_dist))
		return NULL;

	if (PyUnicode_Check(arg1) && PyUnicode_Check(arg2)) {
	
		if (PyUnicode_READY(arg1) != 0)
			return NULL;
		if (PyUnicode_READY(arg2) != 0)
			return NULL;
		
		len1 = PyUnicode_GET_LENGTH(arg1);
		len2 = PyUnicode_GET_LENGTH(arg2);
		
		if (len1 > len2)
			dist = uni_levenshtein(arg1, arg2, len1, len2, max_dist);
		else
			dist = uni_levenshtein(arg2, arg1, len2, len1, max_dist);
	
	}

	else if (PySequence_Check(arg1) && PySequence_Check(arg2)) {
	
		PyObject *seq1 = PySequence_Fast(arg1, "");
		PyObject *seq2 = PySequence_Fast(arg2, "");
	
		if (seq1 == NULL || seq2 == NULL) {
			Py_XDECREF(seq1);
			Py_XDECREF(seq2);
			PyErr_SetString(PyExc_RuntimeError, "failed to get objects as tuples");
			return NULL;
		}
	
		len1 = PySequence_Fast_GET_SIZE(seq1);
		len2 = PySequence_Fast_GET_SIZE(seq2);
		if (len1 == -1 || len2 == -1) {
			Py_DECREF(seq1);
			Py_DECREF(seq2);
			PyErr_SetString(PyExc_RuntimeError, "failed to get len of objects");
			return NULL;
		}
	
		if (len1 > len2)
			dist = rich_levenshtein(arg1, arg2, len1, len2, max_dist);
		else
			dist = rich_levenshtein(arg2, arg1, len2, len1, max_dist);
		
		Py_DECREF(seq1);
		Py_DECREF(seq2);
	}
	
	else {
		PyErr_SetString(PyExc_TypeError, "expected two sequence objects");
		return NULL;
	}

	if (dist == WE_GOT_A_PROBLEM)
		return NULL;
	
	if (do_normalize) {
		if (len1 == 0 && len2 == 0)
			return Py_BuildValue("f", 0.0);
		double max_len = (len1 > len2 ? len1 : len2);
		return Py_BuildValue("d", dist / max_len);
	}
	return Py_BuildValue("n", dist);
	
}



/* Fast comp and co. */

static short
uni_fast_comp(void *ptr1, void *ptr2, int kind1, int kind2,
	Py_ssize_t len1, Py_ssize_t len2, int transpositions)
{
	char *models[3];
	short m, cnt, res = 3;
	Py_ssize_t i, j, c;
	
	Py_ssize_t ldiff = len1 - len2;

	/* i, d, r = insert, delete, replace */
	switch (ldiff) {
		case 0:
			models[2] = "id";
			models[1] = "di";
			models[0] = "rr";
			m = 2;
			break;
		case 1:
			models[1] = "dr";
			models[0] = "rd";
			m = 1;
			break;
		case 2:
			models[0] = "dd";
			m = 0;
			break;
		default:
			return -1;
	}

	for (; m >= 0; m--) {
	
		i = j = c = 0;
		
		while (i < len1 && j < len2)
		{
			if (PyUnicode_READ(kind1, ptr1, i) != PyUnicode_READ(kind2, ptr2, j)) {
				c++;
				if (c > 2)
					break;
				
				if (transpositions && ldiff != 2 && i < len1 - 1 && j < len2 - 1 && \
					PyUnicode_READ(kind1, ptr1, i + 1) == PyUnicode_READ(kind2, ptr2, j) && \
					PyUnicode_READ(kind1, ptr1, i) == PyUnicode_READ(kind2, ptr2, j + 1)) {
					i = i + 2;
					j = j + 2;
				}
				else {
					if (models[m][c - 1] == 'd')
						i++;
					else if (models[m][c - 1] == 'i')
						j++;
					else {
						i++;
						j++;
					}
				}
			}
			else {
				i++;
				j++;
			}
		}
		
		if (c > 2)
			continue;

		else if (i < len1) {
			if (c == 1)
				cnt = (models[m][1] == 'd');
			else
				cnt = (models[m][0] == 'd') + (models[m][1] == 'd');
			if (len1 - i <= cnt) {
				c = c + (len1 - i);
			}
			else
				continue;
		}
		else if (j < len2) {
			if (len2 - j <= (models[m][c] == 'i'))
				c = c + (len2 - j);
			else
				continue;
		}
		if (c < res) {
			res = c;
		}
	}

	if (res == 3)
		res = -1;
		
	return res;
}


static PyObject *
fast_comp(PyObject *self, PyObject *args, PyObject *kwargs)
{
	PyObject *arg1, *arg2;
	Py_ssize_t len1, len2;
	void *ptr1, *ptr2;
	int kind1, kind2;
	short dist;
	int transpositions = 0;
	static char *keywords[] = {"arg1", "arg2", "transpositions", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "UU|p:fast_comp",
		keywords, &arg1, &arg2, &transpositions))
		return NULL;

	if (PyUnicode_READY(arg1) != 0)
		return NULL;
	if (PyUnicode_READY(arg2) != 0)
		return NULL;

	len1 = PyUnicode_GET_LENGTH(arg1);
	len2 = PyUnicode_GET_LENGTH(arg2);
	ptr1 = PyUnicode_DATA(arg1);
	ptr2 = PyUnicode_DATA(arg2);
	kind1 = PyUnicode_KIND(arg1);
	kind2 = PyUnicode_KIND(arg2);
	
	if (len1 > len2)
		dist = uni_fast_comp(ptr1, ptr2, kind1, kind2, len1, len2, transpositions);
	else
		dist = uni_fast_comp(ptr2, ptr1, kind2, kind1, len2, len1, transpositions);
	
	return Py_BuildValue("h", dist);	
}


typedef struct {
	PyObject_HEAD
	PyObject *itor;
	PyObject *str1;
	void *ptr1;
	int kind1;
	Py_ssize_t len1;
	int transpos;
} ItorState;


static void itor_dealloc(ItorState *state)
{
	Py_XDECREF(state->str1);
	Py_XDECREF(state->itor);
	Py_TYPE(state)->tp_free(state);
}


static PyObject * ifast_comp(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
	PyObject *arg1, *arg2, *itor;
	int transpositions = 0;
	static char *keywords[] = {"str1", "strs", "transpositions", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "UO|p:ifast_comp",
		keywords, &arg1, &arg2, &transpositions))
		return NULL;

	if (PyUnicode_READY(arg1) != 0)
		return NULL;
	if ((itor = PyObject_GetIter(arg2)) == NULL) {
		PyErr_SetString(PyExc_ValueError, "expected an iterable");
		return NULL;
	}

	ItorState *state = (ItorState *)type->tp_alloc(type, 0);
	if (state == NULL) {
		Py_DECREF(itor);
		return NULL;
	}
    
	state->itor = itor;
	Py_INCREF(arg1);
	state->str1 = arg1;
	state->len1 = PyUnicode_GET_LENGTH(arg1);
	state->ptr1 = PyUnicode_DATA(arg1);
	state->kind1 = PyUnicode_KIND(arg1);
	state->transpos = transpositions;
	  
	return (PyObject *)state;
}


static PyObject * ifast_comp_next(ItorState *state)
{
	PyObject *str2, *rv;
	Py_ssize_t len2;
	void *ptr2;
	int kind2;
	short dist = -1;
	
	while ((str2 = PyIter_Next(state->itor)) != NULL) {
	
		if (!PyUnicode_Check(str2)) {
			Py_DECREF(str2);
			PyErr_SetString(PyExc_ValueError, "expected unicodes in iterable");
			return NULL;
		}
		if (PyUnicode_READY(str2) != 0) {
			Py_DECREF(str2);
			return NULL;
		}
	
		len2 = PyUnicode_GET_LENGTH(str2);
		ptr2 = PyUnicode_DATA(str2);
		kind2 = PyUnicode_KIND(str2);
		
		if (state->len1 > len2)
			dist = uni_fast_comp(state->ptr1, ptr2, state->kind1, kind2,
				state->len1, len2, state->transpos);
		else
			dist = uni_fast_comp(ptr2, state->ptr1, kind2, state->kind1,
				len2, state->len1, state->transpos);
		
		if (dist != -1) {
			rv = Py_BuildValue("(hO)", dist, str2);
			Py_DECREF(str2);
			return rv;
		}
		
		Py_DECREF(str2);
	}

	return NULL;
}


PyTypeObject IFastComp_Type = {
	PyVarObject_HEAD_INIT(&PyType_Type, 0)
	"distance.ifast_comp", /* tp_name */
	sizeof(ItorState), /* tp_basicsize */
	0, /* tp_itemsize */
	(destructor)itor_dealloc, /* tp_dealloc */
	0, /* tp_print */
	0, /* tp_getattr */
	0, /* tp_setattr */
	0, /* tp_reserved */
	0, /* tp_repr */
	0, /* tp_as_number */
	0, /* tp_as_sequence */
	0, /* tp_as_mapping */
	0, /* tp_hash */
	0, /* tp_call */
	0, /* tp_str */
	0, /* tp_getattro */
	0, /* tp_setattro */
	0, /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT, /* tp_flags */
	ifast_comp_doc, /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	0, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	PyObject_SelfIter, /* tp_iter */
	(iternextfunc)ifast_comp_next, /* tp_iternext */
	0, /* tp_methods */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_dictoffset */
	0, /* tp_init */
	PyType_GenericAlloc, /* tp_alloc */
	ifast_comp, /* tp_new */
};


static PyMethodDef CDistanceMethods[] = {
	{"levenshtein", (PyCFunction)levenshtein, METH_VARARGS | METH_KEYWORDS, levenshtein_doc},
	{"hamming", (PyCFunction)hamming, METH_VARARGS | METH_KEYWORDS, hamming_doc},
	{"fast_comp", (PyCFunction)fast_comp, METH_VARARGS | METH_KEYWORDS, fast_comp_doc},
	{NULL, NULL, 0, NULL}
};


static struct PyModuleDef cdistancemodule = {
	PyModuleDef_HEAD_INIT, "cdistance", NULL, -1, CDistanceMethods
};


PyMODINIT_FUNC PyInit_cdistance(void)
{
	PyObject *module = PyModule_Create(&cdistancemodule);
	if (!module)
		return NULL;

	if (PyType_Ready(&IFastComp_Type) != 0)
		return NULL;
	
	Py_INCREF((PyObject *)&IFastComp_Type);
	PyModule_AddObject(module, "ifast_comp", (PyObject *)&IFastComp_Type);
	
	return module;
}
