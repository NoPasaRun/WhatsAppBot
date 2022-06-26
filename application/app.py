from fastapi import FastAPI, requests, Request
import json
from application.database import engine, Base, session
from sqlalchemy import select
from application.models import Message


app = FastAPI()


@app.on_event("startup")
async def shutdown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get("/")
async def return_messages():
    output = await session.execute(select(Message))
    return output.fetchall()


@app.post("/recived_messages")
async def print_recived_messages(request: Request) -> tuple:
    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))
    return "Successful", 200
