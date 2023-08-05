/*
This file implements the basic interface to libqhull. Essentially,
it is a port of the original qconvex, qdelaunay, qvoronoi sources from qhull
(http://www.qhull.org) as a Python extension. Three methods are defined,
essentially, qconvex, qdelaunay and qvoronoi.

In the original qhull implementation, each command takes input in the form of
"qhull_command [options] <stdin>" and the results are dumped to stdout. To
minimize the impact on the underlying C code (so that future qhull versions
can be incorporated easily), the implementation in this file is as follows:
i) Obtain options and data from Python. The options are represented as a
space-separated string (e.g., "i o") and the data is represented as a string
(e.g., "2\n4\n-0.5   -0.5\n-0.5    0.5\n0.5   -0.5\n0.5    0.5\n"). The
string format is the same format as that which the qhull commands expect from
stdin. The conversion of actual Python number arrays to this string is done
on the Python end because it is much easier.

The data string is then converted to a FILE* string stream using fmemopen and
a FILE* output stream is created using open_memstream (for BSD systems such
as Mac OS, simulated versions using funopen are implemented). These are
supplied in place of stdin and stdout. The resulting string output from the
qhull command is then returned as a Python string.

Author: Shyue Ping Ong
Date: Nov 23 2012
*/

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "libqhull.h"
#include "mem.h"
#include "qset.h"

#if __MWERKS__ && __POWERPC__
#include <SIOUX.h>
#include <Files.h>
#include <console.h>
#include <Desk.h>

#elif __cplusplus
extern "C" {
  int isatty(int);
}

#elif _MSC_VER
#include <io.h>
#define isatty _isatty
int _isatty(int);

#else
int isatty(int);  /* returns 1 if stdin is a tty
                   if "Undefined symbol" this can be deleted along with call in main() */
#endif

/* Use simulated fmemopen and open_memstream for Mac systems.*/
#if (defined(BSD) || __APPLE__)
#include "fmemopen.h"
#include "open_memstream.h"
#endif

char hidden_options[]=" d v H Qbb Qf Qg Qm Qr Qu Qv Qx Qz TR E V Fp Gt Q0 Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 ";


static PyObject* qconvex(PyObject *self, PyObject *args) {
    const char *arg;
    const char *data;
    int curlong, totlong; /* used !qh_NOmem */
    int exitcode, numpoints, dim;
    coordT *points;
    boolT ismalloc;
    if (!PyArg_ParseTuple(args, "ss", &arg, &data))
        return NULL;
    char* argv[10];
    int argc = 1;
    char *rest;
    char *token;
    /* Defensively copy the string first */
    char tempstr[30];
    strcpy(tempstr, arg);
    char* ptr = tempstr;

    while(token = strtok_r(ptr, " ", &rest)) {
        argv[argc] = token;
        ptr = rest;
        argc  += 1;
    }
    argv[0] = "qconvex";

    char *bp;
    size_t size;

    /* Because qhull uses stdin and stdout streams for io, we need to create
    FILE* stream to simulate these io streams.*/
    FILE* fin = fmemopen(data, strlen(data), "r");
    FILE* fout = open_memstream(&bp, &size);

    if ((fin != NULL) && (fout != NULL))
    {
        /* Now do the usual qhull code (modified from qconvex.c). */
        qh_init_A(fin, fout, stderr, argc, argv);

        exitcode= setjmp(qh errexit);
        if (!exitcode) {
            qh_checkflags(qh qhull_command, hidden_options);
            qh_initflags(qh qhull_command);
            points= qh_readpoints(&numpoints, &dim, &ismalloc);
        if (dim >= 5) {
            qh_option("Qxact_merge", NULL, NULL);
            qh MERGEexact= True;
        }
        qh_init_B(points, numpoints, dim, ismalloc);
        qh_qhull();
        qh_check_output();
        qh_produce_output();
        if (qh VERIFYoutput && !qh FORCEoutput && !qh STOPpoint && !qh STOPcone)
            qh_check_points();
        exitcode= qh_ERRnone;
        }
        qh NOerrexit= True;  /* no more setjmp */
        #ifdef qh_NOmem
            qh_freeqhull( True);
        #else
            qh_freeqhull( False);
            qh_memfreeshort(&curlong, &totlong);
            if (curlong || totlong)
                fprintf(stderr, "qhull internal warning (main): did not free %d bytes of long memory(%d pieces)\n", totlong, curlong);
        #endif
        fclose(fin);
        fclose(fout);
        return Py_BuildValue("s", bp);
    }
    else
    {
        return NULL;
    }
}

