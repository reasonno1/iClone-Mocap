import math

def smoothList(list,degree=10,strippedXs=False):
    if (degree == 0):
        return list
    if strippedXs==True: return Xs[0:-(len(list)-(len(list)-degree+1))]  
    smoothed=[0]*(len(list)-degree+1)  
    for i in range(len(smoothed)):  
        smoothed[i]=sum(list[i:i+degree])/float(degree)  
    return smoothed  

def smoothListTriangle(list,degree=5,strippedXs=False):  
    if (degree == 0):
        return list
    weight=[]  
    window=degree*2-1  
    smoothed=[0.0]*(len(list)-window) 
    for x in range(1,2*degree):weight.append(degree-abs(degree-x)) 
    s=weight
    for i in range(len(smoothed)):  
        lst = list[i:i+window]
        aaa = [x*y for x,y in zip(lst,s)] 
        smoothed[i] = sum(aaa)/float(sum(s))

    return smoothed  

def smoothListGaussian(list,degree=5,strippedXs=False):
    if (degree == 0):
        return list
    window=degree*2-1  
    w = [1.0]*window
    weightGauss=[]  
    
    for i in range(window):  
        i=i-degree+1  
        frac=i/float(window)  
        gauss = 1/(math.exp((4*(frac))**2)) 
        weightGauss.append(gauss)  
        
    w = [x*y for x,y in zip(weightGauss,w)] 

    smoothed=[0.0]*(len(list)-window)  
    for i in range(len(smoothed)):  
        lst = list[i:i+window]
        aaa = [x*y for x,y in zip(lst,w)] 
        smoothed[i] = sum(aaa)/float(sum(w))
    return smoothed  