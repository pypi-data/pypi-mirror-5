/*
 * Copyright (c) 2011 Outpost Embedded, LLC
 *
 * This file is part of the pylibsensors software package.
 *
 * pylibsensors is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * version 2 as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * A copy of the license has been included in the COPYING file.
 */

#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <structmember.h>
#include <pythread.h>
#include <sensors/sensors.h>


#define BUFSIZE 256


typedef enum {FALSE = 0, TRUE = 1} BOOL;


typedef struct BusId BusId;
typedef struct ChipName ChipName;
typedef struct Feature Feature;
typedef struct Subfeature Subfeature;


static PyTypeObject BusIdType;
static PyTypeObject ChipNameType;
static PyTypeObject FeatureType;
static PyTypeObject SubfeatureType;


static BOOL _PyObject_TypeRequire(PyObject *o, PyTypeObject *t)
{
	if (! PyObject_TypeCheck(o, t)) {
		PyErr_SetString(PyExc_TypeError, "Incorrect type");
		return FALSE;
	}

	return TRUE;
}


static int _PyObject_ReadOnlySetAttr(PyObject *self, PyObject *attr_name, PyObject *value)
{
	PyErr_SetString(PyExc_TypeError, "Read-only object");
	return -1;
}



/*** BusId ***/


struct BusId {
	PyObject_HEAD
	sensors_bus_id *data;
	ChipName *owner;
};


static BusId *_BusId_New(sensors_bus_id *data, ChipName *owner)
{
	BusId *instance;

	instance = (BusId *)PyObject_GC_New(BusId, &BusIdType);
	if (instance == NULL)
		return (BusId *)PyErr_NoMemory();

	instance->data = data;
	if (owner != NULL)
		Py_INCREF(owner);
	instance->owner = owner;

	PyObject_GC_Track(instance);

	return instance;
}


static sensors_bus_id *BusId_get_data(BusId *self)
{
	return self->data;
}


static int BusId_clear(BusId *self)
{
	Py_CLEAR(self->owner);

	return 0;
}


static void BusId_dealloc(BusId *self)
{
	PyObject_GC_UnTrack((PyObject *)self);
	BusId_clear(self);
	PyObject_GC_Del((PyObject *)self);
}


static int BusId_traverse(BusId *self, visitproc visit, void *arg)
{
	if (self->owner != NULL)
		Py_VISIT(self->owner);

	return 0;
}


static PyObject *BusId__repr__(PyObject *self)
{
	char buf[BUFSIZE];
	int ret;
	sensors_bus_id *bus_id;

	bus_id = BusId_get_data((BusId *)self);

	ret = snprintf(buf, BUFSIZE, "<BusId type=%d nr=%d>",
					bus_id->type, bus_id->nr);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError, "snprintf returned %d", ret);

	return PyString_FromString(buf);
}


static PyObject *BusId__getattr__(PyObject *self, PyObject *attr_name)
{
	char *name;
	sensors_bus_id *data;

	if (PyString_Check(attr_name)) {
		data = BusId_get_data((BusId *)self);
		name = PyString_AsString(attr_name);
		if (strcmp(name, "type") == 0)
			return Py_BuildValue("h", data->type);
		if (strcmp(name, "nr") == 0)
			return Py_BuildValue("h", data->nr);
	}

	return PyObject_GenericGetAttr(self, attr_name);
}


PyDoc_STRVAR(BusId__doc__,
"Wrapper for sensors_bus_id.\n\n\
This class cannot be instantiated directly.\n\n\
");

static PyTypeObject BusIdType = {
	PyObject_HEAD_INIT(NULL)
	0,						/*ob_size*/
	"libsensors.BusId",				/*tp_name*/
	sizeof(BusId),					/*tp_basicsize*/
	0,						/*tp_itemsize*/
	(destructor)BusId_dealloc,			/*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	BusId__repr__,					/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,						/*tp_call*/
	0,						/*tp_str*/
	BusId__getattr__,				/*tp_getattro*/
	_PyObject_ReadOnlySetAttr,			/*tp_setattro*/
	0,						/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,	/*tp_flags*/
	BusId__doc__,					/*tp_doc*/
	(traverseproc)BusId_traverse,			/*tp_traverse*/
	(inquiry)BusId_clear,				/*tp_clear*/
};



/*** ChipName ***/


struct ChipName {
	PyObject_HEAD
	sensors_chip_name *data;
	BusId *bus;
	BOOL should_free_data;
};



static PyMemberDef ChipName_members[] = {
	{"bus", T_OBJECT, offsetof(ChipName, bus), READONLY, "bus"},
	{NULL}
};


