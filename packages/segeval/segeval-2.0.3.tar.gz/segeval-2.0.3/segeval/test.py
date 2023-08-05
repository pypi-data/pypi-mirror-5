'''
Tests overall package functions and classes.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
import unittest
from decimal import Decimal
import segeval
from segeval import (KAZANTSEVA2012_G5, actual_agreement_linear,
    artstein_poesio_bias_linear, fleiss_kappa_linear, fleiss_pi_linear,
    precision, recall, pk, window_diff, summarize, fmeasure,
    boundary_confusion_matrix, boundary_statistics, boundary_edit_distance,
    compute_window_size, boundary_string_from_masses,
    convert_positions_to_masses, convert_masses_to_positions)


class TestModule(unittest.TestCase):
    '''
    Test module loading.
    '''
    #pylint: disable=R0904,C0103
    def test_dir(self):
        self.assertEquals(set(dir(segeval)),
            set(['Average', 'BoundaryFormat', 'COMPLETE_AGREEMENT',
             'ConfusionMatrix', 'Dataset', 'Field', 'KAZANTSEVA2012_G2',
             'KAZANTSEVA2012_G5', 'LARGE_DISAGREEMENT', 'HYPOTHESIS_STARGAZER',
             'HEARST_1997_STARGAZER', '__all__', '__doc__',
             '__docformat__', '__file__', '__name__', '__package__',
             '__path__', '__path__', '__project__', '__version__', 'actual_agreement_linear',
             'artstein_poesio_bias_linear', 'boundary_confusion_matrix',
             'boundary_edit_distance', 'boundary_statistics',
             'boundary_similarity', 'segmentation_similarity',
             'boundary_string_from_masses', 'compute_window_size',
             'convert_masses_to_positions', 'convert_positions_to_masses',
             'fleiss_kappa_linear', 'fleiss_pi_linear', 'fmeasure',
             'input_linear_mass_json', 'input_linear_mass_tsv',
             'load_nested_folders_dict', 'output_linear_mass_json', 'pk',
             'precision', 'recall', 'summarize', 'weight_t', 'weight_s_scale',
             'weight_t_scale', 'weight_s', 'weight_a', 'window_diff']))

    def test_get_attr(self):
        self.assertEquals(segeval.__getattr__('__package__'), 'segeval')


class TestExamples(unittest.TestCase):
    '''
    Example of segeval function usage.
    '''
    #pylint: disable=R0904,C0103

    masses_an1 = KAZANTSEVA2012_G5['ch1']['an1']
    masses_an2 = KAZANTSEVA2012_G5['ch1']['an2']

    
    def test_actual_agreement_linear(self):
        '''
        Test actual_agreement_linear.
        '''
        #pylint: disable=C0324

        self.assertAlmostEquals(Decimal('0.25645756'),
            actual_agreement_linear(KAZANTSEVA2012_G5))

    
    def test_artstein_poesio_bias_linear(self):
        '''
        Test artstein_poesio_bias_linear.
        '''
        #pylint: disable=C0324

        self.assertAlmostEquals(Decimal('0.00841453'),
            artstein_poesio_bias_linear(KAZANTSEVA2012_G5))

    
    def test_fleiss_kappa_linear(self):
        '''
        Test fleiss_kappa_linear.
        '''
        #pylint: disable=C0324

        self.assertAlmostEquals(Decimal('0.23740302'),
            fleiss_kappa_linear(KAZANTSEVA2012_G5))

    
    def test_fleiss_pi_linear(self):
        '''
        Test fleiss_pi_linear.
        '''
        #pylint: disable=C0324

        self.assertAlmostEquals(Decimal('0.23076438'),
            fleiss_pi_linear(KAZANTSEVA2012_G5))

    
    def test_precision(self):
        '''
        Test precision.
        '''
        #pylint: disable=C0324
        cm = boundary_confusion_matrix(self.masses_an1, self.masses_an2)
        self.assertAlmostEquals(Decimal('0.14285714'), precision(cm))

    
    def test_recall(self):
        '''
        Test recall.
        '''
        #pylint: disable=C0324
        cm = boundary_confusion_matrix(self.masses_an1, self.masses_an2)
        self.assertAlmostEquals(Decimal('0.14285714'), recall(cm))

    
    def test_fmeasure(self):
        '''
        Test fmeasure.
        '''
        #pylint: disable=C0324
        cm = boundary_confusion_matrix(self.masses_an1, self.masses_an2)
        self.assertAlmostEquals(Decimal('0.25000000'), fmeasure(cm))

    
    def test_boundary_statistics(self):
        '''
        Test boundary_statistics.
        '''
        #pylint: disable=C0324
        self.assertEquals(24, len(boundary_statistics(KAZANTSEVA2012_G5)))


    def test_boundary_edit_distance(self):
        '''
        Test boundary_edit_distance.
        '''
        #pylint: disable=C0324
        edits = ([(1, 'b'), (1, 'b'), (1, 'b')], [], [(9, 10, 1)])
        self.assertEquals(edits, boundary_edit_distance(
            boundary_string_from_masses(self.masses_an1),
            boundary_string_from_masses(self.masses_an2)))

    
    def test_compute_window_size(self):
        '''
        Test compute_window_size.
        '''
        #pylint: disable=C0324
        self.assertEquals(3, compute_window_size(self.masses_an1))
        self.assertEquals(3, compute_window_size(KAZANTSEVA2012_G5))

    
    def test_pk(self):
        '''
        Test pk.
        '''
        #pylint: disable=C0324
        mean, std, var, stderr, count = \
            summarize(pk(KAZANTSEVA2012_G5))
        self.assertAlmostEquals(Decimal('0.35530058'), mean)
        self.assertAlmostEquals(Decimal('0.11001760'), std)
        self.assertAlmostEquals(Decimal('0.01210387'), var)
        self.assertAlmostEquals(Decimal('0.01587967'), stderr)
        self.assertEquals(48, count)

    
    def test_window_diff(self):
        '''
        Test window_diff.
        '''
        #pylint: disable=C0324
        mean, std, var, stderr, count = \
            summarize(window_diff(KAZANTSEVA2012_G5))
        self.assertAlmostEquals(Decimal('0.42514977'), mean)
        self.assertAlmostEquals(Decimal('0.14960495'), std)
        self.assertAlmostEquals(Decimal('0.02238164'), var)
        self.assertAlmostEquals(Decimal('0.02159361'), stderr)
        self.assertEquals(48, count)

    
    def test_boundary_string_from_masses(self):
        '''
        Test boundary_string_from_masses.
        '''
        #pylint: disable=C0324

        self.assertEquals((
            frozenset([]), frozenset([]), frozenset([]), frozenset([]),
            frozenset([]), frozenset([]), frozenset([]), frozenset([]),
            frozenset([]), frozenset([]), frozenset([1]), frozenset([])),
            boundary_string_from_masses(self.masses_an1))


    def test_convert_positions_to_masses(self):
        '''
        Test convert_positions_to_masses.
        '''
        #pylint: disable=C0324
        self.assertEquals((4,2), convert_positions_to_masses([1,1,1,1,2,2]))


    def test_convert_masses_to_positions(self):
        '''
        Test convert_masses_to_positions.
        '''
        #pylint: disable=C0324

        self.assertAlmostEquals((1,1,1,1,2,2),
            convert_masses_to_positions((4,2)))
