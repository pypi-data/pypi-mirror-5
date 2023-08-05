# freqplot.py - frequency domain plots for control systems
#
# Author: Richard M. Murray
# Date: 24 May 09
#
# This file contains some standard control system plots: Bode plots,
# Nyquist plots and pole-zero diagrams.  The code for Nichols charts
# is in nichols.py.
#
# Copyright (c) 2010 by California Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the California Institute of Technology nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CALTECH
# OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# $Id: freqplot.py 179 2012-01-08 02:56:24Z murrayrm $

import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
from ctrlutil import unwrap
from bdalg import feedback

#
# Main plotting functions
#
# This section of the code contains the functions for generating
# frequency domain plots
#

# Bode plot
# ModelicaRes 7/30/12:
#def bode_plot(syslist, omega=None, dB=False, Hz=False, deg=True,
#        color=None, Plot=True):
def bode_plot(syslist, omega=None, dB=False, Hz=False, deg=True,
        color=None, style='-', Plot=True, label=None, *args, **kwargs):
    """Bode plot for a system

    Plots a Bode plot for the system over a (optional) frequency range.

    Parameters
    ----------
    syslist : linsys
        List of linear input/output systems (single system is OK)
    omega : freq_range
        Range of frequencies (list or bounds) in rad/sec
    dB : boolean
        If True, plot result in dB
    Hz : boolean
        If True, plot frequency in Hz (omega must be provided in rad/sec)
    color : matplotlib color
        Color of line in bode plot
    # ModelicaRes 7/30/12:
    style : matplotlib style
        Style of line in bode plot
    deg : boolean
        If True, return phase in degrees (else radians)
    Plot : boolean
        If True, plot magnitude and phase
    # ModelicaRes 7/30/12:
    *args, **kwargs: Propagated to matplotlib.pyplot.semilogx AND matplotlib.pyplot.loglog

    Returns
    -------
    mag : array (list if len(syslist) > 1)
        magnitude
    phase : array (list if len(syslist) > 1)
        phase
    omega : array (list if len(syslist) > 1)
        frequency

    Notes
    -----
    1. Alternatively, you may use the lower-level method
    (mag, phase, freq) = sys.freqresp(freq) to generate the frequency
    response for a system, but it returns a MIMO response.

    Examples
    --------
    >>> from matlab import ss
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> mag, phase, omega = bode(sys)
    """
    # If argument was a singleton, turn it into a list
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)

    mags, phases, omegas = [], [], []
    for sys in syslist:
        if (sys.inputs > 1 or sys.outputs > 1):
            #TODO: Add MIMO bode plots.
            raise NotImplementedError("Bode is currently only implemented for SISO systems.")
        else:
            # Select a default range if none is provided
            if (omega == None):
                omega = default_frequency_range(syslist)

            # Get the magnitude and phase of the system
            mag_tmp, phase_tmp, omega = sys.freqresp(omega)
            mag = np.squeeze(mag_tmp)
            phase = np.squeeze(phase_tmp)
            phase = unwrap(phase)
            if Hz: omega = omega/(2*sp.pi)
            if dB: mag = 20*sp.log10(mag)
            if deg: phase = phase * 180 / sp.pi

            mags.append(mag)
            phases.append(phase)
            omegas.append(omega)
            # Get the dimensions of the current axis, which we will divide up
            #! TODO: Not current implemented; just use subplot for now

            if (Plot):
                # Magnitude plot
                plt.subplot(211);
                if dB:
                    if color==None:
                        # ModelicaRes 5/23/11:
                        #plt.semilogx(omega, mag)
                        if type(style)==str:
                            plt.semilogx(omega, mag, linestyle=style, label=label, *args, **kwargs)
                        else:
                            plt.semilogx(omega, mag, dashes=style, label=label, *args, **kwargs)
                    else:
                        # ModelicaRes 5/23/11:
                        #plt.semilogx(omega, mag, color=color)
                        if type(style)==str:
                            plt.semilogx(omega, mag, color=color, linestyle=style, label=label, *args, **kwargs)
                        else:
                            plt.semilogx(omega, mag, color=color, dashes=style, label=label, *args, **kwargs)
                    plt.ylabel("Magnitude (dB)")
                else:
                    if color==None:
                        # ModelicaRes 5/23/11:
                        #plt.loglog(omega, mag)
                        if type(style)==str:
                            plt.loglog(omega, mag, linestyle=style, label=label, *args, **kwargs)
                        else:
                            plt.loglog(omega, mag, dashes=style, label=label, *args, **kwargs)
                    else:
                        # ModelicaRes 5/23/11:
                        #plt.loglog(omega, mag, color=color)
                        if type(style)==str:
                            plt.loglog(omega, mag, color=color, linestyle=style, label=label, *args, **kwargs)
                        else:
                            plt.loglog(omega, mag, color=color, dashes=style, label=label, *args, **kwargs)
                    plt.ylabel("Magnitude")

                # Add a grid to the plot
                plt.grid(True)
                plt.grid(True, which='minor')
                plt.hold(True);

                # Phase plot
                plt.subplot(212);
                if deg:
                    phase_deg = phase
                else:
                    phase_deg = phase * 180 / sp.pi
                if color==None:
                    # ModelicaRes 5/23/11:
                    #plt.semilogx(omega, phase_deg)
                    if type(style)==str:
                        plt.semilogx(omega, phase_deg, linestyle=style, label=label, *args, **kwargs)
                    else:
                        plt.semilogx(omega, phase_deg, dashes=style, label=label, *args, **kwargs)
                else:
                    # ModelicaRes 5/23/11:
                    #plt.semilogx(omega, phase_deg, color=color)
                    if type(style)==str:
                        plt.semilogx(omega, phase_deg, color=color, linestyle=style, label=label, *args, **kwargs)
                    else:
                        plt.semilogx(omega, phase_deg, color=color, dashes=style, label=label, *args, **kwargs)
                plt.hold(True)

                # Add a grid to the plot
                plt.grid(True)
                plt.grid(True, which='minor')
                # ModelicaRes 5/23/11:
                #plt.ylabel("Phase (deg)")
                plt.ylabel("Phase / deg")

                # Label the frequency axis
                if Hz:
                    # ModelicaRes 5/23/11:
                    #plt.xlabel("Frequency (Hz)")
                    plt.xlabel("Frequency / Hz")
                else:
                    # ModelicaRes 5/23/11:
                    #plt.xlabel("Frequency (rad/sec)")
                    plt.xlabel(r'Frequency / rad s$^{-1}$')

    if len(syslist) == 1:
        return mags[0], phases[0], omegas[0]
    else:
        return mags, phases, omegas

