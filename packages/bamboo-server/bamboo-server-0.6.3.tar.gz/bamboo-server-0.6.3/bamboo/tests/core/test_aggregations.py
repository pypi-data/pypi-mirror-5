from collections import defaultdict
import pickle

import numpy as np

from bamboo.tests.core.test_calculator import TestCalculator


AGG_CALCS_TO_DEPS = {
    'pearson(gps_latitude, amount)': ['gps_latitude', 'amount'],
    'var(amount)': ['amount'],
    'std(amount)': ['amount'],
    'max(amount)': ['amount'],
    'mean(amount)': ['amount'],
    'median(amount)': ['amount'],
    'min(amount)': ['amount'],
    'sum(amount)': ['amount'],
    'sum(gps_latitude)': ['gps_latitude'],
    'ratio(amount, gps_latitude)': ['amount', 'gps_latitude'],
    'sum(risk_factor in ["low_risk"])': ['risk_factor'],
    'ratio(risk_factor in ["low_risk"], risk_factor in ["low_risk",'
    ' "medium_risk"])': ['risk_factor'],
    'ratio(risk_factor in ["low_risk"], 1)': ['risk_factor'],
    'count(risk_factor in ["low_risk"])': ['risk_factor'],
    'count()': [],
    'argmax(submit_date)': ['submit_date'],
    'newest(submit_date, amount)': ['amount', 'submit_date'],
}


class TestAggregations(TestCalculator):

    AGGREGATION_RESULTS = {
        'var(amount)': 132918.536184,
        'std(amount)': 364.57994,
        'max(amount)': 1600,
        'mean(amount)': 105.65789473684211,
        'median(amount)': 12,
        'min(amount)': 2.0,
        'sum(amount)': 2007.5,
        'sum(gps_latitude)': 624.089497667,
        'ratio(amount, gps_latitude)': 3.184639,
        'sum(risk_factor in ["low_risk"])': 18,
        'ratio(risk_factor in ["low_risk"], risk_factor in ["low_risk",'
        ' "medium_risk"])': 18.0 / 19,
        'ratio(risk_factor in ["low_risk"], 1)': 18.0 / 19,
        'count()': 19.0,
        'count(risk_factor in ["low_risk"])': 18.0,
        'argmax(submit_date)': 18.0,
        'newest(submit_date, amount)': 28.0,
        'pearson(gps_latitude, amount)': -0.67643,
    }

    GROUP_TO_RESULTS = {
        'food_type':
        pickle.load(
            open('tests/fixtures/good_eats_agg_group_food_type.pkl', 'rb')),
        'food_type,rating':
        pickle.load(
            open('tests/fixtures/good_eats_agg_group_food_type_rating.pkl',
                 'rb')),
    }

    def setUp(self):
        TestCalculator.setUp(self)
        self.calculations = AGG_CALCS_TO_DEPS.keys()
        self.expected_length = defaultdict(int)
        self.groups_list = None

    def _offset_for_formula(self, formula, num_columns):
        if formula[:4] in ['mean', 'rati']:
            num_columns += 2
        elif formula[:7] == 'pearson':
            num_columns += 1

        return num_columns

    def _get_initial_len(self, formula, groups_list):
        initial_len = 0 if self.group == '' else len(groups_list)
        return self._offset_for_formula(formula, initial_len)

    def _columns_per_aggregation(self, formula, initial_num_columns=1):
        return self._offset_for_formula(formula, initial_num_columns)

    def _calculations_to_results(self, formula, row):
        if self.group:
            res = self.GROUP_TO_RESULTS[self.group][formula]
            column = row[self.groups_list[0]] if len(self.groups_list) <= 1\
                else tuple([row[group] for group in self.groups_list])
            res = res[column]
            return res
        else:
            return self.AGGREGATION_RESULTS[formula]

    def _test_calculation_results(self, name, formula):
        self.expected_length[self.group] += self._columns_per_aggregation(
            formula)

        # retrieve linked dataset
        linked_dset = self.dataset.aggregated_dataset(self.group)
        self.assertFalse(linked_dset is None)
        linked_dframe = linked_dset.dframe()

        name = linked_dset.schema.labels_to_slugs[name]

        self.assertTrue(name in linked_dframe.columns)
        self.assertEqual(len(linked_dframe.columns),
                         self.expected_length[self.group])

        # test that the schema is up to date
        self.assertTrue(linked_dset.SCHEMA in linked_dset.record.keys())
        self.assertTrue(isinstance(linked_dset.schema, dict))
        schema = linked_dset.schema

        # test slugified column names
        column_names = [name]
        if self.groups_list:
            column_names.extend(self.groups_list)
        for column_name in column_names:
            self.assertTrue(column_name in schema.keys())

        for idx, row in linked_dframe.iterrows():
            result = np.float64(row[name])
            stored = self._calculations_to_results(formula, row)
            # np.nan != np.nan, continue if we have two nan values
            if np.isnan(result) and np.isnan(stored):
                continue
            msg = self._equal_msg(result, stored, formula)
            self.assertAlmostEqual(result, stored, self.places, msg)

    def _test_aggregation(self):
        if self.group:
            self.groups_list = self.dataset.split_groups(self.group)
            self.expected_length[self.group] += len(self.groups_list)
        else:
            self.group = ''

        self._test_calculator()

    def test_aggregation(self):
        self._test_aggregation()

    def test_aggregation_with_group(self):
        self.group = 'food_type'
        self._test_aggregation()

    def test_aggregation_with_multigroup(self):
        self.group = 'food_type,rating'
        self._test_aggregation()
