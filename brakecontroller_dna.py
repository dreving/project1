import numpy as np
from scipy.optimize import fsolve


class Controller(object):
    def __init__(self, svm, scaler, riseP, riseXL, fallP, fallXL, boundP):
        self.prevcmd = [0.0]
        self.torques = [0.0]
        self.states = [1]
        self.limbo_ends = (None, None)
        self.limbo_slope = None
        self.riseXL = riseXL
        self.riseP = riseP[::-1]
        self.fallXL = fallXL
        self.fallP = fallP[::-1]
        self.upperFix = 90  # point above which you stay on upper curve
        self.lowerFix = 25  # point below which you stay on lower curve

    def model(self, torques, *args):
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

    def riseEval(self, data):
        return np.polyval(self.riseP,data)
        # p = self.riseP
        # val = p[0]
        # xPL = self.riseXL
        # for i in range(1, len(p)):
        #     val += p[i] * data**(int(i >= xPL) + (i) % xPL)
        # return val

    def fallEval(self, data,):
        return np.polyval(self.fallP,data)
        # p = self.fallP
        # val = p[0]
        # xPL = self.fallXL
        # for i in range(1, len(p)):
        #     val += p[i] * data**(int(i >= xPL) + (i) % xPL)
        # return val

    def find_slope(self, torque, dir):
        if dir < 0:
            m = -0.0002 * torque**2 + 0.027 * torque + 0.1705
        else:
            m = -4E-05 * torque**2 - 0.0004 * torque + 1.2663
        return m

    def point_slope_x(self, m, x1, y1, y):
        if m != 0:
            x = x1 + (y - y1) / m
        else:
            x = None
        return x

    def point_slope_y(self, m, x1, y1, x):
        y = y1 + m * (x - x1)
        return y

    def get_state(self, torque, prevtorque):
        state = self.states[-1]

        # on upper curve decision
        if state == -1:
            if torque < prevtorque or prevtorque > self.upperFix:
                return -1
            else:
                (lowRung, highRung) = self.make_limbo_state(
                    1,self.find_slope(prevtorque,1), prevtorque, self.fallEval(prevtorque))
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
                # print(self.find_slope(prevtorque,-1))
                (lowRung, highRung) = self.make_limbo_state(-1,self.find_slope(prevtorque,-1), prevtorque,
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
        in torque would be linear with current """
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

    def reset(self):
        self.prevcmd = [0]
        self.torques = [0.0]
        self.states = [1]
        self.clear_limbo()

    def exportLog(self):
        return (np.vstack((self.torques, self.prevcmd, self.states))).T