# ModelicaRes 5/23/11:
# This function is also in res.py.  **Install res.py, import it here, and delete this copy.
def get_pow1000(num):
    '''Determine the exponent for which the significand of a number is within the
    range [1, 1000).
    '''
    # Based on algorithm from http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html, accessed 2010/11/7
    # by Jason Heeris 2009/11/18
    from decimal import Decimal
    from math import floor
    dnum = Decimal(str(num))
    if dnum == 0:
        return 0
    elif dnum < 0:
        dnum = -dnum
    return int(floor(dnum.log10()/3))

# ModelicaRes 5/23/11:
# This function is also in res.py.  **Install res.py, import it here, and delete this copy.
def gen_prefix(pow1000):
    '''Return the SI prefix for a power of 1000.
    '''
    # Prefixes according to Table 5 of [BIPM 2006] (excluding hecto, deca, deci, and centi).
    if pow1000 < -8 or pow1000 > 8:
        raise ValueError("Value is out of the range covered by the SI prefixes.")
    return ['Y', # yotta (10^24)
            'Z', # zetta (10^21)
            'E', # exa (10^18)
            'P', # peta (10^15)
            'T', # tera (10^12)
            'G', # giga (10^9)
            'M', # mega (10^6)
            'k', # kilo (10^3)
            '', # (10^0)
            'm', # milli (10^-3)
            r'$\mu$', # micro (10^-6)
            'n', # nano (10^-9)
            'p', # pico (10^-12)
            'f', # femto (10^-15)
            'a', # atto (10^-18)
            'z', # zepto (10^-21)
            'y'][8 - pow1000] # yocto (10^-24)

