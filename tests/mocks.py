from pathlib import Path
from datetime import datetime

from sqlmodel import create_engine, Field, Relationship, Session, select
from pydantic import EmailStr

from sqlmodel_yaml import YAMLModel


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
]

country_data_yaml = """- !Country
  display_name: Ashjikistan
  canonical_name: ashjikistan
- !Country
  display_name: Kamzikstan
  canonical_name: kamzikstan
- !Country
  display_name: Cosmoslavia
  canonical_name: cosmoslavia"""

city_data_yaml = """- !City
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
  display_name: Cosmotopia"""


create_user_data = {
    "name": "Cameron Ratchford",
    "username": "cam",
    "email": "camratchford@example.com",
    "password": "Test123",
}

valid_user_data = [
    {
        "name": "Cameron Ratchford",
        "email": "camratchford@example.com",
        "username": "cam",
        "id": 1,
    }
]

fixtures_path = Path(__file__).parent / "fixtures"

countries_path = fixtures_path / "countries.yaml"
countries_str = str(countries_path)

static_file_list = [
    "sorted_imports/0_countries.yml",
    "sorted_imports/1_users.yml",
    "users/root_users.yml",
    "users/standard_users.yml",
    "users.yml",
    "countries.yaml",
]

static_file_list_jumbled = [
    "sorted_imports/0_countries.yml",
    "users/root_users.yml",
    "sorted_imports/1_users.yml",
    "users/standard_users.yml",
    "users.yml",
    "countries.yaml",
]

valid_merged_city_yaml = """- !City
  canonical_name: ashopolis
  country: !Country
    canonical_name: ashjikistan
    display_name: Ashjikistan
  country_cname: ashjikistan
  display_name: Ashopolis
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

db_path = fixtures_path / "database.db"
sqlite_file_name = db_path.relative_to(Path().cwd()).as_posix()
sqlite_url = f"sqlite:///{sqlite_file_name}?"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

static_file_list_paths = [fixtures_path / p for p in static_file_list]
static_file_list_paths_jumbled = [fixtures_path / p for p in static_file_list_jumbled]
static_file_list_strings = [str(p) for p in static_file_list_paths]

users_templates_path = fixtures_path / "users/user_with_country_lookup.yml"


class Country(YAMLModel, table=True):
    canonical_name: str = Field(alias="cname", default=None, primary_key=True)
    display_name: str = Field(alias="name")
    cities: list["City"] = Relationship(back_populates="country")
    users: list["User"] = Relationship(back_populates="country")


class City(YAMLModel, table=True):
    canonical_name: str = Field(alias="cname", primary_key=True)
    display_name: str = Field(alias="name")
    country_cname: str = Field(default=None, foreign_key="country.canonical_name")
    country: Country = Relationship(back_populates="cities")


class UserBase(YAMLModel):
    name: str = Field()
    email: EmailStr = Field()
    username: str = Field(unique=True)
    date_created: datetime = Field(default_factory=datetime.now)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    country_cname: str | None = Field(
        nullable=True, default=None, foreign_key="country.canonical_name"
    )
    country: Country = Relationship(back_populates="users")
    hashed_password: str = Field()


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int


class UserUpdate(YAMLModel):
    name: str | None = None
    password: str = None


def create_country(name: str, cname: str):
    with Session(engine) as session:
        country = Country(display_name=name, canonical_name=cname)
        session.add(country)
        session.commit()
        session.refresh(country)
        return country


def get_country_by_name(name: str):
    with Session(engine) as session:
        return session.exec(select(Country).where(Country.display_name == name)).first()


def create_db_and_tables():
    YAMLModel.metadata.drop_all(engine)
    YAMLModel.metadata.create_all(engine)
