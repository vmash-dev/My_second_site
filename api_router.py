from fastapi import APIRouter, status, Query
from schemas import TourCreateSchema, TourSavedSchema, TourPriceImageSchema

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


@api_router.delete("/{tour_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tour(tour_id: str) -> None:
    storage.delete_tour(tour_id)


@api_router.patch("/{tour_id}")
def patch_tour(tour_id: str, new_tour_data: TourPriceImageSchema) -> TourSavedSchema:
    patched_tour = storage.update_tour(tour_id, new_tour_data)

    return patched_tour


@api_router.put("/{tour_id}")
def put_tour(tour_id: str, tour: TourCreateSchema) -> TourSavedSchema:
    put_tour_obj = storage.update_tour(tour_id, tour)

    return put_tour_obj