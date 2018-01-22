import numpy as np
from scipy.optimize import fsolve

'''
This is the brake Controller Class for determining proper brake command
from desired torque. Initialize the class with the parameters of fit
for the lower and upper curve
See TorqueCommandTest.py for examples
'''


class Controller(object):
    def __init__(self, riseP, fallP, toFallP=(-0.0002, 0.027, 0.1705),
                 toRiseP=(-4E-05, - 0.0004, 1.2663),
                 lowerFix=25, lowerShift=150,
                 upperFix=90, upperShift=-10):
        self.prevcmd = [0.0]
        self.torques = [0.0]
        self.states = [1]
        self.limbo_ends = (None, None)
        self.limbo_slope = None
        self.riseP = riseP
        self.fallP = fallP
        self.toRiseP = toRiseP
        self.toFallP = toFallP
        self.upperFix = upperFix  # point above which you stay on upper curve
        self.upperShift = upperShift  # point below which you insta switch to lower curve
        self.lowerFix = lowerFix  # point below which you stay on lower curve
        self.lowerShift = lowerShift  # point above which you insta switch to upper curve
    # linear transitions (limbo) between curves

    def model_DNA(self, torques, *args):
        cmds = np.full(len(torques), np.nan)
        states = np.full(len(torques), np.nan)
        torques = np.asarray(torques, dtype=np.float64)
        for i in range(len(torques)):
            # get state
            state = self.get_state(torques[i], self.torques[-1])
            states[i] = state
            # eval torque command for state
            if state == -1:
                cmds[i] = self.fallEval(torques[i])
            elif state == 1:
                cmds[i] = self.riseEval(torques[i])
            else:
                cmds[i] = self.point_slope_x(self.limbo_slope,
                                             self.limbo_ends[0][0],
                                             self.limbo_ends[0][1], torques[i])
            # log lists
            self.states.append(state)
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
        return (cmds, states)

    # just switch between the two curves just based on if new torque
    # is higher or lower
    def model_2lane(self, torques, *args):
        cmds = np.full(len(torques), np.nan)
        states = np.full(len(torques), np.nan)
        torques = np.asarray(torques, dtype=np.float64)
        for i in range(len(torques)):
            if torques[i] >= self.torques[-1]:
                cmds[i] = self.riseEval(torques[i])
                states[i] = 1
            else:
                cmds[i] = self.fallEval(torques[i])
                states[i] = -1
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
            self.states.append(states[i])
        return (cmds, states)

    # lower curve only
    def model_low(self, torques, *args):
        cmds = np.full(len(torques), np.nan)
        states = np.full(len(torques), np.nan)
        torques = np.asarray(torques, dtype=np.float64)
        for i in range(len(torques)):
            sample = np.asarray([[self.prevcmd[-1], self.torques[-1]]])
            sample.reshape(1, -1)
            cmds[i] = self.riseEval(torques[i])
            states[i] = 1
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
            self.states.append(1)
        return (cmds, states)

    def riseEval(self, data):
        return np.polyval(self.riseP, data)

    def fallEval(self, data,):
        return np.polyval(self.fallP, data)

    # helper functions for DNA controller
    def find_slope(self, torque, dir):
        if dir < 0:
            m = np.polyval(self.toFallP, torque)
        else:
            m = np.polyval(self.toRiseP, torque)
        return m

    # solve point slope equation for command at torque y
    def point_slope_x(self, m, x1, y1, y):
        if m != 0:
            x = x1 + (y - y1) / m
        else:
            x = None
        return x

    # solve point slope equation for torque at command x
    def point_slope_y(self, m, x1, y1, x):
        y = y1 + m * (x - x1)
        return y

    # determine which curve (or linear transition) you are on
    def get_state(self, torque, prevtorque):
        state = self.states[-1]

        # on upper curve decision
        if state == -1:
            if torque < prevtorque or prevtorque > self.upperFix:
                return -1
            if (torque > prevtorque) and (prevtorque < self.upperShift):
                return 1
            else:
                (lowRung, highRung) = self.make_limbo_state(
                    1, self.find_slope(prevtorque, 1),
                    prevtorque, self.fallEval(prevtorque))
                if torque <= highRung[1]:
                    return 0
                else:
                    return 1

        # limbo
        elif state == 0:
            # print(self.limbo_ends[0][1])
            if torque < self.limbo_ends[0][1]:

                return -1
            if torque > self.limbo_ends[1][1]:
                return 1
            else:
                return 0

        # lower
        elif state == 1:
            if torque > prevtorque or prevtorque < self.lowerFix:
                return 1
            else:
                (lowRung, highRung) = self.make_limbo_state(-1,
                                                            self.find_slope(
                                                                prevtorque, -1),
                                                            prevtorque,
                                                            self.prevcmd[-1])
                if torque >= lowRung[1]:
                    return 0
                else:
                    return -1

        else:
            print('illegal state')
            return None

    def make_limbo_state(self, direction, m, torque, command):
        """ return tuple of two torque values, between which the change
        in torque would be linear with command """
        self.limbo_slope = m
        if direction < 0:
            def f(y): return np.polyval(self.fallP, y) - \
                self.point_slope_x(m, command, torque, y)
            lowTorque = fsolve(f, torque)
            lowCMD = self.fallEval(lowTorque)
            self.limbo_ends = ((lowCMD, lowTorque), (command, torque))
            return ((lowCMD, lowTorque), (command, torque))
        else:
            def f(x): return np.polyval(self.riseP, x) - \
                self.point_slope_x(m, command, torque, x)
            highTorque = fsolve(f, torque)
            # point_slope_x(m, command, torque, highTorque)
            highCMD = self.riseEval([highTorque])
            self.limbo_ends = ((command, torque), (highCMD, highTorque))
            return ((command, torque), (highCMD, highTorque))

    def make_rise_state(self):
        self.states.append(1)
        self.clear_limbo()

    def make_fall_state(self):
        self.states.append(-1)
        self.clear_limbo()

    def clear_limbo(self):
        self.limbo_slope = None
        self.limbo_ends = ((None, None), (None, None))

    # for all
    def reset(self):
        self.prevcmd = [0]
        self.torques = [0.0]
        self.states = [1]
        self.clear_limbo()

    def exportLog(self):
        return (np.vstack((self.torques, self.prevcmd, self.states))).T
