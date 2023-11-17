from pathlib import Path
import tempfile
from datamodel_code_generator.__main__ import main
from importlib import machinery
import sys
from polyfactory.factories.pydantic_factory import ModelFactory
from uuid import UUID, uuid4
from inspect import getmembers
import inspect
import json
from pydantic import create_model
from typing import Any, Generic, TypeVar
from pydantic import BaseModel
from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
import logging
import sys
from app.config import settings

from app.exceptions import ModelNotFound, RegistrationFailed
from app.persistor import BasePersistor

logger = logging.getLogger(__name__)

datastore_client = datastore.Client()

KIND = "ModelModule"

T = TypeVar("T", bound=BaseModel)
TEMP_MODULE_PATH = tempfile.TemporaryDirectory()

def patterned_field_fixup(model_str: str) -> str:
    # This is a very specific fix for Canopy specs that use patterned fields.
    return model_str.replace("pattern='^(?!can_).*$',", "")


def create_model_from_url(url, persistor: BasePersistor) -> str:
    spec_id = uuid4().hex
    output_path = Path(TEMP_MODULE_PATH.name) / f"{spec_id}.py"
    
    main(["--url", url, "--input-file-type", "openapi", "--output", str(output_path), "--output-model-type", "pydantic_v2.BaseModel", "--use-annotated"])
    if not output_path.exists():
        raise RegistrationFailed(spec_id)
    model_str = output_path.read_text()

    fixed_model_str = patterned_field_fixup(model_str)
    if fixed_model_str != model_str:
        output_path.write_text(fixed_model_str)
    
    persistor.write(spec_id, fixed_model_str)
    return spec_id


def get_model_list(spec_id: str) -> list[str]:
    _add_finder(TEMP_MODULE_PATH.name)
    try:
        #TODO: just check for existence here
        module = __import__(spec_id)
    except ModuleNotFoundError:
        logger.info(f"{spec_id} not found in local filesystem, checking datastore.")

        # get the model from datastore
        query = datastore_client.query(kind=KIND)
        query.add_filter(filter=PropertyFilter("model_id", "=", spec_id))
        results = query.fetch()
        try:
            model = next(results)
            model_str = model["model"]
        except StopIteration:
            logger.exception(f"{spec_id} not found in datastore.")
            raise ModelNotFound(model_id=spec_id)
        else:
            # write the model to fs 
            output_path = Path(TEMP_MODULE_PATH.name) / f"{spec_id}.py" 
            with open(str(output_path), "w") as f:
                f.write(model_str)
            
            module = __import__(spec_id)
    
    # get all the classes defined in this module
    members = (getmembers(module, inspect.isclass))
    return [x[0] for x in members if x[1].__module__ == spec_id]


def get_random_instance(spec_id: str, reader: BasePersistor, models: list[str] = []) -> dict:
    # to allow_none_optional False on all dynmically created instances
    class MyModelFactory(Generic[T], ModelFactory[T]):
        __is_base_factory__ = True
        __allow_none_optionals__ = False
        def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
            super().__init_subclass__(*args, **kwargs)
    
    # add customer importer finder that searches the temp dir for modules
    _add_finder(TEMP_MODULE_PATH.name)
    try:
        #TODO: just check for existence here
        # import from local path if exists
        module = __import__(spec_id)
    except ModuleNotFoundError:
        logger.info(f"{spec_id} not found in local filesystem, checking datastore.")
        model_str = reader.read(spec_id)
        
        # write the model to fs
        output_path = Path(TEMP_MODULE_PATH.name) / f"{spec_id}.py" 
        output_path.write_text(model_str)

        # then import it
        module = __import__(spec_id)


    # get all the classes defined in this module
    members = (getmembers(module, inspect.isclass))
    if models:
        target_models = [x.lower() for x in models]
        clzs = [x[1] for x in members if x[1].__module__ == spec_id and x[0].lower() in target_models]
    else:
        clzs = [x[1] for x in members if x[1].__module__ == spec_id]

    if len(clzs) == 0:
        return {}
    
    # create the Pydantic model that returns  the results, easier to serialize this way
    field_definitions = {x.__name__:(x, ...) for x in clzs}
    ResultsModel = create_model("ResultsModel", **field_definitions) # type: ignore

    # use polyfactory to generate random data for imported models
    rand_data_instences = {}
    for clz in clzs:
        factory = MyModelFactory.create_factory(clz)
        # factory.__allow_none_optionals__ = False
        rand_data_instences[clz.__name__] = factory.build()

    if settings.remove_module:
        sys.modules.pop(spec_id, None)

    # return serialized results
    return  ResultsModel(**rand_data_instences).model_dump()


def _add_finder(path: str) -> None:
    class CustomFinder(machinery.PathFinder):
        _path = [path]

        @classmethod
        def find_spec(cls, fullname, path=None, target=None):
            return super().find_spec(fullname, cls._path, target)

    sys.meta_path.append(CustomFinder)