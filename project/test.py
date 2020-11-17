# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:24:46 2020

@author: theor
"""

test1 = "tcp://127.0.0.1:2000"
test2 = "tcp://127.0.0.1:2001"
test3 = "tcp://128.0.0.1:2000"

def toInt( someString ):
    charList = []
    valueList = []
    for c in someString:
        charList.append(c)
        valueList.append(ord(c))
    print(sum(valueList))
    strList = [str(x) for x in valueList]
    concat = int("".join(strList))
    print(concat)
    return concat

def hashfn( num ):
    x = num % 360
    a = 24601 % 360
    b = 1347 % 360
    print(x,a,b)
    return (a*x + b) % 360