import os
import typing
import tempfile

import pytest


@pytest.fixture(scope="package", autouse=True)
def setup_files() -> typing.Generator[tuple[str, ...], None, None]:
    """Создание файлов для тестирование"""
    with tempfile.NamedTemporaryFile(
        "w",
        prefix="valid_",
        suffix=".csv",
        delete=False,
        delete_on_close=False,
    ) as data_1:
        data_1.writelines(
            [
                "id,email,name,department,hours_worked,hourly_rate\n",
                "1,alice@example.com,Alice Johnson,Marketing,160,50\n",
                "2,bob@example.com,Bob Smith,Design,150,40\n",
                "3,carol@example.com,Carol Williams,Design,170,60\n",
            ]
        )

    with tempfile.NamedTemporaryFile(
        "w",
        prefix="valid_",
        suffix=".csv",
        delete=False,
        delete_on_close=False,
    ) as data_2:
        data_2.writelines(
            [
                "department,id,email,name,hours_worked,rate\n",
                "HR,101,grace@example.com,Grace Lee,160,45\n",
                "Marketing,102,henry@example.com,Henry Martin,150,35\n",
                "HR,103,ivy@example.com,Ivy Clark,158,38\n",
            ]
        )

    with tempfile.NamedTemporaryFile(
        "w",
        prefix="valid_",
        suffix=".csv",
        delete=False,
        delete_on_close=False,
    ) as data_3:
        # NOTE (ames0k0): Added `WRONG` data type for `salary`
        data_3.writelines(
            [
                "email,name,department,hours_worked,salary,id\n",
                "karen@example.com,Karen White,Sales,165,WRONG,201\n",
                "liam@example.com,Liam Harris,HR,155,42,202\n",
                "mia@example.com,Mia Young,Sales,160,37,203\n",
            ]
        )

    with tempfile.NamedTemporaryFile(
        "w",
        prefix="invalid_",
        suffix=".csv",
        delete=False,
        delete_on_close=False,
    ) as data_4:
        data_4.writelines(
            [
                "эл. почта,имя,отдел,часы_работы,зарплата,id\n",
                "karen@example.com,Karen White,Sales,165,50,201\n",
            ]
        )

    with tempfile.NamedTemporaryFile(
        "w",
        prefix="invalid_",
        suffix=".txt",
        delete=False,
        delete_on_close=False,
    ) as data_n:
        data_n.writelines(
            [
                "эл. почта,имя,отдел,часы_работы,зарплата,id\n",
                "karen@example.com,Karen White,Sales,165,50,201\n",
            ]
        )

    test_files = (
        data_1.name,
        data_2.name,
        data_3.name,
        data_4.name,
        data_n.name,
        "invalid_not_exist_file.txt",
    )

    yield test_files

    for test_file in test_files[:-1]:
        os.remove(test_file)
