from pydantic import BaseModel, Field
from datetime import datetime

class TourCreateSchema(BaseModel):
    tour_name: str = Field(examples=['Атлантида'])
    hotel_view: str = Field(examples=['Водичка'])
    price: float = Field(ge=10000)
    tour_description: str = Field(examples=['Буль буль'])

class TourSavedSchema(TourCreateSchema):
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
