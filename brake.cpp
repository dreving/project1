// brake.cpp
#include <Python.h>
#include "C:/Program Files (x86)/Ingenia/MCLIB/includes/MCLIB.h"
#include <iostream>
#include "C:/Program Files (x86)/Ingenia/MCLIB/includes/MotionController.h"
#include "C:/Program Files (x86)/Ingenia/MCLIB/includes/MCLIBDefinitions.h"
#include "C:/Program Files (x86)/Ingenia/MCLIB/includes/MCLIBEnums.h"
#include "C:/Program Files (x86)/Ingenia/MCLIB/includes/INode.h"



/* Docstrings */
static char module_docstring[] =
    "This module provides an interface for the Nebula Controller using C++.";
static char initNebula_docstring[] =
    "Initializes Nebula controller in Torque mode and passes reference";
static char setTorque_docstring[] =
    "Sets Nebula specified in first argument to percentage of rated torque (int, tenth of a percent) given in second argument";
static char close_docstring[] =
    "Closes all Nebula Communication and frees memory";
static char readCurrent_docstring[] = 
    "Reads the actual current sent to the brake";
/* Available functions */

static PyObject *initNebula(PyObject *self);
static PyObject *setTorque(PyObject *self, PyObject *args);
static PyObject *close(PyObject *self, PyObject *args);
static PyObject *readCurrent(PyObject *self, PyObject *args);
/* Module specification */
static PyMethodDef module_methods[] = {
    {"initNebula", (PyCFunction)initNebula, METH_NOARGS, initNebula_docstring},
    {"setTorque", (PyCFunction)setTorque, METH_VARARGS, setTorque_docstring},
    {"close", (PyCFunction)close, METH_VARARGS, close_docstring},
    {"readCurrent", (PyCFunction)readCurrent, METH_VARARGS, readCurrent_docstring},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "brake_implement",
    module_docstring,
    -1,
    module_methods,
};

/* Initialize the module */
PyObject *PyInit_brake_implement(void)
{
    PyObject *m = PyModule_Create(&moduledef);
    /*if (m == NULL) {
        PyErr_SetString(PyExc_TypeError, "parameter must be callable");
        return NULL; 
    } */
    return m;

}


// Perform scan to update the connected devices
static PyObject *initNebula(PyObject * self)
{
    try{
	MCLIB::Init();

    // Load Serial Driver Libary
    MCLIB::LoadLib(MCLIB::DRIVER_SERIAL_RS232);

    MCLIB::ScanDevices();
      
    // Get the devices vector pointer
    vector<MCLIB::IDevice*>* pDevices = pDevices = MCLIB::GetDevices();

    // Iterate over the devices connected
    uint32_t numberOfDevices = pDevices->size();
    for (int i = 0; i < numberOfDevices; i++) {

        try {
    /*
    QStringList strlistDevices;
    for (uint32_t i = 0; i < numberOfDevices; i++)
    {
        TDeviceInfo deviceInfo;
        TDeviceInfo* pDeviceInfo = &deviceInfo;
        // Get the device information to show the friendly name to the user interface
        pDeviceInfo = pDevices->at(i)->GetInfo();
        strlistDevices << QString::fromUtf8(pDeviceInfo->friendlyName.c_str());
    }
    */
    // Get the index from the device selected
    // int index = strlistDevices.indexOf(item);

    // Get the channels for the selected device
    //
    vector<MCLIB::IChannel*>* pChannels = pDevices->at(i)->GetChannels();

    // Select the current channel
    
        MCLIB::IChannel* currentChannel = pChannels->at(0);
    
    // Close the communication to ensure that its not opened
    currentChannel->Close();

    // Open the communication with the first channel
    currentChannel->Open(NULL, MCLIB::BAUDRATE_1M);

    // Scan nodes over the first channel
    currentChannel->ScanNodes(NULL, 250);

    // Get list of nodes from the first channel
    vector<MCLIB::INode*>* pNodes = currentChannel->GetNodes();

     
    // Store the ponter to the Ingenia drive
    MCLIB::INode* ingeniaDrive = pNodes->at(0);

    // Enable Motor
    ingeniaDrive->GetMotionController()->EnableMotor();

    ingeniaDrive->GetMotionController()->SetModeOfOperation(MCLIB::DRIVE_MODE_PROFILE_TORQUE);
    // ingeniaDrive->GetMotionController()->SetTargetTorque(40);
    PyObject* Drive = PyLong_FromVoidPtr(ingeniaDrive);
    PyObject* Channel = PyLong_FromVoidPtr(currentChannel);
    PyObject* ret = Py_BuildValue("(OO)",Channel,Drive);
    return ret;
} catch (...) {;}
}
PyErr_SetString(PyExc_RuntimeError,
                    "Nebula Controller Not Found");
        return NULL;
    } catch (...) {
        PyErr_SetString(PyExc_RuntimeError,
                    "Unknown Initialization Error");
        return NULL;

    }
}



