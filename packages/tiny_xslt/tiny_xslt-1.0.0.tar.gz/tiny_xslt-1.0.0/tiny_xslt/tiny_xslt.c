/*
 * Author  : Jerome ODIER
 *
 * Email   : jerome.odier@lpsc.in2p3.fr
 *
 * Version : 1.0.0 (2013)
 */

/*-------------------------------------------------------------------------*/

#include <Python.h>
#include <string.h>

#include <libxslt/transform.h>
#include <libxslt/xsltutils.h>

/*-------------------------------------------------------------------------*/

static const char py_xslt_docstring[] = "This function performs a XSL transformation.";

static const char py_verbose_docstring[] = "This function enables/disables error outputs.";

/*-------------------------------------------------------------------------*/

static xsltStylesheet *xsltParseStylesheetMemory(const char *buffer, int size)
{
	xmlDoc *doc = xmlParseMemory(buffer, size);

	if(doc == NULL)
	{
		return NULL;
	}

	return xsltParseStylesheetDoc(doc);
}

/*-------------------------------------------------------------------------*/

static PyObject *py_xslt(PyObject *self, PyObject *args)
{
	xmlInitParser();

	xsltStylesheet *cur = NULL;

	xmlDoc *doc = NULL;

	/*-----------------------------------------------------------------*/
	/* PARSE ARGUMENTS						   */
	/*-----------------------------------------------------------------*/

	char *xsl;
	char *xml;

	if(PyArg_ParseTuple(args, "ss", &xsl, &xml) == 0)
	{
		Py_RETURN_NONE;
	}

	/*-----------------------------------------------------------------*/
	/* OPEN XSL FILE						   */
	/*-----------------------------------------------------------------*/

	cur = xsltParseStylesheetMemory(xsl, (int) strlen(xsl));

	if(cur == NULL)
	{
		goto __error;
	}

	/*-----------------------------------------------------------------*/
	/* OPEN XML FILE						   */
	/*-----------------------------------------------------------------*/

	doc = xmlParseMemory(xml, (int) strlen(xml));

	if(doc == NULL)
	{
		goto __error;
	}

	/*-----------------------------------------------------------------*/
	/* APPLY SHEET							   */
	/*-----------------------------------------------------------------*/

	xmlDoc *res = xsltApplyStylesheet(cur, doc, NULL);

	if(res == NULL)
	{
		goto __error;
	}

	/*-----------------------------------------------------------------*/
	/* GET RESULT							   */
	/*-----------------------------------------------------------------*/

	xmlChar *buffer = BAD_CAST "";
	int length = 0;

	xsltSaveResultToString(&buffer, &length, res, cur);
	PyObject *result = Py_BuildValue("s", (char *) buffer);
	free(buffer);

	xmlFreeDoc(res);

	/*-----------------------------------------------------------------*/
	/* SUCCESS							   */
	/*-----------------------------------------------------------------*/

	xsltFreeStylesheet(cur);

	xmlFreeDoc(doc);

	xsltCleanupGlobals();
	xmlCleanupParser();

	return result;

	/*-----------------------------------------------------------------*/
	/* ERROR							   */
	/*-----------------------------------------------------------------*/
__error:
	if(cur != NULL)
	{
		xsltFreeStylesheet(cur);
	}

	if(doc != NULL)
	{
		xmlFreeDoc(doc);
	}

	xsltCleanupGlobals();
	xmlCleanupParser();

	Py_RETURN_NONE;
}

/*-------------------------------------------------------------------------*/

static void __errorFunc(void *ctx, const char *msg, ...) { }

/*-------------------------------------------------------------------------*/

static PyObject *py_verbose(PyObject *self, PyObject *args)
{
	/*-----------------------------------------------------------------*/
	/* PARSE ARGUMENTS						   */
	/*-----------------------------------------------------------------*/

	int verbose;

	if(PyArg_ParseTuple(args, "i", &verbose) == 0)
	{
		Py_RETURN_NONE;
	}

	/*-----------------------------------------------------------------*/

	if(verbose == 0)
	{
		xsltSetGenericDebugFunc(NULL, __errorFunc);
		xsltSetGenericErrorFunc(NULL, __errorFunc);
	}
	else
	{
		xsltSetGenericDebugFunc(NULL, NULL);
		xsltSetGenericErrorFunc(NULL, NULL);
	}

	/*-----------------------------------------------------------------*/

	Py_RETURN_NONE;
}

/*-------------------------------------------------------------------------*/

static PyMethodDef tiny_xslt_methods[] = {
	{"xslt", py_xslt, METH_VARARGS, py_xslt_docstring},
	{"verbose", py_verbose, METH_VARARGS, py_verbose_docstring},
	{NULL, NULL}
};

/*-------------------------------------------------------------------------*/

void inittiny_xslt(void)
{
	Py_InitModule3("tiny_xslt", tiny_xslt_methods, "This module provides an interface for XSL transformations.");
}

/*-------------------------------------------------------------------------*/
