import os
import aiohttp
import secrets
import openpyxl
from fastapi import FastAPI, Request, APIRouter, Form, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response, FileResponse
import json
from application.database import async_engine, Base, async_session
from sqlalchemy import select, insert, update, delete, func
from application.models import Message, User, Ltree
from application.settings import root, config
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()
router = APIRouter()
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, config.get("username"))
    correct_password = secrets.compare_digest(credentials.password, config.get("password"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app.mount("/static", StaticFiles(directory=os.path.join(root, "static")), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()


@router.get("/admin", dependencies=[Depends(get_current_username)])
async def admin_panel(request: Request) -> templates.TemplateResponse:

    session = async_session()

    output = await session.execute(select(User))
    users = [user for raw in output.fetchall() for user in raw]

    await session.close()

    return templates.TemplateResponse(
        "admin.html", {
            "request": request,
            "users": users
        }
    )


def xlsx_file(users, file_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "users"

    sheet["A1"].value = "Username"
    sheet["B1"].value = "Phone number"

    for row in range(len(users)):
        for column, key in enumerate(["username", "phone_number"]):
            cell = sheet.cell(row=row+2, column=column+1)
            cell.value = getattr(users[row], key)
    workbook.save(file_path)


@router.post("/admin", dependencies=[Depends(get_current_username)])
async def get_users_file(request: Request) -> FileResponse:

    session = async_session()

    output = await session.execute(select(User))

    users = [user for raw in output.fetchall() for user in raw]

    file_name = "users.xlsx"
    file_location = os.path.join(root, f'media/{file_name}')

    xlsx_file(users, file_location)

    await session.close()

    return FileResponse(path=file_location, filename=file_name)


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


@router.get("/bot_config", dependencies=[Depends(get_current_username)])
async def bot_configuration(request: Request) -> templates.TemplateResponse:

    session = async_session()

    output = await session.execute(select(Message))

    messages = [message for raw in output.fetchall() for message in raw]
    messages = list_to_data(messages, [])

    await session.close()

    return templates.TemplateResponse(
        "messages.html",
        {
            "request": request,
            "message_data": json.dumps(messages)
        }
    )


@router.post("/create_message", dependencies=[Depends(get_current_username)])
async def create_message(request: Request):

    session = async_session()

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
    await session.close()

    return RedirectResponse(url="/bot_config", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/update_message", dependencies=[Depends(get_current_username)])
async def update_message(id: int = Form(), user_phrase: str = Form(), bot_reply: str = Form()):

    session = async_session()

    if all([id, user_phrase, bot_reply]):
        await session.execute(
            update(Message).where(Message.id == id).values(
                {
                    "user_phrase": user_phrase,
                    "bot_reply": bot_reply
                }
            )
        )
        await session.commit()
        await session.close()

        return RedirectResponse(url="/bot_config", status_code=status.HTTP_303_SEE_OTHER)
    return Response("Frontend form was changed", status_code=400)


@app.delete("/delete_user", dependencies=[Depends(get_current_username)])
async def delete_user(request: Request):

    session = async_session()

    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))

    await session.execute(delete(User).where(User.id == int(data.get("id"))))

    await session.commit()
    await session.close()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/delete_message", dependencies=[Depends(get_current_username)])
async def delete_message(request: Request):

    session = async_session()

    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))

    message = Message()
    message.path = Ltree(data.get("path_id"))

    output = await session.execute(select(Message).filter(Message.path.descendant_of(message.path)))
    message_ids = [message.id for row in output.fetchall() for message in row]

    await session.execute(delete(Message).where(Message.id.in_(message_ids)))
    await session.commit()
    await session.close()

    return RedirectResponse(url="/bot_config", status_code=status.HTTP_303_SEE_OTHER)


async def get_message_from_bd(text, session):
    output = await session.execute(select(Message).where(func.lower(Message.user_phrase).like(text)))
    result = output.fetchone()

    if result:
        result, *_ = result
        return result.bot_reply
    output = await session.execute(select(Message).filter(func.nlevel(Message.path) == 1))
    texts = '\n'.join([text.user_phrase for row in output.fetchall() for text in row])
    output_text = f"Можете начать общение с помощью этих фраз:\n{texts}"
    return output_text


@router.post("/recived_messages")
async def get_recived_messages(request: Request) -> tuple:

    b_data = await request.body()
    data = json.loads(b_data.decode("utf-8"))

    try:

        message = data["messageData"]["textMessageData"]["textMessage"]
        username = data["senderData"]["senderName"]
        phone_number = data["senderData"]["chatId"].replace("@c.us", "")

    except KeyError:

        return "Send by bot successfully", 200

    session = async_session()
    user_data = {"username": username, "phone_number": phone_number}
    if User.is_unique(session, user_data):
        await session.execute(insert(User).values(user_data))
        await session.commit()

    message = await get_message_from_bd(message, session)

    message_data = {"message": message, "chatId": phone_number + "@c.us"}

    url = f"https://api.green-api.com/waInstance{config['IdInstance']}/SendMessage/{config['apiTokenInstance']}"

    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(url=url, data=json.dumps(message_data)) as response:
            content = await response.text()

    await session.close()

    return content, response.status


app.include_router(router, prefix="")