# ModelicaRes 5/23/11 copied and modified from nyquist():
def nyquist_label(syslist, omega=None, inclText=True, color='b', *args, **kwargs):
    """Denote frequencies on a Nyquist plot.

    Usage
    =====
    real, imag, freq = nyquist(sys, omega=None)

    Plots discrete points on a Nyquist diagram (at frequency decades) for the system
    over a (optional) frequency range.  Labels the frequencies of those points
    in Hz (optional).

    Parameters
    ----------
    syslist : linsys
        List of linear input/output systems (single system is OK)
    omega : freq_range
        Range of frequencies (list or bounds) in rad/s
    *args, **kwargs: Propagated to matplotlib.pyplot.plot

    Return values
    -------------
    real : real part of the frequency response array
    imag : imaginary part of the frequency response array
    freq : frequencies
    """
    # If argument was a singleton, turn it into a list
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)

    # Select a default range if none is provided
    if (omega == None):
        omega = default_frequency_range(syslist)
        omega = (min(omega), max(omega))
    # Interpolate between wmin and wmax if a tuple or list are provided
    elif (isinstance(omega,list) | isinstance(omega,tuple)) and len(omega) != 2:
        # Only accept tuple or list of length 2
        raise ValueError("Supported frequency arguments are (wmin,wmax) tuple or list, or frequency vector. ")
    w = (np.ceil(np.log10(omega[0]/(2*sp.pi))), np.ceil(np.log10(omega[1]/(2*sp.pi)))) # Find the log10 of the min and max decade frequencies that are within the range.
    omega = 2*sp.pi*np.logspace(w[0],w[1],num=w[1]-w[0]+1,endpoint=True,base=10.0) # Create the array of angular frequencies.

    for sys in syslist:
        if (sys.inputs > 1 or sys.outputs > 1):
            #TODO: Add MIMO nyquist plots.
            raise NotImplementedError("Nyquist is currently only implemented for SISO systems.")
        else:
            # Get the magnitude and phase of the system
            mag_tmp, phase_tmp, omega = sys.freqresp(omega)
            mag = np.squeeze(mag_tmp)
            phase = np.squeeze(phase_tmp)

            # Compute the primary curve
            x = sp.multiply(mag, sp.cos(phase));
            y = sp.multiply(mag, sp.sin(phase));

            # Plot the primary curve and mirror image
            plt.plot(x, y, '.', color=color, *args, **kwargs);
            plt.plot(x, -y, '.', color=color, *args, **kwargs);

            # Label the frequencies of the points
            if (inclText):
                for xpt, ypt, omegapt in zip(x, y, omega):
                    f = omegapt/(2*sp.pi) # Convert to Hz.
                    pow1000 = max(min(get_pow1000(f),8),-8) # Factor out multiples of 1000 and limit the result to the range [-8, 8].
                    prefix = gen_prefix(pow1000) # Get the SI prefix.
                    plt.text(xpt, ypt, ' ' + str(int(np.round(f/1000**pow1000, 0))) + ' ' + prefix + 'Hz') # Apply the text. (Use a space before the text to prevent overlap with the data.)
                    # np.round() is used because 0.99... appears instead of 1.0, and this would otherwise be truncated to 0.
        return x, y, omega

# Nyquist plot
# ModelicaRes 5/23/11:
#def nyquist_plot(syslist, omega=None, Plot=True):
def nyquist_plot(syslist, omega=None, Plot=True, label=None, color='b', mark=True, *args, **kwargs):
    """Nyquist plot for a system

    Plots a Nyquist plot for the system over a (optional) frequency range.

    Parameters
    ----------
    syslist : list of Lti
        List of linear input/output systems (single system is OK)
    omega : freq_range
        Range of frequencies (list or bounds) in rad/sec
    Plot : boolean
        if True, plot magnitude
    # ModelicaRes 7/30/12:
    *args, **kwargs: Propagated to matplotlib.pyplot.plot

    Returns
    -------
    real : array
        real part of the frequency response array
    imag : array
        imaginary part of the frequency response array
    freq : array
        frequencies

    Examples
    --------
    >>> from matlab import ss
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> real, imag, freq = nyquist(sys)
    """
    # If argument was a singleton, turn it into a list
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)

    # Select a default range if none is provided
    if (omega == None):
        omega = default_frequency_range(syslist)
    # Interpolate between wmin and wmax if a tuple or list are provided
    elif (isinstance(omega,list) | isinstance(omega,tuple)):
        # Only accept tuple or list of length 2
        if (len(omega) != 2):
            raise ValueError("Supported frequency arguments are (wmin,wmax) tuple or list, or frequency vector. ")
        omega = np.logspace(np.log10(omega[0]),np.log10(omega[1]),num=50,endpoint=True,base=10.0)
    for sys in syslist:
        if (sys.inputs > 1 or sys.outputs > 1):
            #TODO: Add MIMO nyquist plots.
            raise NotImplementedError("Nyquist is currently only implemented for SISO systems.")
        else:
            # Get the magnitude and phase of the system
            mag_tmp, phase_tmp, omega = sys.freqresp(omega)
            mag = np.squeeze(mag_tmp)
            phase = np.squeeze(phase_tmp)

            # Compute the primary curve
            x = sp.multiply(mag, sp.cos(phase));
            y = sp.multiply(mag, sp.sin(phase));

            if (Plot):
                # Plot the primary curve and mirror image
                # ModelicaRes 5/23/11:
                #plt.plot(x, y, '-');
                #plt.plot(x, -y, '--');
                plt.plot(x, y, '-', label=label, color=color, *args, **kwargs);
                plt.plot(x, -y, '--', color=color, *args, **kwargs);

                # ModelicaRes 5/25/11:
                # plt.plot([-1], [0], 'r+')
                if (mark):
                    # Mark the -1 point
                    plt.plot([-1], [0], 'r+')

        return x, y, omega

