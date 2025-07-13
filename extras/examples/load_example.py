from pathlib import Path
import yaml
from sqlmodel import create_engine, Field, Relationship, Session, select
from yaml_model import YAMLModel

db_path = Path(__file__).parent / "database.db"
sqlite_file_name = db_path.relative_to(Path().cwd()).as_posix()
sqlite_url = f"sqlite:///{sqlite_file_name}?"

connect_kwargs = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_kwargs)


class Country(YAMLModel, table=True):
    canonical_name: str = Field(alias="cname", default=None, primary_key=True)
    display_name: str = Field(alias="name")
    cities: list["City"] = Relationship(back_populates="country")


class City(YAMLModel, table=True):
    canonical_name: str = Field(alias="cname", primary_key=True)
    display_name: str = Field(alias="name")
    country_cname: str = Field(default=None, foreign_key="country.canonical_name")
    country: Country = Relationship(back_populates="cities")


def create_db_and_tables():
    # Only drop the tables when testing
    YAMLModel.metadata.drop_all(engine)
    YAMLModel.metadata.create_all(engine)


country_data_yaml = """
- !Country
  display_name: Ashjikistan
  canonical_name: ashjikistan
  
- !Country
  display_name: Kamzikstan
  canonical_name: kamzikstan
  
- !Country
  display_name: Cosmoslavia
  canonical_name: cosmoslavia
"""

city_data_yaml = """
- !City
  canonical_name: ashopolis
  country_cname: ashjikistan
  display_name: Ashopolis
  
- !City
  canonical_name: kamingrad
  country_cname: kamzikstan
  display_name: Kamingrad
  
- !City
  canonical_name: cosmotopia
  country_cname: cosmoslavia
  display_name: Cosmotopia
  
- !City
  canonical_name: ashdurabad
  country_cname: ashjikistan
  display_name: Ashdurabad
"""

city_data_yaml_with_country = """
- !City
  canonical_name: ashopolis
  country: !Country
    canonical_name: ashjikistan
    display_name: Ashjikistan
  country_cname: ashjikistan
  display_name: Ashopolis
  
- !City
  canonical_name: ashdurabad
  # Duplicate country
  country: !Country
    canonical_name: ashjikistan
    display_name: Ashjikistan
  country_cname: ashjikistan
  display_name: Ashdurabad
  
- !City
  canonical_name: kamingrad
  country: !Country
    canonical_name: kamzikstan
    display_name: Kamzikstan
  country_cname: kamzikstan
  display_name: Kamingrad
  
- !City
  canonical_name: cosmotopia
  country: !Country
    canonical_name: cosmoslavia
    display_name: Cosmoslavia
  country_cname: cosmoslavia
  display_name: Cosmotopia
"""


def load_cities_then_countries():
    with Session(engine) as session:
        cities = yaml.load(city_data_yaml, Loader=yaml.FullLoader)
        for city in cities:
            session.add(city)
            session.commit()
            session.refresh(city)

        countries = yaml.load(country_data_yaml, Loader=yaml.FullLoader)
        for country in countries:
            session.add(country)
            session.commit()
            session.refresh(country)

    countries = session.exec(select(Country)).all()
    print(countries)

    cities = session.exec(select(City)).all()
    print(cities)


def load_cities_with_countries_nested():
    with Session(engine) as session:
        cities_with_countries = yaml.load(
            city_data_yaml_with_country, Loader=yaml.FullLoader
        )
        for city in cities_with_countries:
            # Replace the inlined Country with one from the DB, if it exists
            existing_country = session.exec(
                select(Country).where(Country.canonical_name == city.country_cname)
            ).first()

            if existing_country:
                city.country = existing_country

            session.add(city)
            session.commit()
            session.refresh(city)

    countries = session.exec(select(Country)).all()
    print(countries)

    cities = session.exec(select(City)).all()
    print(cities)


if __name__ == "__main__":
    # From YAML (to pre-load your database)
    create_db_and_tables()
    load_cities_then_countries()
    # drop the tables before adding repeated data
    create_db_and_tables()
    load_cities_with_countries_nested()
