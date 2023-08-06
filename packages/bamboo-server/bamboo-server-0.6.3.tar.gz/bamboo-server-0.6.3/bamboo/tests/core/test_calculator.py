from bamboo.core.parser import Parser
from bamboo.core.calculator import calculate_columns
from bamboo.lib.datetools import now, recognize_dates
from bamboo.models.calculation import Calculation
from bamboo.models.dataset import Dataset
from bamboo.tests.test_base import TestBase


class TestCalculator(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.dataset = Dataset()
        self.dataset.save(
            self.test_dataset_ids['good_eats_with_calculations.csv'])
        dframe = recognize_dates(
            self.get_data('good_eats_with_calculations.csv'))
        self.dataset.save_observations(dframe)
        self.group = None
        self.places = 5

    def _equal_msg(self, calculated, stored, formula):
        return '(calculated %s) %s != (stored %s) %s ' % (type(calculated),
               calculated, type(stored), stored) +\
            '(within %s places), formula: %s' % (self.places, formula)

    def _test_calculator(self):
        self.dframe = self.dataset.dframe()

        columns = self.dframe.columns.tolist()
        self.start_num_cols = len(columns)
        self.added_num_cols = 0

        column_labels_to_slugs = {
            column_attrs[Dataset.LABEL]: (column_name) for
            (column_name, column_attrs) in self.dataset.schema.items()
        }
        self.label_list, self.slugified_key_list = [
            list(ary) for ary in zip(*column_labels_to_slugs.items())
        ]

        for idx, formula in enumerate(self.calculations):
            name = 'test-%s' % idx

            Parser.validate_formula(formula, self.dataset)

            calculation = Calculation()
            calculation.save(self.dataset, formula, name, self.group)
            self.now = now()
            calculate_columns(self.dataset, [calculation])

            self.column_labels_to_slugs = self.dataset.schema.labels_to_slugs

            self._test_calculation_results(name, formula)
