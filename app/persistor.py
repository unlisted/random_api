from abc import ABC, abstractmethod
from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
import logging

from app.exceptions import ModelNotFound

logger = logging.getLevelName(__name__)

class BasePersistor(ABC):
    @abstractmethod
    def write(self, spec_id: str, model: str) -> None:
        pass

    @abstractmethod
    def read(self, spec_id: str) -> str:
        pass

# GCP Datastore is a decent document store. it's pretty cheap, free in some cases
# https://cloud.google.com/datastore/pricing
class DatastorePersistor(BasePersistor):
    def __init__(self, kind: str = "ModelModule"):
        self.kind = kind
        self.datastore_client = datastore.Client()

    def write(self, spec_id: str, model: str) -> None:
        key = self.datastore_client.key(self.kind, spec_id)
        entity = self.datastore_client.entity(key=key, exclude_from_indexes=(("model",)))
        entity.update({"model": model, "model_id": spec_id})
        self.datastore_client.put(entity)

    def read(self, spec_id: str) -> str:
        query = self.datastore_client.query(kind=self.kind)
        query.add_filter(filter=PropertyFilter("model_id", "=", spec_id))
        results = query.fetch()
        try:
            model = next(results)
            model_str = model["model"]
        except StopIteration:
            logger.exception(f"{spec_id} not found in datastore.")
            raise ModelNotFound(model_id=spec_id)

        return model_str