# Gang of Four
#! TODO: think about how (and whether) to handle lists of systems
def gangof4_plot(P, C, omega=None):
    """Plot the "Gang of 4" transfer functions for a system

    Generates a 2x2 plot showing the "Gang of 4" sensitivity functions
    [T, PS; CS, S]

    Parameters
    ----------
    P, C : Lti
        Linear input/output systems (process and control)
    omega : array
        Range of frequencies (list or bounds) in rad/sec

    Returns
    -------
    None
    """
    if (P.inputs > 1 or P.outputs > 1 or C.inputs > 1 or C.outputs >1):
        #TODO: Add MIMO go4 plots.
        raise NotImplementedError("Gang of four is currently only implemented for SISO systems.")
    else:

        # Select a default range if none is provided
        #! TODO: This needs to be made more intelligent
        if (omega == None):
            omega = default_frequency_range((P,C))

        # Compute the senstivity functions
        L = P*C;
        S = feedback(1, L);
        T = L * S;

        # Plot the four sensitivity functions
        #! TODO: Need to add in the mag = 1 lines
        mag_tmp, phase_tmp, omega = T.freqresp(omega);
        mag = np.squeeze(mag_tmp)
        phase = np.squeeze(phase_tmp)
        plt.subplot(221); plt.loglog(omega, mag);

        mag_tmp, phase_tmp, omega = (P*S).freqresp(omega);
        mag = np.squeeze(mag_tmp)
        phase = np.squeeze(phase_tmp)
        plt.subplot(222); plt.loglog(omega, mag);

        mag_tmp, phase_tmp, omega = (C*S).freqresp(omega);
        mag = np.squeeze(mag_tmp)
        phase = np.squeeze(phase_tmp)
        plt.subplot(223); plt.loglog(omega, mag);

        mag_tmp, phase_tmp, omega = S.freqresp(omega);
        mag = np.squeeze(mag_tmp)
        phase = np.squeeze(phase_tmp)
        plt.subplot(224); plt.loglog(omega, mag);

#
# Utility functions
#
# This section of the code contains some utility functions for
# generating frequency domain plots
#

# Compute reasonable defaults for axes
def default_frequency_range(syslist):
    """Compute a reasonable default frequency range for frequency
    domain plots.

    Finds a reasonable default frequency range by examining the features
    (poles and zeros) of the systems in syslist.

    Parameters
    ----------
    syslist : list of Lti
        List of linear input/output systems (single system is OK)

    Returns
    -------
    omega : array
        Range of frequencies in rad/sec

    Examples
    --------
    >>> from matlab import ss
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> omega = default_frequency_range(sys)
    """
    # This code looks at the poles and zeros of all of the systems that
    # we are plotting and sets the frequency range to be one decade above
    # and below the min and max feature frequencies, rounded to the nearest
    # integer.  It excludes poles and zeros at the origin.  If no features
    # are found, it turns logspace(-1, 1)

    # Find the list of all poles and zeros in the systems
    features = np.array(())

    # detect if single sys passed by checking if it is sequence-like
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)
    for sys in syslist:
        # Add new features to the list
        features = np.concatenate((features, np.abs(sys.pole())))
        features = np.concatenate((features, np.abs(sys.zero())))

    # Get rid of poles and zeros at the origin
    features = features[features != 0];

    # Make sure there is at least one point in the range
    if (features.shape[0] == 0): features = [1];

    # Take the log of the features
    features = np.log10(features)

    # Set the range to be an order of magnitude beyond any features
    omega = sp.logspace(np.floor(np.min(features))-1,
                        np.ceil(np.max(features))+1)

    return omega

# Function aliases
bode = bode_plot
nyquist = nyquist_plot
gangof4 = gangof4_plot
