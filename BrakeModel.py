import numpy as np


class BrakeModel(object):
    def __init__(self, svm, risep, fallp):
        self.prevcmd = [0]
        self.torques = [0]
        self.svm = svm
        self.risep = risep
        self.fallp = fallp

    def model(self, cmds):
        torques = np.full(len(cmds), np.nan)
        for i in range(len(torques)):
            sample = np.asarray([cmds[i], self.prevcmd[-1], self.torques[-1]])
            sample.reshape(1, -1)
            if self.svm.predict(sample) > 0:
                torques[i] = np.polyval(self.risep, cmds[i])
            else:
                torques[i] = np.polyval(self.fallp, cmds[i])
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
        return torques

    def reset(self):
        self.prevcmd = [0]
        self.torque = [0]