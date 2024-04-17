# Programming vacancies compare
This script calculates the average salary of programmers by programming language. 
The data source is vacancies indicating salaries in Russian rubles, which are posted on the HeadHunter and SuperJob services. 
Vacancies posted during the last month are used for the calculation.

# How to install

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```bash
pip install -r requirements.txt
```

### Environment variables.

- SJ_SECRET_KEY

.env example:

```
SJ_SECRET_KEY = "v3.r.123456789.123456789a123456789b123456789c123456789de.123456789a123456789b123456789c123456789d"
```
### How to get

To get the key and use all API methods, you need to [register](https://api.superjob.ru/register) the application.

### Run

Launch on Linux or Windows as simple

```bash
$ python main.py

# You will see

$ python main.py
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| Python                | 516              | 129                 | 227054           |
| C#                    | 381              | 100                 | 210690           |
| Go                    | 262              | 42                  | 319228           |
| PHP                   | 505              | 219                 | 183226           |
| JavaScript            | 339              | 125                 | 191720           |
| C++                   | 499              | 122                 | 218363           |
| Java                  | 943              | 126                 | 264018           |
| C                     | 351              | 160                 | 209920           |
+-----------------------+------------------+---------------------+------------------+
+SuperJob Moscow--------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| Python                | 9                | 6                   | 192916           |
| C#                    | 3                | 2                   | 136250           |
| Go                    | 2                | 1                   | 300000           |
| PHP                   | 7                | 5                   | 105500           |
| JavaScript            | 9                | 5                   | 103500           |
| C++                   | 11               | 9                   | 175333           |
| Java                  | 2                | 1                   | 92500            |
| C                     | 12               | 9                   | 198333           |
+-----------------------+------------------+---------------------+------------------+
```

# Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).