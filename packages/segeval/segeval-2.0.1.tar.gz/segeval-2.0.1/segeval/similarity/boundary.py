'''
Boundary Similarity (B) package.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
from __future__ import division
from . import __boundary_statistics__, SIMILARITY_METRIC_DEFAULTS
from ..util import __fnc_metric__
from decimal import Decimal


def __boundary_similarity__(*args, **kwargs):
    # pylint: disable=C0103,R0913,R0914
    metric_kwargs = dict(kwargs)
    del metric_kwargs['return_parts']
    del metric_kwargs['one_minus']
    # Arguments
    return_parts = kwargs['return_parts']
    one_minus = kwargs['one_minus']
    # Compute
    statistics = __boundary_statistics__(*args, **metric_kwargs)
    additions = statistics['additions']
    substitutions = statistics['substitutions']
    transpositions = statistics['transpositions']
    count_unweighted = len(additions) + len(substitutions) + len(transpositions)
    # Fraction
    denominator = count_unweighted + len(statistics['matches'])
    numerator   = denominator - statistics['count_edits']
    if return_parts:
        return numerator, denominator, additions, substitutions, transpositions
    else:
        value = numerator / denominator if denominator > 0 else 1
        if one_minus:
            return Decimal('1') - value
        else:
            return value


def boundary_similarity(*args, **kwargs):
    '''
    Computes Boundary Similarity (B)
    '''
    # pylint: disable=W0142
    return __fnc_metric__(__boundary_similarity__, args, kwargs,
                          SIMILARITY_METRIC_DEFAULTS)

