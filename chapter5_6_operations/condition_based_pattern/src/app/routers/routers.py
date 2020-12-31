from fastapi import APIRouter
import uuid
from src.app.api import api
from src.ml.prediction import Data
from logging import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health():
    return api.health()


@router.get("/health/sync")
def health_sync():
    return api.health_sync()


@router.get("/health/async")
async def health_async():
    result = await api.health_async()
    return result


@router.get("/metadata")
def metadata():
    return api.metadata()


@router.get("/predict/test")
async def predict_test(id: str = str(uuid.uuid4())[:6]):
    return await api.predict_test(id=id)


@router.post("/predict")
async def predict(data: Data, id: str = str(uuid.uuid4())[:6]):
    return await api.predict(data=data, id=id)
