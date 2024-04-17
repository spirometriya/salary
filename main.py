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
        vacancies += response.json().get("items", [])
        pages_number = response.json()["pages"]
        payload["page"] += 1
    return vacancies


def get_sj_vacancies(catalogues, language, town, period):
    vacancies = []
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
        vacancies += response.json().get("objects", [])
        more = response.json()["more"]
        payload["page"] += 1
    return vacancies


def aagregate_hh_vacancies(languages):
    vacancies_by_language = {}
    for lang in LANGUAGES:
        vacancies = get_hh_vacancies(HH_VACANCY, lang, CITIES["hh"]["Москва"], VACANCY_PERIOD)
        vacancies_found = len(vacancies)
        valid_salary = [predict_rub_salary_hh(v) for v in vacancies if predict_rub_salary_hh(v)]
        if vacancies_found > 100:
            vacancies_by_language[lang] = {}
            vacancies_by_language[lang]["vacancies_found"] = vacancies_found
            vacancies_by_language[lang]["vacancies_processed"] = len(valid_salary)
            vacancies_by_language[lang]["average_salary"] = int(sum(valid_salary) / len(valid_salary))
    return vacancies_by_language


def aagregate_sj_vacancies(languages):
    vacancies_by_language = {}
    for lang in LANGUAGES:
        vacancies = get_sj_vacancies(SJ_CATALOGUES["Разработка, программирование"], lang, CITIES["sj"]["Москва"],
                                     VACANCY_PERIOD)
        vacancies_found = len(vacancies)
        valid_salary = [predict_rub_salary_sj(v) for v in vacancies if predict_rub_salary_sj(v)]
        if vacancies_found:
            vacancies_by_language[lang] = {}
            vacancies_by_language[lang]["vacancies_found"] = vacancies_found
            vacancies_by_language[lang]["vacancies_processed"] = len(valid_salary)
            vacancies_by_language[lang]["average_salary"] = int(sum(valid_salary) / len(valid_salary))
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
    if salary:
        if salary.get("currency") != CURRENCIES["hh"]:
            return
        return predict_salary(salary["from"], salary["to"])


def predict_rub_salary_sj(vacancy):
    salary = {k: v for k, v in vacancy.items() if k in ("payment_from", "payment_to", "currency")}
    if salary:
        if salary.get("currency") != CURRENCIES["sj"]:
            return
        return predict_salary(salary["payment_from"], salary["payment_to"])


def parse_vacancies(vacancies):
    parsed_vacancies = []
    for lang, vacancies_data in vacancies.items():
        vacancy_values = []
        vacancy_values.append(lang)
        vacancy_values.append(vacancies_data.get("vacancies_found"))
        vacancy_values.append(vacancies_data.get("vacancies_processed"))
        vacancy_values.append(vacancies_data.get("average_salary"))
        parsed_vacancies.append(vacancy_values)
    return parsed_vacancies


def create_vacancies_table(vacancies, title):
    title = title
    columns = [["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]]
    table_data = parse_vacancies(vacancies)
    table = AsciiTable(columns + table_data, title)
    return table.table


def main():
    load_dotenv()
    print(create_vacancies_table(aagregate_hh_vacancies(LANGUAGES), "HeadHunter Moscow"))
    print(create_vacancies_table(aagregate_sj_vacancies(LANGUAGES), "SuperJob Moscow"))


if __name__ == "__main__":
    main()
