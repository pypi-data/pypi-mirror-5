.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Thu Jul  4 12:22:22 CEST 2013

Wrapper classes for the CSU facerec2010 classes
===============================================

This satellite package to the FaceRecLib_ provides wrapper classes for the `CSU Face Recognition Resources`_.
Two algorithms are provided by the CSU toolkit (and also by this satellite package): the local region PCA (LRPCA) and the LDA-IR (also known as CohortLDA).

In fact, this satallite package just provides the source to be able to execute experiments using LRPCA and LDA-IR.
Though you actually can, this package is not designed to run any face recognition experiment with it.
Please refer to the FaceRecLib_ documentation to get more information on how to use this package to run face recognition experiments.
A working example, which is able to re-run the original LRPCA and LDA-IR experiments, which are reported in [PBD+11]_ and [LBP+12]_, respectively, can be found under `xfacereclib.paper.BeFIT2012 <http://pypi.python.org/pypiu/xfacereclib.paper.BeFIT2012>`_.


.. [PBD+11]        P.J. Phillips, J.R. Beveridge, B.A. Draper, G. Givens, A.J. O'Toole, D.S. Bolme, J. Dunlop, Y.M. Lui, H. Sahibzada and S. Weimer. "An introduction to the good, the bad, & the ugly face recognition challenge problem". Automatic face gesture recognition and workshops (FG 2011), pages 346-353. 2011.
.. [LBP+12]        Y.M. Lui, D. Bolme, P.J. Phillips, J.R. Beveridge and B.A. Draper. "Preliminary studies on the good, the bad, and the ugly face recognition challenge problem". Computer vision and pattern recognition workshops (CVPRW), pages 9-16. 2012.

Code documentation
------------------

.. note::
  If this section is empty, please go to the console and type:

  .. code-block:: sh

    $ bin/sphinx-build docs sphinx

  again, after you have successfully patched the CSU code.

LRPCA
.....

.. automodule:: xfacereclib.extension.CSU.lrpca

LDA-IR
......

.. automodule:: xfacereclib.extension.CSU.ldair


.. _idiap: http://www.idiap.ch
.. _bob: http://www.idiap.ch/software/bob
.. _facereclib: http://www.github.com/bioidiap/facereclib
.. _csu face recognition resources: http://www.cs.colostate.edu/facerec/
.. _github: http://www.github.com/bioidiap/xfacereclib.extension.CSU
.. _buildout.cfg: file:../buildout.cfg
