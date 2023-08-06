from base64 import b64encode

import simplejson as json

from bamboo.lib.mongo import ILLEGAL_VALUES
from bamboo.controllers.datasets import Datasets
from bamboo.core.summary import SUMMARY
from bamboo.models.dataset import Dataset
from bamboo.tests.controllers.test_abstract_datasets import\
    TestAbstractDatasets
from bamboo.tests.decorators import requires_async


class TestDatasetsSummary(TestAbstractDatasets):

    def setUp(self):
        TestAbstractDatasets.setUp(self)

    def test_summary(self):
        dataset_id = self._post_file()
        results = self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY)
        results = self._test_summary_results(results)
        self._test_summary_no_group(results, dataset_id)

    @requires_async
    def test_summary_async(self):
        dataset_id = self._post_file()
        results = self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY)
        dataset = Dataset.find_one(dataset_id)

        self.assertEqual(dataset.state, Dataset.STATE_PENDING)

        results = self._test_summary_results(results)

        self.assertTrue(Datasets.ERROR in results.keys())
        self.assertTrue('not finished' in results[Datasets.ERROR])

    def test_summary_restrict_by_cardinality(self):
        dataset_id = self._post_file('good_eats_huge.csv')
        results = self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY)
        results = self._test_summary_results(results)

        # food_type has unique greater than the limit in this csv
        self.assertEqual(len(results.keys()), self.NUM_COLS - 1)
        self.assertFalse('food_type' in results.keys())

    def test_summary_illegal_keys(self):
        dataset_id = self._post_file(file_name='good_eats_illegal_keys.csv')
        results = self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY)

        results = self._test_summary_results(results)

    def test_summary_decode_illegal_keys(self):
        dataset_id = self._post_file('good_eats_illegal_keys.csv')
        summaries = json.loads(self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY))

        encoded_values = [b64encode(value) for value in ILLEGAL_VALUES]

        for column, summary in summaries.iteritems():
            # check the column names
            for encoded_value in encoded_values:
                self.assertFalse(encoded_value in column, '%s in %s' %
                                 (encoded_value, column))
            # check in "summary" for encoded keys (possibly from data)
            for key in summary.values()[0].keys():
                for encoded_value in encoded_values:
                    self.assertFalse(encoded_value in key, '%s in %s' %
                                     (encoded_value, key))

    def test_summary_unicode(self):
        file_name = 'unicode.csv'
        dataset_id = self._post_file(file_name=file_name)
        results = self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY)
        results = self._test_summary_results(results)
        columns = [col for col in
                   self.get_data(file_name).columns.tolist()]
        summary_keys = results.keys()
        for column in columns:
            self.assertTrue(column in summary_keys)

    def test_summary_no_select(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.summary(dataset_id))

        self.assertTrue(Datasets.ERROR in results.keys())

    def test_summary_with_query(self):
        dataset_id = self._post_file()
        # (sic)
        query_column = 'rating'
        results = self.controller.summary(
            dataset_id,
            query='{"%s": "delectible"}' % query_column,
            select=self.controller.SELECT_ALL_FOR_SUMMARY)

        results = self._test_summary_results(results)
        # ensure only returned results for this query column
        self.assertEqual(len(results[query_column][SUMMARY].keys()), 1)
        self._test_summary_no_group(results, dataset_id)

    def test_summary_with_group(self):
        dataset_id = self._post_file()
        groups = [
            ('rating', ['delectible', 'epic_eat']),
            ('amount', []),
        ]

        for group, column_values in groups:
            json_results = self.controller.summary(
                dataset_id,
                group=group,
                select=self.controller.SELECT_ALL_FOR_SUMMARY)
            results = self._test_summary_results(json_results)
            result_keys = results.keys()

            if len(column_values):
                self.assertTrue(group in result_keys, 'group: %s in: %s'
                                % (group, result_keys))
                self.assertEqual(column_values, results[group].keys())

                for column_value in column_values:
                    self._test_summary_no_group(
                        results[group][column_value],
                        dataset_id=dataset_id,
                        group=group)
            else:
                self.assertFalse(group in results.keys())
                self.assertTrue(Datasets.ERROR in results.keys())

    def test_summary_with_select_as_list(self):
        dataset_id = self._post_file()

        json_results = self.controller.summary(
            dataset_id,
            select=json.dumps('[]'))

        results = self._test_summary_results(json_results)
        self.assertTrue(Datasets.ERROR in results.keys())
        self.assertTrue('must be a' in results[Datasets.ERROR])

    def test_summary_with_group_select(self):
        dataset_id = self._post_file()
        group = 'food_type'
        json_select = {'rating': 1}

        json_results = self.controller.summary(
            dataset_id,
            group=group,
            select=json.dumps(json_select))

        results = self._test_summary_results(json_results)

        self.assertTrue(group in results.keys())
        for summary in results[group].values():
            self.assertTrue(len(summary.keys()), 1)

    def test_summary_with_multigroup(self):
        dataset_id = self._post_file()
        group_columns = 'rating,food_type'

        results = self.controller.summary(
            dataset_id,
            group=group_columns,
            select=self.controller.SELECT_ALL_FOR_SUMMARY)

        results = self._test_summary_results(results)

        self.assertFalse(Datasets.ERROR in results.keys())
        self.assertTrue(group_columns in results.keys())
        # for split
        dataset = Dataset()
        self.assertEqual(
            len(dataset.split_groups(results[group_columns].keys()[0])),
            len(dataset.split_groups(group_columns)))

    def test_summary_with_multigroup_flat(self):
        dataset_id = self._post_file()
        col1 = 'rating'
        col1_values = ['delectible', 'epic_eat']
        col2 = 'food_type'
        group_columns = '%s,%s' % (col1, col2)

        results = json.loads(self.controller.summary(
            dataset_id,
            group=group_columns,
            select=self.controller.SELECT_ALL_FOR_SUMMARY,
            flat=True))

        self.assertTrue(isinstance(results, list))

        for i in results:
            self.assertTrue(i[col1] in col1_values)
            self.assertTrue(col2 in i.keys())

    def test_summary_multigroup_noncat_group(self):
        dataset_id = self._post_file()
        group_columns = 'rating,amount'

        results = self.controller.summary(
            dataset_id,
            group=group_columns,
            select=self.controller.SELECT_ALL_FOR_SUMMARY)

        results = self._test_summary_results(results)
        self.assertTrue(Datasets.ERROR in results.keys())

    def test_summary_nonexistent_group(self):
        dataset_id = self._post_file()
        group_columns = 'bongo'

        results = self.controller.summary(
            dataset_id,
            group=group_columns,
            select=self.controller.SELECT_ALL_FOR_SUMMARY)

        results = self._test_summary_results(results)
        self.assertTrue('not a column' in results[Datasets.ERROR])

    def test_summary_with_group_and_query(self):
        dataset_id = self._post_file()
        query_column = 'rating'

        results = self.controller.summary(
            dataset_id,
            group='rating',
            query='{"%s": "delectible"}' % query_column,
            select=self.controller.SELECT_ALL_FOR_SUMMARY)

        results = self._test_summary_results(results)
        self.assertEqual(len(results[query_column].keys()), 1)
