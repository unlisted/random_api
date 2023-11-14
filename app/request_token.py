from google.cloud import datastore
from google.cloud.datastore import Entity
from enum import Enum
from app.exceptions import TokenNotFound

class RequestType(str, Enum):
    REGISTRATION = "registration"
    GENERATION = "generation"

datastore_client = datastore.Client()

KIND = "RequestToken"


def build_entity(token_id: int, token_values: dict) -> Entity:
    key = datastore_client.key(KIND, token_id)
    token = datastore_client.entity(key=key)
    token.update(token_values)
    return token


def update_token(token_id: int, token_values: dict | Entity, request_type: RequestType, count: int = 1) -> dict:
    token = build_entity(token_id, token_values)
    match request_type:
        case RequestType.REGISTRATION:
            token["registrations_used"] = token["registrations_used"] + count
        case RequestType.GENERATION:
            token["generations_used"] = token["generations_used"] + count
    datastore_client.put(token)
    return {k:v for k,v in token.items()}


def generations_count(token_id: int) -> int:
    token = retrieve_token(token_id)
    return token["generations_count"]


def registrations_count(token_id: int) -> int:
    token = retrieve_token(token_id)
    return token["registrations_count"]


def retrieve_token(token_id: int) -> dict:
    key = datastore_client.key(KIND, token_id)
    token = datastore_client.get(key)
    if token is None:
        raise TokenNotFound(token_id)
    return {k:v for k,v in token.items()}


def valid_request(request_type: RequestType, token: dict) -> bool:
    match request_type:
        case RequestType.REGISTRATION:
            return token["registrations_used"] < token["registrations_total"]
        case RequestType.GENERATION:
            return token["generations_used"] < token["generations_total"]