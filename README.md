# Подсчёт зарплаты сотрудников

CLI сприпт для подсчёта зарплаты сотрудников

### Скачивание проекта
```bash
git clone \
  --single-branch \
  --depth=1 \
  https://github.com/ames0k0/TT--Python--Calculate-employee-salaries

cd TT--Python--Calculate-employee-salaries
```

### Запуск скрипта
Аргументы к скрипту
- Название и/или путь к файлам
- `--report` Название файла для записи результата
- `-h` Посмотреть справки скрипта

```bash
python main.py data1.csv data2.csv data3.csv --report payout
```

Пример входных данных
```csv
id,email,name,department,hours_worked,hourly_rate
1,alice@example.com,Alice Johnson,Marketing,160,50
```

Пример выходных данных
```json
{
    "Design": {
        "Alice": {
            "hours": 150,
            "rate": 40,
            "payout": "$6000",
        },
        "__summary__": {
            "hours": 150,
            "payout": "$6000",
        }
    }
}
```

> [!NOTE]
> Выбрасывает исключение в случае если:
> - Передан невалидный путь к файлам
> - Передан другой расширение файлов экспорта
> - Передан другой расширение файла для отчета
> - Передан генерации отчета не по `PAYOUT`
> - Отсутствуют необходимые колонки

<p align="center"><img src="./data/Diagram.drawio.png" /></p>