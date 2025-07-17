from pathlib import Path

from sqlmodel import Session
from sqlmodel_yaml.yaml_loader import YAMLLoader, path_levels_sort_function

from mocks import (
    fixtures_path,
    engine,
    countries_path,
    countries_str,
    create_db_and_tables,
    static_file_list_paths,
    static_file_list_paths_jumbled,
    get_country_by_name,
    users_templates_path,
    create_country
)


def test_yaml_single_file_path():
    importer = YAMLLoader(countries_path)
    assert len(importer.list_paths()) == 1
    assert all(isinstance(p, Path) for p in importer.list_paths())


def test_yaml_single_file_str():
    importer = YAMLLoader(countries_str)
    assert len(importer.list_paths()) == 1
    assert all(isinstance(p, Path) for p in importer.list_paths())


def test_yaml_dir_path():
    importer = YAMLLoader(fixtures_path)
    file_list = importer.list_paths()
    assert len(file_list) == 2


def test_yaml_dir_str():
    importer = YAMLLoader(str(fixtures_path.absolute()))
    file_list = importer.list_paths()
    assert len(file_list) == 2


def test_yaml_dir_recurse():
    importer = YAMLLoader(str(fixtures_path.absolute()), recurse=True)
    file_list = importer.list_paths()
    print([str(i) for i in file_list])
    assert len(file_list) == 6


def test_yaml_path_list():
    importer = YAMLLoader(static_file_list_paths)
    file_list = importer.list_paths()
    assert len(file_list) == 6
    assert all([p in static_file_list_paths for p in file_list])
    assert file_list != static_file_list_paths


def test_yaml_custom_path_levels_sort():
    importer = YAMLLoader(
        static_file_list_paths_jumbled, importer_sort_function=path_levels_sort_function
    )
    file_list = importer.list_paths()
    assert file_list != static_file_list_paths_jumbled


def test_yaml_loader_load():
    create_db_and_tables()
    importer = YAMLLoader(countries_path, engine)
    with Session(engine) as session:
        countries = importer.load_all(session)
    assert len(countries) == 3


def test_jinja():
    create_db_and_tables()
    jinja_vars = {"get_country_by_name": get_country_by_name}
    importer = YAMLLoader()
    create_country("Rootzikstan", "rootzikstan")
    with Session(engine) as session:

        importer.load_template_file(session, users_templates_path, jinja_vars)


if __name__ == "__main__":
    test_yaml_single_file_path()
    test_yaml_single_file_str()
    test_yaml_dir_path()
    test_yaml_dir_str()
    test_yaml_dir_recurse()
    test_yaml_path_list()
    test_yaml_custom_path_levels_sort()
