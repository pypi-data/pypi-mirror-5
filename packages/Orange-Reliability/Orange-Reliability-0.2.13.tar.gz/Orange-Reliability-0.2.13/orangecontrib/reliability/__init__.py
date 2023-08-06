import Orange

import random
from Orange import statc
import math
import warnings
import numpy

from collections import defaultdict
from itertools import izip

# All the estimator method constants
SAVAR_ABSOLUTE = 0
SABIAS_SIGNED = 1
SABIAS_ABSOLUTE = 2
BAGV_ABSOLUTE = 3
CNK_SIGNED = 4
CNK_ABSOLUTE = 5
LCV_ABSOLUTE = 6
BVCK_ABSOLUTE = 7
MAHAL_ABSOLUTE = 8
BLENDING_ABSOLUTE = 9
ICV_METHOD = 10
MAHAL_TO_CENTER_ABSOLUTE = 13
DENS_ABSOLUTE = 14
ERR_ABSOLUTE = 15
STACKING = 101

# Type of estimator constant
SIGNED = 0
ABSOLUTE = 1

# Names of all the estimator methods
METHOD_NAME = {0: "SAvar absolute", 1: "SAbias signed", 2: "SAbias absolute",
               3: "BAGV absolute", 4: "CNK signed", 5: "CNK absolute",
               6: "LCV absolute", 7: "BVCK absolute", 8: "Mahalanobis absolute",
               9: "BLENDING absolute", 10: "ICV", 11: "RF Variance", 12: "RF Std",
               13: "Mahalanobis to center", 14: "Density based", 15: "Reference expected error",
               101: "Stacking" }

def get_reliability_estimation_list(res, i):
    return [ result.probabilities[0].reliability_estimate[i].estimate for result in res.results], \
        res.results[0].probabilities[0].reliability_estimate[i].signed_or_absolute, \
        res.results[0].probabilities[0].reliability_estimate[i].method

def get_prediction_error_list(res):
    return [result.actual_class - result.classes[0] for result in res.results]

def get_description_list(res, i):
    return [result.probabilities[0].reliability_estimate[i].text_description for result in res.results]

def get_pearson_r(res):
    """
    :param res: results of evaluation, done using learners,
        wrapped into :class:`Orange.evaluation.reliability.Classifier`.
    :type res: :class:`Orange.evaluation.testing.ExperimentResults`

    Return Pearson's coefficient between the prediction error and each of the
    used reliability estimates. Also, return the p-value of each of
    the coefficients.
    """
    prediction_error = get_prediction_error_list(res)
    results = []
    for i in xrange(len(res.results[0].probabilities[0].reliability_estimate)):
        reliability_estimate, signed_or_absolute, method = get_reliability_estimation_list(res, i)
        try:
            if signed_or_absolute == SIGNED:
                r, p = statc.pearsonr(prediction_error, reliability_estimate)
            else:
                r, p = statc.pearsonr([abs(pe) for pe in prediction_error], reliability_estimate)
        except Exception:
            r = p = float("NaN")
        results.append((r, p, signed_or_absolute, method))
    return results

def get_spearman_r(res):
    """
    :param res: results of evaluation, done using learners,
        wrapped into :class:`Orange.evaluation.reliability.Classifier`.
    :type res: :class:`Orange.evaluation.testing.ExperimentResults`

    Return Spearman's coefficient between the prediction error and each of the
    used reliability estimates. Also, return the p-value of each of
    the coefficients.
    """
    prediction_error = get_prediction_error_list(res)
    results = []
    for i in xrange(len(res.results[0].probabilities[0].reliability_estimate)):
        reliability_estimate, signed_or_absolute, method = get_reliability_estimation_list(res, i)
        try:
            if signed_or_absolute == SIGNED:
                r, p = statc.spearmanr(prediction_error, reliability_estimate)
            else:
                r, p = statc.spearmanr([abs(pe) for pe in prediction_error], reliability_estimate)
        except Exception:
            r = p = float("NaN")
        results.append((r, p, signed_or_absolute, method))
    return results

def get_pearson_r_by_iterations(res):
    """
    :param res: results of evaluation, done using learners,
        wrapped into :class:`Orange.evaluation.reliability.Classifier`.
    :type res: :class:`Orange.evaluation.testing.ExperimentResults`

    Return average Pearson's coefficient over all folds between prediction error
    and each of the used estimates.
    """
    results_by_fold = Orange.evaluation.scoring.split_by_iterations(res)
    number_of_estimates = len(res.results[0].probabilities[0].reliability_estimate)
    number_of_instances = len(res.results)
    number_of_folds = len(results_by_fold)
    results = [0 for _ in xrange(number_of_estimates)]
    sig = [0 for _ in xrange(number_of_estimates)]
    method_list = [0 for _ in xrange(number_of_estimates)]

    for res in results_by_fold:
        prediction_error = get_prediction_error_list(res)
        for i in xrange(number_of_estimates):
            reliability_estimate, signed_or_absolute, method = get_reliability_estimation_list(res, i)
            try:
                if signed_or_absolute == SIGNED:
                    r, _ = statc.pearsonr(prediction_error, reliability_estimate)
                else:
                    r, _ = statc.pearsonr([abs(pe) for pe in prediction_error], reliability_estimate)
            except Exception:
                r = float("NaN")
            results[i] += r
            sig[i] = signed_or_absolute
            method_list[i] = method

    # Calculate p-values
    results = [float(res) / number_of_folds for res in results]
    ps = [p_value_from_r(r, number_of_instances) for r in results]

    return zip(results, ps, sig, method_list)

def p_value_from_r(r, n):
    """
    Calculate p-value from the paerson coefficient and the sample size.
    """
    df = n - 2
    t = r * (df / ((-r + 1.0 + 1e-30) * (r + 1.0 + 1e-30))) ** 0.5
    return statc.betai (df * 0.5, 0.5, df / (df + t * t))


