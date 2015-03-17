# r2 coefficient. I know there must be libraries, but
# I wanted to try to code it.
# source:
# http://en.wikipedia.org/wiki/Coefficient_of_determination
import numpy as np
import math

def r2(data,f):
    ys = data[1,:]
    xs = data[0,:]
    meany = 1 / data.shape[1] * np.sum(ys)
    sstot = np.sum(np.power(ys - meany,2))
    ssres = np.sum(np.power(ys - f(xs),2))
    r2 = 1 - ssres / sstot
    return meany

def test_r2():
    def f(x):
        return x*2
    data = np.random.randint(100,size=(2,100))
    
    print(r2(data,f))
    
test_r2()

