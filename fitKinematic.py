import numpy,math,utils,minuit

###########################
class linearHadronicTop(object) :
    '''Fit three jets to the hypothesis t-->bqq.

    Index 0 is the b-jet.
    Resolutions are expected in units of sigma(pT)/pT.'''

    def chi2(self, key = None) :
        if key==None : return sum( [self.chi2(key) for key in ["J","W","T"]])
        elif key=="J": return sum([ d*d*r for d,r in zip( self.J.delta, self.J.invRes2 ) ])
        elif key=="W": return self.W.invWidth2 * ( self.W.mass - (self.J.fitted[1] + self.J.fitted[2]).M() )**2
        elif key=="T": return self.T.invWidth2 * ( self.T.mass - sum( self.J.fitted, utils.LorentzV()).M() )**2

    def __init__(self, jetP4s, jetResolutions, massT = 172.0, widthT = 13.1/2, massW = 80.4, widthW = 2.085/2 ) :
        assert len(jetP4s) == 3 == len(jetResolutions), "Please specify 3 and only 3 jets."
        J,W,T = tuple( utils.vessel() for i in range(3) )

        J.raw = jetP4s
        J.invRes2 = [ r**(-2) for r in jetResolutions ]
        m2 = [(J.raw[i]+J.raw[j]).M2() for i,j in [tuple(set([0,1,2])-set([k])) for k in [0,1,2]]]

        T.rawMass2 = sum( jetP4s, utils.LorentzV()).M2()
        T.mass = massT ;   T.invWidth2 = widthT**(-2) ;   T.R = massT / math.sqrt(T.rawMass2) ; T.L = 0.5 * T.invWidth2 / T.rawMass2
        W.mass = massW ;   W.invWidth2 = widthW**(-2) ;   W.R = massW / math.sqrt(m2[0])      ; W.Lambda =  W.invWidth2 * m2[0]     

        for item in ["J","T","W","m2"] : setattr(self,item,eval(item))
        J.delta = numpy.linalg.solve( self.matrix(), -self.constants() )
        J.fitted = [ r * (1+d) for r,d in zip(J.raw,J.delta) ]

    def matrix(self) :
        m = []
        m.append([     self.element(0,i) for i in range(3)       ])
        m.append([ m[0][1], self.element(1,1), self.element(1,2) ])
        m.append([ m[0][2],            m[1,2], self.element(2,2) ])
        return numpy.array(m)

    def constants(self) : return numpy.array([self.constant(i) for i in range(3)])
    def constant(self, i, key = None):
        if key==None : return sum( [self.constant(i,key) for key in ["W","T"]] )
        elif key=="W": return ( 1 - self.W.R ) * self.W.Lambda
        elif key=="T": return ( 1 - self.T.R ) * self.T.invWidth2 * (sum(self.m2)-self.m2[i])

    def element(self,i,j, key = None) :
        if key==None : return sum( [self.element(i,j,key) for key in ["J","W","T"]] )
        elif key=="J": return [ 0, 2*self.J.invRes2[i] ][i==j]
        elif key=="W": return self.W.Lambda * [ 1-0.5*self.W.R,  0.5*self.W.R ][i==j] if i and j else 0
        elif key=="T":
            T = self.T
            sumM2 = sum(self.m2)
            m2_i = sumM2 - self.m2[i]
            m2_j = sumM2 - self.m2[j]
            term2 = [(1-T.R) * T.invWidth2 * (sumM2 - self.m2[i] - self.m2[j] ) , 0 ][i==j]
            return term2  +  m2_i * m2_j * T.L * T.R


###########################
class linearWbTop(object) :
    '''Fit the b jet in the hypothesis t-->bW'''

    def chi2(self) :
        return ( self.b.invRes2 * self.b.delta**2 +
                 self.topInvWidth2 * (self.massTop - (self.b.fitted+self.W).M())**2 )

    def __init__(self,bjet,bresolution,W,
                 massTop=172.0,widthTop=13.1/2) :

        rawTop2 = (b+W).M2()
        topInvWidth2 = widthTop**(-2)

        R = massTop / math.sqrt(rawTop2)
        A = (rawTop2 - W.M2()) * topInvWidth2
        B = rawTop2 * topInvWidth2

        b = utils.vessel()
        b.raw = bjet
        b.invRes2 = bresolution**(-2)
        b.delta = A*(R-1) / (2*bjet.invRes2 + 0.5*R*A*A/B)
        b.fitted = (1+bjet.delta) * b.raw

        for item in ['b','W','massTop','topInvWidth2'] : setattr(self,item,eval(item))

