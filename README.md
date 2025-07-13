
# YAMLModel

> [SQLModel](https://sqlmodel.tiangolo.com/) models with dynamically generated PyYaml Constructors and Representers

- Declare your `YAMLModel` subclasses in the same way as you would `SQLModel`
  - Calling `yaml.load` produces initialized instances of your declared models
    - You only need to commit the changes in a database session.
    - See `extras/examples/load_example.py`
  - Calling `yaml.dump` on a model's instance exports the model data into YAML
    - Assuming your database query contains the generated fields, 
      the resulting YAML will contain relationships as well.
    - See `extras/examples/dump_example.py`


