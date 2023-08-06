from datetime import datetime
import pickle
from tempfile import NamedTemporaryFile
from time import mktime, sleep
from urllib2 import URLError

from mock import patch
import simplejson as json

from bamboo.controllers.datasets import Datasets
from bamboo.lib.datetools import now
from bamboo.lib.query_args import QueryArgs
from bamboo.lib.schema_builder import CARDINALITY, DATETIME, OLAP_TYPE,\
    SIMPLETYPE
from bamboo.models.dataset import Dataset
from bamboo.tests.controllers.test_abstract_datasets import\
    TestAbstractDatasets
from bamboo.tests.decorators import requires_async


class TestDatasets(TestAbstractDatasets):

    def setUp(self):
        TestAbstractDatasets.setUp(self)
        self._file_path = self._fixture_path_prefix(self._file_name)
        self._file_uri = self._local_fixture_prefix(self._file_name)
        self.url = 'http://formhub.org/mberg/forms/good_eats/data.csv'

    def __test_get_with_query_or_select(
            self, query='{}', select=None, distinct=None, num_results=None,
            result_keys=None):
        dataset_id = self._post_file()
        results = json.loads(self.controller.show(dataset_id, query=query,
                             select=select, distinct=distinct))

        self.assertTrue(isinstance(results, list))

        if num_results:
            self.assertEqual(len(results), num_results)
        if num_results > 3:
            self.assertTrue(isinstance(results[3], dict))
        if select:
            self.assertEqual(sorted(results[0].keys()), result_keys)
        if query != '{}':
            self.assertEqual(len(results), num_results)

    def __upload_mocked_file(self, **kwargs):
        mock_uploaded_file = self._file_mock(self._file_path)

        return json.loads(self.controller.create(
            csv_file=mock_uploaded_file, **kwargs))

    def __wait_for_dataset(self, dataset_id):
        while True:
            results = json.loads(self.controller.show(dataset_id))
            if len(results):
                break
            sleep(self.SLEEP_DELAY)

        sleep(self.SLEEP_DELAY)

        return results

    def test_create_from_csv(self):
        result = self.__upload_mocked_file()
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        # test parse type as date correctly
        dframe = Dataset.find_one(result[Dataset.ID]).dframe()
        self.assertTrue(isinstance(dframe.submit_date[0], datetime))

        results = self._test_summary_built(result)
        self._test_summary_no_group(results)

    def test_create_from_csv_unicode(self):
        dframe_length = 1
        dframe_data = [{u'\u03c7': u'\u03b1', u'\u03c8': u'\u03b2'}]

        _file_name = 'unicode.csv'
        self._file_path = self._file_path.replace(self._file_name, _file_name)
        result = self.__upload_mocked_file()

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        dataset = Dataset.find_one(result[Dataset.ID])

        self.assertEqual(Dataset.STATE_READY, dataset.state)

        dframe = dataset.dframe()

        self.assertEqual(dframe_length, len(dframe))
        self.assertEqual(dframe_data, dframe.to_jsondict())

        self._test_summary_built(result)

    def test_create_from_csv_custom_na(self):
        dframe_length = 4
        _file_name = 'wp_data.csv'
        self._file_path = self._file_path.replace(self._file_name, _file_name)
        result = self.__upload_mocked_file(na_values=json.dumps(['n/a']))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        dataset = Dataset.find_one(result[Dataset.ID])

        self.assertEqual(Dataset.STATE_READY, dataset.state)
        self.assertEqual(dframe_length, len(dataset.dframe()))
        self.assertTrue(isinstance(dataset.dframe().wp_id[1], float))

        self._test_summary_built(result)

    def test_create_from_csv_mixed_col(self):
        dframe_length = 8
        _file_name = 'good_eats_mixed.csv'
        self._file_path = self._file_path.replace(self._file_name, _file_name)
        result = self.__upload_mocked_file()

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        dataset = Dataset.find_one(result[Dataset.ID])

        self.assertEqual(Dataset.STATE_READY, dataset.state)
        self.assertEqual(dframe_length, len(dataset.dframe()))

        self._test_summary_built(result)

    def test_create_from_file_for_nan_float_cell(self):
        """First data row has one cell blank, which is usually interpreted
        as nan, a float value."""
        _file_name = 'good_eats_nan_float.csv'
        self._file_path = self._file_path.replace(self._file_name, _file_name)
        result = self.__upload_mocked_file()

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        results = self._test_summary_built(result)
        self._test_summary_no_group(results)
        results = json.loads(self.controller.info(self.dataset_id))
        simpletypes = pickle.load(
            open(self._fixture_path_prefix('good_eats_simpletypes.pkl'), 'rb'))

        for column_name, column_schema in results[Dataset.SCHEMA].items():
            self.assertEqual(
                column_schema[SIMPLETYPE], simpletypes[column_name])

    def test_create_from_url_failure(self):
        result = json.loads(self.controller.create(url=self._file_uri))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Datasets.ERROR in result)

    def test_create_from_url(self):
        dframe = self.get_data('good_eats.csv')
        with patch('pandas.read_csv', return_value=dframe):
            result = json.loads(self.controller.create(url=self.url))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        results = json.loads(self.controller.show(result[Dataset.ID]))

        self.assertEqual(len(results), self.NUM_ROWS)
        self._test_summary_built(result)

    @requires_async
    @patch('pandas.read_csv', return_value=None)
    def test_create_from_not_csv_url(self, read_csv):
        result = json.loads(self.controller.create(
            url='http://74.125.228.110/'))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        results = json.loads(self.controller.show(result[Dataset.ID]))

        self.assertEqual(len(results), 0)

    @requires_async
    @patch('pandas.read_csv', return_value=None, side_effect=URLError(''))
    def test_create_from_bad_url(self, read_csv):
        result = json.loads(self.controller.create(
            url='http://dsfskfjdks.com'))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        dataset_id = result[Dataset.ID]
        dataset = self._wait_for_dataset_state(dataset_id)

        self.assertEqual(Dataset.STATE_FAILED, dataset.state)

    @requires_async
    def test_create_from_bad_csv(self):
        tmp_file = NamedTemporaryFile(delete=False)
        mock = self._file_mock(tmp_file.name)
        result = json.loads(self.controller.create(
            csv_file=mock))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        dataset_id = result[Dataset.ID]
        dataset = self._wait_for_dataset_state(dataset_id)

        self.assertEqual(Dataset.STATE_FAILED, dataset.state)

    def test_create_from_json(self):
        mock = self._file_mock(self._fixture_path_prefix('good_eats.json'))
        result = json.loads(self.controller.create(
            json_file=mock))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        # test parse type as date correctly
        dframe = Dataset.find_one(result[Dataset.ID]).dframe()
        self.assertTrue(isinstance(dframe.submit_date[0], datetime))

        results = self._test_summary_built(result)
        self._test_summary_no_group(results)

    @requires_async
    def test_create_from_json_async(self):
        mock = self._file_mock(self._fixture_path_prefix('good_eats.json'))
        result = json.loads(self.controller.create(
            json_file=mock))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        self.__wait_for_dataset(result[Dataset.ID])

        results = self._test_summary_built(result)
        self._test_summary_no_group(results)

    def test_create_no_url_or_csv(self):
        result = json.loads(self.controller.create())

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Datasets.ERROR in result)

    def test_show(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.show(dataset_id))

        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(results[0], dict))
        self.assertEqual(len(results), self.NUM_ROWS)

    def test_show_csv(self):
        dataset_id = self._post_file()
        results = self.controller.show(dataset_id, format='csv')

        self.assertTrue(isinstance(results, str))
        self.assertEqual(len(results.split('\n')[0].split(',')), self.NUM_COLS)
        # one for header, one for empty final line
        self.assertEqual(len(results.split('\n')), self.NUM_ROWS + 2)

    @requires_async
    def test_show_async(self):
        dataset_id = self._post_file()

        results = self.__wait_for_dataset(dataset_id)

        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(results[0], dict))
        self.assertEqual(len(results), self.NUM_ROWS)

    def test_show_after_calculation(self):
        self.dataset_id = self._post_file()
        self._post_calculations(['amount < 4'])
        results = json.loads(self.controller.show(self.dataset_id,
                             select='{"amount___4": 1}'))

        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(results[0], dict))
        self.assertEqual(len(results), self.NUM_ROWS)

    def test_show_index(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.show(dataset_id, index=True))

        for row in results:
            self.assertTrue('index' in row.keys())

    def test_info(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.info(dataset_id))
        expected_keys = [Dataset.ID, Dataset.LABEL, Dataset.DESCRIPTION,
                         Dataset.LICENSE, Dataset.ATTRIBUTION,
                         Dataset.CREATED_AT, Dataset.PARENT_IDS,
                         Dataset.UPDATED_AT,
                         Dataset.SCHEMA, Dataset.NUM_ROWS, Dataset.NUM_COLUMNS,
                         Dataset.STATE]

        self.assertTrue(isinstance(results, dict))

        for key in expected_keys:
            self.assertTrue(key in results.keys())

        self.assertEqual(results[Dataset.NUM_ROWS], self.NUM_ROWS)
        self.assertEqual(results[Dataset.NUM_COLUMNS], self.NUM_COLS)
        self.assertEqual(results[Dataset.STATE], Dataset.STATE_READY)
        self.assertEqual(results[Dataset.PARENT_IDS], [])

    def test_info_parent_ids(self):
        self.dataset_id = self._post_file()
        self._post_calculations(self.default_formulae + ['sum(amount)'])
        agg_id = json.loads(self.controller.aggregations(self.dataset_id))['']
        results = json.loads(self.controller.info(agg_id))
        self.assertEqual([self.dataset_id], results[Dataset.PARENT_IDS])

    def test_info_cardinality(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.info(dataset_id))

        self.assertTrue(isinstance(results, dict))
        self.assertTrue(Dataset.SCHEMA in results.keys())

        schema = results[Dataset.SCHEMA]
        cardinalities = pickle.load(open(
            self._fixture_path_prefix('good_eats_cardinalities.pkl'), 'rb'))

        for key, column in schema.items():
            self.assertTrue(CARDINALITY in column.keys())
            self.assertEqual(
                column[CARDINALITY], cardinalities[key])

    def test_info_after_adding_calculations(self):
        self.dataset_id = self._post_file()
        self._post_calculations(formulae=self.default_formulae)
        results = json.loads(self.controller.info(self.dataset_id))
        self.assertEqual(results[Dataset.NUM_COLUMNS], self.NUM_COLS +
                         len(self.default_formulae))

    def test_info_schema(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.info(dataset_id))
        self.assertTrue(isinstance(results, dict))
        result_keys = results.keys()
        for key in [
                Dataset.CREATED_AT, Dataset.ID, Dataset.SCHEMA,
                Dataset.UPDATED_AT]:
            self.assertTrue(key in result_keys)
        self.assertEqual(
            results[Dataset.SCHEMA]['submit_date'][SIMPLETYPE], DATETIME)

    def test_show_bad_id(self):
        results = self.controller.show('honey_badger')
        self.assertTrue(Datasets.ERROR in results)

    def test_show_with_query(self):
        query = '{"rating": "delectible"}'
        self.__test_get_with_query_or_select(query, num_results=11)

    def test_show_with_or_query(self):
        self.__test_get_with_query_or_select(
            '{"$or": [{"food_type": "lunch"}, {"food_type": "deserts"}]}',
            num_results=9)

    @requires_async
    def test_show_with_query_async(self):
        self.__test_get_with_query_or_select('{"rating": "delectible"}',
                                             num_results=0)

    def test_show_with_query_limit_order_by(self):

        def get_results(query='{}', select=None, limit=None, order_by=None):
            dataset_id = self._post_file()
            return json.loads(self.controller.show(dataset_id,
                                                   query=query,
                                                   select=select,
                                                   limit=limit,
                                                   order_by=order_by))

        # test the limit
        limit = 4
        results = get_results(limit=limit)
        self.assertEqual(len(results), limit)

        # test the order_by
        limit = 1
        results = get_results(limit=limit, order_by='rating')
        self.assertEqual(results[0].get('rating'), 'delectible')

        limit = 1
        results = get_results(limit=limit, order_by='-rating')
        self.assertEqual(results[0].get('rating'), 'epic_eat')

    def test_show_with_bad_query(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.show(dataset_id,
                             query='bad json'))
        self.assertTrue('JSON' in results[Datasets.ERROR])

    def test_show_with_date_query(self):
        query = {
            'submit_date': {'$lt': mktime(now().timetuple())}
        }
        self.__test_get_with_query_or_select(
            query=json.dumps(query),
            num_results=self.NUM_ROWS)
        query = {
            'submit_date': {'$gt': mktime(now().timetuple())}
        }
        self.__test_get_with_query_or_select(
            query=json.dumps(query),
            num_results=0)
        date = mktime(datetime(2012, 2, 1, 0).timetuple())
        query = {
            'submit_date': {'$gt': date}
        }
        self.__test_get_with_query_or_select(
            query=json.dumps(query),
            num_results=4)

    def test_show_with_formatted_date_query(self):
        query = '{"submit_date": {"$lt": "2012-01-06"}}'
        self.__test_get_with_query_or_select(query, num_results=11)

    def test_show_with_select(self):
        self.__test_get_with_query_or_select(select='{"rating": 1}',
                                             num_results=self.NUM_ROWS,
                                             result_keys=['rating'])

    def test_show_with_distinct(self):
        dataset_id = self._post_file()
        results = json.loads(self.controller.show(dataset_id, query='{}',
                             distinct='rating'))
        self.assertTrue(isinstance(results, list))
        self.assertEqual(['delectible', 'epic_eat'], results)

    def test_show_with_select_and_query(self):
        self.__test_get_with_query_or_select('{"rating": "delectible"}',
                                             '{"rating": 1}',
                                             num_results=11,
                                             result_keys=['rating'])

    def test_aggregations_datasets_empty(self):
        self.dataset_id = self._post_file()
        self._post_calculations(formulae=self.default_formulae)
        results = json.loads(self.controller.aggregations(self.dataset_id))

        self.assertTrue(isinstance(results, dict))
        self.assertEqual(len(results.keys()), 0)

    def test_aggregations_datasets(self):
        self.dataset_id = self._post_file()
        self._post_calculations(self.default_formulae + ['sum(amount)'])

        results = self._test_aggregations()

        row_keys = ['sum_amount_']

        for row in results:
            self.assertEqual(row.keys(), row_keys)
            self.assertTrue(isinstance(row.values()[0], float))

    def test_aggregations_datasets_with_group(self):
        self.dataset_id = self._post_file()
        group = 'food_type'
        self._post_calculations(self.default_formulae + ['sum(amount)'], group)
        results = self._test_aggregations([group])
        row_keys = [group, 'sum_amount_']

        for row in results:
            self.assertEqual(row.keys(), row_keys)
            self.assertTrue(isinstance(row.values()[0], basestring))
            self.assertTrue(isinstance(row.values()[1], float))

    def test_aggregations_datasets_with_multigroup(self):
        self.dataset_id = self._post_file()
        group = 'food_type,rating'
        self._post_calculations(self.default_formulae + ['sum(amount)'], group)
        results = self._test_aggregations([group])
        # only so we can split
        dataset = Dataset()
        row_keys = (dataset.split_groups(group) +
                    ['sum_amount_']).sort()

        for row in results:
            sorted_row_keys = row.keys().sort()
            self.assertEqual(sorted_row_keys, row_keys)
            self.assertTrue(isinstance(row.values()[0], basestring))
            self.assertTrue(isinstance(row.values()[1], basestring))
            self.assertTrue(isinstance(row.values()[2], float))

    def test_aggregations_datasets_with_group_two_calculations(self):
        self.dataset_id = self._post_file()
        group = 'food_type'
        self._post_calculations(
            self.default_formulae + ['sum(amount)', 'sum(gps_alt)'], group)
        results = self._test_aggregations([group])
        row_keys = [group, 'sum_amount_', 'sum_gps_alt_']

        for row in results:
            self.assertEqual(row.keys(), row_keys)
            self.assertTrue(isinstance(row.values()[0], basestring))
            for value in row.values()[1:]:
                self.assertTrue(isinstance(value, float) or value == 'null')

    def test_aggregations_datasets_with_two_groups(self):
        self.dataset_id = self._post_file()
        group = 'food_type'
        self._post_calculations(self.default_formulae + ['sum(amount)'])
        self._post_calculations(['sum(gps_alt)'], group)
        groups = ['', group]
        results = self._test_aggregations(groups)

        for row in results:
            self.assertEqual(row.keys(), ['sum_amount_'])
            self.assertTrue(isinstance(row.values()[0], float))

        # get second linked dataset
        results = json.loads(self.controller.aggregations(self.dataset_id))

        self.assertEqual(len(results.keys()), len(groups))
        self.assertEqual(results.keys(), groups)

        linked_dataset_id = results[group]

        self.assertTrue(isinstance(linked_dataset_id, basestring))

        # inspect linked dataset
        results = json.loads(self.controller.show(linked_dataset_id))
        row_keys = [group, 'sum_gps_alt_']

        for row in results:
            self.assertEqual(row.keys(), row_keys)

    def test_delete(self):
        dataset_id = self._post_file()
        result = json.loads(self.controller.delete(dataset_id))

        self.assertEqual(result[Datasets.SUCCESS], 'deleted dataset')
        self.assertEqual(result[Dataset.ID], dataset_id)

    def test_delete_bad_id(self):
        for dataset_name in self.TEST_DATASETS:
            result = json.loads(self.controller.delete(
                                self.test_dataset_ids[dataset_name]))

            self.assertTrue(Datasets.ERROR in result)

    def test_delete_with_query(self):
        dataset_id = self._post_file()
        query = {'food_type': 'caffeination'}
        dataset = Dataset.find_one(dataset_id)
        dframe = dataset.dframe(query_args=QueryArgs(query=query))
        len_after_delete = len(dataset.dframe()) - len(dframe)

        query = json.dumps(query)
        result = json.loads(self.controller.delete(dataset_id, query=query))
        message = result[Datasets.SUCCESS]

        self.assertTrue('deleted dataset' in message)
        self.assertTrue(query in message)
        self.assertEqual(result[Dataset.ID], dataset_id)

        dframe = Dataset.find_one(dataset_id).dframe()

        self.assertEqual(len(dframe), len_after_delete)

    def test_show_jsonp(self):
        dataset_id = self._post_file()
        results = self.controller.show(dataset_id, callback='jsonp')

        self.assertEqual('jsonp(', results[0:6])
        self.assertEqual(')', results[-1])

    def test_drop_columns(self):
        dataset_id = self._post_file()
        results = json.loads(
            self.controller.drop_columns(dataset_id, ['food_type']))

        self.assertTrue(isinstance(results, dict))
        self.assertTrue(Datasets.SUCCESS in results)
        self.assertTrue('dropped' in results[Datasets.SUCCESS])

        results = json.loads(self.controller.show(dataset_id))

        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(results[0], dict))
        self.assertEqual(len(results[0].keys()), self.NUM_COLS - 1)

    def test_drop_columns_non_existent_id(self):
        results = json.loads(
            self.controller.drop_columns('313514', ['food_type']))

        self.assertTrue(isinstance(results, dict))
        self.assertTrue(Datasets.ERROR in results)

    def test_drop_columns_non_existent_column(self):
        dataset_id = self._post_file()
        results = json.loads(
            self.controller.drop_columns(dataset_id, ['foo']))

        self.assertTrue(isinstance(results, dict))
        self.assertTrue(Datasets.ERROR in results)

    def test_bad_date(self):
        dataset_id = self._post_file('bad_date.csv')
        dataset = Dataset.find_one(dataset_id)

        self.assertEqual(dataset.num_rows, 1)
        self.assertEqual(len(dataset.schema.keys()), 3)

        result = json.loads(self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY,
            group='name'))

        self.assertTrue('name' in result.keys())

    def test_multiple_date_formats(self):
        dataset_id = self._post_file('multiple_date_formats.csv')
        dataset = Dataset.find_one(dataset_id)

        self.assertEqual(dataset.num_rows, 2)
        self.assertEqual(len(dataset.schema.keys()), 4)

    def test_boolean_column(self):
        dataset_id = self._post_file('water_points.csv')
        summaries = json.loads(self.controller.summary(dataset_id,
                               select=self.controller.SELECT_ALL_FOR_SUMMARY))

        for summary in summaries.values():
            self.assertFalse(summary is None)

    @requires_async
    def test_perishable_dataset(self):
        perish_after = 2
        result = self.__upload_mocked_file(perish=perish_after)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)
        dataset_id = result[Dataset.ID]

        while True:
            results = json.loads(self.controller.show(dataset_id))
            if len(results):
                self.assertTrue(len(results), self.NUM_ROWS)
                break
            sleep(self.SLEEP_DELAY)

        # test that later it is deleted
        sleep(perish_after)
        result = json.loads(self.controller.show(dataset_id))
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Datasets.ERROR in result)

    def test_set_info(self):
        dataset_id = self._post_file('multiple_date_formats.csv')
        kwargs = {
            'attribution': '1',
            'description': '2',
            'label': '3',
            'license': '4',
        }
        results = json.loads(self.controller.set_info(dataset_id, **kwargs))

        self.assertEqual(results[Dataset.ID], dataset_id)

        dataset = Dataset.find_one(dataset_id)

        for key, value in dataset.info().items():
            if kwargs.get(key):
                self.assertEqual(value, kwargs[key])

    def test_count(self):
        dataset_id = self._post_file()

        results = json.loads(self.controller.show(dataset_id, count=True))

        self.assertEqual(results, self.NUM_ROWS)

    def test_count_with_distinct(self):
        dataset_id = self._post_file()

        results = json.loads(self.controller.show(
            dataset_id, count=True, distinct='amount'))

        self.assertEqual(results, self.NUM_ROWS - 4)

    def test_count_with_limit(self):
        dataset_id = self._post_file()
        limit = 10

        results = json.loads(self.controller.show(
            dataset_id, count=True, limit=limit))

        self.assertEqual(results, limit)

    def test_count_with_query(self):
        dataset_id = self._post_file()

        results = json.loads(self.controller.show(
            dataset_id, query='{"rating": "delectible"}',
            count=True))

        self.assertEqual(results, 11)

    def test_set_olap_type(self):
        new_olap_type = 'dimension'
        column = 'amount'

        dataset_id = self._post_file()

        results = json.loads(self.controller.info(dataset_id))
        expected_schema = results[Dataset.SCHEMA]
        expected_schema[column][OLAP_TYPE] = new_olap_type

        # set OLAP Type
        results = json.loads(self.controller.set_olap_type(
            dataset_id, column, new_olap_type))
        self.assertTrue(Datasets.SUCCESS in results.keys())

        # Check new schema
        results = json.loads(self.controller.info(dataset_id))
        new_schema = results[Dataset.SCHEMA]
        self.assertEqual(expected_schema, new_schema)

        # Check summary
        results = json.loads(self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY))
        summary = results[column]['summary']
        self.assertFalse('count' in summary.keys())

        # set OLAP Type back
        new_olap_type = 'measure'
        expected_schema[column][OLAP_TYPE] = new_olap_type
        results = json.loads(self.controller.set_olap_type(
            dataset_id, column, new_olap_type))
        self.assertTrue(Datasets.SUCCESS in results.keys())

        # Check new schema
        results = json.loads(self.controller.info(dataset_id))
        new_schema = results[Dataset.SCHEMA]
        self.assertEqual(expected_schema, new_schema)

        # Check summary
        results = json.loads(self.controller.summary(
            dataset_id, select=self.controller.SELECT_ALL_FOR_SUMMARY))
        summary = results[column]['summary']
        self.assertTrue('count' in summary.keys())

    def test_set_olap_type_fails_for_dimension(self):
        new_olap_type = 'measure'
        column = 'food_type'

        dataset_id = self._post_file()

        results = json.loads(self.controller.info(dataset_id))
        expected_schema = results[Dataset.SCHEMA]

        # set OLAP Type
        results = json.loads(self.controller.set_olap_type(
            dataset_id, column, new_olap_type))
        self.assertTrue(Datasets.ERROR in results.keys())

        # Check schema does not change
        results = json.loads(self.controller.info(dataset_id))
        new_schema = results[Dataset.SCHEMA]
        self.assertEqual(expected_schema, new_schema)

    def test_reset(self):
        dataset_id = self._post_file()
        mock_uploaded_file = self._file_mock(self._file_path)

        result = json.loads(self.controller.reset(dataset_id,
                                                  csv_file=mock_uploaded_file))

        self.assertEqual(result[Dataset.ID], dataset_id)

        # test parse type as date correctly
        dframe = Dataset.find_one(result[Dataset.ID]).dframe()
        self.assertTrue(isinstance(dframe.submit_date[0], datetime))

        results = self._test_summary_built(result)
        self._test_summary_no_group(results)