###########################
class minuitMuNuW(object) :

    def __init__(self, muP4, nuX, nuY, covErr, massW=80.4) :
        self.nuP4 = utils.LorentzV().SetPxPyPzE(nuX,nuY,0.0,math.sqrt(nuX**2+nuY**2))
        for item in ['muP4','covErr','massW'] : setattr(self,item,eval(item))
        self.fittedNu = (utils.LorentzV(),utils.LorentzV())

        if 0 <= self.discriminent() : self.solve()
        else : self.fit()

    def discriminant(self) :
        self.nuT2 = nuP4.Perp2()

        self.P = self.massW**2 + 2 * self.muP4.Dot(self.nuP4)
        self.muZ = muP4.Z()
        self.muT2 = muP4.Perp2()
        self.muE2 = muP4.E()**2
        self.discriminant = 1 + 4*(muT2/muZ**2)*(1 - 4*muE2*nuT2 / P**2)
        return self.discriminant

    def solve(self) :
        sqrtDisc = math.sqrt(self.discriminant)
        base = 0.5 * self.muZ * self.P / self.muT2
        x,y = self.nuP4.x(),self.nuP4.y()
        zplus = base*(1+sqrtDisc)
        zminus = base*(1-sqrtDisc)
        self.fittedNu[0].SetPxPyPzE(x,y, zplus,  math.sqrt(x*x+y*y+zplus*zplus))
        self.fittedNu[1].SetPxPyPzE(x,y, zminus, math.sqrt(x*x+y*y+zminus*zminus))
        self.chi2 = 0.0

    def fit(self) :
        phi = 0.5 * math.arctan(self.covErr[1]/(self.covErr[0]-self.covErr[2])) if self.covErr[0]!=self.covErr[2] else 0.25*math.pi * (-1 if self.covErr[1]<0 else 1)
        R = r.RotationZ(phi)
        rNuP4 = R(self.NuP4)
        rMuP4 = R(self.MuP4)
        cos = R.CosAngle()
        sin = R.SinAngle()
        sigma2x = self.covErr[0]*cos**2 - 2*self.covErr[1]*cos*sin + self.covErr[2]*sin**2
        sigma2y = self.covErr[1]*sin**2 + 2*self.covErr[1]*cos*sin + self.covErr[2]*cos**2
        rnuX,rnuY = rNuP4.x(),rNuP4.y()
        rmuX,rmuY = rMuP4.x(),rMuP4.y()

        def fnc(deltax,deltay,Lambda) :
            return (
                (deltax*rnuX)**2/sigma2x +
                (deltay*rnuY)**2/sigma2y +
                Lambda * (1+4*(self.muT2/self.muZ**2) * (1 - 4*self.muE2 * ((1+deltax)**2 * rnuX*rnuX + (1+deltay)**2 * rnuY*rnuY) / (self.P + 2*(rmuX*rnuX*deltaX+rmuY*rnuY*deltaY))**2 )  )
                )

        m = minuit.minuit(fnc, deltax=(0.,0.01), deltay=(0.,0.01))
        if m.mnexcm("MIGRAD", 500, 1) : m.printStatus()
        fitted = m.values()
        
        fitNuX = (1+fitted['deltax'])*rnux
        fitNuY = (1+fitted['deltay'])*rnuy
        P = self.massW**2 + 2 * (rmuX*fitNuX + rmuY*fitNuY)
        fitNuZ = 0.5 * self.muZ * P / self.muT2
        self.fittedNu[0].SetPxPyPzE(fitNuX,fitNuY,fitNuZ,math.sqrt(fitNuX**2+fitNuY**2+fitNuZ**2))

        R.Invert()
        self.fittedNu = tuple( R(self.fittedNu[0]), None)
        self.chi2 = fnc(**fitted)
        
