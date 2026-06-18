from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from abc import ABC, abstractmethod

from schemas import TourCreateSchema, TourSavedSchema, TourPriceImageSchema
from settings import settings

class BaseStorage(ABC):
    @abstractmethod
    def create_tour(self, book: TourCreateSchema) -> TourSavedSchema:
        pass

    @abstractmethod
    def update_tour(self, tour_id: str, new_tour_data: TourPriceImageSchema | TourCreateSchema) -> TourSavedSchema:
        pass

    @abstractmethod
    def get_tour(self, tour_id: str) -> TourSavedSchema:
        pass

    @abstractmethod
    def delete_tour(self, tour_id: str) -> None:
        pass

    @abstractmethod
    def get_tours(self, q: str = "", page: int = 1)-> list[TourSavedSchema]:
        pass


class MongoDBStorage(BaseStorage):
    def __init__(self):
        client = MongoClient(settings.MONGO_URI, server_api=ServerApi('1'))
        db = client[settings.MONGO_DB]
        self.collection = db[settings.MONGO_COLLECTION]

    def create_tour(self, tour: TourCreateSchema) -> TourSavedSchema:
        tour_dict = tour.model_dump()
        tour_dict['created_at'] = datetime.now()
        saved_tour_in_db = self.collection.insert_one(tour_dict)

        saved_tour = self.get_tour(saved_tour_in_db.inserted_id)

        return saved_tour

    def update_tour(self, tour_id: str, new_tour_data: TourPriceImageSchema | TourCreateSchema) -> TourSavedSchema:
        payload = {'$set': new_tour_data.model_dump()}
        result = self.collection.update_one(self._get_object_id_query(tour_id), payload)
        if not result.raw_result['n']:
            raise HTTPException(
                detail=f'Tour with id={tour_id} not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

        saved_tour = self.get_tour(tour_id)
        return saved_tour

    def _get_object_id_query(self, tour_id: str) -> dict[str, ObjectId]:
        try:
            query = {"_id": ObjectId(tour_id)}
            return query
        except InvalidId:
            raise HTTPException(
                detail=f"Invalid tour id {tour_id}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def get_tour(self, tour_id: str) -> TourSavedSchema:
        tour = self.collection.find_one(self._get_object_id_query(tour_id))

        if not tour:
            raise HTTPException(
                detail=f'Tour with id={tour_id} not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

        tour = self.transform_tour(tour)

        return tour

    def delete_tour(self, tour_id: str) -> None:
        self.get_tour(tour_id)
        self.collection.delete_one(self._get_object_id_query(tour_id))

    def transform_tour(self, tour: dict) -> TourSavedSchema:
        tour = TourSavedSchema(
            tour_name=tour['tour_name'],
            hotel_view=tour['hotel_view'],
            price=tour['price'],
            tour_description=tour['tour_description'],
            id=str(tour['_id']),
            created_at=tour['created_at'],
        )
        return tour


    def get_tours(self, q: str = "", page: int = 1)-> list[TourSavedSchema]:
        query = {}
        if q:
            query_words = q.split()
            print(query_words)

            # target_list = []
            # for word in query_words:
            #     if len(word) > 1:
            #         target_list.append(word.lower())
            query_words = [word.lower() for word in query_words if len(word) > 1]

            if query_words:
                query_words_dicts = [{'title': {"$regex": word, "$options": 'i'}} for word in query_words]
                query = {
                    "$and": query_words_dicts
                }
        skip = (page - 1) *  settings.PAGE_SIZE
        tours = self.collection.find(query).limit(settings.PAGE_SIZE).skip(skip)
        saved_tours = []
        for tour in tours:
            saved_tours.append(self.transform_tour(tour))

        return saved_tours



storage: BaseStorage = MongoDBStorage()
