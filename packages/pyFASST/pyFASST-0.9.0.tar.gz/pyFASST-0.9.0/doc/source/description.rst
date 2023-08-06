=======
pyFASST
=======

 :contributors: Jean-Louis Durrieu
 :web: https://git.epfl.ch/repo/pyfasst/ https://github.com/wslihgt/pyfasst

A Python implementation to the Flexible Audio Source Separation Toolbox

Abstract
========
This toolbox is meant to allow to use the framework FASST and extend it within a python program. It is primarily a re-write in Python of the original Matlab (C) version. The object programming framework allows to extend and create new models an easy way, by subclassing the :py:class:`pyfasst.audioModel.FASST` and re-implementing some methods (in particular methods like :py:meth:`pyfasst.audioModel.MultiChanNMFInst_FASST._initialize_structures`)

Using the Python package
========================

Dependencies
------------

Most of the code is written in `Python <http://www.python.org>`_, but occasionally, there may be some C source code, requiring either Cython or SWIG for compiling. In general, to run this code, the required components are:

  * Matplotlib http://matplotlib.sourceforge.net 
  * Numpy http://numpy.scipy.org
  * Scipy http://www.scipy.org
  * setuptool https://pypi.python.org/pypi/setuptools

Install
-------

Unpack the tarball, change directory to it, and run the installation with `setup.py`. Namely:
 1. ``tar xvzf pyFASST-X.Y.Z.tar.gz``
 2. ``cd pyFASST-X.Y.Z``
 3. ``python setup.py build``
 4. [if you want to install it] ``[sudo] python setup.py install [--user]``

In addition to the aforementioned packages, installing this package requires to compile the tracking part, in :py:mod:`pyfasst.SeparateLeadStereo.tracking`. In the corresponding folder, type::

  python setup.py build_ext --inplace

Examples
--------

Using the provided audio model classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have implemented several classes that can be used directly, without the need to re-implement or sub-class :py:class:`pyfasst.audioModel.FASST`. In particular, we have:

 * :py:class:`pyfasst.audioModel.MultiChanNMFInst_FASST`, :py:class:`pyfasst.audioModel.MultiChanNMFConv`, :py:class:`pyfasst.audioModel.MultiChanHMM`: these classes originate from the distributed Matlab version of FASST_. For example, the separation of the voice and the guitar on the `tamy <>` example gives, with a simple model with 2 sources, with instantaneous mixing parameters and NMF model on the spectral parameters (to run from where one can find the `tamy.wav` file) - don't expect very good results!::

    >>> import pyfasst.audioModel as am
    >>> filename = 'data/tamy.wav'
    >>> # initialize the model
    >>> model = am.MultiChanNMFInst_FASST(
            audio=filename,
            nbComps=2, nbNMFComps=32, spatial_rank=1,
            verbose=1, iter_num=50)
    >>> # estimate the parameters
    >>> model.estim_param_a_post_model()
    >>> # separate the sources using these parameters
    >>> model.separate_spat_comps(dir_results='data/')

   Somewhat improving the results could be to use the convolutive mixing parameters::
  
    >>> import pyfasst.audioModel as am
    >>> filename = 'data/tamy.wav'
    >>> # initialize the model
    >>> model = am.MultiChanNMFConv(
            audio=filename,
            nbComps=2, nbNMFComps=32, spatial_rank=1,
            verbose=1, iter_num=50)
    >>> # to be more flexible, the user _has to_ make the parameters
    >>> # convolutive by hand. This way, she can also start to estimate
    >>> # parameters in an instantaneous setting, as an initialization, 
    >>> # and only after "upgrade" to a convolutive setting:
    >>> model.makeItConvolutive()
    >>> # estimate the parameters
    >>> model.estim_param_a_post_model()
    >>> # separate the sources using these parameters
    >>> model.separate_spat_comps(dir_results='data/')

   The following example shows the results for a more synthetic example (synthetis anechoic mixture of the voice and the guitar, with a delay of 0 for the voice and 10 samples from the left to the right channel for the guitar)::

    >>> import pyfasst.audioModel as am
    >>> filename = 'data/dev1__tamy-que_pena_tanto_faz___thetas-0.79,0.79_delays-10.00,0.00.wav'
    >>> # initialize the model
    >>> model = am.MultiChanNMFConv(
            audio=filename,
            nbComps=2, nbNMFComps=32, spatial_rank=1,
            verbose=1, iter_num=200)
    >>> # to be more flexible, the user _has to_ make the parameters
    >>> # convolutive by hand. This way, she can also start to estimate
    >>> # parameters in an instantaneous setting, as an initialization, 
    >>> # and only after "upgrade" to a convolutive setting:
    >>> model.makeItConvolutive()
    >>> # we can initialize these parameters with the DEMIX algorithm:
    >>> model.initializeConvParams(initMethod='demix')
    >>> # and estimate the parameters:
    >>> model.estim_param_a_post_model()
    >>> # separate the sources using these parameters
    >>> model.separate_spat_comps(dir_results='data/')

 * :py:class:`pyfasst.audioModel.multiChanSourceF0Filter`: this class assumes that all the sources share the same spectral shape dictionary and spectral structure, _i.e._ a source/filter model (2 _factors_, in FASST terminology), with a filter spectral shape dictionary generated as a collection of *smooth* windows (overlapping Hann windows), and the source dictionary is computed as a collection of spectral *combs* following a simple vocal glottal model (see [Durrieu2010]_). The advantage of this class is that in terms of memory, all the sources share the same dictionaries. However, that means it makes no sense to modify these dictionaries (at least not individually - which is the case in this algorithm) and they are therefore fixed by default. This class also provides methods that help to initialize the various parameters, assuming the specific structure presented above.

 * :py:class:`pyfasst.audioModel.multichanLead`

 * Additionally, we provide a (not-very-exhaustive) plotting module which helps in displaying some interesting features from the model, such as::

    >>> import pyfasst.tools.plotTools as pt
    >>> # display the estimated spectral components
    >>> # (one per row of subplot)
    >>> pt.subplotsAudioModelSpecComps(model)
    >>> # display a graph showing where the sources have been "spatially"
    >>> # estimated: in an anechoic case, ideally, the graph for the 
    >>> # corresponding source is null everywhere, except at the delay 
    >>> # between the two channels:
    >>> delays, delayDetectionFunc = pt.plotTimeCorrelationMixingParams(model)

