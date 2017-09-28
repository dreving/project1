from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
from mvnaiveanalyze import mvnaiveanalyze as analyze


test = 'Test1.csv'
(data, BrakeStrength) = collect(300, test)
compData = arrange(data, BrakeStrength, test)
# p = analyze(compData, 10, True)
# print(p)