static ChipName *_ChipName_New(sensors_chip_name *data, BOOL should_free_data)
{
	ChipName *instance;

	instance = (ChipName *)PyObject_GC_New(ChipName, &ChipNameType);
	if (instance == NULL)
		return (ChipName *)PyErr_NoMemory();

	instance->data = data;
	instance->bus = _BusId_New(&(instance->data->bus), instance);
	instance->should_free_data = should_free_data;

	PyObject_GC_Track(instance);

	return instance;
}


static sensors_chip_name *ChipName_get_data(ChipName *self)
{
	return self->data;
}


static int ChipName_clear(ChipName *self)
{
	Py_CLEAR(self->bus);

	return 0;
}


static void ChipName_dealloc(ChipName *self)
{
	PyObject_GC_UnTrack((PyObject *)self);

	ChipName_clear(self);

	if (self->should_free_data)
		sensors_free_chip_name(self->data);

	PyObject_GC_Del((PyObject *)self);
}


static int ChipName_traverse(ChipName *self, visitproc visit, void *arg)
{
	Py_VISIT(self->bus);

	return 0;
}


static PyObject *ChipName__str__(PyObject *self)
{
	char buf[BUFSIZE];
	int ret;
	sensors_chip_name *chip_name;

	chip_name = ChipName_get_data((ChipName *)self);

	ret = sensors_snprintf_chip_name(buf, BUFSIZE, chip_name);
	if (ret < 0)
		/* Note: I think we get this if the chip name contains wildcard
		 * values. */
		return PyErr_Format(PyExc_IOError,
				"sensors_snprintf_chip_name returned %d", ret);

	return PyString_FromString(buf);
}


static PyObject *ChipName__repr__(PyObject *self)
{
	char buf[BUFSIZE];
	int ret;
	sensors_chip_name *chip_name;

	chip_name = ChipName_get_data((ChipName *)self);

	ret = snprintf(buf, BUFSIZE,
				"<ChipName prefix=%s bus=%p addr=%d path=%s>",
					chip_name->prefix, &(chip_name->bus),
					chip_name->addr, chip_name->path);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError, "snprintf returned %d", ret);

	return PyString_FromString(buf);
}


static PyObject *ChipName__getattr__(PyObject *self, PyObject *attr_name)
{
	char *name;
	sensors_chip_name *data;

	if (PyString_Check(attr_name)) {
		data = ChipName_get_data((ChipName *)self);
		name = PyString_AsString(attr_name);
		if (strcmp(name, "prefix") == 0)
			return PyString_FromString(data->prefix);
		if (strcmp(name, "addr") == 0)
			return Py_BuildValue("i", data->addr);
		if (strcmp(name, "path") == 0)
			return PyString_FromString(data->path);
	}

	return PyObject_GenericGetAttr(self, attr_name);
}


PyDoc_STRVAR(ChipName__doc__,
"Wrapper for sensors_chip_name.\n\n\
This class cannot be instantiated directly.\n\n\
");

static PyTypeObject ChipNameType = {
	PyObject_HEAD_INIT(NULL)
	0,						/*ob_size*/
	"libsensors.ChipName",				/*tp_name*/
	sizeof(ChipName),				/*tp_basicsize*/
	0,						/*tp_itemsize*/
	(destructor)ChipName_dealloc,			/*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	ChipName__repr__,				/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,						/*tp_call*/
	ChipName__str__,				/*tp_str*/
	ChipName__getattr__,				/*tp_getattro*/
	_PyObject_ReadOnlySetAttr,			/*tp_setattro*/
	0,						/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,	/*tp_flags*/
	ChipName__doc__,				/*tp_doc*/
	(traverseproc)ChipName_traverse,		/*tp_traverse*/
	(inquiry)ChipName_clear,			/*tp_clear*/
	0,						/*tp_richcompare*/
	0,						/*tp_weaklistoffset*/
	0,						/*tp_iter*/
	0,						/*tp_iternext*/
	0,						/*tp_methods*/
	ChipName_members,				/*tp_members*/
};



/*** Feature ***/


struct Feature {
	PyObject_HEAD
	sensors_feature *data;
};


static Feature *_Feature_New(sensors_feature *data)
{
	Feature *instance;

	instance = (Feature *)PyObject_New(Feature, &FeatureType);
	if (instance == NULL)
		return (Feature *)PyErr_NoMemory();

	instance->data = data;

	return instance;
}


static sensors_feature *Feature_get_data(Feature *self)
{
	return self->data;
}


static PyObject *Feature__repr__(PyObject *self)
{
	char buf[BUFSIZE];
	int ret;
	sensors_feature *feature;

	feature = Feature_get_data((Feature *)self);

	ret = snprintf(buf, BUFSIZE, "<Feature name=%s number=%d type=%d>",
				feature->name, feature->number, feature->type);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError, "snprintf returned %d", ret);

	return PyString_FromString(buf);
}