# Distances between two discrete probability distributions
#TODO Document those.
def normalize_both(p, q):
    if not p.normalized:
        p.normalize()
    if not q.normalized:
        q.normalize()
    return p, q

def minkowsky_dist(p, q, m=2):
    p, q = normalize_both(p, q)
    dist = 0
    for i in range(len(p)):
        dist += abs(p[i]-q[i])**m
    return dist**(1./m)

def manhattan_distance(p, q):
    return minkowsky_dist(p, q, m=1)

def euclidean_dist(p, q):
    return minkowsky_dist(p, q, m=2)

def variance_dist(p, q):
    return euclidean_dist(p, q) ** 2

def max_dist(p, q):
    p, q = normalize_both(p, q)
    return max([abs(p[i]-q[i]) for i in range(len(p))])

def hellinger_dist(p, q):
    p, q = normalize_both(p, q)
    dist = 0
    for i in range(len(p)):
        dist += (math.sqrt(p[i])-math.sqrt(q[i])) ** 2
    return dist

def my_log(x):
    return 0 if x == 0 else x * math.log(x)

def kullback_leibler(p, q):
    p, q = normalize_both(p, q)
    dist = 0
    for i in range(len(p)):
        dist += my_log(p[i]-q[i])
    return dist

def cosine(p, q):
    p, q = normalize_both(p, q)
    p, q = [pp for pp in p], [qq for qq in q]
    return 1 - numpy.dot(x,y) / (numpy.linalg.norm(p)*numpy.linalg.norm(q))


class Estimate:
    """
    Reliability estimate. Contains attributes that describe the results of
    reliability estimation.

    .. attribute:: estimate

        A numerical reliability estimate.

    .. attribute:: signed_or_absolute

        Determines whether the method used gives a signed or absolute result.
        Has a value of either :obj:`SIGNED` or :obj:`ABSOLUTE`.

    .. attribute:: method

        An integer ID of reliability estimation method used.

    .. attribute:: method_name

        Name (string) of reliability estimation method used.

    """
    def __init__(self, estimate, signed_or_absolute, method):
        self.estimate = estimate
        self.signed_or_absolute = signed_or_absolute
        self.method = method
        self.method_name = METHOD_NAME[method]
        self.text_description = None

class DescriptiveAnalysis:
    def __init__(self, estimator, desc=["high", "medium", "low"], procentage=[0.00, 0.33, 0.66], name="da"):
        self.desc = desc
        self.procentage = procentage
        self.estimator = estimator
        self.name = name

    def __call__(self, instances, weight=None, **kwds):

        # Calculate borders using cross validation
        res = Orange.evaluation.testing.cross_validation([self.estimator], instances)
        all_borders = []
        for i in xrange(len(res.results[0].probabilities[0].reliability_estimate)):
            estimates, signed_or_absolute, method = get_reliability_estimation_list(res, i)
            sorted_estimates = sorted(abs(x) for x in estimates)
            borders = [sorted_estimates[int(len(estimates) * p) - 1]  for p in self.procentage]
            all_borders.append(borders)

        # Learn on whole train data
        estimator_classifier = self.estimator(instances)

        return DescriptiveAnalysisClassifier(estimator_classifier, all_borders, self.desc)

class DescriptiveAnalysisClassifier:
    def __init__(self, estimator_classifier, all_borders, desc):
        self.estimator_classifier = estimator_classifier
        self.all_borders = all_borders
        self.desc = desc

    def __call__(self, instance, result_type=Orange.core.GetValue):
        predicted, probabilities = self.estimator_classifier(instance, Orange.core.GetBoth)

        for borders, estimate in zip(self.all_borders, probabilities.reliability_estimate):
            estimate.text_description = self.desc[0]
            for lower_border, text_desc in zip(borders, self.desc):
                if estimate.estimate >= lower_border:
                    estimate.text_description = text_desc

        # Return the appropriate type of result
        if result_type == Orange.core.GetValue:
            return predicted
        elif result_type == Orange.core.GetProbabilities:
            return probabilities
        else:
            return predicted, probabilities

class SensitivityAnalysis:
    """
    
    :param e: List of possible :math:`\epsilon` values for SAvar and SAbias
        reliability estimates.
    :type e: list of floats
    
    :rtype: :class:`Orange.evaluation.reliability.SensitivityAnalysisClassifier`
    
    To estimate the reliability of prediction for given instance,
    the learning set is extended with this instance, labeled with
    :math:`K + \epsilon (l_{max} - l_{min})`,
    where :math:`K` denotes the initial prediction,
    :math:`\epsilon` is sensitivity parameter and :math:`l_{min}` and
    :math:`l_{max}` denote lower and the upper bound of the learning
    instances' labels. After computing different sensitivity predictions
    using different values of :math:`\epsilon`, the prediction are combined
    into SAvar and SAbias. SAbias can be used in a signed or absolute form.

    :math:`SAvar = \\frac{\sum_{\epsilon \in E}(K_{\epsilon} - K_{-\epsilon})}{|E|}`

    :math:`SAbias = \\frac{\sum_{\epsilon \in E} (K_{\epsilon} - K ) + (K_{-\epsilon} - K)}{2 |E|}`
    
    
    """
    def __init__(self, e=[0.01, 0.1, 0.5, 1.0, 2.0], name="sa"):
        self.e = e
        self.name = name

    def __call__(self, instances, learner):
        min_value = max_value = instances[0].getclass().value
        for ex in instances:
            if ex.getclass().value > max_value:
                max_value = ex.getclass().value
            if ex.getclass().value < min_value:
                min_value = ex.getclass().value
        return SensitivityAnalysisClassifier(self.e, instances, min_value, max_value, learner)

