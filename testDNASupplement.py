import numpy as np
import os
from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
import matplotlib.pyplot as plt
import pickle


def cutOffInd(data, fromBack=False):
    # returns array value whose next value differs by more than two
    # use on array of indexes of interest
    # used in finding where None and nans end in DNA torque range
    if len(data) == 0:
        return None
    if fromBack:
        data = data[::-1]
        if len(data) - data[0] > 2:
            return None
    else:
        if data[0] > 1:
            return None
    for i in range(len(data) - 1):
        if abs(data[i + 1] - data[i]) > 2:
            return data[i]
    return data[-1]

# starts from a point and step in specified direction to base
def tumble(peak, base, dec, trials):
    tumList = []
    for t in range(trials):
        if peak > base:
            tumList.extend(np.arange(peak, base - 1, -dec))
        else:
            tumList.extend(np.arange(peak, base + 1, dec))
        dec += 1
    return tumList

# creates full list of tumbles (with starting 0 and)
def tumList(lowEnd, upEnd, tumLength, resol, dec, trials):
        # randomize order
    tumList = []
    ladderpts = np.arange(lowEnd, upEnd, resol)
    fromFallList = np.vstack((ladderpts, np.full(len(ladderpts), -1)))
    fromRiseList = np.vstack((ladderpts, np.full(len(ladderpts), 1)))
    riseFallList = np.vstack((fromFallList.T, fromRiseList.T))
    # print(riseFallList)
    np.random.seed(44)
    np.random.shuffle(riseFallList)
    # print(riseFallList)
    for pt in range(len(riseFallList[:, 0])):
        tum = [0]
        peak = riseFallList[pt, 0]
        if riseFallList[pt, 1] == 1:
            base = max(peak - tumLength, 0)
            tum.extend(tumble(peak, base, dec, trials))
            tumList.append(tum)
            # return list of lists, flatten later
        else:
            tum = [100]
            base = min(peak + tumLength, 100)
            tum.extend(tumble(peak, base, dec, trials))
            tumList.append(tum)
    return tumList


# set metadata
brakeID = 1742
breed = 'DNATest'
calTestBreed = 'PG188Test'
testID = '3'
test = breed + str(testID)
currdir = 'data/' + str(brakeID) + '/' + breed + \
    '/' + breed + str(testID) + '/'

# name of test from which to extract curve parameters
paramTestID = 2
paramdir = 'data/' + str(brakeID) + '/' + calTestBreed + \
    '/' + calTestBreed + str(paramTestID) + '/'


# set test parameters
fuzz = 0.01 # percentage from one curve to the other to form curve threshold
resol = 5 # distance between starting commands for each
steps = 2 # percentage points to step down within each tumble
torqueList = tumList(10, 95, 30, resol, steps, 1)
brakeStrength = []
for tum in torqueList:
    brakeStrength.extend(tum)


# collect brake Data
if not os.path.exists(currdir):
    os.makedirs(currdir)
if (not os.path.exists(currdir + test + '.csv')):
    (data, brakeStrength) = collect(brakeStrength, currdir, test,
                                    timeLength=10,
                                    mode='warmup', breed=breed, stepwise=True)

data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                           test + '.csv', delimiter=',', comments='# ')
# arrange brake Data
compData = arrange(data, brakeStrength, currdir, test, )
# import curve information
with open(paramdir + 'curveP.pickle', 'rb') as g:
    (riseP, fallP) = pickle.load(g)


tumInd = 0
toFallTable = []
toRiseTable = []

# parse data into sets of tumbles based on index
for tum in torqueList:
    # use curve information to determine linear points
    dna_pts = []

    curveChange = False
    # True means rising to falling curve
    riseToFall = (tum[1] >= tum[-1])
    # print(riseToFall)
    # iterate points in tumble list until you cross appropriate threshold
    # (other curve plus)
    # then stop and analyze those points
    for pt in range(len(tum)):
        if pt == 0:
            continue
        cmd = compData[tumInd + pt, 0]
        torque = compData[tumInd + pt, -1]
        # add points to new formatted array for analysis
        dna_pts.append([cmd, torque])

        if riseToFall:
            #left rising curve
            if cmd < (1 - fuzz) * np.polyval(riseP, torque) + fuzz * np.polyval(fallP, torque):
                # if cmd < (np.polyval(riseP, torque + fuzz) - fuzz):
                curveChange = True
            # reached falling curve
            if cmd < (1 - fuzz) * np.polyval(fallP, torque) + fuzz * np.polyval(riseP, torque):
                # if cmd < (np.polyval(fallP, torque - fuzz) + fuzz):
                break
        else:
            # left falling curve
            if cmd > (1 - fuzz) * np.polyval(fallP, torque) + fuzz * np.polyval(riseP, torque):
                # if cmd > (np.polyval(fallP, torque - fuzz) + fuzz):
                curveChange = True
            # reached rising curve
            if cmd > (1 - fuzz) * np.polyval(riseP, torque) + fuzz * np.polyval(fallP, torque):
                # if cmd > (np.polyval(riseP, torque + fuzz) - fuzz):
                break

    tumInd += len(tum)
    dna_pts = np.asarray(dna_pts) 
    # print(np.shape(dna_pts))

