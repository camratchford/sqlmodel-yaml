from typing import Callable, Optional, Union
from pathlib import Path

import yaml
from sqlmodel import Session
from sqlmodel_yaml import YAMLModel

YamlSuffixes = frozenset([".yaml", ".yml"])

AnyPathType = Union[str, list[str], Path, list[Path]]
ImporterSortFunctionType = Optional[Callable[[list[Path], bool], list[Path]]]


def is_valid_suffix(suffix: str) -> bool:
    return suffix.lower() in YamlSuffixes


def default_importer_sort_function(
    path_list: list[Path], reverse: bool = False
) -> list[Path]:
    return sorted(path_list, reverse=reverse)


def path_levels_sort_function(
    path_list: list[Path], reverse: bool = False
) -> list[Path]:
    return sorted(path_list, key=lambda p: len(p.resolve().parts), reverse=reverse)


def null_sort_function(path_list: list[Path], _) -> list[Path]:
    return path_list


class YAMLLoader:
    def __init__(
        self,
        path_or_path_list: AnyPathType,
        recurse: bool = False,
        reversed_sort: bool = False,
        importer_sort_function: ImporterSortFunctionType = default_importer_sort_function,
    ):
        self.reversed_sort = reversed_sort
        if importer_sort_function is None:
            importer_sort_function = null_sort_function
        self.importer_sort_function = importer_sort_function

        self.sorted_path_list = self.generate_path_list(path_or_path_list, recurse)

    def generate_path_list(
        self, path_or_path_list: AnyPathType, recurse: bool = False
    ) -> list[Path]:
        if not isinstance(path_or_path_list, list):
            path_list = [Path(path_or_path_list)]
        else:
            path_list = [Path(p).absolute() for p in path_or_path_list]
        files: list[Path] = []

        for path in path_list:
            if not path.exists():
                continue

            if path.is_file() and is_valid_suffix(path.suffix):
                files.append(path)
            elif path.is_dir():
                entries = list(path.iterdir())

                if not recurse and len(path_list) == 1:
                    files = [
                        p for p in entries if p.is_file() and is_valid_suffix(p.suffix)
                    ]
                else:
                    files.extend(self.generate_path_list(entries))

        return self.importer_sort_function(files, self.reversed_sort)

    def list_paths(self):
        return self.sorted_path_list

    def load(self, session: Session) -> list["YAMLModel"]:
        for path in self.sorted_path_list:
            loaded_yaml_objs = yaml.load(path.read_text(), Loader=yaml.FullLoader)

            if not hasattr(loaded_yaml_objs, "__iter__"):
                loaded_yaml_objs = [loaded_yaml_objs]

            if isinstance(loaded_yaml_objs, dict):
                loaded_yaml_objs = list(loaded_yaml_objs.values())

            objects: list[YAMLModel] = []
            for yaml_obj in loaded_yaml_objs:
                session.add(yaml_obj)
                session.commit()
                session.refresh(yaml_obj)
                objects.append(yaml_obj)

            return objects
