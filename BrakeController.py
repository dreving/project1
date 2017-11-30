import numpy as np


class Controller(object):
    def __init__(self, svm, scaler, risep, riseXL, fallp, fallXL, boundP):
        self.prevcmd = [0.0, 0.0]
        self.torques = [0.0, 0.0]
        self.svm = svm
        self.scaler = scaler
        self.riseXL = riseXL
        self.risep = risep
        self.fallXL = fallXL
        self.fallp = fallp
        self.boundP = boundP

    def qmodel(self, torques):
        cmds = np.full(len(torques), np.nan)
        labels = np.full(len(torques), np.nan)
        torques = np.asarray(torques, dtype=np.float64)
        for i in range(len(torques)):
            sample = np.asarray([[self.prevcmd[-1], self.torques[-1]]])
            sample.reshape(1, -1)
            # sample = self.scaler.transform(sample)
            datapoint = np.asarray(
                [torques[i], torques[i] - self.torques[-1]]).T
            # print (np.shape(datapoint))
            if np.polyval(self.boundP, self.prevcmd[-1]) >= self.torques[-1]:
                cmds[i] = self.riseEval(datapoint)
                labels[i] = -1
            else:
                cmds[i] = self.fallEval(datapoint)
                labels[i] = 1
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
        return (cmds, labels)

    def model(self, torques):
        cmds = np.full(len(torques), np.nan)
        labels = np.full(len(torques), np.nan)
        torques = np.asarray(torques, dtype=np.float64)
        for i in range(len(torques)):
            sample = np.asarray([[self.prevcmd[-1], self.torques[-1]]])
            sample.reshape(1, -1)
            sample = self.scaler.transform(sample)
            datapoint = np.asarray(
                [torques[i], torques[i] - self.torques[-1]]).T
            # print (np.shape(datapoint))
            if self.svm.predict(sample) < 0:
                cmds[i] = self.riseEval(datapoint)
                labels[i] = -1
            else:
                cmds[i] = self.fallEval(datapoint)
                labels[i] = 1
            self.prevcmd.append(cmds[i])
            self.torques.append(torques[i])
        return (cmds, labels)

    def riseEval(self, data):
        p = self.risep
        val = p[0]
        # print(type(data[0]))
        # global xParamLength
        xPL = self.riseXL
        # print(xPL)
        for i in range(1, len(p)):
            i // xPL
            # coefficients of ascending degree
            # print(p[i])
            # print(data[int(i >= xPL)
            # ]**(int(i >= xPL) + (i) % xPL))
            val += p[i] * data[int(i >= xPL)
                               ]**(int(i >= xPL) + (i) % xPL)
            # print(val)
        return val

    def fallEval(self, data,):
        p = self.fallp
        val = p[0]
        # global xParamLength
        xPL = self.fallXL
        # print(xPL)
        for i in range(1, len(p)):
            i // xPL
            # coefficients of ascending degree
            val += p[i] * data[int(i >= xPL)
                               ]**(int(i >= xPL) + (i) % xPL)
        return val

    def reset(self):
        self.prevcmd = [0, 0]
        self.torques = [1.25, 1.25]