# Make table of linear slopes for valid points, None for points
# that do not change curves, or NaN for two few points for analysis
# (treated for analysis land)
    # if points do not change curve, label None 
    if not(curveChange):
        p = None
    # if not enough points for linear fit, label NaN
    elif len(dna_pts[:, 0]) < 2:
        p = np.nan
    else:
        p = np.polyfit(dna_pts[:, 0], dna_pts[:, 1], 1)
        p = p[0]
    if riseToFall:
        toFallTable.append((dna_pts[0, 1], p))
    else:
        toRiseTable.append((dna_pts[0, 1], p))
# save slope points to a table
# sort in order of torque
toFallTable.sort(key=lambda tup: tup[0])
toRiseTable.sort(key=lambda tup: tup[0])



# plot fuzzy curves to show boundaries
fig = plt.figure()
torRange = np.linspace(0, 115, 100)
plt.plot(np.polyval(riseP, torRange), torRange, 'b')
plt.plot(np.polyval(fallP, torRange), torRange, 'r')
plt.plot((1 - fuzz) * np.polyval(fallP, torRange) + fuzz *
         np.polyval(riseP, torRange), torRange, 'r--')
plt.plot((1 - fuzz) * np.polyval(riseP, torRange) + fuzz *
         np.polyval(fallP, torRange), torRange, 'b--')
# plt.show()


'''
Analysis of points:
Iterate over points in order:
Identify points that are None and NaN, and figure out 
how far into the list they extend (index closest to the middle that is not
more than one away from a chain of the same point)
Round those points based on resol, to form Fix and Shift points
Fix- Changing direction stays on same curve (too low current on low curve)
Shift- Changing Direction = Instanteous Change
Fix and Shift default to impossible points if no points are found
A polynomial fit is then done for the list of valid slopes (y) and the 
torque values, to make a general slope equation
'''
noneInd = []
nanInd = []
toRiseData = []
for pt in range(len(toRiseTable)):
    if toRiseTable[pt][1] is None:
        noneInd.append(pt)
    elif np.isnan(toRiseTable[pt][1]):
        nanInd.append(pt)
    else:
        toRiseData.append(toRiseTable[pt])

toRiseData = np.asarray(toRiseData)
toRiseP = np.polyfit(toRiseData[:, 0], toRiseData[:, 1], 3)

upperFixIND = cutOffInd(noneInd, fromBack=True)
if upperFixIND is None:
    upperFix = 150
else:
    upperFix = np.floor(toRiseTable[upperFixIND][0] / resol) * resol

upperShiftIND = cutOffInd(nanInd)
if upperShiftIND is None:
    upperShift = -10
else:
    upperShift = np.ceil(toRiseTable[upperShiftIND][0] / resol) * resol

#  repeat for lines from rising curve to falling curve ###################
noneInd = []
nanInd = []
toFallData = []


for pt in range(len(toFallTable)):
    if toFallTable[pt][1] is None:
        noneInd.append(pt)
    elif np.isnan(toFallTable[pt][1]):
        nanInd.append(pt)
    else:
        toFallData.append(toFallTable[pt])

toFallData = np.asarray(toFallData)
toFallP = np.polyfit(toFallData[:, 0], toFallData[:, 1], 3)
print(noneInd)
print(nanInd)
lowerFixIND = cutOffInd(noneInd)
if lowerFixIND is None:
    lowerFix = -10
else:
    lowerFix = np.ceil(toRiseTable[lowerFixIND][0] / resol) * resol
lowerShiftIND = cutOffInd(nanInd, fromBack=True)
if lowerShiftIND is None:
    lowerShift = 150
else:
    lowerShift = np.floor(toRiseTable[lowerShiftIND][0] / resol) * resol


# quick test plots of fits, save in supertuple
plt.figure()
plt.scatter(toRiseData[:, 0], toRiseData[:, 1])
plt.plot(torRange, np.polyval(toRiseP, torRange))
plt.show()
plt.figure()
plt.scatter(toFallData[:, 0], toFallData[:, 1])
plt.plot(torRange, np.polyval(toFallP, torRange))
plt.show()
print(lowerFix)
print(lowerShift)
print(upperShift)
print(upperFix)

# return two slope generating functions, and cutoff values
DNAP = (toFallP, toRiseP, lowerFix, lowerShift, upperFix, upperShift)
with open(currdir + 'DNAP' + '.pickle', 'wb') as f:
    pickle.dump(DNAP, f)