class SensitivityAnalysisClassifier:
    def __init__(self, e, instances, min_value, max_value, learner):
        self.e = e
        self.instances = instances
        self.max_value = max_value
        self.min_value = min_value
        self.learner = learner

    def __call__(self, instance, predicted, probabilities):
        # Create new dataset
        r_data = Orange.data.Table(self.instances)

        # Create new instance
        modified_instance = Orange.data.Instance(instance)

        # Append it to the data
        r_data.append(modified_instance)

        # Calculate SAvar & SAbias
        SAvar = SAbias = 0

        for eps in self.e:
            # +epsilon
            r_data[-1].setclass(predicted.value + eps * (self.max_value - self.min_value))
            c = self.learner(r_data)
            k_plus = c(instance, Orange.core.GetValue)

            # -epsilon
            r_data[-1].setclass(predicted.value - eps * (self.max_value - self.min_value))
            c = self.learner(r_data)
            k_minus = c(instance, Orange.core.GetValue)
            #print len(r_data)
            #print eps*(self.max_value - self.min_value)
            #print k_plus
            #print k_minus
            # calculate part SAvar and SAbias
            SAvar += k_plus.value - k_minus.value
            SAbias += k_plus.value + k_minus.value - 2 * predicted.value

        SAvar /= len(self.e)
        SAbias /= 2 * len(self.e)

        return [Estimate(SAvar, ABSOLUTE, SAVAR_ABSOLUTE),
                Estimate(SAbias, SIGNED, SABIAS_SIGNED),
                Estimate(abs(SAbias), ABSOLUTE, SABIAS_ABSOLUTE)]



class ReferenceExpectedError:
    """

    :rtype: :class:`Orange.evaluation.reliability.ReferenceExpectedErrorClassifier`

    Reference reliability estimation method for classification [Pevec2011]_:

    :math:`O_{ref} = 2 (\hat y - \hat y ^2) = 2 \hat y (1-\hat y)`,

    where :math:`\hat y` is the estimated probability of the predicted class.

    Note that for this method, in contrast with all others, a greater estimate means lower reliability (greater expected error).

    """
    def __init__(self, name="reference"):
        self.name = name

    def __call__(self, instances, learner):
        classifier = learner(instances)
        return ReferenceExpectedErrorClassifier(classifier)

    
class ReferenceExpectedErrorClassifier:

    def __init__(self, classifier):
        self.classifier = classifier

    def __call__(self, instance, *args):
        y_hat = max(self.classifier(instance, Orange.classification.Classifier.GetProbabilities))
        return [Estimate(2 * y_hat * (1 - y_hat), ABSOLUTE, ERR_ABSOLUTE)]


class BaggingVariance:
    """
    
    :param m: Number of bagging models to be used with BAGV estimate
    :type m: int
    
    :rtype: :class:`Orange.evaluation.reliability.BaggingVarianceClassifier`
    
    :math:`m` different bagging models are constructed and used to estimate
    the value of dependent variable for a given instance. In regression,
    the variance of those predictions is used as a prediction reliability
    estimate.

    :math:`BAGV = \\frac{1}{m} \sum_{i=1}^{m} (K_i - K)^2`

    where :math:`K = \\frac{\sum_{i=1}^{m} K_i}{m}` and :math:`K_i` are
    predictions of individual constructed models. Note that a greater value
    implies greater error.

    For classification, 1 minus the average Euclidean distance between class
    probability distributions predicted by the model, and distributions
    predicted by the individual bagged models, is used as the BAGV reliability
    measure. Note that in this case a greater value implies a better
    prediction.
    
    This reliability measure can run out of memory fast if individual classifiers
    use a lot of memory, as it build m of them, thereby using :math:`m` times memory
    for a single classifier. If instances for measuring predictions
    are given as a parameter, this class can only compute their reliability,
    which saves memory. 

    """
    def __init__(self, m=50, name="bv", randseed=0, for_instances=None):
        """
        for_instances: 
        """
        self.m = m
        self.name = name
        self.select_with_repeat = Orange.core.MakeRandomIndicesMultiple()
        self.select_with_repeat.random_generator = Orange.misc.Random(randseed)
        self.for_instances = for_instances

    def __call__(self, instances, learner):
        classifiers = []

        if instances.domain.class_var.var_type == Orange.feature.Descriptor.Discrete:
            classifier = learner(instances)
        else:
            classifier = None

        for_inst_class = defaultdict(list)
        this_iteration = None
        
        if self.for_instances:
            his = map(_hashable_instance, self.for_instances)

        # Create bagged classifiers using sampling with replacement
        for i in xrange(self.m):
            this_iteration = set()
            selection = self.select_with_repeat(len(instances))
            data = instances.select(selection)
            cl = learner(data)
            if cl:
                if self.for_instances: # predict reliability for testing instances and throw cl away
                    for instance, hi in zip(self.for_instances, his):
                        if hi not in this_iteration:
                            for_inst_class[hi].append(_bagged_value(instance, cl, classifier))
                            this_iteration.add(hi)
                else:
                    classifiers.append(cl)

        return BaggingVarianceClassifier(classifiers, classifier, for_inst_class=dict(for_inst_class))

class BaggingVarianceClassifier:
    def __init__(self, classifiers, classifier=None, for_inst_class=None):
        self.classifiers = classifiers
        self.classifier = classifier
        self.for_inst_class = for_inst_class

    def __call__(self, instance, *args):
        BAGV = 0

        # Calculate the bagging variance
        if self.for_inst_class:
            bagged_values = self.for_inst_class[_hashable_instance(instance)]
        else:
            bagged_values = [ _bagged_value(instance, c, self.classifier) for c in self.classifiers ]

        k = sum(bagged_values) / len(bagged_values)

        BAGV = sum((bagged_value - k) ** 2 for bagged_value in bagged_values) / len(bagged_values)
        if instance.domain.class_var.var_type == Orange.feature.Descriptor.Discrete:
            BAGV = 1 - BAGV

        return [Estimate(BAGV, ABSOLUTE, BAGV_ABSOLUTE)]

