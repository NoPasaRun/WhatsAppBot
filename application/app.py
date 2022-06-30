import os
from typing import Type
import starlette.status as status
import aiohttp
from fastapi import FastAPI, Request, APIRouter, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response
import json
from application.database import async_engine, Base, session
from sqlalchemy import select, insert, update, delete, func
from application.models import Message, User, Ltree
from application.settings import root, config

app = FastAPI()
router = APIRouter()

app.mount("/static", StaticFiles(directory=os.path.join(root, "static")), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()


@router.route("/admin", methods=["GET", "POST"])
async def admin_panel(request: Request) -> templates.TemplateResponse:
    users = []

    if request.method == "GET":

        output = await session.execute(select(User))
        users = [user for raw in output.fetchall() for user in raw]

    elif request.method == "POST":

        b_data = await request.body()
        data = json.loads(b_data.decode("utf-8"))

        await session.execute(insert(User).values(data))
        output = await session.execute(select(User))

        users = [user for raw in output.fetchall() for user in raw]

    return templates.TemplateResponse(
        "admin.html", {
            "request": request,
            "users": users
        }
    )


def list_to_data(data_list: list, data: list, dot_count: int = 0, path: str = "") -> list:
    for message in filter(lambda mes: str(mes.path).count(".") == dot_count and path in str(mes.path), data_list):
        data.append(
            {
                "id": message.id,
                "user_phrase": message.user_phrase,
                "path_id": str(message.path),
                "children": [],
                "bot_reply": message.bot_reply
            })

        list_to_data(data_list, data[-1]["children"], dot_count + 1, str(message.path))

    return data


@router.route("/bot_config", methods=["GET"])
async def bot_configuration(request: Request) -> templates.TemplateResponse:

    output = await session.execute(select(Message))

    messages = [message for raw in output.fetchall() for message in raw]
    messages = list_to_data(messages, [])
    return templates.TemplateResponse(
        "messages.html",
        {
            "request": request,
            "message_data": json.dumps(messages)
        }
    )


@router.post("/create_message")
async def create_message(request: Request):

    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))

    if data.get("path_id"):
        parent = Message()
        parent.path = Ltree(data["path_id"])
    else:
        parent = None

    message = Message(parent=parent)
    session.add(message)

    await session.commit()

    return RedirectResponse(url="/bot_config", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/update_message")
async def update_message(id: int = Form(), user_phrase: str = Form(), bot_reply: str = Form()):

    if all([id, user_phrase, bot_reply]):
        await session.execute(
            update(Message).where(Message.id == id).values(
                {
                    "user_phrase": user_phrase,
                    "bot_reply": bot_reply
                }
            )
        )

        return RedirectResponse(url="/bot_config", status_code=status.HTTP_303_SEE_OTHER)
    return Response("Frontend form was changed", status_code=400)


@router.post("/delete_message")
async def delete_message(request: Request):

    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))

    message = Message()
    message.path = Ltree(data.get("path_id"))

    output = await session.execute(select(Message).filter(Message.path.descendant_of(message.path)))
    message_ids = [message.id for row in output.fetchall() for message in row]
    await session.execute(delete(Message).where(Message.id.in_(message_ids)))
    await session.commit()

    return RedirectResponse(url="/bot_config", status_code=status.HTTP_303_SEE_OTHER)


async def get_message_from_bd(text):
    output = await session.execute(select(Message).where(Message.user_phrase == text))
    result = output.fetchone()
    if result:
        result, *_ = result
        return result.bot_reply
    output = await session.execute(select(Message).filter(func.nlevel(Message.path) == 1))
    texts = '\n'.join([text.bot_reply for row in output.fetchall() for text in row])
    output_text = f"Приветствую вас! Вы можете спросить у бота:\n{texts}"
    return output_text


@router.post("/recived_messages")
async def get_recived_messages(request: Request) -> tuple:
    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))

    try:

        message = data["messageData"]["textMessageData"]["textMessage"]
        phone_number = data["senderData"]["chatId"].replace("@c.us", "")

    except KeyError:

        return "Send by bot successfully", 200

    # await session.execute(insert(User).values({"phone_number": phone_number}))

    message = await get_message_from_bd(message)

    message_data = {"message": message, "chatId": phone_number + "@c.us"}

    url = f"https://api.green-api.com/waInstance{config['IdInstance']}/SendMessage/{config['apiTokenInstance']}"

    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(url=url, data=json.dumps(message_data)) as response:
            content = await response.text()

    return content, response.status


app.include_router(router, prefix="")
