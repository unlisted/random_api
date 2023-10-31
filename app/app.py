from flask import Flask, Response, request, make_response
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from importer import create_model_from_url, get_random_instance
import debugpy
import os 
from exceptions import ModelNotFoundError
from config import settings 

if settings.debug:
    debugpy.listen(("0.0.0.0", 5678))

app = Flask(__name__)


@app.post("/specs/")
def create_model():
    request_json = request.get_json()
    url = request_json["url"]
    spec_id = create_model_from_url(url)
    return make_response({"spec_id": spec_id})


@app.get("/specs/<string:spec_id>/")
def get_model(spec_id):
    models = request.args.getlist("models")
    try:
        rand_inst = get_random_instance(spec_id, models=models)
    except ModelNotFoundError as ex:
        return Response(response=f"{ex.model_id} not found", status=404)
    return(make_response(rand_inst))