def _hashable_instance(instance):
    return tuple(instance[i].value for i in range(len(instance.domain.attributes)))

def _bagged_value(instance, c, classifier):
    if instance.domain.class_var.var_type == Orange.feature.Descriptor.Continuous:
        return c(instance, Orange.core.GetValue).value
    elif instance.domain.class_var.var_type == Orange.feature.Descriptor.Discrete:
        estimate = classifier(instance, Orange.core.GetProbabilities)
        return euclidean_dist(c(instance, Orange.core.GetProbabilities), estimate)


class LocalCrossValidation:
    """

    :param k: Number of nearest neighbours used in LCV estimate
    :type k: int

    :param distance: function that computes a distance between two discrete
        distributions (used only in classification problems). The default
        is Hellinger distance.
    :type distance: function

    :param distance_weighted: for classification reliability estimation,
        use an average distance between distributions, weighted by :math:`e^{-d}`,
        where :math:`d` is the distance between predicted instance and the
        neighbour.

    :rtype: :class:`Orange.evaluation.reliability.LocalCrossValidationClassifier`

    :math:`k` nearest neighbours to the given instance are found and put in
    a separate data set. On this data set, a leave-one-out validation is
    performed. Reliability estimate for regression is then the distance
    weighted absolute prediction error. In classification, 1 minus the average
    distance between the predicted class probability distribution and the
    (trivial) probability distributions of the nearest neighbour.

    If a special value 0 is passed as :math:`k` (as is by default),
    it is set as 1/20 of data set size (or 5, whichever is greater).

    Summary of the algorithm for regression:

    1. Determine the set of k nearest neighours :math:`N = { (x_1, c_1),...,
       (x_k, c_k)}`.
    2. On this set, compute leave-one-out predictions :math:`K_i` and
       prediction errors :math:`E_i = | C_i - K_i |`.
    3. :math:`LCV(x) = \\frac{ \sum_{(x_i, c_i) \in N} d(x_i, x) * E_i }{ \sum_{(x_i, c_i) \in N} d(x_i, x) }`

    """
    def __init__(self, k=0, distance=hellinger_dist, distance_weighted=True, name="lcv"):
        self.k = k
        self.distance = distance
        self.distance_weighted = distance_weighted
        self.name = name

    def __call__(self, instances, learner):
        nearest_neighbours_constructor = Orange.classification.knn.FindNearestConstructor()
        nearest_neighbours_constructor.distanceConstructor = Orange.distance.Euclidean()

        distance_id = Orange.feature.Descriptor.new_meta_id()
        nearest_neighbours = nearest_neighbours_constructor(instances, 0, distance_id)

        if self.k == 0:
            self.k = max(5, len(instances) / 20)

        return LocalCrossValidationClassifier(distance_id, nearest_neighbours, self.k, learner,
            distance=self.distance, distance_weighted=self.distance_weighted)

class LocalCrossValidationClassifier:
    def __init__(self, distance_id, nearest_neighbours, k, learner, **kwds):
        self.distance_id = distance_id
        self.nearest_neighbours = nearest_neighbours
        self.k = k
        self.learner = learner
        for a,b in kwds.items():
            setattr(self, a, b)

    def __call__(self, instance, *args):
        LCVer = 0
        LCVdi = 0

        # Find k nearest neighbors

        knn = [ex for ex in self.nearest_neighbours(instance, self.k)]

        # leave one out of prediction error
        for i in xrange(len(knn)):
            train = knn[:]
            del train[i]

            classifier = self.learner(Orange.data.Table(train))

            if instance.domain.class_var.var_type == Orange.feature.Descriptor.Continuous:
                returned_value = classifier(knn[i], Orange.core.GetValue)
                e = abs(knn[i].getclass().value - returned_value.value)

            elif instance.domain.class_var.var_type == Orange.feature.Descriptor.Discrete:
                returned_value = classifier(knn[i], Orange.core.GetProbabilities)
                probabilities = [knn[i].get_class() == val for val in instance.domain.class_var.values]
                e = self.distance(returned_value, Orange.statistics.distribution.Discrete(probabilities))

            dist = math.exp(-knn[i][self.distance_id]) if self.distance_weighted else 1.0
            LCVer += e * dist
            LCVdi += dist

        LCV = LCVer / LCVdi if LCVdi != 0 else 0
        if math.isnan(LCV):
            LCV = 0.0

        if instance.domain.class_var.var_type == Orange.feature.Descriptor.Discrete:
            LCV = 1 - LCV

        return [ Estimate(LCV, ABSOLUTE, LCV_ABSOLUTE) ]