static PyObject *Feature__getattr__(PyObject *self, PyObject *attr_name)
{
	char *name;
	sensors_feature *data;

	if (PyString_Check(attr_name)) {
		data = Feature_get_data((Feature *)self);
		name = PyString_AsString(attr_name);
		if (strcmp(name, "name") == 0)
			return PyString_FromString(data->name);
		if (strcmp(name, "number") == 0)
			return Py_BuildValue("i", data->number);
		if (strcmp(name, "type") == 0)
			return Py_BuildValue("i", data->type);
	}

	return PyObject_GenericGetAttr(self, attr_name);
}


PyDoc_STRVAR(Feature__doc__,
"Wrapper for sensors_feature.\n\n\
This class cannot be instantiated directly.\n\n\
");

static PyTypeObject FeatureType = {
	PyObject_HEAD_INIT(NULL)
	0,						/*ob_size*/
	"libsensors.Feature",				/*tp_name*/
	sizeof(Feature),				/*tp_basicsize*/
	0,						/*tp_itemsize*/
	0,						/*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	Feature__repr__,				/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,						/*tp_call*/
	0,						/*tp_str*/
	Feature__getattr__,				/*tp_getattro*/
	_PyObject_ReadOnlySetAttr,			/*tp_setattro*/
	0,						/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,				/*tp_flags*/
	Feature__doc__,					/*tp_doc*/
};



/*** Subfeature ***/


struct Subfeature {
	PyObject_HEAD
	sensors_subfeature *data;
};


static Subfeature *_Subfeature_New(sensors_subfeature *data)
{
	Subfeature *instance;

	instance = (Subfeature *)PyObject_New(Subfeature, &SubfeatureType);
	if (instance == NULL)
		return (Subfeature *)PyErr_NoMemory();

	instance->data = data;

	return instance;
}


static sensors_subfeature *Subfeature_get_data(Subfeature *self)
{
	return self->data;
}


static PyObject *Subfeature__repr__(PyObject *self)
{
	char buf[BUFSIZE];
	int ret;
	sensors_subfeature *subfeature;

	subfeature = Subfeature_get_data((Subfeature *)self);

	ret = snprintf(buf, BUFSIZE,
		"<Subfeature name=%s number=%d type=%d mapping=%d flags=%d>",
			subfeature->name, subfeature->number, subfeature->type,
					subfeature->mapping, subfeature->flags);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError, "snprintf returned %d", ret);

	return PyString_FromString(buf);
}


static PyObject *Subfeature__getattr__(PyObject *self, PyObject *attr_name)
{
	char *name;
	sensors_subfeature *data;

	if (PyString_Check(attr_name)) {
		data = Subfeature_get_data((Subfeature *)self);
		name = PyString_AsString(attr_name);
		if (strcmp(name, "name") == 0)
			return PyString_FromString(data->name);
		if (strcmp(name, "number") == 0)
			return Py_BuildValue("i", data->number);
		if (strcmp(name, "type") == 0)
			return Py_BuildValue("i", data->type);
		if (strcmp(name, "mapping") == 0)
			return Py_BuildValue("i", data->mapping);
		if (strcmp(name, "flags") == 0)
			return Py_BuildValue("I", data->flags);
	}

	return PyObject_GenericGetAttr(self, attr_name);
}


PyDoc_STRVAR(Subfeature__doc__,
"Wrapper for sensors_subfeature.\n\n\
This class cannot be instantiated directly.\n\n\
");

static PyTypeObject SubfeatureType = {
	PyObject_HEAD_INIT(NULL)
	0,						/*ob_size*/
	"libsensors.Subfeature",			/*tp_name*/
	sizeof(Subfeature),				/*tp_basicsize*/
	0,						/*tp_itemsize*/
	0,						/*tp_dealloc*/
	0,						/*tp_print*/
	0,						/*tp_getattr*/
	0,						/*tp_setattr*/
	0,						/*tp_compare*/
	Subfeature__repr__,				/*tp_repr*/
	0,						/*tp_as_number*/
	0,						/*tp_as_sequence*/
	0,						/*tp_as_mapping*/
	0,						/*tp_hash*/
	0,						/*tp_call*/
	0,						/*tp_str*/
	Subfeature__getattr__,				/*tp_getattro*/
	_PyObject_ReadOnlySetAttr,			/*tp_setattro*/
	0,						/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,				/*tp_flags*/
	Subfeature__doc__,				/*tp_doc*/
};



/*** Module ***/


PyDoc_STRVAR(init__doc__,
"init([f])\n\n\
Wrapper for sensors_init.\n\n\
An open file object may optionally be passed to load an alternate\n\
configuration file.\n\n\
");

