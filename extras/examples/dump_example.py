from pathlib import Path
import yaml
from sqlmodel import create_engine, Field, Relationship, Session, select
from sqlalchemy.orm import selectinload
from sqlmodel_yaml import YAMLModel

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


country_data_dict = [
    {"display_name": "Ashjikistan", "canonical_name": "ashjikistan"},
    {"display_name": "Kamzikstan", "canonical_name": "kamzikstan"},
    {"display_name": "Cosmoslavia", "canonical_name": "cosmoslavia"},
]

city_data_dict = [
    {
        "display_name": "Ashopolis",
        "canonical_name": "ashopolis",
        "country_cname": "ashjikistan",
    },
    {
        "display_name": "Kamingrad",
        "canonical_name": "kamingrad",
        "country_cname": "kamzikstan",
    },
    {
        "display_name": "Cosmotopia",
        "canonical_name": "cosmotopia",
        "country_cname": "cosmoslavia",
    },
    {
        "display_name": "Ashdurabad",
        "canonical_name": "ashdurabad",
        "country_cname": "ashjikistan",
    },
]

create_db_and_tables()

if __name__ == "__main__":
    # From a list of dicts (like when used in a fastapi route)
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
        # Necessary to retrieve the `City.country` one-one relationship's backref,
        # can be used to initialize both Cities and Countries at the same time
        cities = session.exec(select(City).options(selectinload(City.country))).all()
        yaml_from_cities = yaml.dump(cities)
        print(yaml_from_cities)

        # We don't want to store the `Country.cities` one-many relationship's backref as YAML, it's a lot of data.
        # Plus, it won't do you any good
        countries = session.exec(select(Country)).all()
        yaml_from_countries = yaml.dump(countries)
        print(yaml_from_countries)
