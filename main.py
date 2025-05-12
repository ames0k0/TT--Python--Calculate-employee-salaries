#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import abc
import enum
import json
import typing
import argparse
from collections import defaultdict
from dataclasses import dataclass


ProcessDataType = dict[str, int | str]
ReportFileDataType = dict[str, dict[str, ProcessDataType]]


class ReportFileFormatsEnum(str, enum.Enum):
    JSON = "JSON"


class ReportDataProcessorsEnum(str, enum.Enum):
    PAYOUT = "PAYOUT"


class AbcExportFileReader(abc.ABC):
    @abc.abstractmethod
    def __init__(self, filepath: str):
        """Initiates the export reader

        :param filepath: str, Export filepath to stream
        :returns: None
        """

    @abc.abstractmethod
    def stream(self) -> typing.Generator[list[str], None, None]:
        """Streams export file

        :param filepath: str, Export filepath to stream
        :yields: Generator[list[str], None, None], Yields the data
        :returns: None
        """


class AbcReportFileWriter(abc.ABC):
    @abc.abstractmethod
    def __init__(self, filename: str):
        """Initiates the report writer

        :param filename: str, Report filename
        :returns: None
        """

    @abc.abstractmethod
    def write(self, data: ReportFileDataType) -> None:
        """Writes report to file

        :param data: dict[str, dict], Report data to write
        :returns: None
        """


class AbcDataProcessor(abc.ABC):
    @abc.abstractmethod
    def process(self, data: "Employee") -> ProcessDataType:
        """Processes the given data"""

    @abc.abstractmethod
    def summarize(self) -> ProcessDataType:
        """Summarize the processed data"""

    @abc.abstractmethod
    def finish(self) -> ProcessDataType:
        """Finish the processing data"""


class CSVExportFileReader(AbcExportFileReader):
    DATA_DELIMITER: str = ","

    def __init__(self, filepath: str):
        self.filepath = filepath

    def stream(self):
        with open(self.filepath) as ftr:
            for line in ftr.read().split("\n"):
                line = line.strip()
                if not line:
                    continue
                yield line.split(self.DATA_DELIMITER)


class JSONReportFileWriter(AbcReportFileWriter):
    FILE_EXT: str = ".json"

    def __init__(self, filename: str):
        self.filename = os.path.splitext(filename)[0] + self.FILE_EXT

    def write(self, data: ReportFileDataType):
        with open(self.filename, "w") as ftw:
            json.dump(data, ftw, indent=2)


class CalcEmployeePayout(AbcDataProcessor):
    def __init__(self):
        self.sum_hours: int = 0
        self.sum_payout: int = 0

    def view_payout(self, payout: int, format: str = "$%s") -> str:
        return format % payout

    def process(self, data: "Employee") -> ProcessDataType:
        payout = data.rate * data.hours
        self.sum_hours += data.hours
        self.sum_payout += payout
        return {
            "hours": data.hours,
            "rate": data.rate,
            "payout": self.view_payout(payout),
        }

    def summarize(self) -> ProcessDataType:
        summarized_data: ProcessDataType = {
            "hours": self.sum_hours,
            "payout": self.view_payout(self.sum_payout),
        }
        # XXX (ames0k0): Clean up init data
        self.sum_hours = 0
        self.sum_payout = 0

        return summarized_data

    def finish(self) -> ProcessDataType:
        return {}


@dataclass
class Employee:
    id: str
    name: str
    email: str
    department: str
    hours: int  # type: ignore
    rate: int  # type: ignore

    @property  # type: ignore
    def hours(self) -> int:
        return self._hours

    @hours.setter
    def hours(self, value: str) -> None:
        # NOTE (ames0k0): No type checking
        self._hours = int(value)

    @property  # type: ignore
    def rate(self) -> int:
        return self._rate

    @rate.setter
    def rate(self, value: str) -> None:
        # NOTE (ames0k0): No type checking
        self._rate = int(value)


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
        self.data_order: dict[int, str] = dict()

    def match_columns(self, columns: list[str]) -> None:
        """Matching given columns name with the expected columns name

        :param columns: list[str], Column names to match
        :return: None
        :raises: ValueError, For not matched expected columns name
        """
        for index, column in enumerate(columns):
            # XXX (ames0k0): Ищем только нужных колонок
            if column not in self.COLUMNS_NAMES_TO_MATCH:
                continue
            self.data_order[index] = self.COLUMNS_NAMES_TO_MATCH[column]

        columns_diff = set(self.COLUMNS_NAMES_TO_MATCH.values()).difference(
            self.data_order.values()
        )

        if columns_diff:
            raise ValueError(
                "Отсутствуют колонки: %s" % ",".join(sorted(columns_diff)),
            )

    def dump(self, data: list[str]) -> Employee:
        """Returns `Employee` object generated by the given data

        :param data: list[str], Raw data from `export_files_reader`
        :returns Employee: Employee object
        """
        values = {}
        for index, value in enumerate(data):
            values[self.data_order[index]] = value.strip()

        return Employee(**values)  # type: ignore


