# This file is part of xrayutilities.
#
# xrayutilities is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012 Dominik Kriegner <dominik.kriegner@gmail.com>
"""
module with a function wrapper to scipy.optimize.leastsq
for fitting of a 2D function to a peak or a 1D Gauss fit with
the odr package
"""

from __future__ import print_function
import numpy
import scipy.optimize as optimize
import time
from scipy.odr import odrpack as odr
from scipy.odr import models

from .. import config
from .functions import Gauss1d,Gauss1d_der_x,Gauss1d_der_p

try:
    from matplotlib import pyplot as plt
except RuntimeError:
    if config.VERBOSITY >= config.INFO_ALL:
        print("XU.analysis.sample_align: warning; plotting functionality not available")

def gauss_fit(xdata,ydata,iparams=[],maxit=200):
    """
    Gauss fit function using odr-pack wrapper in scipy similar to
    https://github.com/tiagopereira/python_tips/wiki/Scipy%3A-curve-fitting

    Parameters
    ----------
     xdata:     xcoordinates of the data to be fitted
     ydata:     ycoordinates of the data which should be fit

    keyword parameters:
     iparams:   initial paramters for the fit (determined automatically if nothing is given
     maxit:     maximal iteration number of the fit
    
    Returns
    -------
     params,sd_params,itlim

    the Gauss parameters as defined in function Gauss1d(x, *param)
    and their errors of the fit, as well as a boolean flag which is false in the case of a 
    successful fit
    """

    gfunc = lambda param,x: Gauss1d(x, *param)
    gfunc_dx = lambda param,x: Gauss1d_der_x(x, *param)
    gfunc_dp = lambda param,x: Gauss1d_der_p(x, *param)

    if not any(iparams):
        cen = numpy.sum(xdata*ydata)/numpy.sum(ydata)
        iparams = numpy.array([cen,\
            numpy.sqrt(numpy.abs(numpy.sum((xdata-cen)**2*ydata)/numpy.sum(ydata))),\
            numpy.max(ydata),\
            numpy.min(ydata)])

    if config.VERBOSITY >= config.DEBUG:
        print("XU.math.gauss_fit: iparams: [%f %f %f %f]" %tuple(iparams))

    gauss  = odr.Model(gfunc, fjacd=gfunc_dx, fjacb=gfunc_dp)

    sy = numpy.sqrt(ydata)
    sy[sy==0] = 1
    mydata = odr.RealData(xdata, ydata, sy=sy)

    myodr  = odr.ODR(mydata, gauss, beta0=iparams,maxit=maxit)

    # use least-square fit
    myodr.set_job(fit_type=2)

#    # DK comment out because this command triggers a synthax error with new scipy version 2013/5/7
#    if config.VERBOSITY >= config.DEBUG:
#        myodr.set_iprint(final=1)

    fit = myodr.run()

    #fit.pprint() # prints final message from odrpack

    if config.VERBOSITY >= config.DEBUG:
        print("XU.math.gauss_fit: params: [%f %f %f %f]" %tuple(fit.beta))
        print("XU.math.gauss_fit: params std: [%f %f %f %f]" %tuple(fit.sd_beta))
        print("XU.math.gauss_fit: %s" %fit.stopreason[0])

    itlim = False
    if fit.stopreason[0] == 'Iteration limit reached':
        itlim = True
        if config.VERBOSITY >= config.INFO_LOW:
            print("XU.math.gauss_fit: Iteration limit reached, do not trust the result!")

    return fit.beta, fit.sd_beta, itlim


