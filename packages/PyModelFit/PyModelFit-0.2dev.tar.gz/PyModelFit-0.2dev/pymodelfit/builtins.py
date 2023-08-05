#Copyright 2008 Erik Tollerud
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
This module contains builtin function models that use the framework of the
:mod:`core` module.
"""

from __future__ import division,with_statement

import numpy as np
#from core import * #includes pi
from core import ParametricModel,FunctionModel,FunctionModel1DAuto, \
                 DatacentricModel1DAuto,FunctionModel2DScalarAuto,register_model
from math import e,pi
from abc import abstractmethod



class ConstantModel(FunctionModel1DAuto):
    """
    The simplest model imaginable - just a constant value.
    """
    def f(self,x,C=0):
        return C*np.ones_like(x)
    
    def derivative(self,x,dx=None):
        if dx is not None:
            return FunctionModel1D.derivative(self,x,dx)
        
        return np.zeros_like(x)
    
    def integrate(self,lower,upper,method=None,**kwargs):
        if method is not None:
            return FunctionModel1D.integrate(self,lower,upper,method,**kwargs)
        
        if 'jac' in kwargs and kwargs['jac'] is not None:
            return FunctionModel1D.integrate(self,lower,upper,**kwargs)
        else:
            return self.C*(upper-lower)
    
class LinearModel(FunctionModel1DAuto):
    """
    :math:`y = mx+b` linear model.
    
    A number of different fitting options are available - the :attr:`fittype`
    attribute determines which type should be used on calls to fitData. It can
    be:
    
    * 'basic' 
        Analytically compute the parameters from simple least-squares form. If
        `weights` are provided they will be interpreted as :math:`1/y_{\\rm
        err}` or :math:`\\sqrt{(x/x_{\\rm err})^2+(y/y_{\\rm err})^2}` if a
        2-tuple.
    * 'yerr': 
        Same as weighted version of basic, but `weights` are interpreted as
        y-error instead of inverse.
    * 'fiterrxy': 
        Allows errors in both x and y using the chi^2 from the fitexy algorithm
        from numerical recipes. `weights` must be a 2-tuple (xerr,yerr).
        
    """
    
    def f(self,x,m=1,b=0):
        return m*x+b
    
    def _linearFit(self,x,y,fixedpars=(),weights=None,**kwargs):
        """
        Does least-squares fit on the x,y data
        
        fixint and fixslope can be used to specify the intercept or slope of the 
        fit or leave them free by having fixint or fixslope be False or None
        
        lastfit stores ((m,b),dm,db)
        """  
        if self.fittype == 'basic':
            if weights is None:
                (m,b),merr,berr,dy = self.fitBasic(x,y,
                                          self.m if 'm' in fixedpars else False,
                                          self.b if 'b' in fixedpars else False)
            else:
                fixslope = fixint = None
                if 'm' in fixedpars:
                    fixslope = self.m
                if 'b' in fixedpars:
                    fixint = self.b
                kwargs['fixint'] = fixint
                kwargs['fixslope'] = fixslope
                    
                weights = np.array(weights,copy=False)
                if len(weights.shape) == 2:
                    weights = ((x/weights[0])**2+(y/weights[1])**2)**0.5
                m,b,merr,berr = self.fitWeighted(x,y,1/weights,**kwargs)
        elif self.fittype == 'yerr':
            weights = np.array(weights,copy=False) if weights is not None else None
            if weights is not None and len(weights.shape) == 2:
                weights = weights[1]
            m,b,merr,berr = self.fitWeighted(x,y,weights,**kwargs)
        elif self.fittype == 'fiterrxy':
            if len(fixedpars)>0:
                raise ValueError('cannot fix parameters and do fiterrxy fit')
            if weights is None:
                xerr = yerr = None
            else:
                weights = np.array(weights,copy=False)
                if len(weights.shape)==1:
                    xerr = yerr = 1/(weights*2**-0.5)
                else:
                    xerr,yerr = 1/weights
            m,b = self.fitErrxy(x,y,xerr,yerr,**kwargs)
            merr = berr = None
        else:
            raise ValueError('invalid fittype %s'%self.fittype)
            
        if len(fixedpars)>0:
            if 'b' in fixedpars:
                return ((m,),merr,berr)
            elif 'm' in fixedpars:
                return ((b,),merr,berr)
        else:
            return ((m,b),merr,berr)
    
    _fittypes = {'basic':_linearFit,'yerr':_linearFit,'fiterrxy':_linearFit}
    fittype = 'basic'
    
    def derivative(self,x,dx=None):
        if dx is not None:
            return FunctionModel1D.derivative(self,x,dx)
        
        return np.ones_like(x)*self.m
    
    def integrate(self,lower,upper,method=None,**kwargs):
        if method is not None:
            return FunctionModel1D.integrate(self,lower,upper,method,**kwargs)
        
        m,b = self.m,self.b
        return m*upper*upper/2+b*upper-m*lower*lower/2+b*lower
    
    @staticmethod
    def fitBasic(x,y,fixslope=False,fixint=False):
        """
        Does the traditional fit based on simple least-squares regression for
        a linear model :math:`y=mx+b`.
        
        :param x: x data for the fit
        :type x: array-like
        :param y: y data for the fit
        :type y: array-like
        :param fixslope: 
            If False or None, the best-fit slope will be found.
            Otherwise,specifies the value to assume for the slope.
        :type fixslope: scalar or False or None
        :param fixint: 
            If False or None, the best-fit intercept will be found.
            Otherwise,specifies the value to assume for the intercept.
        :type fixint: scalar or False or None
        
        :returns: ((m,b)),dm,db,dy)
        
        """
        N=len(x) 
        if (fixint is False or fixint is None) and \
           (fixslope is False or fixslope is None):
            if len(y)!=N:
                raise ValueError('data arrays are not same length!')
            sxsq = np.sum(x*x)
            sx,sy = np.sum(x),np.sum(y)
            sxy = np.sum(x*y)
            delta=N*sxsq-sx**2
            m=(N*sxy-sx*sy)/delta
            b=(sxsq*sy-sx*sxy)/delta
            dy=(y-m*x-b).std(ddof=2)
            dm=dy*(sxsq/delta)**0.5 
            db=dy*(N/delta)**0.5 
            
        elif fixint is False or fixint is None:
            m,dm = fixslope,0
            
            b = np.sum(y-m*x)/N 
            
            dy = (y-m*x-b).std(ddof=1)
            #db= sum(dy*dy)**0.5/N
            db = dy
            
        elif fixslope is False or fixslope is None:
            b,db = fixint,0
            
            sx=np.sum(x)
            sxy=np.sum(x*y)
            sxsq=np.sum(x*x)
            m=(sxy-b*sx)/sxsq
            
            dy=(y-m*x-b).std(ddof=1) 
            #dm=(np.sum(x*dy*x*dy))**0.5/sxsq
            dm = dy*sxsq**-0.5
        else:
            raise ValueError("can't fix both slope and intercept")
        
        return np.array((m,b)),dm,db,dy
        
        
    @staticmethod
    def fitWeighted(x,y,sigmay=None,doplot=False,fixslope=None,fixint=None):
        """
        Does a linear weighted least squares fit and computes the coefficients 
        and errors.
        
        :param x: x data for the fit
        :type x: array-like
        :param y: y data for the fit
        :type y: array-like
        :param sigmay: 
            Error/standard deviation on y.  If None, weights are equal.
        :type sigmay: array-like or None
        :param fixslope:
            The value to force the slope to or None to leave the slope free.
        :type fixslope: scalar or None
        :param fixint: 
            The value to force the intercept to or None to leave intercept free.
        :type fixint: scalar or None
        
        :returns: tuple (m,b,sigma_m,sigma_b)
        
        """
        from numpy import array,ones,sum
        if sigmay is None:
            sigmay=ones(len(x))
        else:
            sigmay=array(sigmay)
        if len(x)!=len(y)!=len(sigmay):
            raise ValueError('arrays not matching lengths')
        N=len(x)
        x,y=array(x),array(y)
        
        w=1.0/sigmay/sigmay
        
        #B=slope,A=intercept
        if (fixint is None or fixint is False) and \
           (fixslope is None or fixslope is False):
            delta=sum(w)*sum(w*x*x)-(sum(w*x))**2
            A=(sum(w*x*x)*sum(w*y)-sum(w*x)*sum(w*x*y))/delta
            B=(sum(w)*sum(w*x*y)-sum(w*x)*sum(w*y))/delta
            diff=y-A-B*x
            sigmaysq=sum(w*diff*diff)/(sum(w)*(N-2)/N) #TODO:check
            sigmaA=(sigmaysq*sum(w*x*x)/delta)**0.5
            sigmaB=(sigmaysq*sum(w)/delta)**0.5
            
        elif fixint is False or fixint is None:
            B,sigmaB = fixslope,0
            
            A = np.sum(w*(y-B*x))/np.sum(w) 
            
            dy = (y-A-B*x).std(ddof=1)
            sigmaA = dy
            
        elif fixslope is False or fixslope is None:
            A,sigmaA = fixint,0
            
            sx = np.sum(w*x)
            sxy = np.sum(w*x*y)
            sxsq = np.sum(w*x*x)
            B = (sxy-A*sx)/sxsq
            
            dy = (y-B*x-A).std(ddof=1) 
            sigmaB = dy*sxsq**-0.5
        else:
            raise ValueError("can't fix both slope and intercept")
        
        if doplot:
            from matplotlib.pyplot import plot,errorbar,legend
            errorbar(x,y,sigmay,fmt='o',label='Data')
            plot(x,B*x+A,label='Best Fit')
            plot(x,(B+sigmaB)*x+A-sigmaA,label='$1\sigma$ Up')
            plot(x,(B-sigmaB)*x+A+sigmaA,label='$1\sigma$ Down')
            legend(loc=0)
        
        return B,A,sigmaB,sigmaA
    
    def fitErrxy(self,x,y,xerr,yerr,**kwargs):
        """
        Uses the chi^2 statistic
        
        .. math::
           \\frac{(y_{\\rm data}-y_{\\rm model})^2}{(y_{\\rm err}^2+m^2 x_{\\rm err}^2)}`

        to fit the data with errors in both x and y.
        
        :param x: x data for the fit
        :type x: array-like
        :param y: y data for the fit
        :type y: array-like
        :param xerr: Error/standard deviation on x.
        :type xerr: array-like
        :param yerr: Error/standard deviation on y.
        :type yerr: array-like
        
        kwargs are passed into :mod:`scipy.optimize.leastsq`
        
        :returns: best-fit (m,b)
        
        .. note::
            Fitting results are saved to :attr:`lastfit`
            
        """
        from scipy.optimize import leastsq
        if xerr is None and yerr is None:
            def chi(v,x,y,xerr,yerr):
                return y-self.f(x,*v)
        elif xerr is None:
            def chi(v,x,y,xerr,yerr):
                wsqrt = xerr
                return (y-self.f(x,*v))/wsqrt
        elif yerr is None:
            def chi(v,x,y,xerr,yerr):
                wsqrt = yerr
                return (y-self.f(x,*v))/wsqrt
        else:
            def chi(v,x,y,xerr,yerr):
                wsqrt = (yerr**2+(v[0]*xerr)**2)**0.5
                return (y-self.f(x,*v))/wsqrt
        
        kwargs.setdefault('full_output',1)
        self.lastfit = leastsq(chi,(self.m,self.b),args=(x,y,xerr,yerr),**kwargs)
        self.data = (x,y,(xerr,yerr))
        
        self._fitchi2 = np.sum(chi(self.lastfit[0],x,y,xerr,yerr)**2)
        
        return self.lastfit[0]
    
    def pointSlope(self,m,x0,y0):
        """
        Sets model parameters for the given slope that passes through the point.
        
        :param m: slope for the model
        :type m: float
        :param x0: x-value of the point
        :type x0: float
        :param y0: y-value of the point
        :type y0: float
        
        """
        self.m = m
        self.b = y0-m*x0
        
    def twoPoint(self,x0,y0,x1,y1):
        """
        Sets model parameters to pass through two lines (identical behavior
        in fitData).
        
        :param x0: x-value of the first point
        :type x0: float
        :param y0: y-value of the first point
        :type y0: float
        :param x1: x-value of the second point
        :type x1: float
        :param y1: y-value of the second point
        :type y1: float
        """
        self.pointSlope((y0-y1)/(x0-x1),x0,y0)
        
    def distanceToPoint(self,xp,yp):
        """
        Computes the shortest distance from this line to a provided point or
        points. 
        
        The distance is signed in the sense that a positive distance indicates
        the point is above the line (y_point>y_model) while negative is below.
            
        
        :param xp: The x-coordinate of the point(s).
        :type xp: scalar or array-like
        :param yp: The y-coordinate of the point(s). Length must match `xp`.
        :type yp: scalar or array-like
        
        :returns:
            The (signed) shortest distance from this model to the point(s). If
            `xp` and `yp` are scalars, this will be a scalar.  Otherwise, it is
            an array of shape matching `xp` and `yp`.            
        
        """
        isscal = np.isscalar(xp)
        xp = np.array(xp,copy=False)
        yp = np.array(yp,copy=False)
        
        if xp.shape!=yp.shape:
            raise ValueError("distanceToPoint xp and yp shapes don't match")
        
        res = (yp-self(xp))*(self.m**2+1)**-0.5
        if isscal:
            return res.ravel()[0] #regular instead of numpy scalar
        else:
            return res
        
        
    @staticmethod
    def fromPowerLaw(plmod,base=10):
        """
        Takes a PowerLawModel and converts it to a linear model assuming 
        ylinear = log_base(ypowerlaw) and xlinear = log_base(xpowerlaw) 
        
        returns the new LinearModel instance
        """
        if base == 'e' or base == 'ln':
            base = np.exp(1)
        
        logfactor=1/np.log(base)
        
        m = plmod.p
        b = logfactor*np.log(plmod.A)
        
        if plmod.data is not None:
            data = list(plmod.data)
            data[0] = logfactor*np.log(data[0])
            data[1] = logfactor*np.log(data[1])
            
        lmod = LinearModel(m=m,b=b)
        lmod.data = tuple(data)
        return lmod
        
    
class QuadraticModel(FunctionModel1DAuto):
    """
    2-degree polynomial :math:`f(x)=c_2 x^2 + c_1 x + c_0`
    """
    def f(self,x,c2=1,c1=0,c0=0):
        return c2*x*x+c1*x+c0

class PolynomialModel(FunctionModel1DAuto):
    """
    Arbitrary-degree polynomial
    """
    
    paramnames = 'c'
    
    #TODO: use polynomial objects that are only updated when necessary
    def f(self,x,*args): 
        return np.polyval(np.array(args)[::-1],x)
    
    def derivative(self,x,dx=None):
        if dx is not None:
            return FunctionModel1D.derivative(self,x,dx)
        
        return np.polyder(np.array(self.parvals)[::-1])(x)

    def integrate(self,lower,upper,method=None,**kwargs):
        if method is not None:
            return FunctionModel1D.integrate(self,lower,upper,method,**kwargs)
        
        p = np.polyint(np.array(self.parvals)[::-1])
        return p(upper)-p(lower)
    
class FourierModel(FunctionModel1DAuto):
    """
    A Fourier model composed of sines and cosines:
    
    .. math::
        f(x) = \displaystyle\sum\limits_{k=0}^n A_k sin(kx) + B_k cos(kx)
    
    The number of parameters must be even so as to include both terms.
    """
    paramnames = ('A','B')
    #note that A0 has no effect
    
    def f(self,x,*args):
        xr = x.ravel()
        n = len(args)/2
        As = np.array(args[::2]).reshape((n,1))
        Bs = np.array(args[1::2]).reshape((n,1))
        ns = np.arange(len(As)).reshape((n,1))
        res = np.sum(As*np.sin(ns*xr),axis=0)+np.sum(Bs*np.cos(ns*xr),axis=0)
        return res.reshape(x.shape)
#        val = np.empty_like(x)
#        for n,(A,B) in enumerate(zip(args[::2],args[:1:2])):
#            val += A*sin(n*x)+B*cos(n*x)
#        return val

class GaussianModel(FunctionModel1DAuto):
    """
    Normalized 1D gaussian function:
    
    .. math::
        f(x) = \\frac{A}{\\sqrt{2 \\pi \\sigma^2} } e^{\\frac{-(x-\\mu)^2}{2 \\sigma^2}}
        
    """
    def f(self,x,A=1,sig=1,mu=0):
        tsq=(x-mu)*2**-0.5/sig
        return A*np.exp(-tsq*tsq)*(2*pi)**-0.5/sig
    
    def _getPeak(self):
        return self(self.mu)
    
    def _setPeak(self,peakval):
        self.A = 1
        self.A = peakval/self._getPeak()
        
    peak=property(_getPeak,_setPeak,doc='Value of the model at the peak')
    
    __fwhmfactor = 2*(2*np.log(2))**0.5
    def _getFWHM(self):
        return self.sig*self.__fwhmfactor
    def _setFWHM(self,val):
        self.sig = val/self.__fwhmfactor
    FWHM = property(_getFWHM,_setFWHM,doc='Full Width at Half Maximum')
    
        
    def derivative(self,x,dx=None):
        if dx is not None:
            return FunctionModel1D.derivative(self,x,dx)
        
        sig=self.sig
        return self(x)*-x/sig/sig
    
    def integrate(self,lower,upper,method=None,**kwargs):
        if method is not None:
            return FunctionModel1D.integrate(self,lower,upper,method,**kwargs)
        
        if len(kwargs)>0:
            return super(GaussianModel,self).integrate(lower,upper,**kwargs)
        else:
            from scipy.special import erf
            l = (lower-self.mu)/self.sig
            u = (upper-self.mu)/self.sig
            uval = erf(u*2**-0.5)
            lval = erf(-l*2**-0.5)
            return self.A*(uval+lval)/2
        
    @property
    def rangehint(self):
        asig = abs(self.sig) #can't guarantee sigma is positive right now
        return (self.mu-asig*4,self.mu+asig*4)
    
class DoubleGaussianModel(FunctionModel1DAuto):
    """
    Sum of two normalized 1D gaussian functions. Note that fitting often can be
    tricky with this model, as it's easy to find lots of false minima.
    """
    def f(self,x,A=1,B=1,sig1=1,sig2=1,mu1=-0.5,mu2=0.5):
        tsq1=(x-mu1)*2**-0.5/abs(sig1)
        tsq2=(x-mu2)*2**-0.5/abs(sig2)
        return (A*np.exp(-tsq1*tsq1)/sig1+B*np.exp(-tsq2*tsq2)/sig2)*(2*pi)**-0.5
    
    @property
    def rangehint(self):
        asig1,asig2 = abs(self.sig1),abs(self.sig2)
        lower1 = self.mu1-asig1*4
        lower2 = self.mu2-asig2*4
        upper1 = self.mu1+asig1*4
        upper2 = self.mu2+asig2*4
        return(min(lower1,lower2),max(upper1,upper2))
    
    @staticmethod
    def autoDualModel(x,y,taller='A',wider='B',**kwargs):
        """
        Generates and fits a double-gaussian model where one of the peaks is on
        top of the other and much stronger. the taller and wider argument must
        be either 'A' or 'B' for the two components.
        """
        gm=GaussianModel()
        gm.fitData(x,y,**kwargs)
        dgm=DoubleGaussianModel()
        dgm.mu1=dgm.mu2=gm.mu
        if taller == 'A':
            dgm.A=gm.A
            dgm.B=gm.A/2
            dgm.sig1=gm.sig
            if wider =='A':
                dgm.sig2=gm.sig/2
            elif wider =='B':
                dgm.sig2=gm.sig*2
            else:
                raise ValueError('unrecognized wider component')
            
            dgm.fitData(x,y,fixedpars=('mu1','A','sig1'),**kwargs)
        elif taller == 'B':
            dgm.B=gm.A
            dgm.A=gm.A/2
            dgm.sig2=gm.sig
            if wider =='B':
                dgm.sig1=gm.sig/2
            elif wider =='A':
                dgm.sig1=gm.sig*2
            else:
                raise ValueError('unrecognized wider component')
            
            dgm.fitData(x,y,fixedpars=('mu2','B','sig2'),**kwargs)
        else:
            raise ValueError('unrecognized main component')
        
        dgm.fitData(x,y,fixedpars=(),**kwargs)
        return dgm
    
class DoubleOpposedGaussianModel(DoubleGaussianModel):
    """
    This model is a DoubleGaussianModel that *forces* one of the gaussians to
    have negative amplitude and the other positive. A is the amplitude of the
    positive gaussian, while B is always taken to be negative.
    """
    def f(self,x,A=1,B=1,sig1=1,sig2=1,mu1=-0.5,mu2=0.5):
        A,B=abs(A),-abs(B) #TODO:see if we should also force self.A and self.B
        return DoubleGaussianModel.f(self,x,A,B,sig1,sig2,mu1,mu2)
    
class LognormalModel(FunctionModel1DAuto):
    """
    A normalized Lognormal model
    
    .. math::
        f(x) = A (\\sqrt{2\\pi}/\\sigma_{\\rm log}) e^{-(\\log_{\\rm base}(x)-\\mu_{\\rm log})^2/2 \\sigma_{\\rm log}^2}
    
    By default, the 'base' parameter does not vary when fitting, and defaults to
    e (e.g. a natural logarithm).
    
    .. note::
        This model is effectively identical to a :class:`GaussianModel` with
        gmodel.setCall(xtrans='log##') where ## is the base, but is included
        because lognormals are often considered to be canonical.
        
    """
    def f(self,x,A=1,siglog=1,mulog=0,base=e):
        return A*np.exp(-0.5*((np.log(x)/np.log(base)-mulog)/siglog)**2)*(2*pi)**-0.5/siglog
    
    fixedpars = ('base',)
    
    @property
    def rangehint(self):
        return (np.exp(self.mulog-self.siglog*4),np.exp(self.mulog+self.siglog*4))
    
class LorentzianModel(FunctionModel1DAuto):
    r"""
    A standard Lorentzian function (also known as the Cauchy distribution):
    
    .. math::
        \frac{A \Gamma}{\pi [(x-\mu)^2+\Gamma^2]}
        
    """
    def f(self,x,A=1,gamma=1,mu=0):
        return A*gamma/pi/(x*x-2*x*mu+mu*mu+gamma*gamma)
    
    def _getPeak(self):
        return self(self.mu)
    
    def _setPeak(self,peakval):
        self.A = 1
        self.A = peakval/self._getPeak()
        
    peak=property(_getPeak,_setPeak)
    
    @property
    def rangehint(self):
        return(self.mu-self.gamma*6,self.mu+self.gamma*6)
    
class VoigtModel(GaussianModel,LorentzianModel):
    """
    A Voigt model constructed as the convolution of a :class:`GaussianModel` and
    a :class:`LorentzianModel` -- commonly used for spectral line fitting.
    """
    def f(self,x,A=1,sig=0.5,gamma=0.5,mu=0):
        from scipy.special import wofz
        if sig == 0:
            return LorentzianModel.f(self,x,A,sig,mu)
        else:
            w=wofz(((x-mu)+1j*gamma)*2**-0.5/sig)
            return A*w.real*(2*pi)**-0.5/sig
    
    @property
    def rangehint(self):
        halfwidth = 3*(self.gamma+self.sig)
        return(self.mu-halfwidth,self.mu+halfwidth)
            
class ExponentialModel(FunctionModel1DAuto):
    """
    exponential function Ae^(kx)
    """
    def f(self,x,A=1,k=1):
        return A*np.exp(k*x)
    
    @property
    def rangehint(self):
        ak = np.abs(self.k)
        return(-1.5/ak,1.5/ak)
    
class PowerLawModel(FunctionModel1DAuto):
    """
    A single power law model :math:`Ax^p` 
    """
    def f(self,x,A=1,p=1):
        return A*x**p
    
    _fittypes=['linearized']
    fittype = 'leastsq'
    
    def fitLinearized(self,x,y,fixedpars=(),**kwargs):
        """
        just fits the spline with the current s-value - if s is not changed,
        it will execute very quickly after
        """
        lm = LinearModel(m=self.p,b=np.log10(self.A))
        lm.fittype = 'basic'
        logx = np.log10(x)
        logy = np.log10(y)
        
        fixedps = []
        if 'A' in fixedpars:
            fixedps.append('b')
        if 'p' in fixedpars:
            fixedps.append('m')
        
        lm.fitData(logx,logy,tuple(fixedps),**kwargs)
        
        return np.array([10**lm.b,lm.m])
    
    @staticmethod
    def fromLinear(lmod,base=10):
        """
        Takes a LinearModel and converts it to a power law model assuming 
        :math:`y_{\\rm linear} = \\log_{\\rm base}(y_{\\rm powerlaw})` and 
        :math:`x_{\\rm linear} = \\log_{\\rm base}(x_{\\rm powerlaw})` 
        
        :returns: the new :class:`PowerLawModel` instance
        """
        if base == 'e' or base == 'ln':
            base = np.exp(1)
        
        p = lmod.m
        A = base**lmod.b
        
        if lmod.data is not None:
            data = list(lmod.data)
            data[0] = base**data[0]
            data[1] = base**data[1]
        else:
            data = None
            
        plmod = PowerLawModel(p=p,A=A)
        if data is not None:
            plmod.data = tuple(data)
        return plmod
    
class SinModel(FunctionModel1DAuto):
    """
    A trigonometric model :math:`A \\sin(kx+p)`
    """
    def f(self,x,A=1,k=2*pi,p=0):
        return A*np.sin(k*x+p)
    
    def derivative(self,x,dx=None):
        if dx is not None:
            return FunctionModel1D.derivative(self,x,dx)
        
        A,k,p=self.A,self.k,self.p
        return A*k*np.cos(k*x+p)
    
    def integrate(self,lower,upper,method=None,**kwargs):
        if method is not None:
            return FunctionModel1D.integrate(self,lower,upper,method,**kwargs)
        
        A,k,p=self.A,self.k,self.p
        return A*(np.cos(k*lower+p)-np.cos(k*upper+p))/k
    
class TwoPowerModel(FunctionModel1DAuto):
    """
    A model that smoothly transitions between two power laws.
    
    The turnover point is given by the parameter `xs`. `a` is the inner slope,
    `b` is the outer slope, and `A` is the overall normalization:
    
    .. math::
        A x^a (x+xs)^{b-a}
        
    """
    def f(self,x,A=1,xs=1,a=1,b=2):
        return A*((x+xs)**(b-a))*(x**a)
    
    def _getFxs(self):
        A,xs,a,b=self.A,self.xs,self.a,self.b
        return A*xs**b*2**(b-a)
    
    def _setFxs(self,fxs):
        xs,a,b=self.xs,self.a,self.b
        self.A=fxs*xs**-b*2**(a-b)
    
    fxs=property(fget=_getFxs,fset=_setFxs,doc="""The function's value at 
                 `xs`- this maps one-to-one onto the `A` parameter, so setting
                 `fxs` also sets `A` (and vice versa).""")
    
    
class TwoSlopeModel(FunctionModel1DAuto):
    """
    This model smoothly transitions from linear with one slope to linear with
    a different slope. It is the linearized equivalent of TwoPowerModel:
    
    .. math::
        a (x-xs)+(b-a) log_{\\rm base}(1+{\\rm base}^{x-xs})+C
    
    By default, the 'base' parameter does not vary when fitting.
    """
    
    fixedpars = ('base',)
    
    def f(self,x,a=1,b=2,C=0,xs=0,base=e):
        z = x-xs
        return a*z+(b-a)*np.log(1+base**z)/np.log(base)+C
    
    @property
    def rangehint(self):
        return(self.xs-3,self.xs+3)
    
class TwoSlopeDiscontinuousModel(FunctionModel1DAuto):
    """
    This model discontinuously transitions between two slopes and is linear
    everywhere else.
    
    `a` is the slope for small x and `b` for large x, with `xs` the transition point.
    The intercept `C` is the intercept for :math:`y_a=ax+C`.
    """
    def f(self,x,a=1,b=2,C=0,xs=0):
        xl = x.copy()
        xl[x>xs]  = 0
        xu = x.copy()
        xu[x<=xs]  = 0
        return a*xl+b*xu+(a*xs-b*xs)*(xu!=0)+C
    
    @property
    def rangehint(self):
        return(self.xs-3,self.xs+3)
        
class TwoSlopeATanModel(FunctionModel1DAuto):
    """
    This model transitions between two asymptotic slopes with an additional
    parameter that allows for a variable transition region size. The functional
    form is
    
    .. math::
        y = (x-x_0) \\frac{a+b}{2} +
                    \\frac{  s - (x-x_0) (a-b)}{\\pi}
                    \\arctan \\left (\\frac{x-x0}{w} \\right) + c
    
    `a` is the slope for small x, `b` for large x, `c` is the value at x=x0,
    `x0` is the location of the transition, `w` is the width of the transition,
    and `s` is the amount of y-axis offset that occurs at the transition
    (positive for left-to-right).
    
    """
    #no-S form from old docs
    #.. math::
    #    y = (x-x_0) \\left[ \\frac{a+b}{2} - 
    #                \\frac{a-b}{\\pi} \\arctan(\\frac{x-x_0}{w})\\right] + c
    #alternative representation of no-S form for docs:
    #.. math::
    #    y = \\frac{a (x-x_0)}{\\pi} \\left(\\frac{\\pi}{2}-\\arctan(\\frac{x-x_0}{w}) \\right) +
    #        \\frac{b (x-x_0)}{\\pi} \\left(\\frac{\\pi}{2}+\\arctan(\\frac{x-x_0}{w}) \\right) + c
    
    #no-s form
    #def f(self,x,a=1,b=2,c=0,x0=0,w=1):
    #    xoff = x-x0
    #    tana = np.arctan(-xoff/w)/pi+0.5
    #    tanb = np.arctan(xoff/w)/pi+0.5
    #    return a*xoff*tana+b*xoff*tanb+c
    
    def f(self,x,a=1,b=2,c=0,x0=0,w=1,s=0):
        xo = x - x0
#        if w==0:
#            tanfactor = .5*np.sign(x-x0)
#        else:
#            tanfactor = np.arctan(xo/w)/pi
        #above is unneccessary b/c numpy division properly does infinities
        tanfactor = np.arctan(xo/w)/pi
        return xo*(a+b)/2 + (s - xo*(a-b))*tanfactor + c
    
    @property
    def rangehint(self):
        return self.x0-3*self.w,self.x0+3*self.w
    
class _InterpolatedModel(DatacentricModel1DAuto):
    
    _fittypes=['interp']
    fittype = 'interp'
    
    def __init__(self,**kwargs):
        """
        Generate a new interpolated model.
        """
        super(_InterpolatedModel,self).__init__()
        self.i1d = lambda x:x #default should never be externally seen
        
        for k,v in kwargs.iteritems():
            setattr(self,k,v)
    
    def f(self,x):
        if self.data is not None:
            res = self.i1d(x)
            xd,yd = self.data[0],self.data[1]
            mi,mx = np.min(xd),np.max(xd)
            res[x<mi] = yd[mi==xd][0]
            res[x>mx] = yd[mx==xd][0]
            return res
        else:
            return x
    
    def fitData(self,x,y,**kwargs):
        kwargs['savedata'] = True
        return super(_InterpolatedModel,self).fitData(x,y,**kwargs)
    
    def fitInterp(self,x,y,fixedpars=(),**kwargs):
        from scipy.interpolate import interp1d
        xi = np.argsort(x)
        self.i1d = interp1d(x[xi],y[xi],kind=self.kind,bounds_error=False)
        
        return []
        
class LinearInterpolatedModel(_InterpolatedModel):
    """
    A model that is the linear interpolation of the data, or if out of bounds, 
    fixed to the edge value.
    """
    kind = 'linear'
    
class NearestInterpolatedModel(_InterpolatedModel):
    """
    A model that is the interpolation of the data by taking the value of the 
    nearest point
    """
    kind = 'nearest'
   
class SmoothSplineModel(DatacentricModel1DAuto):
    """
    This model uses a B-spline as a model for the function. Note that by default
    the parameters are not tuned - the input smoothing and degree are left alone
    when fitting.
    
    The :class:`scipy.interpolate.UnivariateSpline` class is used to do the
    calculation (in the :attr:`spline` attribute).
    """
    def __init__(self,**kwargs):
        super(SmoothSplineModel,self).__init__()
        
        self._oldd = self._olds = self._ws = self._inits = None
        self.data = (np.arange(self.degree+1),np.arange(self.degree+1),self._ws)
        self.fitData(self.data[0],self.data[1])
        self._inits = self.data[:2]
        
        for k,v in kwargs.iteritems():
            setattr(self,k,v)
    
    _fittypes=['spline']
    fittype = 'spline'
    
    def fitSpline(self,x,y,fixedpars=(),**kwargs):
        """
        Fits the spline with the current s-value - if :attr:`s` is not changed,
        it will execute very quickly after, as the spline is saved.
        """
        from scipy.interpolate import UnivariateSpline
        
        #if the spline has never been fit to non-init data, set s appropriately
        if self._inits is not None and not (np.all(self._inits[0] == x) and np.all(self._inits[1] == y)):
            self.s = len(x)
            self._inits = None
        
        self.spline = UnivariateSpline(x,y,s=self.s,k=self.degree,w=kwargs['weights'] if 'weights' in kwargs else None)
        
        self._olds = self.s
        self._oldd = self.degree
        
        return np.array([self.s,self.degree])
        
    def fitData(self,x,y,**kwargs):
        """
        Custom spline data-fitting method.  Kwargs are ignored except 
        `weights` and `savedata` (see :meth:`FunctionModel.fitData` for meaning)
        """
        self._oldd = self._olds = None
        
        if 'savedata' in kwargs and not kwargs['savedata']:
            raise ValueError('data must be saved for spline models')
        else:
            kwargs['savedata']=True
            
        if 'weights' in kwargs:
            self._ws = kwargs['weights']
        else:
            self._ws = None
            
        sorti = np.argsort(x)    
        return super(SmoothSplineModel,self).fitData(x[sorti],y[sorti],**kwargs)
    
    def f(self,x,s=2,degree=3):        
        if self._olds != s or self._oldd != degree:
            xd,yd,weights = self.data
            self.fitSpline(xd,yd,weights=weights)
        
        return self.spline(x)
    
    def derivative(self, x, dx=None, nderivs=1):
        """
        Compute the derivative of this spline at the requested points.
        
        `order` specifies the number of derivatives to take - e.g. ``1`` gives
        the first derivative, ``2`` is the second, etc.  This can go up to the
        number of degrees in the spline+1 (e.g. a cubic spline can go up to 4)
        """
        return np.array([self.spline.derivatives(xi)[order] for xi in x])
        
    @property
    def rangehint(self):
        xd = self.data[0]
        return np.min(xd),np.max(xd)
    
    
class InterpolatedSplineModel(DatacentricModel1DAuto):
    """
    This uses a B-spline as a model for the function. Note that by default the
    degree is left alone when fitting, as this model always fits the points
    exactly.
    
    the :class:`scipy.interpolate.InterpolatedUnivariateSpline` class is used to
    do the calculation (in the :attr:`spline` attribute).
    """
    def __init__(self):
        super(InterpolatedSplineModel,self).__init__()
        
        self._oldd=self._olds=self._ws=None
        self.data = (np.arange(self.degree+1),np.arange(self.degree+1),self._ws)
        self.fitData(self.data[0],self.data[1])
            
            
    _fittypes = ['spline']
    fittype = 'spline'
    
    def fitSpline(self,x,y,fixedpars=(),**kwargs):
        """
        Fits the spline with the current s-value - if :attr:`s` is not changed,
        it will execute very quickly after, as the spline is saved.
        """
        from scipy.interpolate import InterpolatedUnivariateSpline
        
        self.spline = InterpolatedUnivariateSpline(x,y,w=kwargs['weights'] if 'weights' in kwargs else None,k=self.degree)
        
        self._oldd = self.degree
        
        return np.array([self.degree])
        
    def fitData(self,x,y,**kwargs):
        """
        Custom spline data-fitting method.  Kwargs are ignored except 
        `weights` and `savedata` (see :meth:`FunctionModel.fitData` for meaning)
        """
        self._oldd=None
        if 'savedata' in kwargs and not kwargs['savedata']:
            raise ValueError('data must be saved for spline models')
        else:
            kwargs['savedata']=True
            
        if 'weights' in kwargs:
            self._ws = kwargs['weights']
        else:
            self._ws = None
            
        sorti = np.argsort(x)    
        return super(InterpolatedSplineModel,self).fitData(x[sorti],y[sorti],**kwargs)
    
    def f(self,x,degree=3):        
        if self._oldd != degree:
            xd,yd,weights = self.data
            self.fitSpline(xd,yd,weights=weights)
        
        return self.spline(x)
        
    def derivative(self, x, dx=None, nderivs=1):
        """
        Compute the derivative of this spline at the requested points.
        
        `order` specifies the number of derivatives to take - e.g. ``1`` gives
        the first derivative, ``2`` is the second, etc.  This can go up to the
        number of degrees in the spline+1 (e.g. a cubic spline can go up to 4)
        """
        return np.array([self.spline.derivatives(xi)[order] for xi in x])
        
    @property
    def rangehint(self):
        xd = self.data[0]
        return np.min(xd),np.max(xd)
    
class _KnotSplineModel(DatacentricModel1DAuto):
    """
    this uses a B-spline as a model for the function. The knots parameter
    specifies the number of INTERIOR knots to use for the fit.
    
    The :attr:`locmethod` determines how to locate the knots and can be:
    
    * 'cdf'
        The locations of the knots will be determined by evenly sampling the cdf
        of the x-points.
    * 'even'
        The knots are evenly spaced in x.
    
    The :class:`scipy.interpolate.UnivariateSpline` class is used to do the
    calculation (in the "spline" attribute).
    """
    def __init__(self):
        super(_KnotSplineModel,self).__init__()
        
        self._ws = None
        
        self.data = (np.arange(self.degree+self.nknots+1),np.arange(self.degree+self.nknots+1),self._ws)
    
    @abstractmethod        
    def f(self,x):
        raise NotImplemetedError
    
    _fittypes = ['spline']
    fittype = 'spline'
    
    @abstractmethod    
    def fitSpline(self,x,y,fixedpars=(),**kwargs):  
        """
        Fits the spline with the current s-value - if :attr:`s` is not changed,
        it will execute very quickly after, as the spline is saved.
        """
        from scipy.interpolate import LSQUnivariateSpline
        
        self.spline = LSQUnivariateSpline(x,y,t=self.iknots,k=int(self.degree),w=kwargs['weights'] if 'weights' in kwargs else None)
        
    def fitData(self,x,y,**kwargs):
        """
        Custom spline data-fitting method.  Kwargs are ignored except 
        `weights` and `savedata` (see :meth:`FunctionModel.fitData` for meaning)
        """
        self._oldd=self._olds=None
        if 'savedata' in kwargs and not kwargs['savedata']:
            raise ValueError('data must be saved for spline models')
        else:
            kwargs['savedata']=True
            
        if 'weights' in kwargs:
            self._ws = kwargs['weights']
        else:
            self._ws = None
            
        sorti = np.argsort(x)    
        return super(_KnotSplineModel,self).fitData(x[sorti],y[sorti],**kwargs)
    
    def derivative(self, x, dx=None, nderivs=1):
        """
        Compute the derivative of this spline at the requested points.
        
        `order` specifies the number of derivatives to take - e.g. ``1`` gives
        the first derivative, ``2`` is the second, etc.  This can go up to the
        number of degrees in the spline+1 (e.g. a cubic spline can go up to 4)
        """
        return np.array([self.spline.derivatives(xi)[order] for xi in x])
    
    @property
    def rangehint(self):
        xd = self.data[0]
        return np.min(xd),np.max(xd)

class UniformKnotSplineModel(_KnotSplineModel):
    """
    A spline model with a uniform seperation between the internal knots, with
    their number set by the :attr:`nknots` parameter.
    """
    
    def __init__(self):
        self._oldk = self._oldd = None
        super(UniformKnotSplineModel,self).__init__()
        self.fitData(self.data[0],self.data[1])
    
    def fitSpline(self,x,y,fixedpars=(),**kwargs):
        """
        Fits the spline with the current s-value - if :attr:`s` is not changed,
        it will execute very quickly after, as the spline is saved.
        """
        self.iknots = np.linspace(x[0],x[-1],self.nknots+2)[1:-1]
        
        super(UniformKnotSplineModel,self).fitSpline(x,y,fixedpars,**kwargs)
        
        self._oldk = self.nknots
        self._oldd = self.degree
        
        return np.array([self.nknots,self.degree])
    
    def f(self,x,nknots=3,degree=3):
        if self._oldk != nknots or self._oldd != degree:
            xd,yd,weights = self.data
            self.fitSpline(xd,yd,weights=weights)
        
        return self.spline(x)
    
    

class UniformCDFKnotSplineModel(_KnotSplineModel):
    """
    A spline model with a seperation between the internal knots set uniformly on
    the CDF (e.g. knots at the locations that place them unifomly on the
    histogram of x-values), with their number set by the :attr:`nknots`
    parameter.
    """
    
    def __init__(self):
        self._oldk = self._oldd = None
        super(UniformCDFKnotSplineModel,self).__init__()
        self.fitData(self.data[0],self.data[1])
    
    def fitSpline(self,x,y,fixedpars=(),**kwargs):
        """
        Fits the spline with the current s-value - if :attr:`s` is not changed,
        it will execute very quickly after, as the spline is saved.
        """
        cdf,xcdf = np.histogram(x,bins=max(10,max(2*self.nknots,int(len(x)/10))))
        mask = cdf!=0
        cdf,xcdf = cdf[mask],xcdf[np.hstack((True,mask))]
        cdf = np.hstack((0,np.cumsum(cdf)/np.sum(cdf)))
        self.iknots = np.interp(np.linspace(0,1,self.nknots+2)[1:-1],cdf,xcdf)
        
        super(UniformCDFKnotSplineModel,self).fitSpline(x,y,fixedpars,**kwargs)
        
        self._oldk = self.nknots
        self._oldd = self.degree
        
        return np.array([self.nknots,self.degree])
    
    def f(self,x,nknots=3,degree=3):
        if self._oldk != nknots or self._oldd != degree:
            xd,yd,weights = self.data
            self.fitSpline(xd,yd,weights=weights)
        
        return self.spline(x)

class SpecifiedKnotSplineModel(_KnotSplineModel):
    def __init__(self):
        self.nknots = self.__class__._currnparams
        self._oldd = None #this will force a fit at first call
        super(SpecifiedKnotSplineModel,self).__init__()
        
        self.setKnots(np.linspace(-1,1,self.nknots))
    
    def fitSpline(self,x,y,fixedpars=(),**kwargs):
        """
        just fits the spline with the current s-value - if s is not changed,
        it will execute very quickly after
        """
        self.iknots = np.array([v for k,v in self.pardict.iteritems() if k.startswith('k')])
        self.iknots.sort()
        
        super(SpecifiedKnotSplineModel,self).fitSpline(x,y,fixedpars,**kwargs)
        
        self._oldd = self.degree
        
        retlist = list(self.iknots)
        retlist.insert(0,self.degree)
        return np.array(retlist)
    
    def setKnots(self,knots):
        if len(knots) != self.nknots:
            raise ValueError('provided knot sequence does not match the number of parameters')
        for i,k in enumerate(knots):
            setattr(self,'k'+str(i),k)
            
    def getKnots(self):
        ks = []
        for i in range(self.nknots):
            pn = 'k' + str(i)
            ks.append(getattr(self,pn))
        return np.array(ks)
    
    paramnames = 'k'
    
    degree=3 #default cubic
    def f(self,x,degree,*args):
        #TODO:faster way to do the arg check?
        if self._oldd != degree or np.any(self.iknots != np.array(args)):
            xd,yd,weights = self.data
            self.fitSpline(xd,yd,weights=weights)
        
        return self.spline(x)
    
class AlphaBetaGammaModel(FunctionModel1DAuto):
    """
    This model is a generic power-law-like model of the form
    
    .. math::
        \\rho(r) = A (r/rs)^{-\\gamma} (1+(r/r_s)^{\\alpha})^{(\\gamma-\\beta)/\\alpha}.
    
    Thus in this model, `gamma` is the inner log slope, `beta` is the outer log
    slope, and `alpha` controls the transition region.
    
    If a logarithmic version of the profile is desired, use::
    
    >>> m = AlphaBetaGammaModel()
    >>> m.setCall(xtrans='pow',ytrans='log')
    
    In this case the offset is given by :math:`\\log_{10}(A)` and the logaritmhic scale
    radius is :math:`\\log_{10}(r_s)`.
    
    .. note::
        Dehnen (1993) models correspond to :math:`(\\alpha,\\beta,\\gamma) =
        (1,4,\\gamma)` , and hence are not provided as a separate class.
    
    """
    
    def f(self,r,rs=1,A=1,alpha=1,beta=2,gamma=1):
        ro = r/rs
        return A*(ro)**-gamma*(1+(ro)**alpha)**((gamma-beta)/alpha)
    
    @property
    def rangehint(self):
        return self.rs/1000,1000*self.rs

class MaxwellBoltzmannModel(FunctionModel1DAuto):
    """
    A Maxwell-Boltzmann distribution for 1D velocity:
    
    .. math::
        \\sqrt{\\frac{m}{2 \\pi k_b T}} e^{-m v^2/(2 k_b T)}
    
    """
    
    xaxisname = 'v'
    
    from .utils import me #electron
    def f(self,v,T=273,m=me):
        from .utils import kb
        return (m/(2*pi*kb*T))**0.5*np.exp(-m*v*v/2/kb/T)
    
    @property
    def rangehint(self):
        from .utils import kb,c
        return 0,min(3*(2*kb*self.T/self.m)**0.5,c)
    
class MaxwellBoltzmannSpeedModel(MaxwellBoltzmannModel):
    """
    A Maxwell-Boltzmann distribution for 3D average speed:
    
    .. math::
        4 \\pi v^2 (\\frac{m}{2 \\pi k_b T})^{3/2} e^{-m v^2/(2 k_b T)}
    
    """
    
    from .utils import me #electron
    xaxisname = 'v'
    
    def f(self,v,T=273,m=me):
        from .utils import kb
        return 4*pi*v*v*(m/(2*pi*kb*T))**1.5*np.exp(-m*v*v/2/kb/T)
    
    @property
    def rangehint(self):
        from .utils import kb,c
        return 0,min(3*(2*kb*self.T/self.m)**0.5,c)
    


#<-------------------------------------- 2D models ---------------------------->
class Gaussian2DModel(FunctionModel2DScalarAuto):
    """
    Two dimensional Gaussian model (*not* normalized - peak value is 1).
    
    .. math::
        A e^{\\frac{-(x-\\mu_x)^2}{2 \\sigma_x^2}} e^{\\frac{-(y-\\mu_y)^2}{2 \\sigma_y^2}}
    
    """
    
    _fcoordsys='cartesian'
    def f(self,inarr,A=1,sigx=1,sigy=1,mux=0,muy=0):
        x,y = inarr
        xo = x-mux
        xdenom = 2*sigx*sigx
        yo = y-muy
        ydenom = 2*sigy*sigy
        return A*np.exp(-xo*xo/xdenom-yo*yo/ydenom)
    
    @property
    def rangehint(self):
        mux,muy = self.mux,self.muy
        sigx,sigy = self.sigx,self.sigy
        return (mux-4*sigx,mux+4*sigx,muy-4*sigy,muy+4*sigy)
    
class Linear2DModel(FunctionModel2DScalarAuto):
    """
    A simple model that is simply the linear combination of the two inputs.
    
    .. math::
        a x + b y + c
    
    """
    
    _fcoordsys='cartesian'
    def f(self,inarr,a,b,c):
        p1,p2 = inarr
        return a*p1+b*p2+c
        



    
#<-------------------------------Other Models---------------------------------->
    
class Plane(FunctionModel):
    """
    Models a plane of the form 
    
    .. math:
        d = ax+by+cz 
        
    i.e. (a,b,c) is the normal vector and d/a, b ,or c are the intercepts.
    """    
    def __init__(self,varorder='xyz',vn=(1,0,0),wn=(0,1,0),origin=(0,0,0)):
        self.varorder = varorder
        self.vn=vn
        self.wn=wn
        self.origin = origin
    
    def _getvaro(self):
        return self._varo
    def _setvaro(self,val):
        if val == 'xyz':
            self._f = self._fxyz
        elif val == 'yxz':
            self._f = self._fyxz
        elif val == 'xzy':
            self._f = self._fxzy
        elif val == 'zxy':
            self._f = self._fzxy
        elif val == 'yzx':
            self._f = self._fyzx
        elif val == 'zyx':
            self._f = self._fzyx
        else:
            raise ValueError('unrecognized variable order')
        self._varo = val
    varorder = property(_getvaro,_setvaro)
    
    def _getvn(self):
        return self._vn
    def _setvn(self,val):
        vn = np.array(val)
        if vn.shape != (3,):
            raise ValueError('vn must be a length-3 vector')
        self._vn = vn
    vn = property(_getvn,_setvn,doc='3D vector to project on to plane to get 2D basis vector 1')
    
    def _getwn(self):
        return self._wn
    def _setwn(self,val):
        wn = np.array(val)
        if wn.shape != (3,):
            raise ValueError('wn must be a length-3 vector')
        self._wn = wn
    wn = property(_getwn,_setwn,doc='3D vector to project on to plane to get 2D basis vector 2')

    def _getorigin(self):
        n = self.n
        scale = (self.d - np.dot(self._origin,n))/np.dot(n,n)
        return self._origin + scale*n
    def _setorigin(self,val):
        val = np.array(val,copy=False)
        if val.shape == (2,):
            self._origin = self.unproj(*val)[:,0]
        elif val.shape == (3,):
            self._origin = val
        else:
            raise ValueError('invalid shape for orign - must be 2-vector or 3-vector')
    origin = property(_getorigin,_setorigin)
    
    @property
    def n(self):
        """
        non-normalized unit vector
        """
        return np.array((self.a,self.b,self.c))
    
    @property
    def nhat(self):
        """
        normalized unit vector
        """
        n = np.array((self.a,self.b,self.c))
        return n/np.linalg.norm(n)
    
    def f(self,x,a=0,b=0,c=1,d=0):
        x = np.array(x,copy=False)
        shp = x.shape
        if len(shp) > 2: 
            x = x.reshape(2,np.prod(shp[1:]))
            y = self._f(x,a,b,c,d)
            return y.reshape(shp[1:])
        else:
            return self._f(x,a,b,c,d)
    
    def _fxyz(self,v,a,b,c,d):
        M = np.matrix([(a/c,b/c)])
        return d/c-(M*v).A
    def _fyxz(self,v,a,b,c,d):
        M = np.matrix((b/c,a/c))
        return d/c-(M*v).A
    def _fxzy(self,v,a,b,c,d):
        M = np.matrix((a/b,c/b))
        return d/b-(M*v).A
    def _fzxy(self,v,a,b,c,d):
        M = np.matrix((c/b,a/b))
        return d/b-(M*v).A
    def _fyzx(self,v,a,b,c,d):
        M = np.matrix((b/a,c/a))
        return d/a-(M*v).A
    def _fzyx(self,v,a,b,c,d):
        M = np.matrix((c/a,b/a))
        return d/a-(M*v).A
    
    def fitData(self,x,y,z,w=None):
        """
        Least squares fit using the output variable as the dependent variable.
        """
        from scipy.optimize import leastsq
        #reorder vars to get the right fitter
        x,y,z = eval(','.join(self._varo))
        
        xy = np.array([x,y],copy=False)
        if w is None:
            f = lambda v:(self.f(xy,*v)-z).ravel()
        else:
            f = lambda v:(self.f(xy,*v)-z).ravel()*w**0.5
        
        res = leastsq(f,self.parvals,full_output=1)
        self.lastfit = res
        
        self.parvals = res[0]
        return res[0]
    
    def distance(self,x,y,z):
        """
        compute the distance of a set of points in the 3D space from 
        the plane
        """
        shp = list(x.shape)
        x = np.array(x,copy=False).ravel()
        y = np.array(y,copy=False).ravel()
        z = np.array(z,copy=False).ravel()
        p = np.c_[x,y,z]
        
        return (np.dot(p,self.n)+self.d).reshape(shp)
    
    def proj(self,x,y,z):
        """
        Project points onto the plane from the 3D space
        
        :param x: first cartesian coordinate.
        :type x: array-like length N
        :param y: second cartesian coordinate.
        :type y: array-like length N
        :param z: third cartesian coordinate.
        :type z: array-like length N
        
        :returns: A 2 x N array in the plane for each of the input points. 
        """
        n = self.nhat
        
        vn = np.cross(np.cross(n,self.vn),n)
        wn = np.cross(np.cross(n,self.vn),n)
        
        shp = list(x.shape)
        x = np.array(x,copy=False).ravel()
        y = np.array(y,copy=False).ravel()
        z = np.array(z,copy=False).ravel()
        p = np.c_[x,y,z] - self.origin
        
        shp.insert(0,2)
        return (np.c_[np.dot(p,vn),np.dot(p,wn)].T).reshape(shp)
    
    def unproj(self,v,w):
        """
        Extract points from the plane back into the 3D space
        
        :param x: first in-plane coordinate.
        :type x: array-like length N
        :param y: second in-plane coordinate.
        :type y: array-like length N
        
        :returns: a 3 x N (x,y,z) array
        """
        n = self.nhat
        
        vn = np.cross(np.cross(n,self.vn),n)
        wn = np.cross(np.cross(n,self.vn),n)
        
        shp = list(v.shape)
        v = np.array(v,copy=False).ravel()
        w = np.array(w,copy=False).ravel()
        
        shp.insert(0,3)
        return (v*vn+w*wn + self.origin).reshape(shp)
    
    def plot3d(self,data=np.array([(-1,1),(-1,1),(-1,1)]),n=10,
               showdata=False,clf=True,**kwargs):
        """
        data should be 3 x N
        """
        import enthought.mayavi.mlab as M
        data = np.array(data,copy=False)
        
        xi,xx = data[0].min(),data[0].max()
        yi,yx = data[1].min(),data[1].max()
        x,y = np.meshgrid(np.linspace(xi,xx,n),np.linspace(yi,yx,n))
        
        if clf:
            M.clf()
        
        if 'color' not in kwargs:
            kwargs['color']=(1,0,0)
        if 'opacity' not in kwargs:
            kwargs['opacity'] = 0.5
            
        M.mesh(x,y,self([x,y]),**kwargs)
        if showdata:
            from operator import isMappingType
            if isMappingType(showdata):
                M.points3d(*data,**showdata)
            else:
                M.points3d(*data)
    
#register everything in this module
from inspect import isclass
for o in locals().values():
    if isclass(o) and not o.__name__.startswith('_') and issubclass(o,ParametricModel):
        if 'FunctionModel' not in o.__name__ and 'CompositeModel' not in o.__name__:
            register_model(o)
            
#cleanup namespace
del isclass,o