class CNeighbours:
    """
    
    :param k: Number of nearest neighbours used in CNK estimate
    :type k: int

    :param distance: function that computes a distance between two discrete
        distributions (used only in classification problems). The default
        is Hellinger distance.
    :type distance: function
    
    :rtype: :class:`Orange.evaluation.reliability.CNeighboursClassifier`
    
    For regression, CNK is defined for an unlabeled instance as a difference
    between average label of its nearest neighbours and its prediction. CNK
    can be used as a signed or absolute estimate.
    
    :math:`CNK = \\frac{\sum_{i=1}^{k}C_i}{k} - K`
    
    where :math:`k` denotes number of neighbors, C :sub:`i` denotes neighbours'
    labels and :math:`K` denotes the instance's prediction. Note that a greater
    value implies greater prediction error.

    For classification, CNK is equal to 1 minus the average distance between
    predicted class distribution and (trivial) class distributions of the
    $k$ nearest neighbours from the learning set. Note that in this case
    a greater value implies better prediction.
    
    """
    def __init__(self, k=5, distance=hellinger_dist, name = "cnk"):
        self.k = k
        self.distance = distance
        self.name = name

    def __call__(self, instances, learner):
        nearest_neighbours_constructor = Orange.classification.knn.FindNearestConstructor()
        nearest_neighbours_constructor.distanceConstructor = Orange.distance.Euclidean()

        distance_id = Orange.feature.Descriptor.new_meta_id()
        nearest_neighbours = nearest_neighbours_constructor(instances, 0, distance_id)
        return CNeighboursClassifier(nearest_neighbours, self.k, distance=self.distance)

class CNeighboursClassifier:
    def __init__(self, nearest_neighbours, k, distance):
        self.nearest_neighbours = nearest_neighbours
        self.k = k
        self.distance = distance

    def __call__(self, instance, predicted, probabilities):
        CNK = 0

        # Find k nearest neighbors

        knn = [ex for ex in self.nearest_neighbours(instance, self.k)]

        # average label of neighbors
        if ex.domain.class_var.var_type == Orange.feature.Descriptor.Continuous:
            for ex in knn:
                CNK += ex.getclass().value
            CNK /= self.k
            CNK -= predicted.value

            return [Estimate(CNK, SIGNED, CNK_SIGNED),
                    Estimate(abs(CNK), ABSOLUTE, CNK_ABSOLUTE)]
        elif ex.domain.class_var.var_type == Orange.feature.Descriptor.Discrete:
            knn_l = Orange.classification.knn.kNNLearner(k=self.k)
            knn_c = knn_l(knn)
            for ex in knn:
                CNK -= self.distance(probabilities, knn_c(ex, Orange.classification.Classifier.GetProbabilities))
            CNK /= self.k
            CNK += 1

            return [Estimate(CNK, ABSOLUTE, CNK_ABSOLUTE)]

class Mahalanobis:
    """
    
    :param k: Number of nearest neighbours used in Mahalanobis estimate.
    :type k: int
    
    :rtype: :class:`Orange.evaluation.reliability.MahalanobisClassifier`
    
    Mahalanobis distance reliability estimate is defined as
    `Mahalanobis distance <http://en.wikipedia.org/wiki/Mahalanobis_distance>`_
    to the evaluated instance's :math:`k` nearest neighbours.

    
    """
    def __init__(self, k=3, name="mahalanobis"):
        self.k = k
        self.name = name

    def __call__(self, instances, *args):
        nnm = Orange.classification.knn.FindNearestConstructor()
        nnm.distanceConstructor = Orange.distance.Mahalanobis()

        mid = Orange.feature.Descriptor.new_meta_id()
        nnm = nnm(instances, 0, mid)
        return MahalanobisClassifier(self.k, nnm, mid)

class MahalanobisClassifier:
    def __init__(self, k, nnm, mid):
        self.k = k
        self.nnm = nnm
        self.mid = mid

    def __call__(self, instance, *args):
        mahalanobis_distance = 0

        mahalanobis_distance = sum(ex[self.mid].value for ex in self.nnm(instance, self.k))

        return [ Estimate(mahalanobis_distance, ABSOLUTE, MAHAL_ABSOLUTE) ]

class MahalanobisToCenter:
    """
    :rtype: :class:`Orange.evaluation.reliability.MahalanobisToCenterClassifier`
    
    Mahalanobis distance to center reliability estimate is defined as a
    `Mahalanobis distance <http://en.wikipedia.org/wiki/Mahalanobis_distance>`_
    between the predicted instance and the centroid of the data.

    
    """
    def __init__(self, name="mahalanobis to center"):
        self.name = name

    def __call__(self, instances, *args):
        dc = Orange.core.DomainContinuizer()
        dc.classTreatment = Orange.core.DomainContinuizer.Ignore
        dc.continuousTreatment = Orange.core.DomainContinuizer.NormalizeBySpan
        dc.multinomialTreatment = Orange.core.DomainContinuizer.NValues

        new_domain = dc(instances)
        new_instances = instances.translate(new_domain)

        X, _, _ = new_instances.to_numpy()
        instance_avg = numpy.average(X, 0)

        distance_constructor = Orange.distance.Mahalanobis()
        distance = distance_constructor(new_instances)

        average_instance = Orange.data.Instance(new_instances.domain, list(instance_avg) + ["?"])

        return MahalanobisToCenterClassifier(distance, average_instance, new_domain)

class MahalanobisToCenterClassifier:
    def __init__(self, distance, average_instance, new_domain):
        self.distance = distance
        self.average_instance = average_instance
        self.new_domain = new_domain

    def __call__(self, instance, *args):

        inst = Orange.data.Instance(self.new_domain, instance)

        mahalanobis_to_center = self.distance(inst, self.average_instance)

        return [ Estimate(mahalanobis_to_center, ABSOLUTE, MAHAL_TO_CENTER_ABSOLUTE) ]


class BaggingVarianceCNeighbours:
    """
    
    :param bagv: Instance of Bagging Variance estimator.
    :type bagv: :class:`BaggingVariance`
    
    :param cnk: Instance of CNK estimator.
    :type cnk: :class:`CNeighbours`
    
    :rtype: :class:`Orange.evaluation.reliability.BaggingVarianceCNeighboursClassifier`
    
    BVCK is an average of Bagging variance and local modeling of
    prediction error.
    
    """
    def __init__(self, bagv=None, cnk=None, name="bvck"):
        if bagv is None:
            bagv = BaggingVariance()
        if cnk is None:
            cnk = CNeighbours()
        self.bagv = bagv
        self.cnk = cnk
        self.name = "bvck"

    def __call__(self, instances, learner):
        bagv_classifier = self.bagv(instances, learner)
        cnk_classifier = self.cnk(instances, learner)
        return BaggingVarianceCNeighboursClassifier(bagv_classifier, cnk_classifier)