class Report:
    def __init__(
        self,
        export_files: typing.Sequence[str],
        report_filename: str,
        report_file_format: ReportFileFormatsEnum,
        report_by: list[ReportDataProcessorsEnum],
    ):
        self.export_files_reader = self.get_export_files_reader(
            export_files=export_files,
        )
        self.report_file_writer = self.get_report_file_writer(
            report_filename=report_filename,
            report_file_format=report_file_format,
        )
        self.report_data_processors = self.get_report_processors(
            report_by=report_by,
        )
        self.loaded_employees_id: set[str] = set()
        self.departments_and_employees: dict[
            str,
            list[Employee],
        ] = defaultdict(list)

    def get_export_files_reader(
        self,
        export_files: typing.Sequence[str],
    ) -> list[CSVExportFileReader]:
        """Returns file reader objects

        :param export_files: list[str], Export filepaths to read
        :returns: typing.Union[CSVExportFileReader], Reader objects
        """
        if not export_files:
            raise ValueError("Необходимо передать файлы для отчёта")

        files_reader: list[CSVExportFileReader] = list()

        for export_file in set(export_files):
            if not os.path.exists(export_file):
                raise FileNotFoundError("Файл не найден: %s" % export_file)

            _, ext = os.path.splitext(export_file)
            if ext == ".csv":
                files_reader.append(
                    CSVExportFileReader(
                        filepath=export_file,
                    )
                )
            else:
                raise ValueError("Чтение файла не поддерживает: %s" % ext)

        return files_reader

    def get_report_file_writer(
        self,
        report_filename: str,
        report_file_format: ReportFileFormatsEnum,
    ) -> JSONReportFileWriter:
        """Returns `report_file_writer` for the given `report_file_format`"""
        if not report_filename:
            raise ValueError("Необходимо передать название файла для отчёта")

        if not report_file_format:
            raise ValueError("Необходимо передать формат файла для отчёта")

        if report_file_format == ReportFileFormatsEnum.JSON:
            return JSONReportFileWriter(filename=report_filename)
        else:
            raise ValueError(
                "Запись файла не поддерживает: %s" % report_file_format,
            )

    def get_report_processors(
        self,
        report_by: list[ReportDataProcessorsEnum],
    ) -> list[CalcEmployeePayout]:
        """Returns list of `report_data_processors`"""
        if not report_by:
            raise ValueError("Необходимо передать генераторов отчета")

        processors: list[CalcEmployeePayout] = []
        for rp in set(report_by):
            if rp == ReportDataProcessorsEnum.PAYOUT:
                processors.append(CalcEmployeePayout())
            else:
                raise ValueError("Генератор отчёта не поддерживает: %s" % rp)

        return processors

    def group_employees_by_department(
        self,
        file_reader: CSVExportFileReader,
    ) -> None:
        """Groups employees by `department`

        :param file_reader: typing.Union[CSVExportFileReader], Reader object
        :returns: None
        """
        rows: typing.Generator[list[str], None, None] = file_reader.stream()
        data_to_object = Data2Object()
        data_to_object.match_columns(columns=next(rows))
        for row in rows:
            employee = data_to_object.dump(row)
            if employee.id in self.loaded_employees_id:
                print("Duplicated data for employee_id:", employee.id)
                continue
            self.loaded_employees_id.add(employee.id)
            self.departments_and_employees[employee.department].append(
                employee,
            )

    def generate(self) -> None:
        """Generates the report"""
        result: ReportFileDataType = dict()

        # Группировка сотрудников по `department`
        for file_reader in self.export_files_reader:
            self.group_employees_by_department(file_reader=file_reader)

        for department, employees in self.departments_and_employees.items():
            report_per_department: dict[str, ProcessDataType] = dict()

            for employee in employees:
                # Обработка каждого сотрудника
                employee_report: ProcessDataType = dict()
                for rd_processor in self.report_data_processors:
                    employee_report.update(
                        rd_processor.process(data=employee),
                    )
                report_per_department[employee.name] = employee_report

            # Подвести итоги для каждого `department`
            summarized_per_department: ProcessDataType = dict()
            for rd_processor in self.report_data_processors:
                summarized_per_department.update(
                    rd_processor.summarize(),
                )

            # NOTE (ames0k0)
            # В примере выходного файла имеется сумма всех часов и зарплат
            report_per_department["__summary__"] = summarized_per_department
            result[department] = report_per_department

        # XXX (ames0k0)
        # Тут можно подвести финальную обработку `rd_processor.finish()`

        self.report_file_writer.write(data=result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description="\n".join(
            (
                "Скрипт подсчёта зарплаты сотрудников\n",
                "Поддерживает чтение файлов: .csv",
                "Поддерживает запись файлов: .json",
                "Поддерживает генераторов отчёта: PAYOUT",
            )
        ),
        usage="python main.py [export_file]... --report [report_filename]",
        epilog="python main.py data1.csv data2.csv data3.csv --report payout",
    )
    parser.add_argument("--report", help="Report filename")

    args, export_files = parser.parse_known_args()

    if not args.report:
        parser.print_help()
        exit(1)

    report = Report(
        export_files=export_files,
        report_filename=args.report,
        report_file_format=ReportFileFormatsEnum.JSON,
        report_by=[
            ReportDataProcessorsEnum.PAYOUT,
        ],
    )
    report.generate()