static PyObject *setTorque(PyObject * self, PyObject *args)
{
	//set up variables to import from Python
    PyObject* lngDrive;
	MCLIB::INode* Drive;
	int16_t target; //percentage of rated torque
    //void* ptr;
	//assign arguments to variables
    try { 
	if (!PyArg_ParseTuple(args, "Oi", &lngDrive,&target))
        return NULL;
    Drive = (MCLIB::INode*) PyLong_AsVoidPtr(lngDrive);
    } catch (...) {
        PyErr_SetString(PyExc_RuntimeError,
                    "Error (Nebula): Error Connecting to Controller to Set Torque");
        return NULL; }
    
    
    //Py_DECREF(lngDrive)
    //Drive = MCLIB::INode* (ptr);
   // Drive = ptr;
    // target = target *10;
    try {
	Drive->GetMotionController()->SetTargetTorque(target);
	Py_RETURN_NONE; } catch (...) {
        PyErr_SetString(PyExc_RuntimeError,
                    "Error (Nebula): Error Setting Torque");
        return NULL; }

    
}

static PyObject *readCurrent(PyObject * self, PyObject *args)
{
    //set up variables to import from Python
    PyObject* lngDrive;
    MCLIB::INode* Drive;
    int16_t torque;
    try {
    if (!PyArg_ParseTuple(args, "O", &lngDrive))
        return NULL;
    
    Drive = (MCLIB::INode*) PyLong_AsVoidPtr(lngDrive);
    //Py_DECREF(lngDrive)
    //Drive = MCLIB::INode* (ptr);
   // Drive = ptr;
    // target = target *10;
} catch (...) { 
    PyErr_SetString(PyExc_RuntimeError,
                    "Error (Nebula): Error Connecting to Controller to Read Current");
        return NULL; }
try{
    torque = Drive->GetMotionController()->GetActualTorque();
    return Py_BuildValue("i",torque);
    } catch (...) {
        PyErr_SetString(PyExc_RuntimeError,
                    "Error (Nebula): Error Reading Current");
        return NULL; }
}

static PyObject *close(PyObject * self, PyObject *args) {
    PyObject* lngDrive;
    MCLIB::INode* Drive;
    PyObject* lngChannel;
    MCLIB::IChannel* Channel;
    try {
    if (!PyArg_ParseTuple(args, "OO", &lngChannel, &lngDrive)) {
        PyErr_SetString(PyExc_RuntimeError,
                    "Nebula Controller Not Found");
        return NULL;
    }

    Drive = (MCLIB::INode*) PyLong_AsVoidPtr(lngDrive);
    Channel = (MCLIB::IChannel*) PyLong_AsVoidPtr(lngChannel);
    
    Drive->GetMotionController()->DisableMotor();
    Channel->Close();
    MCLIB::LibUnload(MCLIB::DRIVER_SERIAL_RS232);
    MCLIB::Close();
    Py_DECREF(lngDrive);
    Py_DECREF(lngChannel);
    Py_RETURN_NONE; } catch (...) {
        PyErr_SetString(PyExc_RuntimeError,
                    "Error (Nebula): Error Closing Controller");
        return NULL; }
}
