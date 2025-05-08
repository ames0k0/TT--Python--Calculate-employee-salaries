"""Скрипт подсчёта зарплаты сотрудников

XXX (ames0k0): Any duplicates in files (by **id**)
XXX (ames0k0): Filename endswith ?!


{
    "Design": {
        "Alice": {
            "hours": 150,
            "rate": 40,
            "payout": $6000,
        },
        "__report__": {
            "hours": sum(*),
            "payout": sum(*),
        }
    }
}


file_1  ->  [             ]  ->  [              ]  ->  [          ]  -> close
file_2  ->  [ data_to_obj ]  ->  [ filter_by_id ]  ->  [ group_by ]  -> close
...     ->  [             ]  ->  [              ]  ->  [          ]  -> close


{
    "department": {
        "a": [object],
    }
}
"""
import json
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Employee:
    id: str
    name: str
    email: str
    department: str
    hours: int
    rate: str

    @property
    def hours(self) -> int:
        return self._hours
    @hours.setter
    def hours(self, value: str) -> None:
        self._hours = int(value)

    @property
    def rate(self) -> int:
        return self._rate
    @rate.setter
    def rate(self, value: str) -> None:
        self._rate = int(value)

    def payout(self) -> int:
        """Returns the employee payout"""
        # FIXME (ames0k0): Could it be a float ?!
        return self.hours * self.rate


class Data2Object:
    COLUMNS_NAMES_TO_MATCH: dict[str, str] = {
        "id": "id",
        "name": "name",
        "email": "email",
        "department": "department",
        "hours_worked": "hours",
        "rate": "rate",
        "hourly_rate": "rate",
        "salary": "rate",
    }

    def __init__(self):
        self.data_order: dict = dict()

    def _match_column(self, column: str) -> str:
        """Matching column name with the known column names

        :param column: str, Column name to match
        :return: str, Matched column name
        :raises: ValueError, For unknown column name
        """
        if column not in self.COLUMNS_NAMES_TO_MATCH:
            raise ValueError("Не смог распознать название колонки:", column)
        return self.COLUMNS_NAMES_TO_MATCH[column]

    def match_columns(self, columns: list[str]) -> None:
        """Matching given columns name with the expected columns name

        :param columns: list[str], Column names to match
        :return: None
        :raises: ValueError, For not matched expected columns name
        """
        for index, column, in enumerate(columns):
            self.data_order[index] = self._match_column(column)
        columns_diff = set(
            self.COLUMNS_NAMES_TO_MATCH.values()

        ).difference(
            self.data_order.values()
        )
        if columns_diff:
            raise ValueError("Не смог найти колонки:", columns_diff)

    def dump(self, data: list[str]) -> Employee:
        values = {}
        for index, value in enumerate(data):
            values[self.data_order[index]] = value.strip()
        return Employee(**values)


class Report:
    OUTPUT_FILE_EXT: str = ".json"

    def __init__(self, data_files: list[str]):
        self.loaded_employees_id: set[str] = set()
        self.departments_and_employees: dict[
            str,
            list[Employee]
        ] = defaultdict(list)
        self.data_files = data_files

    def group_employees_by_department(self, data_file: str) -> None:
        """Groups employees by department"""
        with open(data_file) as ftr:
            columns, *lines = ftr.read().split("\n")
            columns = columns.split(",")
            # FIXME (ames0k0): What /!
            data_to_object = Data2Object()
            data_to_object.match_columns(columns=columns)
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                line = line.split(",")
                employee = data_to_object.dump(line)
                if employee.id in self.loaded_employees_id:
                    print("Duplicated data for employee_id:", employee.id)
                    continue
                self.loaded_employees_id.add(employee.id)
                self.departments_and_employees[employee.department].append(
                    employee
                )

    def generate(self, output_filename: str):
        result: dict[str, dict] = defaultdict(dict)
        for data_file in self.data_files:
            self.group_employees_by_department(data_file=data_file)

        for department, employees in self.departments_and_employees.items():
            report_per_department: dict[str, dict] = dict()
            sum_hours: int = 0
            sum_payout: int = 0
            for employee in employees:
                report_per_department[employee.name] = {
                    "hours": employee.hours,
                    "rate": employee.rate,
                    "payout": employee.payout(),
                }
                sum_hours += report_per_department[employee.name]["hours"]
                sum_payout += report_per_department[employee.name]["payout"]

            report_per_department["__report__"] = {
                "hours": sum_hours,
                "payout": sum_payout,
            }
            result[department] = report_per_department

        filename, ext = os.path.splitext(output_filename)
        with open(filename + self.OUTPUT_FILE_EXT, "w") as ftw:
            json.dump(result, ftw, indent=2)

if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Скрипт подсчёта зарплаты сотрудников",
        usage="python main.py [input_file]... --report [output_filename]",
        epilog="python main.py data1.csv data2.csv data3.csv --report payout",
    )
    parser.add_argument("--report", help="Report filename")

    args, input_files = parser.parse_known_args()

    if not args.report:
        parser.print_help()
        exit(1)

    any_non_existing_files: bool = False

    for file in input_files:
        if not os.path.exists(file):
            print("File not exists:", file)
            any_non_existing_files = True

    if any_non_existing_files:
        exit(1)

    report = Report(data_files=input_files)
    report.generate(output_filename=args.report)