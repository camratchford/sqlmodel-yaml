from typing_extensions import Unpack

import yaml
from pydantic import ConfigDict
from sqlmodel import SQLModel


class YAMLModel(SQLModel, table=False):
    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]):
        yaml.add_constructor(f"!{cls.__name__}", cls.yaml_constructor())
        yaml.add_representer(cls, cls.yaml_representer())
        super().__init_subclass__(**kwargs)

    @classmethod
    def yaml_representer(cls):
        def wrapper(dumper: yaml.Dumper, instance: "YAMLModel"):
            # Dump only declared fields first
            data = instance.model_dump(mode="json")

            # Include related models stored as SQLModel instances (not fields)
            for attr, value in instance.__dict__.items():
                if attr in data:
                    continue  # already serialized

                # Single related model
                if isinstance(value, YAMLModel):
                    data[attr] = value

                # List of related models (e.g., Country.cities)
                elif isinstance(value, list) and value and all(isinstance(v, YAMLModel) for v in value):
                    data[attr] = value

            return dumper.represent_mapping(
                f"!{cls.__name__}",
                data,
                flow_style=False
            )

        return wrapper

    @classmethod
    def yaml_constructor(cls):
        def wrapper(loader: yaml.loader, node: yaml.nodes.Node):
            dict_data = loader.construct_mapping(node)
            if dict_data:
                try:
                    instance = cls(**dict_data)
                    return instance
                except Exception as e:
                    raise e

        return wrapper
