from fastapi import FastAPI
from api_router import api_router


app = FastAPI(
    title='Турагенство "Перелетный страус"'
)

app.include_router(api_router, tags=['TOURS'])
