from time import sleep

import simplejson as json

from bamboo.controllers.abstract_controller import AbstractController
from bamboo.controllers.calculations import Calculations
from bamboo.controllers.datasets import Datasets
from bamboo.core.frame import DATASET_ID
from bamboo.models.calculation import Calculation
from bamboo.models.dataset import Dataset
from bamboo.tests.decorators import requires_async
from bamboo.tests.test_base import TestBase
from bamboo.tests.controllers.test_abstract_datasets import\
    TestAbstractDatasets
from bamboo.lib.utils import is_float_nan


class TestCalculations(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.controller = Calculations()
        self.dataset_controller = Datasets()
        self.dataset_id = None
        self.formula = 'amount + gps_alt'
        self.name = 'test'

    def __post_formula(self, formula=None, name=None):
        if not formula:
            formula = self.formula
        if not name:
            name = self.name

        if not self.dataset_id:
            self.dataset_id = self._post_file()

        return self.controller.create(self.dataset_id, formula, name)

    def __post_update(self, dataset_id, update):
        return json.loads(self.dataset_controller.update(
            dataset_id=dataset_id, update=json.dumps(update)))

    def __wait_for_calculation_ready(self, dataset_id, name):
        while True:
            calculation = Calculation.find_one(dataset_id, name)

            if calculation.is_ready:
                break

            sleep(self.SLEEP_DELAY)

    def __test_error(self, response, error_text=None):
        response = json.loads(response)

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.ERROR in response)

        if not error_text:
            error_text = 'Must provide'

        self.assertTrue(error_text in response[self.controller.ERROR])

    def __test_create_from_json(self, json_filename, non_agg_cols=1, ex_len=1,
                                group=None):
        json_filepath = 'tests/fixtures/%s' % json_filename
        mock_uploaded_file = self._file_mock(json_filepath)
        dataset = Dataset.find_one(self.dataset_id)
        prev_columns = len(dataset.dframe().columns)
        response = json.loads(self.controller.create(
            self.dataset_id, json_file=mock_uploaded_file, group=group))

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)
        self.assertTrue(self.dataset_id in response[Dataset.ID])

        self.assertEqual(
            ex_len, len(json.loads(self.controller.show(self.dataset_id))))
        self.assertEqual(
            prev_columns + non_agg_cols,
            len(dataset.reload().dframe().columns))

        return dataset

    def __verify_create(self, response):
        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)
        self.assertEqual(response[Dataset.ID], self.dataset_id)

        self.__wait_for_calculation_ready(self.dataset_id, self.name)

        dataset = Dataset.find_one(self.dataset_id)
        dframe = dataset.dframe()

        self.assertTrue(self.name in dataset.schema.keys())
        self.assertTrue(self.name in dframe.columns)
        self.assertEqual(TestAbstractDatasets.NUM_ROWS, len(dframe))
        self.assertEqual(TestAbstractDatasets.NUM_ROWS,
                         dataset.info()[Dataset.NUM_ROWS])

    def test_show(self):
        self.__post_formula()
        response = self.controller.show(self.dataset_id)

        self.assertTrue(isinstance(json.loads(response), list))

    def test_create(self):
        response = json.loads(self.__post_formula())
        self.__verify_create(response)

    @requires_async
    def test_create_async_not_ready(self):
        self.dataset_id = self._create_dataset_from_url(
            '%s%s' % (self._local_fixture_prefix(), 'good_eats_huge.csv'))
        response = json.loads(self.__post_formula())
        dataset = Dataset.find_one(self.dataset_id)

        self.assertFalse(dataset.is_ready)
        self.assertTrue(isinstance(response, dict))
        self.assertFalse(DATASET_ID in response)

        self._wait_for_dataset_state(self.dataset_id)

        self.assertFalse(self.name in dataset.schema.keys())

    @requires_async
    def test_create_async_sets_calculation_status(self):
        self.dataset_id = self._create_dataset_from_url(
            '%s%s' % (self._local_fixture_prefix(), 'good_eats_huge.csv'))

        self._wait_for_dataset_state(self.dataset_id)

        response = json.loads(self.__post_formula())

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)
        self.assertEqual(response[Dataset.ID], self.dataset_id)

        response = json.loads(self.controller.show(self.dataset_id))[0]

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(Calculation.STATE in response)
        self.assertEqual(response[Calculation.STATE],
                         Calculation.STATE_PENDING)

        self.__wait_for_calculation_ready(self.dataset_id, self.name)

        dataset = Dataset.find_one(self.dataset_id)

        self.assertTrue(self.name in dataset.schema.keys())

    @requires_async
    def test_create_async(self):
        self.dataset_id = self._post_file()

        self._wait_for_dataset_state(self.dataset_id)

        response = json.loads(self.__post_formula())
        self.__verify_create(response)

    def test_create_invalid_formula(self):
        dataset_id = self._post_file()
        result = json.loads(
            self.controller.create(dataset_id, '=NON_EXIST', self.name))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Datasets.ERROR in result.keys())

    def test_create_update_summary(self):
        dataset_id = self._post_file()
        Datasets().summary(
            dataset_id,
            select=Datasets.SELECT_ALL_FOR_SUMMARY)
        dataset = Dataset.find_one(dataset_id)

        self.assertTrue(isinstance(dataset.stats, dict))
        self.assertTrue(isinstance(dataset.stats[Dataset.ALL], dict))

        self.__post_formula()

        # stats should have new column for calculation
        dataset = Dataset.find_one(self.dataset_id)
        stats = dataset.stats.get(Dataset.ALL)
        self.assertTrue(self.name in stats.keys())

    def test_delete_nonexistent_calculation(self):
        dataset_id = self._post_file()
        result = json.loads(self.controller.delete(dataset_id, self.name))

        self.assertTrue(Calculations.ERROR in result)

    def test_delete(self):
        self.__post_formula()
        result = json.loads(self.controller.delete(self.dataset_id, self.name))

        self.assertTrue(AbstractController.SUCCESS in result)

        dataset = Dataset.find_one(self.dataset_id)
        self.assertTrue(self.name not in dataset.schema.labels_to_slugs)

    def test_delete_calculation_not_in_dataset(self):
        self.__post_formula()

        # Remove column from dataset
        dataset = Dataset.find_one(self.dataset_id)
        dataset.delete_columns([self.name])

        result = json.loads(self.controller.delete(self.dataset_id, self.name))

        self.assertTrue(AbstractController.SUCCESS in result)

        dataset = Dataset.find_one(self.dataset_id)
        self.assertTrue(self.name not in dataset.schema.labels_to_slugs)

    def test_delete_update_summary(self):
        self.__post_formula()

        dataset = Dataset.find_one(self.dataset_id)
        self.assertTrue(self.name in dataset.stats.get(Dataset.ALL).keys())

        json.loads(self.controller.delete(self.dataset_id, self.name))

        dataset = Dataset.find_one(self.dataset_id)
        self.assertTrue(self.name not in dataset.stats.get(Dataset.ALL).keys())

    def test_show_jsonp(self):
        self.__post_formula()
        results = self.controller.show(self.dataset_id, callback='jsonp')

        self.assertEqual('jsonp(', results[0:6])
        self.assertEqual(')', results[-1])

    def test_create_aggregation(self):
        self.formula = 'sum(amount)'
        self.name = 'test'
        response = json.loads(self.__post_formula())

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)
        self.assertEqual(response[Dataset.ID], self.dataset_id)

        dataset = Dataset.find_one(self.dataset_id)

        self.assertTrue('' in dataset.aggregated_datasets_dict.keys())

    def test_delete_aggregation(self):
        self.formula = 'sum(amount)'
        self.name = 'test'
        json.loads(self.__post_formula())

        result = json.loads(
            self.controller.delete(self.dataset_id, self.name, ''))

        self.assertTrue(AbstractController.SUCCESS in result)

        dataset = Dataset.find_one(self.dataset_id)
        agg_dataset = dataset.aggregated_dataset('')

        self.assertTrue(self.name not in agg_dataset.schema.labels_to_slugs)

    def test_error_on_delete_calculation_with_dependency(self):
        self.__post_formula()
        dep_name = self.name
        self.formula = dep_name
        self.name = 'test1'
        response = json.loads(self.__post_formula())

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)

        result = json.loads(
            self.controller.delete(self.dataset_id, dep_name, ''))

        self.assertTrue(AbstractController.ERROR in result)
        self.assertTrue('depend' in result[AbstractController.ERROR])

    def test_create_multiple(self):
        self.dataset_id = self._post_file()
        self.__test_create_from_json(
            'good_eats.calculations.json', non_agg_cols=2, ex_len=2)

    def test_create_multiple_ignore_group(self):
        self.dataset_id = self._post_file()
        dataset = self.__test_create_from_json(
            'good_eats.calculations.json', non_agg_cols=2, ex_len=2,
            group='risk_factor')

        self.assertEqual(dataset.aggregated_datasets_dict, {})

    def test_create_json_single(self):
        self.dataset_id = self._post_file()
        self.__test_create_from_json('good_eats_single.calculations.json')

    def test_create_multiple_with_group(self):
        self.dataset_id = self._post_file()
        groups = ['risk_factor', 'risk_factor,food_type', 'food_type']
        dataset = self.__test_create_from_json(
            'good_eats_group.calculations.json', non_agg_cols=2, ex_len=6)

        for group in groups:
            self.assertTrue(group in dataset.aggregated_datasets_dict.keys())
            dframe = dataset.aggregated_dataset(group).dframe()

            for column in Calculation().split_groups(group):
                self.assertTrue(column in dframe.columns)

    def test_create_with_missing_args(self):
        self.dataset_id = self._post_file()
        self.__test_error(self.controller.create(self.dataset_id))
        self.__test_error(
            self.controller.create(self.dataset_id, formula='gps_alt'))
        self.__test_error(
            self.controller.create(self.dataset_id, name='test'))

    def test_create_with_bad_json(self):
        self.dataset_id = self._post_file()
        json_filepath = self._fixture_path_prefix(
            'good_eats_bad.calculations.json')
        mock_uploaded_file = self._file_mock(json_filepath)

        self.__test_error(
            self.controller.create(self.dataset_id,
                                   json_file=mock_uploaded_file),
            error_text='Required')

        # Mock is now an empty file
        self.__test_error(
            self.controller.create(self.dataset_id,
                                   json_file=mock_uploaded_file),
            error_text='Improper format for JSON')

    def test_create_reserved_name(self):
        name = 'sum'
        response = json.loads(self.__post_formula(None, name))

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)
        self.assertEqual(response[Dataset.ID], self.dataset_id)

        dataset = Dataset.find_one(self.dataset_id)
        slug = dataset.schema.labels_to_slugs[name]
        response = json.loads(self.__post_formula('%s + amount' % slug))

        self.assertTrue(isinstance(response, dict))
        self.assertTrue(self.controller.SUCCESS in response)
        self.assertTrue(self.dataset_id in response[Dataset.ID])

    def test_create_with_duplicate_names(self):
        formula_names_to_valid = {
            'water_not_functioning_none': True,   # an already slugged column
            'water_not_functioning/none': False,  # a non-slug column
            'region': False,    # an existing column
            'date': False,      # a reserved key and an existing column
            'sum': True,        # a reserved key
        }

        for formula_name, valid in formula_names_to_valid.items():
            dataset_id = self._post_file('water_points.csv')
            dframe_before = Dataset.find_one(dataset_id).dframe()

            # a calculation
            response = json.loads(self.controller.create(
                dataset_id,
                'water_source_type in ["borehole"]',
                formula_name))

            self.assertTrue(isinstance(response, dict))

            if valid:
                self.assertTrue(self.controller.SUCCESS in response)
            else:
                self.assertTrue(self.controller.ERROR in response)
                self.assertTrue(
                    formula_name in response[self.controller.ERROR])

            dataset = Dataset.find_one(dataset_id)

            if valid:
                name = dataset.calculations()[-1].name

            # an aggregation
            response = json.loads(self.controller.create(
                dataset_id,
                'newest(date_, water_functioning)',
                formula_name))

            self.assertTrue(isinstance(response, dict))
            self.assertTrue(self.controller.SUCCESS in response)

            dframe_after = dataset.dframe()

            # Does not change data
            self.assertEqual(len(dframe_before), len(dframe_after))

            if valid:
                slug = dataset.schema.labels_to_slugs[name]
                self.assertTrue(slug not in dframe_before.columns)
                self.assertTrue(slug in dframe_after.columns)

            if valid:
                # Does change columns
                self.assertEqual(
                    len(dframe_before.columns) + 1, len(dframe_after.columns))
            else:
                # Does not change columns
                self.assertEqual(
                    len(dframe_before.columns), len(dframe_after.columns))

            # check OK on update
            update = {
                'date': '2013-01-05',
                'water_source_type': 'borehole',
            }
            result = self.__post_update(dataset_id, update)
            self.assertTrue(Dataset.ID in result)
            dataset = Dataset.find_one(dataset_id)
            dframe_after_update = dataset.dframe()
            self.assertEqual(len(dframe_after) + 1, len(dframe_after_update))

    def test_cannot_create_aggregations_with_duplicate_names(self):
        dataset_id = self._post_file('water_points.csv')

        formula_name = 'name'

        response = json.loads(self.controller.create(
            dataset_id,
            'newest(date_, water_functioning)',
            formula_name))

        self.assertTrue(self.controller.SUCCESS in response)

        # another with the same name
        response = json.loads(self.controller.create(
            dataset_id,
            'newest(date_, water_functioning)',
            formula_name))

        self.assertTrue(formula_name in response[self.controller.ERROR])

    def test_can_create_aggregations_with_duplicate_as_slug_names(self):
        dataset_id = self._post_file('water_points.csv')

        formula_name = 'name*'

        response = json.loads(self.controller.create(
            dataset_id,
            'newest(date_, water_functioning)',
            formula_name))

        self.assertTrue(self.controller.SUCCESS in response)

        # another with the same name
        response = json.loads(self.controller.create(
            dataset_id,
            'newest(date_, water_functioning)',
            'name_'))

        self.assertTrue(self.controller.SUCCESS in response)

    def test_newest(self):
        expected_dataset = {
            u'wp_functional': {0: u'no', 1: u'yes', 2: u'no', 3: u'yes'},
            u'id': {0: 1, 1: 2, 2: 3, 3: 4}}
        dataset_id = self._post_file('newest_test.csv')
        self.controller.create(dataset_id,
                               'newest(submit_date,functional)',
                               'wp_functional', group='id')
        dataset = Dataset.find_one(dataset_id)
        agg_ds = dataset.aggregated_dataset('id')

        self.assertEqual(expected_dataset, agg_ds.dframe().to_dict())

    def test_update_after_agg(self):
        dataset_id = self._post_file('wp_data.csv')
        results = json.loads(self.controller.create(dataset_id,
                             'newest(submit_date,wp_id)', 'wp_newest'))

        dataset = Dataset.find_one(dataset_id)
        previous_num_rows = dataset.num_rows

        self.assertTrue(self.controller.SUCCESS in results)
        self.assertFalse(dataset.aggregated_dataset('') is None)

        update = {
            'submit_date': '2013-01-05',
            'wp_id': 'D',
            'functional': 'no',
        }
        self.__post_update(dataset_id, update)
        update = {
            'wp_id': 'E',
            'functional': 'no',
        }
        self.__post_update(dataset_id, update)

        dataset = Dataset.find_one(dataset_id)
        current_num_rows = dataset.num_rows
        agg_df = dataset.aggregated_dataset('').dframe()

        self.assertEqual(agg_df.get_value(0, 'wp_newest'), 'D')
        self.assertEqual(current_num_rows, previous_num_rows + 2)

    @requires_async
    def test_update_after_agg_group(self):
        dataset_id = self._post_file('wp_data.csv')
        group = 'wp_id'
        self._wait_for_dataset_state(dataset_id)

        test_calculations = {
            'newest(submit_date,functional)': 'wp_functional',
            'max(submit_date)': 'latest_submit_date',
            'ratio(functional in ["yes"], 1)': 'wp_func_ratio'}

        expected_results = {'wp_id': ['A', 'B', 'C', 'n/a'],
                            'wp_functional': ['yes', 'no', 'yes', 'yes'],
                            'wp_func_ratio': [1.0, 0.0, 1.0, 1.0],
                            'wp_func_ratio_denominator': [1, 1, 1, 1],
                            'wp_func_ratio_numerator': [1.0, 0.0, 1.0, 1.0],
                            'latest_submit_date': [1356998400, 1357084800,
                                                   1357171200, 1357257600]}

        expected_results_after = {
            'wp_id': ['A', 'B', 'C', 'D', 'n/a'],
            'wp_functional': ['no', 'no', 'yes', 'yes'],
            'wp_func_ratio': [0.5, 0.0, 1.0, 1.0, 1.0],
            'wp_func_ratio_denominator': [2.0, 1.0, 1.0, 1.0, 1.0],
            'wp_func_ratio_numerator': [1.0, 0.0, 1.0, 1.0, 1.0],
            'latest_submit_date': [1357603200.0, 1357084800.0,
                                   1357171200.0, 1357257600.0]}

        for formula, name in test_calculations.items():
            results = json.loads(self.controller.create(
                dataset_id, formula, name, group=group))

            self.assertTrue(self.controller.SUCCESS in results)

        dataset = Dataset.find_one(dataset_id)
        previous_num_rows = dataset.num_rows

        while True:
            dataset = Dataset.find_one(dataset_id)

            if dataset.aggregated_dataset(group) and all(
                    [not c.is_pending for c in dataset.calculations()]):
                break
            sleep(self.SLEEP_DELAY)

        agg_dframe = dataset.aggregated_dataset(group).dframe()
        self.assertEqual(set(expected_results.keys()),
                         set(agg_dframe.columns.tolist()))

        for column, results in expected_results.items():
            self.assertEqual(results,
                             agg_dframe[column].tolist())

        update = {
            'wp_id': 'D',
            'functional': 'yes',
        }
        self.__post_update(dataset_id, update)
        update = {
            'submit_date': '2013-01-08',
            'wp_id': 'A',
            'functional': 'no',
        }
        self.__post_update(dataset_id, update)

        while True:
            dataset = Dataset.find_one(dataset_id)
            current_num_rows = dataset.num_rows

            if not len(dataset.pending_updates):
                break

            sleep(self.SLEEP_DELAY)

        dataset = Dataset.find_one(dataset_id)
        agg_dframe = dataset.aggregated_dataset(group).dframe()

        self.assertEqual(current_num_rows, previous_num_rows + 2)
        self.assertEqual(set(expected_results_after.keys()),
                         set(agg_dframe.columns.tolist()))
        for column, results in expected_results_after.items():
            column = [x for x in agg_dframe[column].tolist() if not
                      is_float_nan(x)]
            self.assertEqual(results, column)

    @requires_async
    def test_fail_in_background(self):
        dataset_id = self._post_file('wp_data.csv')
        group = 'wp_id'
        self._wait_for_dataset_state(dataset_id)

        self.controller.create(dataset_id,
                               'newest(submit_date,functional)',
                               'wp_functional',
                               group=group)
        self.controller.create(dataset_id,
                               'max(submit_date)',
                               'latest_submit_date',
                               group=group)

        # Update the name to cause has pending to be true and infinite retries.
        # It will fail after 10 retries.
        calc = Calculation.find_one(dataset_id, 'latest_submit_date', group)
        calc.update({calc.NAME: 'another_name'})

        update = {
            'wp_id': 'D',
            'functional': 'yes',
        }
        self.__post_update(dataset_id, update)
        update = {
            'submit_date': '2013-01-08',
            'wp_id': 'A',
            'functional': 'no',
        }
        self.__post_update(dataset_id, update)

        while True:
            dataset = Dataset.find_one(dataset_id)
            calcs_not_pending = [
                c.state != c.STATE_PENDING for c in dataset.calculations()]

            if not len(dataset.pending_updates) and all(calcs_not_pending):
                break

            sleep(self.SLEEP_DELAY)

        for c in dataset.calculations():
            self.assertEqual(c.STATE_FAILED, c.state)
            self.assertTrue('Traceback' in c.error_message)

    def test_fail_then_create(self):
        response = json.loads(self.__post_formula())
        self.__verify_create(response)

        # Overwrite as failed
        calc = Calculation.find_one(self.dataset_id, self.name)
        calc.update({calc.STATE: calc.STATE_FAILED})

        # Test we can still add a calculation
        self.name = 'test2'
        response = json.loads(self.__post_formula())
        self.__verify_create(response)
