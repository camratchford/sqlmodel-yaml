import yaml
from sqlmodel import Session, select

from mocks import (
    create_db_and_tables,
    engine,
    country_data_yaml,
    country_data_dict,
    Country,
    city_data_yaml,
    city_data_dict,
    City,
    valid_merged_city_yaml,
)
from sqlalchemy.orm import selectinload

loader = yaml.FullLoader


def test_yaml_load():
    create_db_and_tables()
    countries_from_yaml = yaml.load(country_data_yaml, Loader=loader)

    assert len(countries_from_yaml) == len(country_data_dict)
    assert isinstance(countries_from_yaml[0], Country)


def test_yaml_dump():
    create_db_and_tables()

    with Session(engine) as session:
        for country_data in country_data_dict:
            country = Country(**country_data)
            session.add(country)
            session.commit()
            session.refresh(country)

        for city_data in city_data_dict:
            city = City(**city_data)
            session.add(city)
            session.commit()
            session.refresh(city)

    with Session(engine) as session:
        cities = session.exec(select(City).options(selectinload(City.country))).all()
        yaml_from_cities = yaml.dump(cities)
        assert valid_merged_city_yaml == yaml_from_cities


def test_db_load():
    create_db_and_tables()
    cities_from_yaml = yaml.load(city_data_yaml, Loader=loader)
    countries_from_yaml = yaml.load(country_data_yaml, Loader=loader)

    with Session(engine) as session:
        for country in countries_from_yaml:
            session.add(country)
            session.commit()
            session.refresh(country)

        for city in cities_from_yaml:
            session.add(city)
            session.commit()
            session.refresh(city)


if __name__ == "__main__":
    test_yaml_load()
    test_yaml_dump()
    test_db_load()