static PyObject *init(PyObject *self, PyObject *args)
{
	int ret;
	FILE *input;
	PyObject *f = Py_None;

	if (! PyArg_ParseTuple(args, "|O", &f))
		return NULL;

	if (f == Py_None) {
		input = NULL;
	} else {
		input = PyFile_AsFile(f);
		if (input == NULL) {
			PyErr_SetString(PyExc_TypeError,
					"argument must be open file");
			return NULL;
		}
	}

	ret = sensors_init(input);

	return Py_BuildValue("i", ret);
}


PyDoc_STRVAR(cleanup__doc__,
"cleanup()\n\n\
Wrapper for sensors_cleanup.\n\n\
");

static PyObject *cleanup(PyObject *self, PyObject *args)
{
	sensors_cleanup();
	Py_RETURN_NONE;
}


PyDoc_STRVAR(parse_chip_name__doc__,
"parse_chip_name(name)  ->  {ChipName}\n\n\
Wrapper for sensors_parse_chip_name.\n\n\
");

static PyObject *parse_chip_name(PyObject *self, PyObject *args)
{
	char *name;
	sensors_chip_name *chip_name;
	ChipName *chip_name_obj;
	int ret;

	if (! PyArg_ParseTuple(args, "s", &name))
		return NULL;

	chip_name = malloc(sizeof(sensors_chip_name));
	if (chip_name == NULL)
		return PyErr_NoMemory();

	ret = sensors_parse_chip_name(name, chip_name);
	if (ret < 0) {
		free(chip_name);
		return PyErr_Format(PyExc_IOError,
			"sensors_parse_chip_name returned %d", ret);
	}

	chip_name_obj = _ChipName_New(chip_name, TRUE);
	if (chip_name_obj == NULL) {
		sensors_free_chip_name(chip_name);
		return NULL;
	}

	return (PyObject *)chip_name_obj;
}


PyDoc_STRVAR(get_adapter_name__doc__,
"get_adapter_name(bus_id)  ->  {str}\n\n\
Wrapper for sensors_get_adapter_name.\n\n\
");

static PyObject *get_adapter_name(PyObject *self, PyObject *args)
{
	PyObject *bus_id_obj;
	sensors_bus_id *bus_id;
	char *adapter_name;

	if (! PyArg_ParseTuple(args, "O", &bus_id_obj))
		return NULL;

	bus_id = BusId_get_data((BusId *)bus_id_obj);

	adapter_name = (char *)sensors_get_adapter_name(bus_id);
	if (adapter_name == NULL) {
		PyErr_SetString(PyExc_IOError,
				"sensors_get_adapter_name returned NULL");
		return NULL;
	}

	return PyString_FromString(adapter_name);
}


PyDoc_STRVAR(get_label__doc__,
"get_label(chip_name, feature)  ->  {str}\n\n\
Wrapper for sensors_get_label.\n\n\
");

static PyObject *get_label(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj;
	sensors_chip_name *chip_name;
	PyObject *feature_obj;
	sensors_feature *feature;
	char *label;
	PyObject *label_obj;

	if (! PyArg_ParseTuple(args, "OO", &chip_name_obj, &feature_obj))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	if (! _PyObject_TypeRequire(feature_obj, &FeatureType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);
	feature = Feature_get_data((Feature *)feature_obj);

	label = sensors_get_label(chip_name, feature);
	if (label == NULL) {
		PyErr_SetString(PyExc_IOError,
				"sensors_get_label returned NULL");
		return NULL;
	}

	label_obj = PyString_FromString(label);

	free(label);

	if (label_obj == NULL)
		return NULL;

	return label_obj;
}


PyDoc_STRVAR(get_value__doc__,
"get_value(chip_name, subfeat_nr)  ->  {float}\n\n\
Wrapper for sensors_get_value.\n\n\
");

static PyObject *get_value(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj;
	sensors_chip_name *chip_name;
	int subfeat_nr;
	double value;
	int ret;

	if (! PyArg_ParseTuple(args, "Oi", &chip_name_obj, &subfeat_nr))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);

	ret = sensors_get_value(chip_name, subfeat_nr, &value);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError,
					"sensors_get_value returned %d", ret);

	return Py_BuildValue("d", value);
}


PyDoc_STRVAR(set_value__doc__,
"set_value(chip_name, subfeat_nr, value)\n\n\
Wrapper for sensors_set_value.\n\n\
");

static PyObject *set_value(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj;
	sensors_chip_name *chip_name;
	int subfeat_nr;
	double value;
	int ret;

	if (! PyArg_ParseTuple(args, "Oid", &chip_name_obj, &subfeat_nr, &value))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);

	ret = sensors_set_value(chip_name, subfeat_nr, value);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError,
					"sensors_set_value returned %d", ret);

	Py_RETURN_NONE;
}