class BaggingVarianceCNeighboursClassifier:
    def __init__(self, bagv_classifier, cnk_classifier):
        self.bagv_classifier = bagv_classifier
        self.cnk_classifier = cnk_classifier

    def __call__(self, instance, predicted, probabilities):
        bagv_estimates = self.bagv_classifier(instance, predicted, probabilities)
        cnk_estimates = self.cnk_classifier(instance, predicted, probabilities)

        bvck_value = (bagv_estimates[0].estimate + cnk_estimates[1].estimate) / 2
        bvck_estimates = [ Estimate(bvck_value, ABSOLUTE, BVCK_ABSOLUTE) ]
        bvck_estimates.extend(bagv_estimates)
        bvck_estimates.extend(cnk_estimates)
        return bvck_estimates

class ErrorPredicting:
    def __init__(self, name = "ep"):
        self.name = name

    def __call__(self, instances, learner):
        res = Orange.evaluation.testing.cross_validation([learner], instances)
        prediction_errors = get_prediction_error_list(res)

        new_domain = Orange.data.Domain(instances.domain.attributes, Orange.core.FloatVariable("pe"))
        new_dataset = Orange.data.Table(new_domain, instances)

        for instance, prediction_error in izip(new_dataset, prediction_errors):
            instance.set_class(prediction_error)

        rf = Orange.ensemble.forest.RandomForestLearner()
        rf_classifier = rf(new_dataset)

        return ErrorPredictingClassification(rf_classifier, new_domain)

class ErrorPredictingClassification:
    def __init__(self, rf_classifier, new_domain):
        self.rf_classifier = rf_classifier
        self.new_domain = new_domain

    def __call__(self, instance, predicted, probabilities):
        new_instance = Orange.data.Instance(self.new_domain, instance)
        value = self.rf_classifier(new_instance, Orange.core.GetValue)

        return [Estimate(value.value, SIGNED, SABIAS_SIGNED)]

def gauss_kernel(x, sigma=1):
    return 1./(sigma*math.sqrt(2*math.pi)) * math.exp(-1./2*(x/sigma)**2)

class ParzenWindowDensityBased:
    """
    :param K: kernel function. Default: gaussian.
    :type K: function

    :param d_measure: distance measure for inter-instance distance.
    :type d_measure: :class:`Orange.distance.DistanceConstructor`

    :rtype: :class:`Orange.evaluation.reliability.ParzenWindowDensityBasedClassifier`

    Returns a value that estimates a density of problem space around the
    instance being predicted.
    """
    def __init__(self, K=gauss_kernel, d_measure=Orange.distance.Euclidean(), name="density"):
        self.K = K
        self.d_measure = d_measure
        self.name = name

    def __call__(self, instances, learner):

        self.distance = self.d_measure(instances)

        def density(x):
            l, dens = len(instances), 0
            for ex in instances:
                dens += self.K(self.distance(x,ex))
            return dens / l

        max_density = max([density(ex) for ex in instances])

        return ParzenWindowDensityBasedClassifier(density, max_density)

class ParzenWindowDensityBasedClassifier:

    def __init__(self, density, max_density):
        self.density = density
        self.max_density = max_density


    def __call__(self, instance, *args):

        DENS = self.max_density-self.density(instance)

        return [Estimate(DENS, ABSOLUTE, DENS_ABSOLUTE)]


def _normalize(data):
    dc = Orange.core.DomainContinuizer()
    dc.classTreatment = Orange.core.DomainContinuizer.Ignore
    dc.continuousTreatment = Orange.core.DomainContinuizer.NormalizeByVariance
    domain = dc(data)
    data = data.translate(domain)
    return data

class _NormalizedLearner(Orange.classification.Learner):
    """
    Wrapper for normalization.
    """
    def __init__(self, learner):
        self.learner = learner

    def __call__(self, data, *args, **kwargs):
        return self.learner(_normalize(data), *args, **kwargs)

