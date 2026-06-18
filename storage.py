from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from schemas import TourCreateSchema, TourSavedSchema
from settings import settings


class MongoDBStorage:
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

    def get_tour(self, tour_id: str) -> TourSavedSchema:
        try:
            query = {"_id": ObjectId(tour_id)}
        except InvalidId:
            raise HTTPException(
                detail=f"Invalid book id {tour_id}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        tour = self.collection.find_one(query)
        if not tour:
            raise HTTPException(
                detail=f'Tour with id={tour_id} not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

        tour = self.transform_tour(tour)

        return tour

    def transform_tour(self, tour: dict) -> TourSavedSchema:
        tour = TourSavedSchema(
            title=tour['title'],
            image=tour['image'],
            price=tour['price'],
            author=tour['author'],
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



storage = MongoDBStorage()