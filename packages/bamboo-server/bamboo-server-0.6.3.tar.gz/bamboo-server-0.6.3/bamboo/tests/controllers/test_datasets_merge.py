from time import sleep

from pandas import concat
import simplejson as json

from bamboo.core.frame import PARENT_DATASET_ID, RESERVED_KEYS
from bamboo.models.dataset import Dataset
from bamboo.tests.controllers.test_abstract_datasets import\
    TestAbstractDatasets
from bamboo.tests.decorators import requires_async


class TestDatasetsMerge(TestAbstractDatasets):

    def _post_merge(self, dataset_ids):
        dataset_id1, dataset_id2 = dataset_ids
        return json.loads(self.controller.merge(
            dataset_ids=json.dumps(dataset_ids),
            mapping=json.dumps({
                dataset_id1: {
                    "food_type": "food_type_2",
                },
                dataset_id2: {
                    "code": "comments",
                    "food_type": "food_type_2",
                },
            })))[Dataset.ID]

    @requires_async
    def test_merge_datasets_0_not_enough(self):
        result = json.loads(self.controller.merge(dataset_ids=json.dumps([])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(self.controller.ERROR in result)

    @requires_async
    def test_merge_datasets_1_not_enough(self):
        dataset_id = self._post_file()
        result = json.loads(self.controller.merge(
            dataset_ids=json.dumps([dataset_id])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(self.controller.ERROR in result)

    @requires_async
    def test_merge_datasets_must_exist(self):
        dataset_id = self._post_file()
        result = json.loads(self.controller.merge(
            dataset_ids=json.dumps([dataset_id, 0000])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(self.controller.ERROR in result)

    def test_merge_datasets(self):
        dataset_id1 = self._post_file()
        dataset_id2 = self._post_file()
        result = json.loads(self.controller.merge(
            dataset_ids=json.dumps([dataset_id1, dataset_id2])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        datasets = [Dataset.find_one(dataset_id)
                    for dataset_id in [dataset_id1, dataset_id2]]

        for dataset in datasets:
            self.assertTrue(result[Dataset.ID] in dataset.merged_dataset_ids)

        dframe1 = datasets[0].dframe()
        merged_dataset = Dataset.find_one(result[Dataset.ID])
        merged_dframe = merged_dataset.dframe(keep_parent_ids=True)

        for _, row in merged_dframe.iterrows():
            self.assertTrue(PARENT_DATASET_ID in row.keys())

        merged_dframe = merged_dataset.dframe()

        self.assertEqual(len(merged_dframe), 2 * len(dframe1))

        expected_dframe = concat([dframe1, dframe1],
                                 ignore_index=True)

        self.assertEqual(list(merged_dframe.columns),
                         list(expected_dframe.columns))

        self._check_dframes_are_equal(merged_dframe, expected_dframe)

    @requires_async
    def test_merge_datasets_async(self):
        dataset_id1 = self._post_file()
        dataset_id2 = self._post_file()

        self.assertEqual(
            Dataset.find_one(dataset_id1).state,
            Dataset.STATE_PENDING)
        self.assertEqual(
            Dataset.find_one(dataset_id2).state,
            Dataset.STATE_PENDING)

        result = json.loads(self.controller.merge(
            dataset_ids=json.dumps([dataset_id1, dataset_id2])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        merged_id = result[Dataset.ID]

        while True:
            datasets = [Dataset.find_one(dataset_id)
                        for dataset_id in [merged_id, dataset_id1, dataset_id2]
                        ]

            if all([dataset.record_ready for dataset in datasets]) and all(
                    [d.merged_dataset_ids for d in datasets[1:]]):
                break

            sleep(self.SLEEP_DELAY)

        datasets = [Dataset.find_one(dataset_id)
                    for dataset_id in [dataset_id1, dataset_id2]]

        for dataset in datasets:
            self.assertTrue(merged_id in dataset.merged_dataset_ids)

        dframe1 = datasets[0].dframe()
        merged_dataset = Dataset.find_one(merged_id)
        merged_dframe = merged_dataset.dframe(keep_parent_ids=True)

        for _, row in merged_dframe.iterrows():
            self.assertTrue(PARENT_DATASET_ID in row.keys())

        merged_dframe = merged_dataset.dframe()

        self.assertEqual(len(merged_dframe), 2 * len(dframe1))

        expected_dframe = concat([dframe1, dframe1],
                                 ignore_index=True)

        self.assertEqual(list(merged_dframe.columns),
                         list(expected_dframe.columns))

        self._check_dframes_are_equal(merged_dframe, expected_dframe)

    @requires_async
    def test_merge_datasets_add_calc_async(self):
        dataset_id1 = self._post_file('good_eats_large.csv')
        dataset_id2 = self._post_file('good_eats_large.csv')
        result = json.loads(self.controller.merge(
            dataset_ids=json.dumps([dataset_id1, dataset_id2])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        self.dataset_id = result[Dataset.ID]
        self.schema = json.loads(
            self.controller.info(self.dataset_id))[Dataset.SCHEMA]

        self._post_calculations(['amount < 4'])

    def test_merge_datasets_no_reserved_keys(self):
        dataset_id1 = self._post_file()
        dataset_id2 = self._post_file()
        result = json.loads(self.controller.merge(
            dataset_ids=json.dumps([dataset_id1, dataset_id2])))

        self.assertTrue(isinstance(result, dict))
        self.assertTrue(Dataset.ID in result)

        response = json.loads(self.controller.show(result[Dataset.ID]))
        row_keys = sum([row.keys() for row in response], [])

        for reserved_key in RESERVED_KEYS:
            self.assertFalse(reserved_key in row_keys)

    def test_merge_with_map(self):
        dataset_id1 = self._post_file()
        dataset_id2 = self._post_file('good_eats_aux.csv')
        merged_dataset_id = self._post_merge([dataset_id1, dataset_id2])

        expected_columns = Dataset.find_one(
            dataset_id1).dframe().columns.tolist()
        expected_columns.remove("food_type")
        expected_columns.append("food_type_2")
        expected_columns = set(expected_columns)

        merged_dataset = Dataset.find_one(merged_dataset_id)
        new_columns = set(merged_dataset.dframe().columns)

        self.assertEquals(expected_columns, new_columns)

    def test_merge_with_map_update(self):
        dataset_id1 = self._post_file()
        dataset_id2 = self._post_file('good_eats_aux.csv')
        merged_dataset_id = self._post_merge([dataset_id1, dataset_id2])

        original_ds2 = json.loads(self.controller.show(dataset_id2))
        original_length = len(original_ds2)
        original_merge = json.loads(self.controller.show(merged_dataset_id))
        original_merge_length = len(original_merge)

        self._put_row_updates(dataset_id2, 'good_eats_aux_update.json')
        response = json.loads(self.controller.show(dataset_id2))
        new_length = len(response)

        for new_row in response:
            if new_row not in original_ds2:
                break

        response = json.loads(self.controller.show(merged_dataset_id))

        for new_merge_row in response:
            if new_merge_row not in original_merge:
                break

        new_merge_length = len(response)

        self.assertEqual(original_length + 1, new_length)
        self.assertEqual(original_merge_length + 1, new_merge_length)
        self.assertEqual(new_row['food_type'], new_merge_row['food_type_2'])
        self.assertEqual(new_row['code'], new_merge_row['comments'])