class Stacking:
    """

    This methods develops a model that integrates reliability estimates
    from all available reliability scoring techniques. To develop such
    model it needs to performs internal cross-validation, similarly to :class:`ICV`.

    :param stack_learner: a data modelling method. Default (if None): unregularized linear regression with prior normalization.
    :type stack_learner: :obj:`Orange.classification.Learner` 

    :param estimators: Reliability estimation methods to choose from. Default (if None): :class:`SensitivityAnalysis`, :class:`LocalCrossValidation`, :class:`BaggingVarianceCNeighbours`, :class:`Mahalanobis`, :class:`MahalanobisToCenter`.
    :type estimators: :obj:`list` of reliability estimators
 
    :param folds: The number of fold for cross validation (default 10).
    :type box_learner: :obj:`int`

    :param save_data: If True, save the data used for training the
        model for intergration into resulting classifier's .data attribute (default False).
    :type box_learner: :obj:`bool`
 
    """
 
    def __init__(self, 
        stack_learner=None, 
        estimators=None, 
        folds=10, 
        save_data=False):
        self.stack_learner = stack_learner
        self.estimators = estimators
        self.folds = folds
        self.save_data = save_data
        if self.stack_learner is None:
            self.stack_learner=_NormalizedLearner(Orange.regression.linear.LinearRegressionLearner(ridge_lambda=0.0))
        if self.estimators is None:
             self.estimators = [SensitivityAnalysis(),
                           LocalCrossValidation(),
                           BaggingVarianceCNeighbours(),
                           Mahalanobis(),
                           MahalanobisToCenter()]
    
    def __call__(self, data, learner):

        newfeatures = None
        
        if self.folds > 1:

            cvi = Orange.data.sample.SubsetIndicesCV(data, self.folds)
            data_cv = [ None ] * len(data)
            for f in set(cvi): #for each fold
                learn = data.select(cvi, f, negate=True)
                test = data.select(cvi, f)

                #learn reliability estimates for the learning set
                lf = Learner(learner, estimators=self.estimators)(learn)
                
                #pos is used to retain the order of instances
                for ex, pos in zip(test, [ i for i,n in enumerate(cvi) if n == f ]):
                    pred = lf(ex, Orange.core.GetBoth)
                    re = pred[1].reliability_estimate
                    names = [ e.method_name for e in re ]
                    assert newfeatures is None or names == newfeatures
                    newfeatures = names
                    estimates = [ abs(e.estimate) for e in re ]
                    error = ex[-1].value - pred[0].value
                    data_cv[pos] = estimates + [ abs(error) ]

        else:
 
            #use half of the data to learn reliability estimates
            #and the other half for induction of a stacking classifier
            cvi = Orange.data.sample.SubsetIndicesCV(data, 2)
            data_cv = []

            learn = data.select(cvi, 0, negate=True)
            test = data.select(cvi, 0)

            #learn reliability estimates for the learning set
            lf = Learner(learner, estimators=self.estimators)(learn)
            
            for ex in test:
                pred = lf(ex, Orange.core.GetBoth)
                re = pred[1].reliability_estimate
                names = [ e.method_name for e in re ]
                assert newfeatures is None or names == newfeatures
                newfeatures = names
                estimates = [ abs(e.estimate) for e in re ]
                error = ex[-1].value - pred[0].value
                data_cv.append(estimates + [ abs(error) ])

        lf = None

        #induce the classifier on cross-validated reliability estimates
        newfeatures = [ Orange.feature.Continuous(name=n) for n in newfeatures ]
        newdomain = Orange.data.Domain(newfeatures, Orange.feature.Continuous(name="error"))
        classifier_data = Orange.data.Table(newdomain, data_cv)
        stack_classifier = self.stack_learner(classifier_data)

        #induce reliability estimates on the whole data set
        lf = Learner(learner, estimators=self.estimators)(data)

        return StackingClassifier(stack_classifier, lf, newdomain, data=classifier_data if self.save_data else None)


class StackingClassifier:

    def __init__(self, stacking_classifier, reliability_classifier, domain, data=None):
        self.stacking_classifier = stacking_classifier
        self.domain = domain
        self.reliability_classifier = reliability_classifier
        self.data = data

    def convert(self, instance):
        """ Return example in the space of reliability estimates. """
        re = self.reliability_classifier(instance, Orange.core.GetProbabilities).reliability_estimate
        #take absolute values for all
        tex = [ abs(e.estimate) for e in re ] + [ "?" ]
        tex =  Orange.data.Instance(self.domain, tex)
        return tex

    def __call__(self, instance, *args):
        tex = self.convert(instance)
        r = self.stacking_classifier(tex)
        r = float(r)
        r = max(0., r)
        return [ Estimate(r, ABSOLUTE, STACKING) ]

class ICV:
    """ Selects the best reliability estimator for
    the given data with internal cross validation [Bosnic2010]_.

    :param estimators: reliability estimation methods to choose from. Default (if None): :class:`SensitivityAnalysis`, :class:`LocalCrossValidation`, :class:`BaggingVarianceCNeighbours`, :class:`Mahalanobis`, :class:`MahalanobisToCenter` ]
    :type estimators: :obj:`list` of reliability estimators
 
    :param folds: The number of fold for cross validation (default 10).
    :type box_learner: :obj:`int`
 
    """
  
    def __init__(self, estimators=None, folds=10):
        self.estimators = estimators
        if self.estimators is None:
             self.estimators = [SensitivityAnalysis(),
                           LocalCrossValidation(),
                           BaggingVarianceCNeighbours(),
                           Mahalanobis(),
                           MahalanobisToCenter()]
        self.folds = folds
    
    def __call__(self, data, learner):

        cvi = Orange.data.sample.SubsetIndicesCV(data, self.folds)
        sum_of_rs = defaultdict(float)
        n_rs = defaultdict(int)

        elearner = Learner(learner, estimators=self.estimators)

        #average correlations from each fold
        for f in set(cvi):
            learn = data.select(cvi, f, negate=True)
            test = data.select(cvi, f)

            res = Orange.evaluation.testing.learn_and_test_on_test_data([elearner], learn, test)
            results = get_pearson_r(res)
    
            for r, p, sa, method in results:
                if not math.isnan(r): #ignore NaN values
                    sum_of_rs[(method, sa)] += r 
                    n_rs[(method, sa)] += 1 

        avg_rs = [ (k,(sum_of_rs[k]/n_rs[k])) for k in sum_of_rs ]

        avg_rs = sorted(avg_rs, key=lambda estimate: estimate[1], reverse=True)
        chosen = avg_rs[0][0]

        lf = elearner(data)
        return ICVClassifier(chosen, lf)


class ICVClassifier:

    def __init__(self, chosen, reliability_classifier):
        self.chosen = chosen
        self.reliability_classifier = reliability_classifier

    def __call__(self, instance, *args):
        re = self.reliability_classifier(instance, Orange.core.GetProbabilities).reliability_estimate
        for e in re:
            if e.method == self.chosen[0] and e.signed_or_absolute == self.chosen[1]:
                r = e.estimate

        return [ Estimate(r, self.chosen[1], ICV_METHOD) ]

