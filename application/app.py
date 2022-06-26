import os
import aiohttp
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from application.database import engine, Base, session
from sqlalchemy import select
from application.models import Message, User
from application.settings import root, config


app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(root, "static")), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def shutdown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get("/admin")
async def return_messages(request: Request) -> templates.TemplateResponse:
    output = await session.execute(select(User))
    users = [user for raw in output.fetchall() for user in raw]
    return templates.TemplateResponse("admin.html", {"request": request, "users": users})


@app.route("/admin")
async def admin_panel():
    pass


@app.post("/recived_messages")
async def print_recived_messages(request: Request) -> tuple:
    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))
    print(data)
    data = {"message": data["messageData"]["textMessageData"]["textMessage"], "chatId": data["senderData"]["chatId"]}
    url = f"https://api.green-api.com/waInstance{config['IdInstance']}/SendMessage/{config['apiTokenInstance']}"
    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(url=url, data=json.dumps(data)) as response:
            content = await response.text()
    return content, response.status
