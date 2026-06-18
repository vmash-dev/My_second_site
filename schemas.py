from pydantic import BaseModel, Field
from datetime import datetime


class TourPriceImageSchema(BaseModel):
    price: float = Field(ge=10000)
    hotel_view: str = Field(examples=['Водичка'])

class TourCreateSchema(TourPriceImageSchema):
    tour_name: str = Field(examples=['Атлантида'])
    tour_description: str = Field(examples=['Буль буль'])


class TourSavedSchema(TourCreateSchema):
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
