import math
import random

from typing import Literal

from collections import namedtuple
from scipy.stats import norm, t
from decimal import Decimal


__all__ = [
    "Sample",
    "Population",
]

from decorators import parse_np_float


class BaseStatisticsAndProbability:


    def __init__(self, data_source, is_sample=False, parent=None):
        self._is_sample = is_sample
        self._parent = parent

        self.data = data_source if isinstance(data_source, list) else self._load_data(data_source)
        self.sum_data = sum(self.data)
        self.len_data = len(self.data)

        self._variance = None

    def _load_data(self, data_source):

        InfoDetails = namedtuple('InfoDetails', ['Salary', 'Age', 'Industry', 'Sex'])

        with open(data_source) as f:
            f.__next__()  # Assumes first line is header
            data = [
                InfoDetails(*i.strip().split(',')) for i in f
            ]

        return [int(i.Salary) for i in data]

    @property
    def average(self):
        return self.sum_data / self.len_data

    @property
    def variance(self):
        if self._variance is not None:
            return self._variance

        avg = self.average
        diffs_sum = sum((n - avg) ** 2 for n in self.data)
        divider = self.len_data - 1 if self._is_sample else self.len_data
        self._variance = diffs_sum / divider

        return self._variance

    @property
    def standard_deviation(self):
        return math.sqrt(self.variance)

    @property
    def standard_error(self):
        return self.standard_deviation / math.sqrt(self.len_data)


    def __str__(self):
        data_type = "SAMPLE" if isinstance(self, Sample) else "POPULATION"
        average = round(self.average, 2)
        variance = round(self.variance, 2)
        st_dev = round(self.standard_deviation, 2)

        return (f"\n-----------------------------------------------------------------\n"
                f"Data Type:             {data_type}\n"
                f"Average:               {average}\n"
                f"Variance:              {variance}\n"
                f"St. Dev:               {st_dev}\n"
                f"------------------------------------------------------------------\n")


class Population(BaseStatisticsAndProbability):
    def get_random_sample(self, n):
        if self._is_sample:
            raise ValueError("get_random_sample can be called only for population!")

        result = []
        for _ in range(n):
            random_index = random.randint(0, self.len_data - 1)
            result.append(self.data[random_index])

        return Sample(data_source=result, is_sample=True, parent=self)

    def __str__(self):
        average = round(self.average, 2)
        variance = round(self.variance, 2)
        st_dev = round(self.standard_deviation, 2)
        st_err = round(self.standard_error, 2)

        return (f"\n-----------------------------------------------------------------\n"
                f"Data Type:             POPULATION\n"
                f"Average:               {average}\n"
                f"Variance:              {variance}\n"
                f"St. Dev:               {st_dev}\n"
                f"St. Err:               {st_err}\n"
                f"------------------------------------------------------------------\n")


class Sample(BaseStatisticsAndProbability):
    @property
    def standard_error_corrected(self):
        return self.standard_error * self.fpc

    @property
    def fpc(self):
        if not self._is_sample:
            return 0

        if self.len_data / self._parent.len_data > 0.05:
            division = self._parent.len_data - self.len_data
            divider = self._parent.len_data - 1
            return math.sqrt(division / divider)

        return 0

    @parse_np_float
    def confidence_interval(self, cl: Decimal | float, score: Literal["T_Score", "Z_Score"]):

        if cl < 0 or cl > 1:
            raise ValueError(f"Confidence interval must be between 0 and 1, got {cl}")

        a = (1 - cl) / 2 # Alpha/2 value
        st_err_fpc = self.standard_error_corrected

        if score == "T_Score":
            t_score = t.ppf(cl + a, self.len_data - 1)
            st_err = self.standard_error
            return [
                (self.average - t_score * st_err, self.average + t_score * st_err),
                (self.average - t_score * st_err_fpc, self.average + t_score * st_err_fpc),
            ]

        if score == "Z_Score":
            z_score = norm.ppf(cl + a)
            if self.len_data < 30:
                raise ValueError("Sample is too small to use z-score for calculating confidence interval")

            parent = self._parent
            margin = z_score * parent.standard_deviation / math.sqrt(self.len_data)
            return [(self.average - margin, self.average + margin)]

        raise ValueError("You should provide Z or T score!")

    def __str__(self):
        average = round(self.average, 2)
        variance = round(self.variance, 2)
        st_dev = round(self.standard_deviation, 2)
        st_err = round(self.standard_error, 2)
        st_err_corr = round(self.standard_error_corrected, 2)
        fpc = round(self.fpc, 2)

        t_score_interval = self.confidence_interval(cl=0.95, score="T_Score")
        z_score_interval = self.confidence_interval(cl=0.95, score="Z_Score")

        return (f"\n-----------------------------------------------------------------\n"
                f"Data Type:             SAMPLE\n"
                f"Average:               {average}\n"
                f"Variance:              {variance}\n"
                f"St. Dev:               {st_dev}\n"
                f"St. Err:               {st_err}\n"
                f"St. Err. Corrected     {st_err_corr}\n"
                f"FPC:                   {fpc}\n"
                f"------------------------------------------------------------------\n"
                f"|  95% Confidence level with {self.len_data} sample participants             |\n"
                f"|  T-score interval corrected:        {t_score_interval[1]}           |\n"
                f"|  T-score interval:                  {t_score_interval[0]}           |\n"
                f"|  Z-score interval:                  {z_score_interval[0]}           |\n"
                f"------------------------------------------------------------------\n")