class Learner:
    """
    Adds reliability estimation to any learner: multiple reliability estimation 
    algorithms can be used simultaneously.
    This learner can be used as any other learner,
    but returns the classifier wrapped into an instance of
    :class:`Orange.evaluation.reliability.Classifier`.
    
    :param box_learner: Learner to wrap into a reliability estimation
        classifier.
    :type box_learner: :obj:`~Orange.classification.Learner`
    
    :param estimators: List of reliability estimation methods. Default (if None): :class:`SensitivityAnalysis`, :class:`LocalCrossValidation`, :class:`BaggingVarianceCNeighbours`, :class:`Mahalanobis`, :class:`MahalanobisToCenter`.
    :type estimators: :obj:`list` of reliability estimators
    
    :param name: Name of this reliability learner.
    :type name: string
    
    :rtype: :class:`Orange.evaluation.reliability.Learner`
    """
    def __init__(self, box_learner, name="Reliability estimation",
                 estimators=None,
                 **kwds):
        self.__dict__.update(kwds)
        self.name = name
        self.estimators = estimators
        if self.estimators is None:
             self.estimators = [SensitivityAnalysis(),
                           LocalCrossValidation(),
                           BaggingVarianceCNeighbours(),
                           Mahalanobis(),
                           MahalanobisToCenter()]
 
        self.box_learner = box_learner
        self.blending = False


    def __call__(self, instances, weight=None, **kwds):
        """Learn from the given table of data instances.
        
        :param instances: Data to learn from.
        :type instances: Orange.data.Table
        :param weight: Id of meta attribute with weights of instances
        :type weight: int

        :rtype: :class:`Orange.evaluation.reliability.Classifier`
        """

        blending_classifier = None
        new_domain = None

#        if instances.domain.class_var.var_type != Orange.feature.Continuous.Continuous:
#            raise Exception("This method only works on data with continuous class.")

        return Classifier(instances, self.box_learner, self.estimators, self.blending, new_domain, blending_classifier)
 
class Classifier:
    """
    A reliability estimation wrapper for classifiers. 
    The returned probabilities contain an
    additional attribute :obj:`reliability_estimate`, which is a list of
    :class:`~Orange.evaluation.reliability.Estimate` (see :obj:`~Classifier.__call__`).
    """

    def __init__(self, instances, box_learner, estimators, blending, blending_domain, rf_classifier, **kwds):
        self.__dict__.update(kwds)
        self.instances = instances
        self.box_learner = box_learner
        self.estimators = estimators
        self.blending = blending
        self.blending_domain = blending_domain
        self.rf_classifier = rf_classifier

        # Train the learner with original data
        self.classifier = box_learner(instances)

        # Train all the estimators and create their classifiers
        self.estimation_classifiers = [estimator(instances, box_learner) for estimator in estimators]

    def __call__(self, instance, result_type=Orange.core.GetValue):
        """
        Classify and estimate reliability of estimation for a new instance.
        When :obj:`result_type` is set to
        :obj:`Orange.classification.Classifier.GetBoth` or
        :obj:`Orange.classification.Classifier.GetProbabilities`,
        an additional attribute :obj:`reliability_estimate`
        (a list of :class:`~Orange.evaluation.reliability.Estimate`)
        is added to the distribution object.
        
        :param instance: instance to be classified.
        :type instance: :class:`Orange.data.Instance`
        :param result_type: :class:`Orange.classification.Classifier.GetValue` or \
              :class:`Orange.classification.Classifier.GetProbabilities` or
              :class:`Orange.classification.Classifier.GetBoth`
        
        :rtype: :class:`Orange.data.Value`, 
              :class:`Orange.statistics.Distribution` or a tuple with both
        """
        predicted, probabilities = self.classifier(instance, Orange.core.GetBoth)

        # Create a place holder for estimates
        if probabilities is None:
            probabilities = Orange.statistics.distribution.Continuous()
        #with warnings.catch_warnings():
        #    warnings.simplefilter("ignore")
        probabilities.setattr('reliability_estimate', [])

        # Calculate all the estimates and add them to the results
        for estimate in self.estimation_classifiers:
            probabilities.reliability_estimate.extend(estimate(instance, predicted, probabilities))

        # Return the appropriate type of result
        if result_type == Orange.core.GetValue:
            return predicted
        elif result_type == Orange.core.GetProbabilities:
            return probabilities
        else:
            return predicted, probabilities

# Functions for testing and plotting
#TODO Document those.
def get_acc_rel(method, data, learner):
    estimators = [method]
    reliability = Orange.evaluation.reliability.Learner(learner, estimators=estimators)
    #results = Orange.evaluation.testing.leave_one_out([reliability], data)
    results = Orange.evaluation.testing.cross_validation([reliability], data)

    rels, acc = [], []

    for res in results.results:
        rels.append(res.probabilities[0].reliability_estimate[0].estimate)
        acc.append(res.probabilities[0][res.actual_class])

    return rels, acc


def rel_acc_plot(rels, acc, file_name=None, colors=None):

    import matplotlib.pylab as plt
    
    if colors is None:
        colors = "k"
    plt.scatter(rels, acc, c=colors)
    plt.xlim(0.,1.)
    plt.ylim(ymin=0.)
    plt.xlabel("Reliability")
    plt.ylabel("Accuracy")
    if file_name is None:
        plt.show()
    else:
        plt.savefig(file_name)

def rel_acc_compute_plot(method, data, learner, file_name=None, colors=None):

    plt.clf()

    rels, acc = get_acc_rel(method, data, learner)
    el_acc_plot(acc, rels, file_name=file_name, colors=colors)
    

def acc_rel_correlation(method, data, learner):
    import scipy.stats
    rels, acc = get_acc_rel(method, data, learner)
    return scipy.stats.spearmanr(acc, rels)[0]
