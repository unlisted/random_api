from pathlib import Path
import tempfile
from datamodel_code_generator.__main__ import main
from importlib import machinery
import sys
from polyfactory.factories.pydantic_factory import ModelFactory
import json
import subprocess
from db import retrieve_model, store_model
from uuid import UUID
from inspect import getmembers
import inspect
import json
from pydantic import create_model

def create_model_from_url(url) -> str:
    temp_module_path = tempfile.TemporaryDirectory()
    output_path = Path(temp_module_path.name) / "model.py"
    
    main(["--url", url, "--input-file-type", "openapi", "--output", str(output_path), "--output-model-type", "pydantic_v2.BaseModel"])
    with open(str(output_path)) as f:
        model_str = f.read()

    return store_model(model_str)

from typing import Any, Generic, TypeVar
from pydantic import BaseModel
T = TypeVar("T", bound=BaseModel)

def get_random_instance(model_id: UUID, inst: str = None) -> str:
    # created this class in order to set allow_none_optional False on all dynmically created instances
    class MyModelFactory(Generic[T], ModelFactory[T]):
        __is_base_factory__ = True
        __allow_none_optionals__ = False
        def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
            super().__init_subclass__(*args, **kwargs)

    temp_module_name = "temp_model"
    temp_module_path = tempfile.TemporaryDirectory()
    output_path = Path(temp_module_path.name) / f"{temp_module_name}.py" 
    
    # create a customer finder so that import knows where to look for module
    _add_finder(temp_module_path.name)

    # get the model and write out to file system as module
    model = retrieve_model(model_id)
    with open(str(output_path), "w") as f:
        f.write(model)
    
    # import the module
    module = __import__(temp_module_name)

    # get all the classes defined in this module
    members = (getmembers(module, inspect.isclass))
    if inst:
        clzs = [x[1] for x in members if x[1].__module__ == temp_module_name and x[0].lower() == inst.lower()]
    else:
        clzs = [x[1] for x in members if x[1].__module__ == temp_module_name]

    if len(clzs) == 0:
        return ""
    
    # create the Pydantic model that returns  the results, easier to serialize this way
    kwargs = {x.__name__:(x, ...) for x in clzs}
    ResultsModel = create_model("ResultsModel", **kwargs)


    # use polyfactory to generate random data for imported models
    rand_data_instences = {}
    for clz in clzs:
        factory = MyModelFactory.create_factory(clz)
        # factory.__allow_none_optionals__ = False
        rand_data_instences[clz.__name__] = factory.build()

    # return serialized results
    return  ResultsModel(**rand_data_instences).model_dump_json(indent=2)


def _add_finder(path: str) -> None:
    class CustomFinder(machinery.PathFinder):
        _path = [path]

        @classmethod
        def find_spec(cls, fullname, path=None, target=None):
            return super().find_spec(fullname, cls._path, target)

    sys.meta_path.append(CustomFinder)