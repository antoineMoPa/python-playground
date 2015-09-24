import matplotlib.pyplot as plt
import numpy as np

def integral(e):
    # definition
    # sum of area of
    sum=0
    t = len(e)
    sum = np.sum(e)
        
    return sum

def derivative(e):
    # definition:
    # lim dx -> 0 ((f(x+dx) - f(x))/dx)
    dt = 2
    t = len(e) - 1
    if(t <= dt):
        dt = t

    if(dt == 0):
        return 0
    
    return (e[t] - e[t-dt])/dt

def u(t,e):
    kp=0.05  # 0.01
    ki=0.005  # 0.009
    kd=1  # 0.05

    return (
        kp * e[t] +
        ki * integral(e) +
        kd * derivative(e)
    )


def simulate():
    t = 0
    ts = []
    mv = []
    sp = []
    e = []
    
    for t in range(0,1000):
        if(t < 20):
            sp.append(0)
        else:
            sp.append(10)
        
        ts.append(t)
        if(t > 0):
            current_val = mv[t-1]
        else:
            current_val =  0
            
        e.append(sp[t] - current_val)
        measured = 0
        if(t > 0):
            measured = mv[t-1]

        mv.append(measured + u(t,e))

    return ts,mv,sp,e
        
ts,mv,sp,e = simulate()
plt.plot(mv,label="Measured Value (simulated)")
plt.plot(sp,label="Set Point",color="orange")
plt.legend()
plt.xlim(0,1000)
plt.ylim(0,15)
plt.show()
