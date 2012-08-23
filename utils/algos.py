import array,math,itertools,operator
from itertools import groupby
try: import numpy as np
except: pass
#####################################
def unionProbability(indPs) :
    indPs = filter(None, indPs)
    return sum([ (-1)**r * sum([reduce(operator.mul,ps,1) for ps in itertools.combinations(indPs, r+1)]) for r in range(len(indPs))])
#####################################
def topologicalSort(paths) :
    '''Algorithm first described by Kahn (1962).

    See http://en.wikipedia.org/wiki/Topological_ordering'''
    edges = set(sum([zip(p[:-1],p[1:]) for p in paths],[]))
    sources,sinks = zip(*edges) if edges else ([],[])
    singles = set(p[0] for p in paths if len(p)==1)
    seeds = list( (set(sources)|singles) - set(sinks) )
    ordered = []
    while seeds :
        ordered.append(seeds.pop())
        for edge in filter(lambda e: e[0]==ordered[-1], edges) :
            edges.remove(edge)
            if not any(edge[1]==e[1] for e in edges) :
                seeds.append(edge[1])
    assert not edges, "graph described by paths contains a cycle: no partial ordering possible.\n edges: %s"%str(edges)
    return ordered
#####################################
def quadraticInterpolation(fZ, fX, fY) :
    # http://cmslxr.fnal.gov/lxr/source/CondFormats/JetMETObjects/src/Utilities.cc?v=CMSSW_3_8_5#099
    # Quadratic interpolation through the points (x[i],y[i]). First find the parabola that
    # is defined by the points and then calculate the y(z).
    D = [0.0]*4; a = [0.0]*3
    D[0] = fX[0]*fX[1]*(fX[0]-fX[1])+fX[1]*fX[2]*(fX[1]-fX[2])+fX[2]*fX[0]*(fX[2]-fX[0])
    D[3] = fY[0]*(fX[1]-fX[2])+fY[1]*(fX[2]-fX[0])+fY[2]*(fX[0]-fX[1])
    D[2] = fY[0]*(pow(fX[2],2)-pow(fX[1],2))+fY[1]*(pow(fX[0],2)-pow(fX[2],2))+fY[2]*(pow(fX[1],2)-pow(fX[0],2))
    D[1] = fY[0]*fX[1]*fX[2]*(fX[1]-fX[2])+fY[1]*fX[0]*fX[2]*(fX[2]-fX[0])+fY[2]*fX[0]*fX[1]*(fX[0]-fX[1])
    if (D[0] != 0) :
        a[0] = D[1]/D[0]
        a[1] = D[2]/D[0]
        a[2] = D[3]/D[0]
    else :
        a[0] = 0.0
        a[1] = 0.0
        a[2] = 0.0
    return a[0]+fZ*(a[1]+fZ*a[2])
#####################################
def edgesRebinned( hist, targetUncRel, pivot = 0, offset = 0 ) :
    '''Symmetric rebinning around the pivot, such that every bin has a
    minimum relative uncertainty.'''

    def uncRel(x) : return (-1 if not x else
                             1e6 if not x[0] else
                             math.sqrt(x[1])/x[0])
    def sumUncRel(_x) :
        v,e2 = zip(*_x)
        return uncRel((sum(v),sum(e2)))

    def blocks(x) :
        for leftmost in range(1,len(x)) :
            if sumUncRel(x[:leftmost]) >  targetUncRel :  continue
            if sumUncRel(x[leftmost:]) >  targetUncRel :  return (x,)
            return (x[:leftmost],) + blocks(x[leftmost:])
        return (x,)

    nBins = hist.GetNbinsX()
    edges = [hist.GetBinLowEdge(i) for i in range(1,nBins+2)]
    vals  = [hist.GetBinContent(i) for i in range(1,nBins+2)]
    errs2 = [hist.GetBinError(i)**2 for i in range(1,nBins+2)]
    iPivot_L = edges.index(pivot) if pivot in edges else edges.index(max([e for e in edges if e<pivot]))
    iPivot_R = iPivot_L if pivot in edges else iPivot_L+1

    R = zip(vals,errs2)[iPivot_R:]
    L = zip(vals,errs2)[:iPivot_L][::-1]
    RL = [max(el,ar, key = uncRel) for el,ar in itertools.izip_longest(L,R)]

    blockLens = [offset] + [len(b) for b in blocks(RL[offset:-1])]
    blockShifts = [sum(blockLens[:i+1]) for i in range(len(blockLens))]
    iEdges = sorted( set( [0,len(edges)-1] + 
                          [min(len(edges)-1, iPivot_R + i) for i in blockShifts[:len(R)]] +
                          [max(0,            iPivot_L - i) for i in blockShifts[:len(L)]] ))
    return array.array('d',[edges[i] for i in iEdges])
#####################################
def dilution( A, B, N = None) :
    '''Power of distribution to distinguish populations A and B, given observed distribution N'''
    A = np.double(A) / sum(A)
    B = np.double(B) / sum(B)
    N = np.double(N) / sum(N) if N is not None else (A+B) / 2

    p = A / np.maximum(1e-50, A+B)
    D = (1-2*p)**2
    return N.dot(D)
#####################################
def longestPrefix(strings) :
    return ( "" if not (len(strings[0]) and
                        all (len(s) and
                             strings[0][0]==s[0] for s in strings[1:])) else
             (strings[0][0] + longestPrefix([s[1:] for s in strings])))

def contract(strings) :
    lpfx = longestPrefix(strings)
    tails = [s[len(lpfx):] for s in strings]
    return lpfx + ( '' if len(tails)==1 else
                    "{%s}"%(','.join([ contract(list(ctails))
                                       for c,ctails in groupby( tails,
                                                                key = lambda s: next(iter(s),''))])))

def pairs(l = []) :
    out = []
    for i,left in enumerate(l[:-1]) :
        for right in l[1+i:] :
            out.append( (left,right) )
    return out
