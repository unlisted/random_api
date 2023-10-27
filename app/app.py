from flask import Flask, Response, request
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from importer import create_model_from_url, get_random_instance

app = Flask(__name__)


@app.get("/")
def hello():
    return Response(response="hi", status=200)


@app.post("/models/")
def create_model():
    request_json = request.get_json()
    url = request_json["url"]
    rand_instance_json = create_model_from_url(url)
    return Response(status=200, response=rand_instance_json)


@app.get("/models/<uuid:model_id>")
def get_model(model_id):
    return get_random_instance(model_id)