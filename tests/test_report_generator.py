import os
import json

import pytest

from main import ReportFileFormatsEnum, ReportDataProcessorsEnum, ReportFileDataType
from main import Report


SETUP_FILES_TYPE = tuple[str, ...]

REPORT_FILENAME = "payout"


def test_with_wrong_export_files_columns(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        report = Report(
            export_files=setup_files[3:4],
            report_filename=REPORT_FILENAME,
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[ReportDataProcessorsEnum.PAYOUT],
        )
        report.generate()
    # NOTE (ames0k0): `id` exists
    assert (
        excinfo.value.args[0] == "Отсутствуют колонки: department,email,hours,name,rate"
    )


def test_with_wrong_export_files_data(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        report = Report(
            export_files=setup_files[2:3],
            report_filename=REPORT_FILENAME,
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[ReportDataProcessorsEnum.PAYOUT],
        )
        report.generate()
    # NOTE (ames0k0): `id` exists
    assert excinfo.value.args[0] == "invalid literal for int() with base 10: 'WRONG'"


def test_with_report_file_generation_with_single_export_files(
    setup_files: SETUP_FILES_TYPE,
):
    report = Report(
        export_files=setup_files[:1],
        report_filename=REPORT_FILENAME,
        report_file_format=ReportFileFormatsEnum.JSON,
        report_by=[ReportDataProcessorsEnum.PAYOUT],
    )
    report.generate()

    assert os.path.exists(report.report_file_writer.filename), (
        "Отчёт не был сформирован"
    )

    generated_report_data: ReportFileDataType = {
        "Marketing": {
            "Alice Johnson": {"hours": 160, "rate": 50, "payout": "$8000"},
            "__summary__": {"hours": 160, "payout": "$8000"},
        },
        "Design": {
            "Bob Smith": {"hours": 150, "rate": 40, "payout": "$6000"},
            "Carol Williams": {"hours": 170, "rate": 60, "payout": "$10200"},
            "__summary__": {"hours": 320, "payout": "$16200"},
        },
    }

    with open(report.report_file_writer.filename, "r") as ftr:
        assert generated_report_data == json.load(ftr)

    os.remove(report.report_file_writer.filename)


def test_with_report_file_generation_with_multiple_export_files(
    setup_files: SETUP_FILES_TYPE,
):
    report = Report(
        export_files=setup_files[:2],
        report_filename=REPORT_FILENAME,
        report_file_format=ReportFileFormatsEnum.JSON,
        report_by=[ReportDataProcessorsEnum.PAYOUT],
    )
    report.generate()

    assert os.path.exists(report.report_file_writer.filename), (
        "Отчёт не был сформирован"
    )

    generated_report_data: ReportFileDataType = {
        "HR": {
            "Grace Lee": {"hours": 160, "rate": 45, "payout": "$7200"},
            "Ivy Clark": {"hours": 158, "rate": 38, "payout": "$6004"},
            "__summary__": {"hours": 318, "payout": "$13204"},
        },
        "Marketing": {
            "Henry Martin": {"hours": 150, "rate": 35, "payout": "$5250"},
            "Alice Johnson": {"hours": 160, "rate": 50, "payout": "$8000"},
            "__summary__": {"hours": 310, "payout": "$13250"},
        },
        "Design": {
            "Bob Smith": {"hours": 150, "rate": 40, "payout": "$6000"},
            "Carol Williams": {"hours": 170, "rate": 60, "payout": "$10200"},
            "__summary__": {"hours": 320, "payout": "$16200"},
        },
    }

    with open(report.report_file_writer.filename, "r") as ftr:
        loaded_data_from_generated_file = json.load(ftr)
    assert (
        generated_report_data["Marketing"]
        == loaded_data_from_generated_file["Marketing"]
    )
    assert generated_report_data["Design"] == loaded_data_from_generated_file["Design"]
    assert generated_report_data["HR"] == loaded_data_from_generated_file["HR"]

    os.remove(report.report_file_writer.filename)