def fit_peak2d(x,y,data,start,drange,fit_function,maxfev=2000):
    """
    fit a two dimensional function to a two dimensional data set
    e.g. a reciprocal space map

    Parameters
    ----------
     x,y:     data coordinates (do NOT need to be regularly spaced)
     data:    data set used for fitting (e.g. intensity at the data coords)
     start:   set of starting parameters for the fit
              used as first parameter of function fit_function
     drange:  limits for the data ranges used in the fitting algorithm
              e.g. it is clever to use only a small region around the peak which
              should be fitted: [xmin,xmax,ymin,ymax]
     fit_function:  function which should be fitted
                    must accept the parameters (x,y,*params)

    Returns
    -------
     (fitparam,cov)   the set of fitted parameters and covariance matrix
    """
    s = time.time()
    if config.VERBOSITY >= config.INFO_ALL:
        print("XU.math.fit: Fitting started... ",end='')

    start = numpy.array(start)
    lx = x.flatten()
    ly = y.flatten()
    mask = (lx>drange[0])*(lx<drange[1])*(ly>drange[2])*(ly<drange[3])
    ly = ly[mask]
    lx = lx[mask]
    ldata = data.flatten()[mask]
    errfunc = lambda p,x,z,data: (fit_function(x,z,*p) - data)#/(numpy.abs(numpy.sqrt(data))+numpy.abs(numpy.sqrt(data[data!=0].min())))
    p, cov, infodict, errmsg, success = optimize.leastsq(errfunc, start, args=(lx,ly,ldata), full_output=1,maxfev=maxfev)

    s = time.time() - s
    if config.VERBOSITY >= config.INFO_ALL:
        print("finished in %8.2f sec, (data length used %d)"%(s,ldata.size))
        print("XU.math.fit: %s"%errmsg)

    # calculate correct variance covariance matrix
    if cov != None:
        s_sq = (errfunc(p,lx,ly,ldata)**2).sum()/(len(ldata)-len(start))
        pcov = cov * s_sq
    else: pcov = numpy.zeros((len(start),len(start)))

    if success not in [1,2,3,4]:
        print("XU.math.fit: Could not obtain fit!")
    return p,pcov


