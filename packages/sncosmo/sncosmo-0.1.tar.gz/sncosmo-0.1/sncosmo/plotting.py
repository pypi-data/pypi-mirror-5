# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Functions to plot light curve data and models."""
from __future__ import division

import math
import numpy as np

from .spectral import get_bandpass, get_magsystem
from .fitting import normalized_flux

__all__ = ['plotlc']

def normalized_flux(data, zp=25., magsys='ab'):
    """Return flux values normalized to a common zeropoint and magnitude
    system."""

    datalen = len(data['flux'])
    magsys = get_magsystem(magsys)
    flux = np.empty(datalen, dtype=np.float)
    fluxerr = np.empty(datalen, dtype=np.float)

    for i in range(datalen):
        ms = get_magsystem(data['zpsys'][i])
        factor = (ms.zpbandflux(data['band'][i]) /
                  magsys.zpbandflux(data['band'][i]) *
                  10.**(0.4 * (zp - data['zp'][i])))
        flux[i] = data['flux'][i] * factor
        fluxerr[i] = data['fluxerr'][i] * factor

    return flux, fluxerr
                       
def plotlc(data, fname=None, model=None, show_pulls=True,
           include_model_error=False, xfigsize=None, yfigsize=None, dpi=100):
    """Plot light curve data.

    Parameters
    ----------
    data : `~numpy.ndarray` or dict thereof
        Structured array or dictionary of arrays, with the following fields:
        {'time', 'band', 'flux', 'fluxerr', 'zp', 'zpsys'}.
    fname : str, optional
        Filename to write plot to. If `None` (default), plot is shown using
        ``show()``.
    model : `~sncosmo.Model`, optional
        If given, model light curve is overplotted.
    show_pulls : bool, optional
        If True (and if model is given), plot pulls. Default is ``True``.
    include_model_error : bool, optional
        Plot model error as a band around the model.
    xfigsize, yfigsize : float, optional
        figure size in inches in x or y. Specify one or the other, not both.
        Default is xfigsize=8.
    dpi : float, optional
        dpi to pass to ``plt.savefig()`` for rasterized images. 
        
    Examples
    --------

    Suppose we have data in a file that looks like this::
 
        time band flux fluxerr zp zpsys
        55070.0 sdssg -0.263064256628 0.651728140824 25.0 ab
        55072.0512821 sdssr -0.836688186816 0.651728140824 25.0 ab
        55074.1025641 sdssi -0.0104080573938 0.651728140824 25.0 ab
        55076.1538462 sdssz -0.0794771107707 0.651728140824 25.0 ab
        55078.2051282 sdssg 0.897840283912 0.651728140824 25.0 ab
        ...

    To read and plot the data:

        >>> meta, data = sncosmo.readlc('mydatafile.dat')  # read the data
        >>> sncosmo.plotlc(data, fname='plotlc_example.png')  # plot the data

    We happen to know the model and parameters that fit this
    data. Specifying the ``model`` keyword will plot the model over
    the data.
    
        >>> model = sncosmo.get_model('salt2')
        >>> model.set(z=0.5, c=0.2, t0=55100., mabs=-19.5, x1=0.5)
        >>> sncosmo.plotlc(data, fname='plotlc_example.png', model=model)

    .. image:: /pyplots/plotlc_example.png

    """

    import matplotlib.pyplot as plt
    from matplotlib import cm
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    cmap = cm.get_cmap('gist_rainbow')
    disprange = (3000., 10000.)

    dataflux, datafluxerr = normalized_flux(data, zp=25., magsys='ab')

    bandnames = np.unique(data['band']).tolist()
    bands = [get_bandpass(bandname) for bandname in bandnames]
    disps = [b.disp_eff for b in bands]

    # Calculate layout of figure (columns, rows, figure size)
    nsubplots = len(bands)
    ncol = 2
    nrow = (nsubplots - 1) // ncol + 1
    if xfigsize is None and yfigsize is None:
        figsize = (4. * ncol, 3. * nrow)
    elif yfigsize is None:
        figsize = (xfigsize, 3. / 4. * nrow / ncol * xfigsize)
    elif xfigsize is None:
        figsize = (4. / 3. * ncol / nrow * yfigsize, yfigsize)
    else:
        raise ValueError('cannot specify both xfigsize and yfigsize')
    fig = plt.figure(figsize=figsize)

    axnum = 0
    for disp, band, bandname in sorted(zip(disps, bands, bandnames)):
        axnum += 1

        idx = data['band'] == bandname
        time = data['time'][idx]
        flux = dataflux[idx]
        fluxerr = datafluxerr[idx]

        color = cmap((disprange[1] - disp) / (disprange[1] - disprange[0]))

        ax = plt.subplot(nrow, ncol, axnum)
        plt.text(0.9, 0.9, bandname, color='k', ha='right', va='top',
                 transform=ax.transAxes)
        if axnum % 2:
            plt.ylabel('flux ($ZP_{AB} = 25$)')

        if model is None:
            plt.errorbar(time, flux, fluxerr, ls='None',
                         color=color, marker='.', markersize=3.)

        if model is not None and model.bandoverlap(band):
            t0 = model.params['t0']
            plt.errorbar(time - t0, flux, fluxerr, ls='None',
                         color=color, marker='.', markersize=3.)

            result = model.bandflux(band, zp=25., zpsys='ab',
                                    include_error=include_model_error)
            if include_model_error:
                modelflux, modelfluxerr = result
            else:
                modelflux = result

            plt.plot(model.times() - t0, modelflux, ls='-', marker='None',
                     color=color)
            if include_model_error:
                plt.fill_between(model.times() - t0, modelflux - modelfluxerr,
                                 modelflux + modelfluxerr, color=color,
                                 alpha=0.2)


            # steal part of the axes and plot pulls
            if show_pulls:
                divider = make_axes_locatable(ax)
                axpulls = divider.append_axes("bottom", size=0.7, pad=0.1,
                                              sharex=ax)
                modelflux = model.bandflux(band, time, zp=25., zpsys='ab') 
                pulls = (flux - modelflux) / fluxerr
                plt.plot(time - t0, pulls, marker='.', markersize=5.,
                         color=color, ls='None')
                plt.axhline(y=0., color=color)
                plt.setp(ax.get_xticklabels(), visible=False)
                plt.xlabel('time - {:.2f}'.format(t0))
                if axnum % 2:
                    plt.ylabel('pull')

            # maximum plot range
            ymin, ymax = ax.get_ylim()
            maxmodelflux = modelflux.max()
            ymin = max(ymin, -0.2 * maxmodelflux)
            ymax = min(ymax, 2. * maxmodelflux)
            ax.set_ylim(ymin, ymax)

    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.97,
                        wspace=0.2, hspace=0.2)
    if fname is None:
        plt.show()
    else:
        plt.savefig(fname, dpi=dpi)
        plt.clf()