PyDoc_STRVAR(do_chip_sets__doc__,
"do_chip_sets(chip_name)\n\n\
Wrapper for sensors_do_chip_sets.\n\n\
");

static PyObject *do_chip_sets(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj;
	sensors_chip_name *chip_name;
	int ret;

	if (! PyArg_ParseTuple(args, "O", &chip_name_obj))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);

	ret = sensors_do_chip_sets(chip_name);
	if (ret < 0)
		return PyErr_Format(PyExc_IOError,
				"sensors_do_chip_sets returned %d", ret);

	Py_RETURN_NONE;
}


PyDoc_STRVAR(get_detected_chips__doc__,
"get_detected_chips([match])  ->  [{ChipName}, {ChipName}, ...]\n\n\
Wrapper for sensors_get_detected_chips.\n\n\
match can be a ChipName instance (with or without wildcard parts),\n\
and should be constructed using ChipName.parse.\n\n\
");

static PyObject *get_detected_chips(PyObject *self, PyObject *args)
{
	PyObject *match_obj = Py_None;
	ChipName *chip_name_obj;
	sensors_chip_name *match;
	const sensors_chip_name *chip_name;
	PyObject *l;
	int i;

	if (! PyArg_ParseTuple(args, "|O", &match_obj))
		return NULL;

	if (match_obj == Py_None) {
		match = NULL;
	} else {
		if (! _PyObject_TypeRequire(match_obj, &ChipNameType))
			return NULL;

		match = ChipName_get_data((ChipName *)match_obj);
	}

	l = PyList_New(0);

	i = 0;
	while (TRUE) {
		chip_name = sensors_get_detected_chips(match, &i);
		if (chip_name == NULL)
			break;

		chip_name_obj = _ChipName_New((sensors_chip_name *)chip_name,
									FALSE);
		PyList_Append(l, (PyObject *)chip_name_obj);
		Py_DECREF(chip_name_obj);
	}

	return l;
}


PyDoc_STRVAR(get_features__doc__,
"get_features(chip_name)  ->  [{Feature}, {Feature}, ...]\n\n\
Wrapper for sensors_get_features.\n\n\
");

static PyObject *get_features(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj = Py_None;
	sensors_chip_name *chip_name;
	Feature *feature_obj;
	sensors_feature *feature;
	PyObject *l;
	int i;

	if (! PyArg_ParseTuple(args, "O", &chip_name_obj))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);

	l = PyList_New(0);

	i = 0;
	while (TRUE) {
		feature = (sensors_feature *)sensors_get_features(chip_name, &i);
		if (feature == NULL)
			break;

		feature_obj = _Feature_New(feature);
		PyList_Append(l, (PyObject *)feature_obj);
		Py_DECREF(feature_obj);
	}

	return l;
}


PyDoc_STRVAR(get_all_subfeatures__doc__,
"get_all_subfeatures(chip_name, feature)  ->  [{Subfeature}, {Subfeature}, ...]\n\n\
Wrapper for sensors_get_all_subfeatures.\n\n\
");

