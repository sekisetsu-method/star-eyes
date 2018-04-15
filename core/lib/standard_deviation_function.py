'''
HOW IT WORKS:
1. derive the simple average of the numbers
2. for each number subtract the mean and square the result
3. work out the mean of those squared differences
4. return the square root of the squared differences
'''
import math
import cmath

def getMean(pNumberSet):
	tmpTotal = 0
	tmpCounter = 0

	for n in pNumberSet:
		tmpTotal += n
		tmpCounter+=1
	return tmpTotal/tmpCounter


def getStandardDeviation(pNumberSet):
	tmpMean = getMean(pNumberSet)

	tmpNewList = []
	for n in pNumberSet:
		tmpCalc = cmath.sqrt(n - tmpMean)
		tmpNewList.append(tmpCalc)

	tmpMeanSquares = getMean(tmpNewList)

	return cmath.sqrt(tmpMeanSquares)

# test it out...
# foo = [1,2,3,4,5,6,7,8,9,1,5,6,3,6,7,0,3,5,5,3,2]
# print(getMean(foo))
# print(getStandardDeviation(foo))
