import pytest

from main import ReportFileFormatsEnum, ReportDataProcessorsEnum
from main import Report


SETUP_FILES_TYPE = tuple[str, ...]

REPORT_FILENAME = "payout"


def test_without_export_files():
    with pytest.raises(ValueError) as excinfo:
        Report(
            export_files=[],
            report_filename="",
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[],
        )
    assert excinfo.value.args[0] == "Необходимо передать файлы для отчёта"


def test_with_wrong_export_files_path(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(FileNotFoundError) as excinfo:
        Report(
            export_files=setup_files[-1:],
            report_filename=REPORT_FILENAME,
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[ReportDataProcessorsEnum.PAYOUT],
        )
    assert excinfo.value.args[0] == "Файл не найден: invalid_not_exist_file.txt"


def test_with_wrong_export_files_ext(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        Report(
            export_files=setup_files[-2:-1],
            report_filename=REPORT_FILENAME,
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[ReportDataProcessorsEnum.PAYOUT],
        )
    assert excinfo.value.args[0] == "Чтение файла не поддерживает: .txt"


def test_without_report_filename(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        Report(
            export_files=setup_files[:4],
            report_filename="",
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[],
        )
    assert excinfo.value.args[0] == "Необходимо передать название файла для отчёта"


def test_without_report_file_format(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        Report(
            export_files=setup_files[:4],
            report_filename=REPORT_FILENAME,
            report_file_format="",  # type: ignore
            report_by=[],
        )
    assert excinfo.value.args[0] == "Необходимо передать формат файла для отчёта"


def test_with_wrong_report_file_format(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        Report(
            export_files=setup_files[:4],
            report_filename=REPORT_FILENAME,
            report_file_format="WRONG",  # type: ignore
            report_by=[],
        )
    assert excinfo.value.args[0] == "Запись файла не поддерживает: WRONG"


def test_without_report_by(setup_files: SETUP_FILES_TYPE):
    with pytest.raises(ValueError) as excinfo:
        Report(
            export_files=setup_files[:4],
            report_filename=REPORT_FILENAME,
            report_file_format=ReportFileFormatsEnum.JSON,
            report_by=[],
        )
    assert excinfo.value.args[0] == "Необходимо передать генераторов отчета"