static PyObject *get_all_subfeatures(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj;
	sensors_chip_name *chip_name;
	PyObject *feature_obj;
	sensors_feature *feature;
	Subfeature *subfeature_obj;
	sensors_subfeature *subfeature;
	PyObject *l;
	int i;

	if (! PyArg_ParseTuple(args, "OO", &chip_name_obj, &feature_obj))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	if (! _PyObject_TypeRequire(feature_obj, &FeatureType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);
	feature = Feature_get_data((Feature *)feature_obj);

	l = PyList_New(0);

	i = 0;
	while (TRUE) {
		subfeature = (sensors_subfeature *)sensors_get_all_subfeatures(
							chip_name, feature, &i);
		if (subfeature == NULL)
			break;

		subfeature_obj = _Subfeature_New(subfeature);
		PyList_Append(l, (PyObject *)subfeature_obj);
		Py_DECREF(subfeature_obj);
	}

	return l;
}


PyDoc_STRVAR(get_subfeature__doc__,
"get_subfeature(chip_name, feature, type)  ->  {Subfeature}\n\n\
Wrapper for sensors_get_subfeature.\n\n\
");

static PyObject *get_subfeature(PyObject *self, PyObject *args)
{
	PyObject *chip_name_obj;
	sensors_chip_name *chip_name;
	PyObject *feature_obj;
	sensors_feature *feature;
	sensors_subfeature_type subfeature_type;
	sensors_subfeature *subfeature;

	if (! PyArg_ParseTuple(args, "OOi", &chip_name_obj, &feature_obj,
							&subfeature_type))
		return NULL;

	if (! _PyObject_TypeRequire(chip_name_obj, &ChipNameType))
		return NULL;

	if (! _PyObject_TypeRequire(feature_obj, &FeatureType))
		return NULL;

	chip_name = ChipName_get_data((ChipName *)chip_name_obj);
	feature = Feature_get_data((Feature *)feature_obj);

	subfeature = (sensors_subfeature *)sensors_get_subfeature(
					chip_name, feature, subfeature_type);

	if (subfeature == NULL) {
		PyErr_SetString(PyExc_IOError,
				"sensors_get_subfeature returned NULL");
		return NULL;
	}

	return (PyObject *)_Subfeature_New(subfeature);
}


static PyMethodDef libsensors_methods[] = {
	{"init", (PyCFunction) init, METH_VARARGS, init__doc__},
	{"cleanup", (PyCFunction) cleanup, METH_NOARGS, cleanup__doc__},
	{"parse_chip_name", (PyCFunction) parse_chip_name,
			METH_VARARGS, parse_chip_name__doc__},
	{"get_adapter_name", (PyCFunction) get_adapter_name,
			METH_VARARGS, get_adapter_name__doc__},
	{"get_label", (PyCFunction) get_label, METH_VARARGS, get_label__doc__},
	{"get_value", (PyCFunction) get_value, METH_VARARGS, get_value__doc__},
	{"set_value", (PyCFunction) set_value, METH_VARARGS, set_value__doc__},
	{"do_chip_sets", (PyCFunction) do_chip_sets,
			METH_VARARGS, do_chip_sets__doc__},
	{"get_detected_chips", (PyCFunction) get_detected_chips,
			METH_VARARGS, get_detected_chips__doc__},
	{"get_features", (PyCFunction) get_features,
			METH_VARARGS, get_features__doc__},
	{"get_all_subfeatures", (PyCFunction) get_all_subfeatures,
			METH_VARARGS, get_all_subfeatures__doc__},
	{"get_subfeature", (PyCFunction) get_subfeature,
			METH_VARARGS, get_subfeature__doc__},
	{NULL, NULL, 0, NULL}
};


PyDoc_STRVAR(libsensors__doc__,
"libsensors bindings.\n\n\
See libsensors(3) and/or www.lm-sensors.org for API documentation.\n\
This Python API is a relatively thin wrapper around the C API.\n\n\
");

PyMODINIT_FUNC initlibsensors(void)
{
	PyObject *mod;

        if (PyType_Ready(&BusIdType) < 0)
                return;

        if (PyType_Ready(&ChipNameType) < 0)
                return;

        if (PyType_Ready(&FeatureType) < 0)
                return;

        if (PyType_Ready(&SubfeatureType) < 0)
                return;

	mod = Py_InitModule3("libsensors", libsensors_methods,
						libsensors__doc__);

	if (mod == NULL)
		return;

	Py_INCREF(&BusIdType);
	PyModule_AddObject(mod, "BusId", (PyObject *)(&BusIdType));

	Py_INCREF(&ChipNameType);
	PyModule_AddObject(mod, "ChipName", (PyObject *)(&ChipNameType));

	Py_INCREF(&FeatureType);
	PyModule_AddObject(mod, "Feature", (PyObject *)(&FeatureType));

	Py_INCREF(&SubfeatureType);
	PyModule_AddObject(mod, "Subfeature", (PyObject *)(&SubfeatureType));

#ifdef PYLIBSENSORS_VERSION
	PyModule_AddStringConstant(mod, "__version__", PYLIBSENSORS_VERSION);
#endif

	PyModule_AddStringConstant(mod, "libsensors_version",
						libsensors_version);

	PyModule_AddIntConstant(mod, "API_VERSION", SENSORS_API_VERSION);

	PyModule_AddIntConstant(mod, "CHIP_NAME_PREFIX_ANY",
					(int) SENSORS_CHIP_NAME_PREFIX_ANY);
	PyModule_AddIntConstant(mod, "CHIP_NAME_ADDR_ANY",
					SENSORS_CHIP_NAME_ADDR_ANY);

	PyModule_AddIntConstant(mod, "BUS_TYPE_ANY", SENSORS_BUS_TYPE_ANY);
	PyModule_AddIntConstant(mod, "BUS_TYPE_I2C", SENSORS_BUS_TYPE_I2C);
	PyModule_AddIntConstant(mod, "BUS_TYPE_ISA", SENSORS_BUS_TYPE_ISA);
	PyModule_AddIntConstant(mod, "BUS_TYPE_PCI", SENSORS_BUS_TYPE_PCI);
	PyModule_AddIntConstant(mod, "BUS_TYPE_SPI", SENSORS_BUS_TYPE_SPI);
	PyModule_AddIntConstant(mod, "BUS_TYPE_VIRTUAL",
					SENSORS_BUS_TYPE_VIRTUAL);
	PyModule_AddIntConstant(mod, "BUS_TYPE_ACPI", SENSORS_BUS_TYPE_ACPI);
	PyModule_AddIntConstant(mod, "BUS_TYPE_HID", SENSORS_BUS_TYPE_HID);
	PyModule_AddIntConstant(mod, "BUS_NR_ANY", SENSORS_BUS_NR_ANY);
	PyModule_AddIntConstant(mod, "BUS_NR_IGNORE", SENSORS_BUS_NR_IGNORE);

	PyModule_AddIntConstant(mod, "MODE_R", SENSORS_MODE_R);
	PyModule_AddIntConstant(mod, "MODE_W", SENSORS_MODE_W);
	PyModule_AddIntConstant(mod, "COMPUTE_MAPPING",
					SENSORS_COMPUTE_MAPPING);

	PyModule_AddIntConstant(mod, "FEATURE_IN", SENSORS_FEATURE_IN);
	PyModule_AddIntConstant(mod, "FEATURE_FAN", SENSORS_FEATURE_FAN);
	PyModule_AddIntConstant(mod, "FEATURE_TEMP", SENSORS_FEATURE_TEMP);
	PyModule_AddIntConstant(mod, "FEATURE_POWER", SENSORS_FEATURE_POWER);
	PyModule_AddIntConstant(mod, "FEATURE_ENERGY", SENSORS_FEATURE_ENERGY);
	PyModule_AddIntConstant(mod, "FEATURE_CURR", SENSORS_FEATURE_CURR);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "FEATURE_HUMIDITY",
					SENSORS_FEATURE_HUMIDITY);
	PyModule_AddIntConstant(mod, "FEATURE_MAX_MAIN",
					SENSORS_FEATURE_MAX_MAIN);
#endif
	PyModule_AddIntConstant(mod, "FEATURE_VID", SENSORS_FEATURE_VID);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "FEATURE_INTRUSION",
					SENSORS_FEATURE_INTRUSION);
	PyModule_AddIntConstant(mod, "FEATURE_MAX_OTHER",
					SENSORS_FEATURE_MAX_OTHER);
