from fastapi import APIRouter, status, Query
from schemas import TourCreateSchema, TourSavedSchema
from bson import ObjectId

from storage import storage

api_router = APIRouter(
    prefix='/api/tours'
)


@api_router.post("", status_code=status.HTTP_201_CREATED)
def create_tour(tour: TourCreateSchema) -> TourSavedSchema:
    saved_tour = storage.create_tour(tour)

    return saved_tour


@api_router.get("/{tour_id}")
def get_tour(tour_id: str) -> TourSavedSchema:
    saved_tour = storage.get_tour(tour_id)

    return saved_tour

@api_router.get("")
def get_tours(
        page: int = Query(default=1, ge=1),
        q: str = Query(default=''),
) -> list[TourSavedSchema]:
    saved_tours = storage.get_tours(q, page=page)

    return saved_tours
