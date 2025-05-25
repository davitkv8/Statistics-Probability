import math
import random


class StatisticsAndProbability:


    def __init__(self, data_source, is_sample=False, parent=None):
        self._is_sample = is_sample
        self._parent = parent

        self.data = data_source if isinstance(data_source, list) else self._load_data(data_source)
        self.sum_data = sum(self.data)
        self.len_data = len(self.data)

        self._variance = None

    def _load_data(self, data_source):
        with open(data_source) as f:
            f.__next__()  # Assumes first line is header
            data = [float(i.strip()) for i in f]

        return data

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

    def confidence_interval(self, **kwargs):
        t_score = kwargs.get("T_score")
        if t_score:
            st_err_fpc = self.standard_error_corrected
            st_err = self.standard_error
            return [
                (self.average - t_score * st_err, self.average + t_score * st_err),
                (self.average - t_score * st_err_fpc, self.average + t_score * st_err_fpc),
            ]

        z_score = kwargs.get("Z_score")
        if z_score:
            population = self._parent
            return [
                (self.average - z_score * population.standard_error, self.average + z_score * population.standard_error),
                (self.average - z_score * population.standard_error_corrected, self.average + z_score * population.standard_error_corrected),
            ]

        raise ValueError("You should provide Z or T score!")


    def get_random_sample(self, n):
        if self._is_sample:
            raise ValueError("get_random_sample can be called only for population!")

        result = []
        for _ in range(n):
            random_index = random.randint(0, self.len_data - 1)
            result.append(self.data[random_index])

        return StatisticsAndProbability(data_source=result, is_sample=True, parent=self)

    def __str__(self):

        data_type = "SAMPLE" if self._is_sample else "POPULATION"
        average = round(self.average, 2)
        variance = round(self.variance, 2)
        st_dev = round(self.standard_deviation, 2)
        st_err = round(self.standard_error, 2)
        st_err_corr = round(self.standard_error_corrected, 2)
        fpc = round(self.fpc, 2)

        return (f"\n-----------------------------------------------------------------\n"
                f"Data Type:         {data_type}\n"
                f"Average:           {average}\n"
                f"Variance:          {variance}\n"
                f"St. Dev:           {st_dev}\n"
                f"St. Err:           {st_err}\n"
                f"St. Err. Corrected {st_err_corr}\n"
                f"FPC:               {fpc}\n"
                f"------------------------------------------------------------------\n")
