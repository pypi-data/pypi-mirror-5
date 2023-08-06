FaceRecLib Wrapper classes for the CSU Face Recognition Resources
=================================================================

This satellite package to the FaceRecLib provides wrapper classes for the CSU face recognition resources, which can be downloaded from http://www.cs.colostate.edu/facerec.
Two algorithms are provided by the CSU toolkit (and also by this satellite package): the local region PCA (LRPCA) and the LDA-IR (also known as CohortLDA).

For more information about the LRPCA and the LDA-IR algorithm, please refer to the documentation on http://www.cs.colostate.edu/facerec/.
For further information about the FaceRecLib, please read its documentation (see http://github.com/bioidiap/facereclib on how to generate it).
On how to use this package in a face recognition experiment, please see http://github.com/bioidiap/xfacereclib.paper.BeFIT2012


Patching the CSU Face Recognition Resources
-------------------------------------------

The current package is just a set of wrapper classes for the CSU facerec2010 module, which is contained in the `CSU Face Recognition Resources <http://www.cs.colostate.edu/facerec>`_, where you need to download the Baseline 2011 Algorithms.

To be compatible with the FaceRecLib, the CSU toolkit needs to be patched.
If you haven't patched it yet, please follow the set of instructions:

1. Generate the binaries of this package without the CSU toolkit.
   We provide a special buildout configuration file for that::

    $ python bootstrap.py
    $ bin/buildout -c buildout-before-patch.cfg

   This will disable the CSU code for a while.

2. Patch the CSU toolkit by calling::

    $ bin/patch_CSU.py [PATH_TO_YOUR_CSU_COPY]

   If you get any error message, the sources of the CSU might have changed (the latest test was done in December 2012).
   Please file a bug report in `our GitHub page <http://www.github.com/bioidiap/xfacereclib.extension.CSU>`_ to inform us so that we can provide a new patch.


3. Update the CSU toolkit path in the **buildout.cfg** file by changing the 'sources-dir' variable::

    sources-dir = [PATH_TO_YOUR_CSU_COPY]

4. Re-generate the binaries, this time including the CSU toolkit::

    $ bin/buildout


.. note::
  At `Idiap <http://www.idiap.ch>`_ there is a pre-patched version of the CSU toolkit available as a git repository.
  You can simply use::

    $ python bootstrap.py
    $ bin/buildout -c buildout-idiap.cfg

  instead of following the four points above.


.. warning::
  After patching the CSU toolkit, the original experiments of the CSU toolkit will not work any more!
  Maybe it is a good idea to make a save-copy of your CSU copy before applying the patch.


Verifying your installation
---------------------------
After the CSU toolkit is patched, please verify that the installation works as expected.
For this, please run our test environment by calling::

  $ bin/nosetests

Please assure that all 6 tests pass.


Running CSU experiments with the FaceRecLib
-------------------------------------------
The easiest way to run any experiment with the CSU tools is to use the FaceRecLib_ directly.
Please check the documentation in the FaceRecLib_ on how to set up the FaceRecLib to include the CSU algorithms.

One example on how to compare the CSU algorithms to other state-of-the-art algorithms using the FaceRecLib_ is given in our paper::

  @inproceedings{Guenther_BeFIT2012,
         author = {G{\"u}nther, Manuel AND Wallace, Roy AND Marcel, S{\'e}bastien},
         editor = {Fusiello, Andrea AND Murino, Vittorio AND Cucchiara, Rita},
       keywords = {Biometrics, Face Recognition, Open Source, Reproducible Research},
          month = oct,
          title = {An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms},
      booktitle = {Computer Vision - ECCV 2012. Workshops and Demonstrations},
         series = {Lecture Notes in Computer Science},
         volume = {7585},
           year = {2012},
          pages = {547-556},
      publisher = {Springer Berlin},
       location = {Heidelberg},
            url = {http://publications.idiap.ch/downloads/papers/2012/Gunther_BEFIT2012_2012.pdf}
  }

The source code for this paper, which actually uses the FaceRecLib_ and this satellite package, can be found under http://pypi.python.org/pypi/xfacereclib.paper.BeFIT2012.


Documentation
-------------

To generate the documentation of this package, please go to the console and write::

  $ python bootstrap.py
  $ bin/buildout -c buildout-before-patch.cfg
  $ bin/sphinx-build docs sphinx

Due to the face that the setup is not yet perfect, during the last step there might be some warnings or errors.
Still, you should be able to open the documentation using more installation instructions by typing, e.g.::

  $ firefox sphinx/index.html

and follow the further installation and setup instructions.

.. _facereclib: http://pypi.python.org/pypi/facereclib

