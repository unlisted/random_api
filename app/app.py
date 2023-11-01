from flask import Flask, request, Response
from uuid import uuid4
from importer import create_model_from_url, get_random_instance, get_model_list
import debugpy
from exceptions import ModelNotFound, RegistrationFailed
from config import settings 
from request_token import retrieve_token, RequestType, valid_request, update_token

if settings.debug:
    debugpy.listen(("0.0.0.0", 5678))

app = Flask(__name__)


@app.post("/specs/")
def create_model():
    token_id = request.headers.get("X-Request-Token", type=int)
    if not token_id:
        return Response("request token not found.", 403)
    token = retrieve_token(token_id)
    if not valid_request(RequestType.REGISTRATION, token):
        return Response("invalid token", 403)
    
    request_json = request.get_json()
    url = request_json["url"]
    try:
        spec_id = create_model_from_url(url)
    except RegistrationFailed:
        return Response(200, "registration failed, try another url.")
    
    updated_token = update_token(token_id, token, RequestType.REGISTRATION, 1)
    return {"spec_id": spec_id, "request_token": updated_token}


@app.get("/specs/<string:spec_id>/")
def get_model(spec_id):
    token_id = request.headers.get("X-Request-Token", type=int)
    if not token_id:
        return Response("request token not found.", 403)

    token = retrieve_token(int(token_id))
    if not valid_request(RequestType.GENERATION, token):
        return Response("invalid token", 403)
    
    models = request.args.getlist("models")
    try:
        rand_inst = get_random_instance(spec_id, models=models)
    except ModelNotFound as ex:
        return Response(f"{ex.model_id} not found", 404)
    
    updated_token = update_token(token_id, token, RequestType.GENERATION, 1)
    return {"data": rand_inst, "request_token": updated_token}


@app.get("/specs/<string:spec_id>/models/")
def get_models(spec_id):
    try:
        models = get_model_list(spec_id)
    except ModelNotFound as ex:
        return Response(f"{ex.model_id} not found", 404)
    return {"models": models}


app.make_response
@app.get("/request_tokens/<int:token_id>/")
def get_request_token(token_id):
    return retrieve_token(token_id)