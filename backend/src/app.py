from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.integrations import router as integrations_router

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(integrations_router, prefix="/integrations")


@app.get("/")
def read_root():
    return {"Ping": "Pong"}
