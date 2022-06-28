import os
from typing import Type

import aiohttp
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from application.database import async_engine, Base, session
from sqlalchemy import select, insert
from application.models import Message, User
from application.settings import root, config

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(root, "static")), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()


@app.route("/admin", methods=["GET", "POST"])
async def admin_panel(request: Request) -> templates.TemplateResponse:
    if request.method == "GET":
        output = await session.execute(select(User))
        users = [user for raw in output.fetchall() for user in raw]
        return templates.TemplateResponse("admin.html", {"request": request, "users": users})
    elif request.method == "POST":
        b_data = await request.body()
        data = json.loads(b_data.decode("utf-8"))
        await session.execute(insert(User).values(data))
        output = await session.execute(select(User))
        users = [user for raw in output.fetchall() for user in raw]
        return templates.TemplateResponse("admin.html", {"request": request, "users": users})


def dict_to_list(data_dict: dict, data_list: list, model: Type[Message], parent=None) -> list:
    for key in data_dict.keys():
        message = model(clue_word=str(key), parent=parent)
        data_list.append(message)
        if type(data_dict[key]) is dict:
            dict_to_list(data_dict[key], data_list, model, message)
        else:
            data_list.append(model(clue_word=str(data_dict[key]), parent=message))
    return data_list


@app.route("/bot_config", methods=["GET", "POST"])
async def bot_configuration(request: Request) -> templates.TemplateResponse:
    if request.method == "GET":
        output = await session.execute(select(Message))
        messages = [message for raw in output.fetchall() for message in raw]
        print(messages)
        return templates.TemplateResponse("admin.html", {"request": request, "messages": messages})
    elif request.method == "POST":
        b_data = await request.body()
        data = json.loads(b_data.decode("utf-8"))
        list_of_messages = dict_to_list(data_dict=data, data_list=[], model=Message)
        session.add_all(list_of_messages)
        await session.commit()
        return templates.TemplateResponse("admin.html", {"request": request})


@app.post("/recived_messages")
async def print_recived_messages(request: Request) -> tuple:
    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))
    try:
        message = data["messageData"]["textMessageData"]["textMessage"]
        phone_number = data["senderData"]["chatId"].replace("@c.us", "")
    except KeyError:
        return "Send by bot successfully", 200
    await session.execute(insert(User).values({"phone_number": phone_number}))
    message_data = {"message": message, "chatId": phone_number + "@c.us"}
    url = f"https://api.green-api.com/waInstance{config['IdInstance']}/SendMessage/{config['apiTokenInstance']}"
    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(url=url, data=json.dumps(message_data)) as response:
            content = await response.text()
    return content, response.status
