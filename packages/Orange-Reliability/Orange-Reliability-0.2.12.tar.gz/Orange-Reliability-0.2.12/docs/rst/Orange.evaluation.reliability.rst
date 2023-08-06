.. automodule:: Orange.evaluation.reliability

.. index:: Reliability Estimation

.. index::
   single: reliability; Reliability Estimation for Regression

##########################################################
Reliability estimation (``Orange.evaluation.reliability``)
##########################################################

********************************************************
Reliability Estimation for Regression and Classification
********************************************************

Reliability assessment aims to predict reliabilities of individual
predictions. Most of implemented algorithms for regression described in
[Bosnic2008]_ and in [Pevec2011]_ for classification.

We can use reliability estimation with any Orange learners. The following example:

 * Constructs reliability estimators (implemented in this module),
 * The :obj:`Learner` wrapper combines a regular learner, here a :obj:`~Orange.classification.knn.kNNLearner`, with reliability estimators.
 * Obtains prediction probabilities from the constructed classifier
   (:obj:`Orange.classification.Classifier.GetBoth` option). The resulting
   probabilities have an additional attribute, :obj:`reliability_estimate`,
   that contains a list of :class:`Orange.evaluation.reliability.Estimate`.

.. literalinclude:: code/reliability-basic.py
    :lines: 7-

We could also evaluate more examples. The next example prints reliability estimates
for first 10 instances (with cross-validation):

.. literalinclude:: code/reliability-run.py
    :lines: 7-

Reliability estimation wrappers
===============================

.. autoclass:: Learner
   :members: __call__

.. autoclass:: Classifier
   :members: __call__


Reliability Methods
===================

All measures except :math:`O_{ref}` work with regression. Classification is
supported by BAGV, LCV, CNK and DENS, :math:`O_{ref}`.

Sensitivity Analysis (SAvar and SAbias)
---------------------------------------
.. autoclass:: SensitivityAnalysis

Variance of bagged models (BAGV)
--------------------------------
.. autoclass:: BaggingVariance

Local cross validation reliability estimate (LCV)
-------------------------------------------------
.. autoclass:: LocalCrossValidation

Local modeling of prediction error (CNK)
----------------------------------------
.. autoclass:: CNeighbours

Bagging variance c-neighbours (BVCK)
------------------------------------

.. autoclass:: BaggingVarianceCNeighbours(bagv=BaggingVariance(), cnk=CNeighbours())

Mahalanobis distance
--------------------

.. autoclass:: Mahalanobis

Mahalanobis to center
---------------------

.. autoclass:: MahalanobisToCenter

Density estimation using Parzen window (DENS)
---------------------------------------------

.. autoclass:: ParzenWindowDensityBased

Internal cross validation (ICV)
-------------------------------

.. autoclass:: ICV


Stacked generalization (Stacking)
---------------------------------

.. autoclass:: Stacking

Reference Estimate for Classification (:math:`O_{ref}`)
-------------------------------------------------------

.. autoclass:: ReferenceExpectedError

Reliability estimation results
==============================

.. data:: SIGNED
    
.. data:: ABSOLUTE

    These constants distinguish signed and
    absolute reliability estimation measures.

.. data:: METHOD_NAME

    A dictionary that that maps reliability estimation
    method IDs (integerss) to method names (strings).

.. autoclass:: Estimate
    :members:
    :show-inheritance:



Reliability estimation scoring
==============================

.. autofunction:: get_pearson_r

.. autofunction:: get_pearson_r_by_iterations

.. autofunction:: get_spearman_r

Example
=======

The following script prints Pearson's correlation coefficient (r) between reliability 
estimates and actual prediction errors, and a corresponding p-value, for 
default reliability estimation measures. 

.. literalinclude:: code/reliability-long.py
    :lines: 7-22

Results::
  
  Estimate               r       p
  SAvar absolute        -0.077   0.454
  SAbias signed         -0.165   0.105
  SAbias absolute        0.095   0.352
  LCV absolute           0.069   0.504
  BVCK absolute          0.060   0.562
  BAGV absolute          0.078   0.448
  CNK signed             0.233   0.021
  CNK absolute           0.058   0.574
  Mahalanobis absolute   0.091   0.375
  Mahalanobis to center  0.096   0.349

References
==========

.. [Bosnic2007]  Bosnić, Z., Kononenko, I. (2007) `Estimation of individual prediction reliability using local sensitivity analysis. <http://www.springerlink.com/content/e27p2584387532g8/>`_ *Applied Intelligence* 29(3), pp. 187-203.

.. [Bosnic2008] Bosnić, Z., Kononenko, I. (2008) `Comparison of approaches for estimating reliability of individual regression predictions. <http://www.sciencedirect .com/science/article/pii/S0169023X08001080>`_ *Data & Knowledge Engineering* 67(3), pp. 504-516.

.. [Bosnic2010] Bosnić, Z., Kononenko, I. (2010) `Automatic selection of reliability estimates for individual regression predictions. <http://journals.cambridge .org/abstract_S0269888909990154>`_ *The Knowledge Engineering Review* 25(1), pp. 27-47.

.. [Pevec2011] Pevec, D., Štrumbelj, E., Kononenko, I. (2011) `Evaluating Reliability of Single Classifications of Neural Networks. <http://www.springerlink.com /content/48u881761h127r33/export-citation/>`_ *Adaptive and Natural Computing Algorithms*, 2011, pp. 22-30.