static PyObject* qdelaunay(PyObject *self, PyObject *args) {
    const char *arg;
    const char *data;
    int curlong, totlong; /* used !qh_NOmem */
    int exitcode, numpoints, dim;
    coordT *points;
    boolT ismalloc;
    if (!PyArg_ParseTuple(args, "ss", &arg, &data))
        return NULL;
    char* argv[10];
    int argc = 1;
    char *rest;
    char *token;
    /* Defensively copy the string first */
    char tempstr[30];
    strcpy(tempstr, arg);
    char* ptr = tempstr;

    while(token = strtok_r(ptr, " ", &rest)) {
        argv[argc] = token;
        ptr = rest;
        argc  += 1;
    }

    argv[0] = "qdelaunay";
    char *bp;
    size_t size;

    /* Because qhull uses stdin and stdout streams for io, we need to create
    FILE* stream to simulate these io streams.*/
    FILE* fin = fmemopen(data, strlen(data), "r");
    FILE* fout = open_memstream(&bp, &size);

    if ((fin != NULL) && (fout != NULL))
    {
        /* Now do the usual qhull code (modified from qdelaunay.c). */
        qh_init_A(fin, fout, stderr, argc, argv);  /* sets qh qhull_command */
        exitcode= setjmp(qh errexit); /* simple statement for CRAY J916 */
        if (!exitcode) {
            qh_option("delaunay  Qbbound-last", NULL, NULL);
            qh DELAUNAY= True;     /* 'd'   */
            qh SCALElast= True;    /* 'Qbb' */
            qh KEEPcoplanar= True; /* 'Qc', to keep coplanars in 'p' */
            qh_checkflags(qh qhull_command, hidden_options);
            qh_initflags(qh qhull_command);
            points= qh_readpoints(&numpoints, &dim, &ismalloc);
            if (dim >= 5) {
                qh_option("Qxact_merge", NULL, NULL);
                qh MERGEexact= True; /* 'Qx' always */
            }
            qh_init_B(points, numpoints, dim, ismalloc);
            qh_qhull();
            qh_check_output();
            qh_produce_output();
            if (qh VERIFYoutput && !qh FORCEoutput && !qh STOPpoint && !qh STOPcone)
                qh_check_points();
            exitcode= qh_ERRnone;
        }
        qh NOerrexit= True;  /* no more setjmp */
        #ifdef qh_NOmem
            qh_freeqhull( True);
        #else
            qh_freeqhull( False);
            qh_memfreeshort(&curlong, &totlong);
            if (curlong || totlong)
                fprintf(stderr, "qhull internal warning (main): did not free %d bytes of long memory(%d pieces)\n",
                totlong, curlong);
        #endif

        fclose(fin);
        fclose(fout);
        return Py_BuildValue("s", bp);
    }
    else
    {
        return NULL;
    }
}


static PyObject* qvoronoi(PyObject *self, PyObject *args) {
    const char *arg;
    const char *data;
    int curlong, totlong; /* used !qh_NOmem */
    int exitcode, numpoints, dim;
    coordT *points;
    boolT ismalloc;
    if (!PyArg_ParseTuple(args, "ss", &arg, &data))
        return NULL;
    char *argv[10];
    int argc = 1;
    char *rest;
    char *token;
    /* Defensively copy the string first */
    char tempstr[30];
    strcpy(tempstr, arg);
    char* ptr = tempstr;

    while(token = strtok_r(ptr, " ", &rest)) {
        argv[argc] = token;
        ptr = rest;
        argc  += 1;
    }
    argv[0] = "qvoronoi";

    char *bp;
    size_t size;

    /* Because qhull uses stdin and stdout streams for io, we need to create
    FILE* stream to simulate these io streams.*/
    FILE* fin = fmemopen(data, strlen(data), "r");
    FILE* fout = open_memstream(&bp, &size);

    if ((fin != NULL) && (fout != NULL))
    {
        /* Now do the usual qhull code (modified from qvoronoi.c). */
        qh_init_A(fin, fout, stderr, argc, argv);  /* sets qh qhull_command */
        exitcode= setjmp(qh errexit); /* simple statement for CRAY J916 */
        if (!exitcode) {
            qh_option("voronoi  _bbound-last  _coplanar-keep", NULL, NULL);
            qh DELAUNAY= True;     /* 'v'   */
            qh VORONOI= True;
            qh SCALElast= True;    /* 'Qbb' */
            qh_checkflags(qh qhull_command, hidden_options);
            qh_initflags(qh qhull_command);
            points= qh_readpoints(&numpoints, &dim, &ismalloc);
            if (dim >= 5) {
                qh_option("_merge-exact", NULL, NULL);
                qh MERGEexact= True; /* 'Qx' always */
            }
            qh_init_B(points, numpoints, dim, ismalloc);
            qh_qhull();
            qh_check_output();
            qh_produce_output();
            if (qh VERIFYoutput && !qh FORCEoutput && !qh STOPpoint && !qh STOPcone)
                qh_check_points();
            exitcode= qh_ERRnone;
        }
        qh NOerrexit= True;  /* no more setjmp */
        #ifdef qh_NOmem
            qh_freeqhull( True);
        #else
            qh_freeqhull( False);
            qh_memfreeshort(&curlong, &totlong);
            if (curlong || totlong)
                fprintf(stderr, "qhull internal warning (main): did not free %d bytes of long memory(%d pieces)\n",
                totlong, curlong);
        #endif
        fclose(fin);
        fclose(fout);

        return Py_BuildValue("s", bp);
    }
    else
    {
        return NULL;
    }
}


static PyMethodDef QhullMethods[] = {
    {"qconvex", qconvex, METH_VARARGS, "qconvex"},
    {"qdelaunay", qdelaunay, METH_VARARGS, "qdelaunay"},
    {"qvoronoi", qvoronoi, METH_VARARGS, "qvoronoi"},
    {NULL, NULL, 0, NULL}
};


void init_pyhull(void)
{
    (void) Py_InitModule("_pyhull", QhullMethods);
}