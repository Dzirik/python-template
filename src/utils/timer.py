"""
Timer
"""

from datetime import datetime
from time import sleep, time

from pandas import DataFrame

DEC_PLACES = 2


class Timer:
    """
    Class for measuring execution time.

    It has initial and final timestamps and as many in the middle as necessary. It can voluntary print out some message.
    """

    def __init__(self) -> None:
        self._timer_start_time: float
        self._timer_end_time: float
        self._task_start_time: float

        self._mean_times_in_sec: list[float]
        self._mean_time_cumulative_secs: list[float]
        self._mean_times_labels: list[str]

        self._print_results: bool = True

    def set_results_printing(self, print_results: bool) -> None:
        """
        Sets if to print the results.
        :param print_results: bool.
        """
        self._print_results = print_results

    def _evaluate_results_printing(self, print_results_local: bool | None) -> bool:
        """
        Evaluates if print the results comparing both print_results_local and global setting.
        :param print_results_local: bool. Local print information.
        :return: bool. If to print results.
        """
        if print_results_local is None:
            return self._print_results
        return print_results_local

    def start(self, print_results_local: bool | None = None) -> None:
        """
        Starts global time measurement.
        :param print_results_local: Optional[bool]. Except global results printing,
                using this variable one can overwrite the global schema. If None, global setting is used. If not
                None, this variable is used. This is not very smart solution, but a need of using this in more flexible
                arose.
        """
        self._timer_start_time = time()
        self._timer_end_time = self._timer_start_time
        self._task_start_time = self._timer_start_time

        self._mean_times_in_sec = []
        self._mean_time_cumulative_secs = []
        self._mean_times_labels = []

        if self._evaluate_results_printing(print_results_local):
            print(
                f"Date and Time of Starting Execution: {self._as_date(self._timer_start_time).strftime('%d/%m/%Y')} "
                f"{self._as_date(self._timer_start_time).strftime('%X')}"
            )

    def get_meantime(self, label: str | None = None) -> tuple[float, float]:
        """
        Adds meantime.
        :param label: str. Label of last interval.
        :return: Tuple[float, float]. Difference from the last meantime in seconds and minutes.
        """
        now = time()
        diff = now - self._task_start_time
        self._mean_times_in_sec.append(diff)
        self._mean_time_cumulative_secs.append(sum(self._mean_times_in_sec))
        self._mean_times_labels.append(label or "")
        self._task_start_time = now
        self._timer_end_time = now

        return round(diff, DEC_PLACES), round(diff / 60, DEC_PLACES)

    def set_meantime(self, label: str | None = None, print_results_local: bool | None = None) -> None:
        """
        Sets end of the mean time interval as time and (voluntary) label. Optionally prints results to the console.
        :param label: str. Label of interval that ended.
        :param print_results_local: Optional[bool]. Except global results printing,
                using this variable one can overwrite the global schema. If None, global setting is used. If not
                None, this variable is used. This is not very smart solution, but a need of using this in more flexible
                arose.
        """
        diff_s, diff_m = self.get_meantime(label)

        if self._evaluate_results_printing(print_results_local):
            print(f"Duration of: {label} is {diff_s} s, {diff_m} mins.")

    def get_end(self, label: str | None) -> tuple[float, float, float, float]:
        """
        Ends global time measurement.
        :param label: str. Label of last interval.
        :return: Tuple[float, float, float, float]. Difference from the last meantime in seconds and minutes and
                                      overall duration, both in seconds and minutes.
        """
        self._timer_end_time = time()
        diff = self._timer_end_time - self._task_start_time
        duration = self._timer_end_time - self._timer_start_time
        self._mean_times_in_sec.append(diff)
        self._mean_time_cumulative_secs.append(sum(self._mean_times_in_sec))
        self._mean_times_labels.append(label or "")

        return (
            round(diff, DEC_PLACES),
            round(diff / 60, DEC_PLACES),
            round(duration, DEC_PLACES),
            round(duration / 60, DEC_PLACES),
        )

    def end(self, label: str | None = None, print_results_local: bool | None = None) -> None:
        """
        Ends and saves the end time. Optionally prints results to the console.
        :param label: str. Label of last interval.
        :param print_results_local: Optional[bool]. Except global results printing,
                using this variable one can overwrite the global schema. If None, global setting is used. If not
                None, this variable is used. This is not very smart solution, but a need of using this in more flexible
                arose.
        """
        diff_s, diff_m, duration_s, duration_m = self.get_end(label)

        if self._evaluate_results_printing(print_results_local):
            print(f"Duration of: {label} is {diff_s} s, {diff_m} mins.")
            print(
                f"Date and Time of Ending Execution: {self._as_date(self._timer_end_time).strftime('%d/%m/%Y')} "
                f"{self._as_date(self._timer_end_time).strftime('%X')}"
            )
            print(f"Overall Duration is: {duration_s} s, {duration_m} mins.")

    # GETTERS -------------------------------------------------------------------------------------

    def get_start_time(self) -> float:
        """
        Returns global start time as timestamp/float.
        :return: float.
        """
        return self._timer_start_time

    def get_end_time(self) -> float:
        """
        Returns global end time as timestamp/float.
        :return: float.
        """
        return self._timer_end_time

    def get_data(self) -> tuple[list[float], list[float], list[str], DataFrame]:
        """
        Returns interval durations, cumulative time, and label times both separately and in the form of a dataframe.
        :return: Tuple[List[float], List[float], List[str], DataFrame]. Mean duration times in seconds, cumulative mean
        times and mean label times.
        """
        df = DataFrame()
        df["LABEL"] = self._mean_times_labels
        df["MEANTIMES [s]"] = self._mean_times_in_sec
        df["CUMULATIVE TIME [s]"] = self._mean_time_cumulative_secs
        return self._mean_times_in_sec, self._mean_time_cumulative_secs, self._mean_times_labels, df

    # HELPER FUNCTIONS ----------------------------------------------------------------------------

    @staticmethod
    def _as_date(timestamp: float) -> datetime:
        """
        Converts timestamp in float format to date format.
        :param timestamp: float. Date as float.
        :return: datetime.
        """
        return datetime.utcfromtimestamp(timestamp)


if __name__ == "__main__":
    t = Timer()

    t.start()
    sleep(0.2)

    t.set_meantime(label="First Interval")
    sleep(0.3)

    t.set_meantime(label="Second Interval")
    sleep(0.1)

    t.end(label="Last Interval")

    (MT, MT_C, MT_L, DATA_FRAME) = t.get_data()
    print(round(sum(MT), 2))

    print(t.get_start_time())
    print(t.get_end_time())
    print(MT)
    print(MT_C)
    print(MT_L)
    print(DATA_FRAME)

    t.start()
    sleep(0.1)

    t.set_meantime(label="First Interval - second round")
    sleep(0.05)

    t.set_meantime(label="Second Interval - second round")
    sleep(0.01)

    t.end(label="Last Interval - second round")

    (MT, MT_C, MT_L, DATA_FRAME) = t.get_data()
    print(round(sum(MT), 2))

    print(t.get_start_time())
    print(t.get_end_time())
    print(MT)
    print(MT_C)
    print(MT_L)
    print(DATA_FRAME)