#endif
	PyModule_AddIntConstant(mod, "FEATURE_BEEP_ENABLE",
					SENSORS_FEATURE_BEEP_ENABLE);
	PyModule_AddIntConstant(mod, "FEATURE_UNKNOWN",
					SENSORS_FEATURE_UNKNOWN);

	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_INPUT",
					SENSORS_SUBFEATURE_IN_INPUT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_MIN",
					SENSORS_SUBFEATURE_IN_MIN);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_MAX",
					SENSORS_SUBFEATURE_IN_MAX);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_LCRIT",
					SENSORS_SUBFEATURE_IN_LCRIT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_CRIT",
					SENSORS_SUBFEATURE_IN_CRIT);
#endif
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_ALARM",
					SENSORS_SUBFEATURE_IN_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_MIN_ALARM",
					SENSORS_SUBFEATURE_IN_MIN_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_MAX_ALARM",
					SENSORS_SUBFEATURE_IN_MAX_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_BEEP",
					SENSORS_SUBFEATURE_IN_BEEP);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_LCRIT_ALARM",
					SENSORS_SUBFEATURE_IN_LCRIT_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_IN_CRIT_ALARM",
					SENSORS_SUBFEATURE_IN_CRIT_ALARM);
#endif

	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_INPUT",
					SENSORS_SUBFEATURE_FAN_INPUT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_MIN",
					SENSORS_SUBFEATURE_FAN_MIN);
	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_ALARM",
					SENSORS_SUBFEATURE_FAN_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_FAULT",
					SENSORS_SUBFEATURE_FAN_FAULT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_DIV",
					SENSORS_SUBFEATURE_FAN_DIV);
	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_BEEP",
					SENSORS_SUBFEATURE_FAN_BEEP);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_FAN_PULSES",
					SENSORS_SUBFEATURE_FAN_PULSES);
#endif

	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_INPUT",
					SENSORS_SUBFEATURE_TEMP_INPUT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_MAX",
					SENSORS_SUBFEATURE_TEMP_MAX);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_MAX_HYST",
					SENSORS_SUBFEATURE_TEMP_MAX_HYST);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_MIN",
					SENSORS_SUBFEATURE_TEMP_MIN);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_CRIT",
					SENSORS_SUBFEATURE_TEMP_CRIT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_CRIT_HYST",
					SENSORS_SUBFEATURE_TEMP_CRIT_HYST);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_LCRIT",
					SENSORS_SUBFEATURE_TEMP_LCRIT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_EMERGENCY",
					SENSORS_SUBFEATURE_TEMP_EMERGENCY);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_EMERGENCY_HYST",
					SENSORS_SUBFEATURE_TEMP_EMERGENCY_HYST);
