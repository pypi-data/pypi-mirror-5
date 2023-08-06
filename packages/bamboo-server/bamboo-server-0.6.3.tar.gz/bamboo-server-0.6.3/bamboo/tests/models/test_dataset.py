from datetime import datetime

from pandas import DataFrame

from bamboo.tests.test_base import TestBase
from bamboo.models.dataset import Dataset
from bamboo.models.observation import Observation
from bamboo.lib.datetools import recognize_dates
from bamboo.lib.mongo import MONGO_ID_ENCODED
from bamboo.lib.schema_builder import OLAP_TYPE, RE_ENCODED_COLUMN, SIMPLETYPE


class TestDataset(TestBase):

    def test_save(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset().save(self.test_dataset_ids[dataset_name])
            record = dataset.record

            self.assertTrue(isinstance(record, dict))
            self.assertTrue('_id' in record.keys())

    def test_find(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset.create(self.test_dataset_ids[dataset_name])
            record = dataset.record
            rows = Dataset.find(self.test_dataset_ids[dataset_name])

            self.assertEqual(record, rows[0].record)

    def test_find_one(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset.create(self.test_dataset_ids[dataset_name])
            record = dataset.record
            row = Dataset.find_one(self.test_dataset_ids[dataset_name])

            self.assertEqual(record, row.record)

    def test_create(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset.create(self.test_dataset_ids[dataset_name])

            self.assertTrue(isinstance(dataset, Dataset))

    def test_delete(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset.create(self.test_dataset_ids[dataset_name])
            records = Dataset.find(self.test_dataset_ids[dataset_name])
            self.assertNotEqual(records, [])
            dataset.delete()
            records = Dataset.find(self.test_dataset_ids[dataset_name])

            self.assertEqual(records, [])
            self.assertEqual(Observation.encoding(dataset), None)

    def test_update(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset.create(self.test_dataset_ids[dataset_name])
            self.assertFalse('field' in dataset.record)
            dataset.update({'field': {'key': 'value'}})
            dataset = Dataset.find_one(self.test_dataset_ids[dataset_name])

            self.assertTrue('field' in dataset.record)
            self.assertEqual(dataset.record['field'], {'key': 'value'})

    def test_build_schema(self):
        for dataset_name in self.TEST_DATASETS:
            dataset = Dataset.create(self.test_dataset_ids[dataset_name])
            dataset.build_schema(self.get_data(dataset_name))

            # get dataset with new schema
            dataset = Dataset.find_one(self.test_dataset_ids[dataset_name])

            for key in [
                    Dataset.CREATED_AT, Dataset.SCHEMA, Dataset.UPDATED_AT]:
                self.assertTrue(key in dataset.record.keys())

            df_columns = self.get_data(dataset_name).columns.tolist()
            seen_columns = []

            for column_name, column_attributes in dataset.schema.items():
                # check column_name is unique
                self.assertFalse(column_name in seen_columns)
                seen_columns.append(column_name)

                # check column name is only legal chars
                self.assertFalse(RE_ENCODED_COLUMN.search(column_name))

                # check has require attributes
                self.assertTrue(SIMPLETYPE in column_attributes)
                self.assertTrue(OLAP_TYPE in column_attributes)
                self.assertTrue(Dataset.LABEL in column_attributes)

                # check label is an original column
                original_col = column_attributes[Dataset.LABEL]
                error_msg = '%s not in %s' % (original_col, df_columns)
                self.assertTrue(original_col in df_columns, error_msg)
                df_columns.remove(column_attributes[Dataset.LABEL])

                # check not reserved key
                self.assertFalse(column_name == MONGO_ID_ENCODED)

            # ensure all columns in df_columns have store columns
            self.assertTrue(len(df_columns) == 0)

    def test_dframe(self):
        dataset = Dataset.create(self.test_dataset_ids['good_eats.csv'])
        dataset.save_observations(
            recognize_dates(self.get_data('good_eats.csv')))
        dframe = dataset.dframe()

        self.assertTrue(isinstance(dframe, DataFrame))
        self.assertTrue(all(self.get_data('good_eats.csv').reindex(
                        columns=dframe.columns).eq(dframe)))
        columns = dframe.columns

        # ensure no reserved keys
        self.assertFalse(MONGO_ID_ENCODED in columns)

        # ensure date is converted
        self.assertTrue(isinstance(dframe.submit_date[0], datetime))

    def test_count(self):
        dataset = Dataset.create(self.test_dataset_ids['good_eats.csv'])
        dataset.save_observations(
            recognize_dates(self.get_data('good_eats.csv')))

        self.assertEqual(len(dataset.dframe()), dataset.count())
