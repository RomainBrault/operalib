"""OVK learning, unit tests.

The :mod:`sklearn.tests.test_ONORMA` tests ONORMA regression estimator.
"""

import operalib as ovk
import numpy as np

from sklearn.utils.estimator_checks import check_estimator
from distutils.version import LooseVersion
from warnings import warn

from sklearn.utils.estimator_checks import MULTI_OUTPUT


MULTI_OUTPUT.append('ONORMA')


np.random.seed(0)

n = 100
d = 20
p = 4

X, y = ovk.datasets.toy_data_multitask(n, d, p)


def test_valid_estimator():
    """Test whether ovk.ONORMA is a valid sklearn estimator."""
    from sklearn import __version__
    # Adding patch revision number cause crash
    if LooseVersion(__version__) >= LooseVersion('0.18'):
        check_estimator(ovk.ONORMA)
    else:
        warn('sklearn\'s check_estimator seems to be broken in __version__ <='
             ' 0.17.x... skipping')


def test_learn_ONORMA_Joint():
    """Test ONORMA joint estimator partial_fit, predict."""
    est = ovk.ONORMA('DGauss', A=.8 * np.eye(p) + .2 * np.ones((p, p)),
                     gamma=.25, learning_rate='invscaling',
                     eta=1., power=.5, lbda=0.00001)
    err = np.empty(n)
    err[0] = np.linalg.norm(y[0, :]) ** 2
    est.partial_fit(X[0, :].reshape(1, -1), y[0, :])
    for t in range(1, n):
        err[t] = np.linalg.norm(est.predict(X[t, :].reshape(1, -1)) -
                                y[t, :].reshape(1, -1)) ** 2
        est.partial_fit(X[t, :].reshape(1, -1), y[t, :].reshape(1, -1))
    err_c = np.cumsum(err) / (np.arange(n) + 1)
    assert err_c[-1] < err_c[0]


def test_learn_ONORMA_Indep():
    """Test ONORMA independant estimator partial_fit, predict."""
    est = ovk.ONORMA('DGauss', A=np.eye(p),
                     gamma=.25, learning_rate=ovk.InvScaling(1.),
                     lbda=0.00001)
    err = np.empty(n)
    err[0] = np.linalg.norm(y[0, :]) ** 2
    est.partial_fit(X[0, :].reshape(1, -1), y[0, :])
    for t in range(1, n):
        err[t] = np.linalg.norm(est.predict(X[t, :].reshape(1, -1)) -
                                y[t, :].reshape(1, -1)) ** 2
        est.partial_fit(X[t, :].reshape(1, -1), y[t, :].reshape(1, -1))
    err_c = np.cumsum(err) / (np.arange(n) + 1)
    assert err_c[-1] < err_c[0]


def test_learn_ONORMA_fit():
    """Test ONORMA independant estimator fit, predict."""
    est = ovk.ONORMA('DGauss', A=np.eye(p),
                     gamma=.25, learning_rate=ovk.InvScaling(2.),
                     lbda=0.00001)
    est.fit(X, y)
    assert est.score(X, y) >= 0.5


def test_learn_ONORMA_dot_fit():
    """Test ONORMA DotProduct kernel estimator fit, predict."""
    est = ovk.ONORMA('DotProduct', mu=.4,
                     learning_rate=ovk.InvScaling(.05, .25),
                     lbda=0.00001)
    est.fit(X, y)
    assert est.score(X, y) >= 0.25
