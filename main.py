import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

HH_API_URL = "https://api.hh.ru/vacancies"
SJ_API_URL = "https://api.superjob.ru/2.0/vacancies/"
SJ_CATALOGUES = {"Разработка, программирование": 48}
HH_VACANCY = "Программист"
CURRENCIES = {"hh": "RUR", "sj": "rub"}
CITIES = {"hh": {"Москва": 1}, "sj": {"Москва": 4}}
VACANCY_PERIOD = 30
LANGUAGES = {
    "JavaScript",
    "Java",
    "Python",
    "Ruby",
    "PHP",
    "C++",
    "C#",
    "C",
    "Go",
    "Scala"
}


def get_hh_vacancies(vacancy, language, area, period):
    vacancies = []
    vacancies_number = None
    payload = {
        "text": f"{vacancy} {language}",
        "search_field": "name",
        "area": area,
        "period": period,
        "page": 0,
        "per_page": 100
    }
    pages_number = 1
    while payload["page"] < pages_number:
        response = requests.get(HH_API_URL, params=payload)
        response.raise_for_status()
        response = response.json()
        vacancies += response.get("items", [])
        pages_number = response.get("pages")
        vacancies_number = response.get("found")
        payload["page"] += 1
    return vacancies, vacancies_number


def get_sj_vacancies(catalogues, language, town, period):
    vacancies = []
    vacancies_number = None
    headers = {"X-Api-App-Id": os.environ["SJ_SECRET_KEY"]}
    payload = {
        "catalogues": catalogues,
        "keyword": language,
        "town": town,
        "period": period,
        "page": 0,
        "count": 100
    }
    more = True
    while more:
        response = requests.get(SJ_API_URL, headers=headers, params=payload)
        response.raise_for_status()
        response = response.json()
        vacancies += response.get("objects", [])
        vacancies_number = response.get("total")
        more = response.get("more")
        payload["page"] += 1
    return vacancies, vacancies_number


def aggregate_hh_vacancies(languages):
    vacancies_by_language = {}
    for lang in LANGUAGES:
        vacancies, vacancies_found = get_hh_vacancies(HH_VACANCY, lang, CITIES["hh"]["Москва"], VACANCY_PERIOD)
        valid_salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                valid_salaries.append(salary)
        if vacancies_found > 100 and valid_salaries:
            vacancies_by_language[lang] = {}
            vacancies_by_language[lang]["vacancies_found"] = vacancies_found
            vacancies_by_language[lang]["vacancies_processed"] = len(valid_salaries)
            vacancies_by_language[lang]["average_salary"] = int(sum(valid_salaries) / len(valid_salaries))
    return vacancies_by_language


def aggregate_sj_vacancies(languages):
    vacancies_by_language = {}
    for lang in LANGUAGES:
        vacancies, vacancies_found = get_sj_vacancies(
            SJ_CATALOGUES["Разработка, программирование"],
            lang, CITIES["sj"]["Москва"],
            VACANCY_PERIOD
        )
        valid_salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                valid_salaries.append(salary)
        if vacancies_found:
            vacancies_by_language[lang] = {}
            vacancies_by_language[lang]["vacancies_found"] = vacancies_found
            vacancies_by_language[lang]["vacancies_processed"] = len(valid_salaries)
            vacancies_by_language[lang]["average_salary"] = int(sum(valid_salaries) / len(valid_salaries))
    return vacancies_by_language


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from and not salary_to:
        return salary_from * 1.2
    if not salary_from and salary_to:
        return salary_to * 0.8


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get("salary")
    if salary and salary.get("currency") == CURRENCIES["hh"]:
        return predict_salary(salary["from"], salary["to"])


def predict_rub_salary_sj(vacancy):
    salary = {k: v for k, v in vacancy.items() if k in ("payment_from", "payment_to", "currency")}
    if salary and salary.get("currency") == CURRENCIES["sj"]:
        return predict_salary(salary["payment_from"], salary["payment_to"])


def create_vacancies_table(vacancies, title):
    title = title
    columns = [["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]]
    rows = []
    for lang, agg_vacancies in vacancies.items():
        row = []
        row.append(lang)
        row.append(agg_vacancies.get("vacancies_found"))
        row.append(agg_vacancies.get("vacancies_processed"))
        row.append(agg_vacancies.get("average_salary"))
        rows.append(row)
    table = AsciiTable(columns + rows, title)
    return table.table


def main():
    load_dotenv()
    print(create_vacancies_table(aggregate_hh_vacancies(LANGUAGES), "HeadHunter Moscow"))
    print(create_vacancies_table(aggregate_sj_vacancies(LANGUAGES), "SuperJob Moscow"))


if __name__ == "__main__":
    main()
