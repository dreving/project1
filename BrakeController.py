import numpy as np


class Controller(object):
    def __init__(self, svm, scaler, risep, fallp):
        self.prevcmd = [0,0]
        self.torques = [1.25,1.25]
        self.svm = svm
        self.scaler = scaler
        self.risep = risep
        self.fallp = fallp

    def model(self, torques):
        cmds = np.full(len(torques), np.nan)
        labels = np.full(len(torques), np.nan)
        for i in range(len(torques)):
            sample = np.asarray([[self.prevcmd[-1],self.torques[-1]]])
            sample.reshape(1, -1)
            sample = self.scaler.transform(sample)
            if self.svm.predict(sample) < 0:
                cmds[i] = np.polyval(self.risep, torques[i])
                labels[i] = -1
            else:
                cmds[i] = np.polyval(self.fallp, torques[i])
                labels[i] = 1
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
        return (cmds, labels)

    def reset(self):
        self.prevcmd = [0,0]
        self.torques = [1.25,1.25]
