from pathlib import Path
import tempfile
from datamodel_code_generator.__main__ import main
from importlib import machinery
import sys
from polyfactory.factories.pydantic_factory import ModelFactory
import json
import subprocess
from db import Session
from models import RenderedModel
from uuid import uuid4, UUID
from sqlalchemy import select

def create_model_from_url(url) -> str:
    temp_module_path = tempfile.TemporaryDirectory()
    output_path = Path(temp_module_path.name) / "model.py"
    
    main(["--url", url, "--input-file-type", "openapi", "--output", str(output_path)])
    with open(str(output_path)) as f:
        model_str = f.read()

    return store_model(model_str)


def get_random_instance(model_id: UUID) -> str:
    # setup
    temp_module_path = tempfile.TemporaryDirectory()
    output_path = Path(temp_module_path.name) / "model.py"
    
    class CustomFinder(machinery.PathFinder):
        _path = [temp_module_path.name]

        @classmethod
        def find_spec(cls, fullname, path=None, target=None):
            return super().find_spec(fullname, cls._path, target)

    sys.meta_path.append(CustomFinder)

    # get the model
    model = retrieve_model(model_id)
    with open(str(output_path), "w") as f:
        f.write(model)
    
    # import, create random inst and return json str
    from model import Pet
    return ModelFactory.create_factory(Pet).build().model_dump_json(indent=2)


def store_model(model: str) -> str:
    with Session() as session:
        rendered_model = RenderedModel(uid=uuid4(), body=model)
        session.add(rendered_model)
        session.commit()
        ret_id = str(rendered_model.id)
        
    return ret_id

def retrieve_model(model_id: UUID) -> str:
    with Session() as session:
        stmt = select(RenderedModel).where(RenderedModel.id == model_id)
        return session.execute(stmt).scalar_one().body


    


#     # input_url = "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.1/webhook-example.yaml"
    


        
#     from model import Pet
#     model = ModelFactory.create_factory(model=Pet).build()
#     return model.model_dump_json(indent=2)