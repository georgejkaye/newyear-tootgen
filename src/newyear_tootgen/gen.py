import json
import requests
import flag
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


countries_json_url = "https://gist.githubusercontent.com/emnsen/a2364b401d1cb02ac09a850a57017994/raw/bada9a4dcc6ac20428d0abfde4204bbce3f0c3f1/country-codes.json"


@dataclass
class Country:
    name: str
    time_zone: str
    capital: str
    code: str


def get_countries_dict() -> list[Country]:
    data = requests.get(countries_json_url)
    json = data.json()
    countries = []
    for country in json:
        capital = country["capital"]
        time_zone = country["time-zone-in-capital"]
        name = country["country-name"]
        code = country["iso2"]
        country_obj = Country(name, time_zone, capital, code)
        countries.append(country_obj)
    return countries


def get_flag_emoji(country_code: str) -> str:
    return flag.flag(country_code)


def get_utc_of_new_year(time_zone: str) -> datetime:
    url = f"http://worldtimeapi.org/api/timezone/{time_zone}"
    response = requests.get(url)
    json = response.json()
    raw_offset = int(json["raw_offset"])
    if json["dst"]:
        dst_offset = int(json["dst_offset"])
    else:
        dst_offset = 0
    utc_newyear = (
        datetime(2024, 1, 1)
        - timedelta(seconds=raw_offset)
        - timedelta(seconds=dst_offset)
    )
    return utc_newyear


def get_newyear_dict(countries: list[Country]) -> dict[datetime, list[Country]]:
    newyear_dict = {}
    for country in countries:
        time_zone = country.time_zone
        newyear_utc = get_utc_of_new_year(time_zone)
        if newyear_dict.get(newyear_utc) is None:
            newyear_dict[newyear_utc] = [country]
        else:
            newyear_dict[newyear_utc].append(country)
    return newyear_dict


def country_to_caps_emoji(country: Country) -> str:
    emoji = get_flag_emoji(country.code)
    name = country.name.upper()
    return f"{name} {emoji}"


toot_length = 400


def get_toots(countries: list[Country], year: int) -> list[str]:
    country_string_list = [country_to_caps_emoji(country) for country in countries]
    string = f"WELCOME TO {year}"
    strings = []
    for country_string in country_string_list:
        if len(string) + len(country_string) > (toot_length - 3):
            string = f"{string}..."
            strings.append(string)
            string = f"...{country_string}"
        else:
            string = f"{string} {country_string}"
    strings.append(string)
    return strings


def write_toot_to_file(toot_time: datetime, toots: list[str]):
    toot_dir = Path("toots")
    file_name = toot_dir / toot_time.strftime("%Y-%m-%d-%H%M")
    with open(file_name, "w") as f:
        json.dump(toots, f)


def main():
    year = datetime.today().year + 1
    countries = get_countries_dict()
    newyear_dict = get_newyear_dict(countries)
    newyear_array = newyear_dict.items()
    newyear_sorted = sorted(newyear_array, key=lambda a: a[0])
    for x in newyear_sorted:
        toots = get_toots(x[1], year)
        write_toot_to_file(x[0], toots)


if __name__ == "__main__":
    main()
