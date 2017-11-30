arrangeBrakeData: Function that Takes raw current data and condenses it to average current or torque data
brakeController: class that predicts proper brake command for desired torque based on parameters
CalibrationMotorFunctions: Functions for controlling the motor based on roboclaw library
collectBrakeData: function that issues brake and motor commands for data collection
controlExport: prints out parameters for controller
RiseFallSVM: Functions for building the Support Vector Machine and Labeling the data
StepwiseScript: Script that performs stepwise tests to correlate motor current to brake torque
testBrake: Main Script that performs tests to determine parameters for the controller
TorqueCommandTest: Test that runs tests for controller model that Anthony prescribed
xyFit: Class to handle multi-variable curve fitting, used in determing hysteresis curves