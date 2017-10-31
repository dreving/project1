import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
import pickle
from naiveanalyze import naiveanalyze as analyze
import time

with open('data/' + 'BackupController' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
# iris = datasets.load_iris()
# X = iris.data
# y = iris.target

# X = X[y != 0, :2]
# y = y[y != 0]

# n_sample = len(X)

# np.random.seed(0)
# order = np.random.permutation(n_sample)
# X = X[order]
# y = y[order].astype(np.float)

# X_train = X[:int(.9 * n_sample)]
# y_train = y[:int(.9 * n_sample)]
# X_test = X[int(.9 * n_sample):]
# y_test = y[int(.9 * n_sample):]

# fit the model
# for fig_num, kernel in enumerate(('linear', 'rbf', 'poly')):
    # clf = svm.SVC(kernel=kernel, gamma=10)
    # clf.fit(X_train, y_train)

plt.figure()
plt.clf()
# plt.scatter(X[:, 0], X[:, 1], c=y, zorder=10, cmap=plt.cm.Paired,
#             edgecolor='k', s=20)

# Circle out the test data
# plt.scatter(X_test[:, 0], X_test[:, 1], s=80, facecolors='none',
#             zorder=10, edgecolor='k')

# plt.axis('tight')
x_min = 0.0
x_max = 100.0
y_min = 0
y_max = 120.0

XX, YY = np.mgrid[x_min:x_max:200j, y_min:y_max:200j]
# scale here brah
data = np.c_[XX.ravel(), YY.ravel()]
sData = scaler.transform(data)
Z = clf.decision_function(sData)

# Put the result into a color plot
Z = Z.reshape(XX.shape)
plt.pcolormesh(XX, YY, Z > 0, cmap=plt.cm.Paired)
plt.contour(XX, YY, Z, colors=['k', 'k', 'k'],
            linestyles=['--', '-', '--'], levels=[-.5, 0, .5])
m = 110 / 90
b1 = 10
b2 = -20

boundpts = np.multiply((abs(Z) < 0.10), (-b1 < m * XX - YY)) > 0
boundpts = np.multiply(boundpts, (-b2 > m * XX - YY)) > 0
# print(boundpts)
Xpts = XX[boundpts]
Ypts = YY[boundpts]
boundData = np.vstack((Xpts, Ypts))
# p= analyze(boundData.T,4,True)
# with open('data/' + 'boundP' + '.pickle', 'wb') as f:
#     pickle.dump(p, f)
with open('data/' + 'boundP' + '.pickle', 'rb') as g:
    p = pickle.load(g)
cmdRange = np.linspace(0, 100, 100)
bpts = np.polyval(p, cmdRange)
plt.pcolormesh(XX, YY, Z > 0, cmap=plt.cm.Paired)
plt.plot(cmdRange, bpts, 'g^')
# plt.title(kernel)
# Make equation based on where Z==0
plt.show()



#Both O(n) wrt inputs
#Polynomial 20x faster
set1 = np.ones((1000000, 2))
set2 = np.ones((10000000, 2))
start = time.time()
clf.predict(set1)
svm1 = time.time() - start
start = time.time()
clf.predict(set2)
svm2 = time.time() - start
start = time.time()
np.polyval(p, set1[:, 1])
pv1 = time.time() - start
start = time.time()
np.polyval(p, set2[:, 1])
pv2 = time.time() - start
print((svm1, svm2, pv1, pv2))
print((svm2 / svm1, pv2 / pv1))