def multGaussFit(x,data,peakpos,peakwidth,dranges=None):
    """
    function to fit multiple Gaussian peaks with linear background to a set of data

    Parameters
    ----------
     x:  x-coordinate of the data
     data:  data array with same length as x
     peakpos:  initial parameters for the peak positions
     peakwidth:  initial values for the peak width
     dranges:  list of tuples with (min,max) value of the data ranges to use.
               does not need to have the same number of entries as peakpos

    Returns
    -------
     pos,sigma,amp,background

    pos:  list of peak positions derived by the fit
    sigma:  list of peak width derived by the fit
    amp:  list of amplitudes of the peaks derived by the fit
    background:  array of background values at positions x
    """
    def deriv_x(p, x):
        """
        function to calculate the derivative of the signal of multiple peaks and background w.r.t. the x-coordinate

        p: list of parameters, for every peak there needs to be position, sigma, amplitude and at the end
           two values for the linear background function (b0,b1)
        x: x-coordinate
        """
        derx = numpy.zeros(x.size)

        # sum up peak functions contributions
        for i in range(len(p)//3):
            ldx = Gauss1d_der_x(x,p[3*i],p[3*i+1],p[3*i+2],0)
            derx += ldx

        # background contribution
        k = p[-2]; d = p[-1]
        b = numpy.ones(x.size)*k

        return derx+b
        
    def deriv_p(p, x):
        """
        function to calculate the derivative of the signal of multiple peaks and background w.r.t. the parameters

        p: list of parameters, for every peak there needs to be position, sigma, amplitude and at the end
           two values for the linear background function (b0,b1)
        x: x-coordinate

        returns derivative w.r.t. all the parameters with shape (len(p),x.size)
        """

        derp = numpy.empty(0)
        # peak functions contributions
        for i in range(len(p)//3):
            lp = (p[3*i],p[3*i+1],p[3*i+2],0)
            derp = numpy.append(derp,-2*(lp[0]-x)*Gauss1d(x,*lp))
            derp = numpy.append(derp,(lp[0]-x)**2/(2*lp[1]**3)*Gauss1d(x,*lp))
            derp = numpy.append(derp,Gauss1d(x,*lp)/lp[2])
        
        # background contributions
        derp = numpy.append(derp,x)
        derp = numpy.append(derp,numpy.ones(x.size))
        
        # reshape output
        derp.shape = (len(p),) + x.shape
        return derp

    def fsignal(p, x):
        """
        function to calculate the signal of multiple peaks and background

        p: list of parameters, for every peak there needs to be position, sigma, amplitude and at the end
           two values for the linear background function (k,d)
        x: x-coordinate
        """
        f = numpy.zeros(x.size)

        # sum up peak functions
        for i in range(len(p)//3):
            lf = Gauss1d(x,p[3*i],p[3*i+1],p[3*i+2],0)
            f += lf

        # background
        k = p[-2]; d = p[-1]
        b = numpy.polyval((k,d),x)

        return f+b

    ##########################
    # create local data set (extract data ranges)
    if dranges:
        mask = numpy.array([False]*x.size)
        for i in range(len(dranges)):
            lrange = dranges[i]
            lmask = numpy.logical_and(x>lrange[0],x<lrange[1])
            mask = numpy.logical_or(mask,lmask)
        lx = x[mask]
        ldata = data[mask]
    else: 
        lx = x
        ldata = data

    # create initial parameter list
    p = []
    
    # background
    k,d = numpy.polyfit(lx, ldata, 1)
    
    # peak parameters
    for i in range(len(peakpos)):
        amp = ldata[(lx-peakpos[i])>=0][0] - numpy.polyval((k,d),lx)[(lx-peakpos[i])>=0][0]
        p += [peakpos[i],peakwidth[i],amp]

    # background parameters
    p += [k,d]

    if(config.VERBOSITY >= config.DEBUG):
        print("XU.math.multGaussFit: intial parameters")
        print(p)

    
    ##########################
    # fit with odrpack
    model =  odr.Model(fsignal, fjacd=deriv_x, fjacb=deriv_p)
    odata = odr.RealData(lx,ldata)
    my_odr = odr.ODR(odata,model,beta0=p)
    # fit type 2 for least squares
    my_odr.set_job(fit_type=2)
    fit = my_odr.run()

    if(config.VERBOSITY >= config.DEBUG):
        print("XU.math.multGaussFit: fitted parameters")
        print(fit.beta)
    try:
        if fit.stopreason[0] not in ['Sum of squares convergence']:
            print("XU.math.multGaussFit: fit NOT converged (%s)" %fit.stopreason[0])
            return None,None,None,None
    except:
        print("XU.math.multGaussFit: fit most probably NOT converged (%s)" %str(fit.stopreason))
        return None,None,None,None
    # prepare return values
    fpos = fit.beta[:-2:3]
    fwidth = fit.beta[1:-2:3]
    famp = fit.beta[2::3]
    background = numpy.polyval((fit.beta[-2],fit.beta[-1]),x)

    return fpos,fwidth,famp,background

def multGaussPlot(x,fpos,fwidth,famp,background,dranges=None,fig="xu_plot",fact=1.):
    """
    function to plot multiple Gaussian peaks with linear background 

    Parameters
    ----------
     x:  x-coordinate of the data
     fpos:  list of positions of the peaks
     fwidth:  list of width of the peaks
     famp:  list of amplitudes of the peaks
     background:  array with background values
     dranges:  list of tuples with (min,max) value of the data ranges to use.
               does not need to have the same number of entries as fpos
     fig:  matplotlib figure number or name
     fact: factor to use as multiplicator in the plot
    """

    try: plt.__name__
    except NameError:
        print("XU.math.multGaussPlot: Warning: plot functionality not available")
        return
    
    plt.figure(fig)
    # plot single peaks
    if dranges:
        mask = numpy.array([False]*x.size)
        for i in range(len(dranges)):
            lrange = dranges[i]
            lmask = numpy.logical_and(x>lrange[0],x<lrange[1])
            mask = numpy.logical_or(mask,lmask)
        lx = x[mask]
        lb = background[mask]
    else: 
        lx = x
        lb = background

    f = numpy.zeros(lx.size)
    for i in range(len(fpos)):
        lf = Gauss1d(lx,fpos[i],fwidth[i],famp[i],0)
        f += lf
        plt.plot(lx,(lf+lb)*fact,'k:')

    # plot summed signal
    plt.plot(lx,(f+lb)*fact,'r-',lw=1.5)