TODO: add typical SDR/SIR results for these examples.

Creating a new audio model class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Algorithms
==========

The FASST framework and the audio signal model are described in [Ozerov2012]_. We have implemented this Python version mostly thanks to the provided Matlab (C) code available at http://bass-db.gforge.inria.fr/fasst/. 

For initialization purposes, several side algorithms and systems have also been implemented:
* SIMM model (Smooth Instantaneous Mixture Model) from [Durrieu2010]_ and [Durrieu2011]_: allows to analyze, detect and separate the lead instrument from a polyphonic audio (musical) mixture. Note: the original purpose of this implementation was to provide a sensible way of using information from the SIMM model into the more general multi-channel audio source separation model provided, for instance, by FASST.  It is implemented in the :py:mod:`pyfasst.SeparateLeadStereo.SeparateLeadStereoTF` module.

* DEMIX algorithm (Direction Estimation of Mixing matrIX) [Arberet2010]_ for spatial mixing parameter initialization. It is implemented as the :py:mod:`pyfasst.demixTF` module.

References
==========
.. [Arberet2010] Arberet, S.; Gribonval, R. and Bimbot, F., 
   `A Robust Method to Count and Locate Audio Sources in a Multichannel 
   Underdetermined Mixture`, IEEE Transactions on Signal Processing, 2010, 
   58, 121 - 133. [`web <http://infoscience.epfl.ch/record/150461/>`_]

.. [Durrieu2010] J.-L. Durrieu, G. Richard, B. David and C. F\\'{e}votte, 
   `Source/Filter Model for Main Melody Extraction From Polyphonic Audio 
   Signals`, IEEE Transactions on Audio, Speech and Language Processing, 
   special issue on Signal Models and Representations of Musical and 
   Environmental Sounds, March 2010, Vol. 18 (3), pp. 564 -- 575.

.. [Durrieu2011] J.-L. Durrieu, G. Richard and B. David, 
   `A Musically Motivated Representation For Pitch Estimation And Musical 
   Source Separation <http://www.durrieu.ch/research/jstsp2010.html>`_, 
   IEEE Journal of Selected Topics on Signal Processing, October 2011, 
   Vol. 5 (6), pp. 1180 - 1191.

.. [Ozerov2012] A. Ozerov, E. Vincent, and F. Bimbot, 
   `A general flexible framework for the handling of prior information in audio
   source separation <http://hal.inria.fr/hal-00626962/>`_, 
   IEEE Transactions on Audio, Speech and Signal Processing, Vol.  20 (4), 
   pp. 1118-1133 (2012).

.. _FASST: http://bass-db.gforge.inria.fr/fasst/
