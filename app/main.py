from flask import Flask, request, Response
from uuid import uuid4
from app.importer import create_model_from_url, get_random_instance, get_model_list
import debugpy
from app.exceptions import ModelNotFound, RegistrationFailed, TokenNotFound
from app.config import settings 
from app.request_token import retrieve_token, RequestType, valid_request, update_token

if settings.debug:
    debugpy.listen(("0.0.0.0", 5678))

app = Flask(__name__)

@app.before_request
def validate_token():
    if not request.endpoint in ["create_model", "get_model"]:
        return None
    token_id = request.headers.get("X-Request-Token", type=int)
    if not token_id:
        return Response("request token not found.", 403)
    token = retrieve_token(token_id)
    if not valid_request(RequestType.REGISTRATION, token):
        return Response("invalid token", 403)
    

@app.after_request
def process_token(response: Response):
    if not request.endpoint in ["create_model", "get_model"]:
        return response

    # only update for successul attempts, maybe??
    if response.status_code < 200 or response.status_code > 299:
        return response
    
    token_id = request.headers.get("X-Request-Token", type=int)
    if not token_id:
        return response
    try:
        token = retrieve_token(token_id)
    except TokenNotFound:
        return response
    
    # which counter do we update?
    match request.method:
        case 'POST':
            update_token(token_id, token, RequestType.REGISTRATION, 1)
        case 'GET':
            update_token(token_id, token, RequestType.GENERATION, 1)
    return response


@app.post("/specs/")
def create_model():    
    request_json = request.get_json()
    url = request_json["url"]
    try:
        spec_id = create_model_from_url(url)
    except RegistrationFailed:
        return Response(200, "registration failed, try another url.")
    
    return {"spec_id": spec_id}


@app.get("/specs/<string:spec_id>/")
def get_model(spec_id):    
    models = request.args.getlist("models")
    try:
        rand_inst = get_random_instance(spec_id, models=models)
    except ModelNotFound as ex:
        return Response(f"{ex.model_id} not found", 404)
    
    return {"data": rand_inst}


@app.get("/specs/<string:spec_id>/models/")
def get_models(spec_id):
    try:
        models = get_model_list(spec_id)
    except ModelNotFound as ex:
        return Response(f"{ex.model_id} not found", 404)
    return {"models": models}


@app.get("/request_tokens/<int:token_id>/")
def get_request_token(token_id):
    return retrieve_token(token_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=False)