#endif
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_ALARM",
					SENSORS_SUBFEATURE_TEMP_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_MAX_ALARM",
					SENSORS_SUBFEATURE_TEMP_MAX_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_MIN_ALARM",
					SENSORS_SUBFEATURE_TEMP_MIN_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_CRIT_ALARM",
					SENSORS_SUBFEATURE_TEMP_CRIT_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_FAULT",
					SENSORS_SUBFEATURE_TEMP_FAULT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_TYPE",
					SENSORS_SUBFEATURE_TEMP_TYPE);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_OFFSET",
					SENSORS_SUBFEATURE_TEMP_OFFSET);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_BEEP",
					SENSORS_SUBFEATURE_TEMP_BEEP);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_EMERGENCY_ALARM",
					SENSORS_SUBFEATURE_TEMP_EMERGENCY_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_TEMP_LCRIT_ALARM",
					SENSORS_SUBFEATURE_TEMP_LCRIT_ALARM);
#endif

	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_AVERAGE",
					SENSORS_SUBFEATURE_POWER_AVERAGE);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_AVERAGE_HIGHEST",
					SENSORS_SUBFEATURE_POWER_AVERAGE_HIGHEST);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_AVERAGE_LOWEST",
					SENSORS_SUBFEATURE_POWER_AVERAGE_LOWEST);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_INPUT",
					SENSORS_SUBFEATURE_POWER_INPUT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_INPUT_HIGHEST",
					SENSORS_SUBFEATURE_POWER_INPUT_HIGHEST);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_INPUT_LOWEST",
					SENSORS_SUBFEATURE_POWER_INPUT_LOWEST);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_CAP",
					SENSORS_SUBFEATURE_POWER_CAP);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_CAP_HYST",
					SENSORS_SUBFEATURE_POWER_CAP_HYST);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_MAX",
					SENSORS_SUBFEATURE_POWER_MAX);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_CRIT",
					SENSORS_SUBFEATURE_POWER_CRIT);
#endif
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_AVERAGE_INTERVAL",
					SENSORS_SUBFEATURE_POWER_AVERAGE_INTERVAL);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_ALARM",
					SENSORS_SUBFEATURE_POWER_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_CAP_ALARM",
					SENSORS_SUBFEATURE_POWER_CAP_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_MAX_ALARM",
					SENSORS_SUBFEATURE_POWER_MAX_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_POWER_CRIT_ALARM",
					SENSORS_SUBFEATURE_POWER_CRIT_ALARM);
#endif

	PyModule_AddIntConstant(mod, "SUBFEATURE_ENERGY_INPUT",
					SENSORS_SUBFEATURE_ENERGY_INPUT);

	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_INPUT",
					SENSORS_SUBFEATURE_CURR_INPUT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_MIN",
					SENSORS_SUBFEATURE_CURR_MIN);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_MAX",
					SENSORS_SUBFEATURE_CURR_MAX);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_LCRIT",
					SENSORS_SUBFEATURE_CURR_LCRIT);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_CRIT",
					SENSORS_SUBFEATURE_CURR_CRIT);
#endif
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_ALARM",
					SENSORS_SUBFEATURE_CURR_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_MIN_ALARM",
					SENSORS_SUBFEATURE_CURR_MIN_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_MAX_ALARM",
					SENSORS_SUBFEATURE_CURR_MAX_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_BEEP",
					SENSORS_SUBFEATURE_CURR_BEEP);
#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_LCRIT_ALARM",
					SENSORS_SUBFEATURE_CURR_LCRIT_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_CURR_CRIT_ALARM",
					SENSORS_SUBFEATURE_CURR_CRIT_ALARM);
#endif

#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_HUMIDITY_INPUT",
					SENSORS_SUBFEATURE_HUMIDITY_INPUT);
#endif

	PyModule_AddIntConstant(mod, "SUBFEATURE_VID", SENSORS_SUBFEATURE_VID);

#if SENSORS_API_VERSION > 0x430
	PyModule_AddIntConstant(mod, "SUBFEATURE_INTRUSION_ALARM",
					SENSORS_SUBFEATURE_INTRUSION_ALARM);
	PyModule_AddIntConstant(mod, "SUBFEATURE_INTRUSION_BEEP",
					SENSORS_SUBFEATURE_INTRUSION_BEEP);
#endif

	PyModule_AddIntConstant(mod, "SUBFEATURE_BEEP_ENABLE",
					SENSORS_SUBFEATURE_BEEP_ENABLE);

	PyModule_AddIntConstant(mod, "SUBFEATURE_UNKNOWN",
					SENSORS_SUBFEATURE_UNKNOWN);
}
