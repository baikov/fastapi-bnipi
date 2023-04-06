import uuid
from typing import List

import aioredis
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.config import REDIS_HOST, REDIS_PORT

app = FastAPI(title="Test App for BNIPI")


# Инициализация клиента Redis
async def get_redis_client():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
    yield redis


class NumList(BaseModel):
    array: List[str | None]


async def calculate_sum(array: list[str | None]) -> int:
    try:
        return sum([int(item) for item in array if item is not None])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Некоторые элементы массива невозможно привести к целому типу",
        )


@app.post("/async-calculate")
async def calculate_sum_handler(
    body: NumList,
    request: Request,
    response: Response,
    redis: aioredis.Redis = Depends(get_redis_client),
):
    """
    Генерирует `session_id` и сохраняет в `cookies`. Сохраняет результат вычисления
    в Redis с ключом `session_id`
    """
    # Получение session_id из cookies. Если сессии нет - создание и запись в cookies
    session_id = request.cookies.get("session_id")

    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id)

    # Вызов функции суммирования элементов массива и сохранение результата в Redis
    result = await calculate_sum(body.array)
    await redis.set(session_id, result)

    return {"session_id": session_id}


@app.get("/async-result")
async def get_result_by_session_from_cookie(
    request: Request, redis: aioredis.Redis = Depends(get_redis_client)
):
    result = None
    session_id = request.cookies.get("session_id")
    if session_id is not None:
        result = await redis.get(session_id)
    if result is None:
        return {"result": "not_found"}
    return {"result": int(result)}


@app.get("/get-result/{session_id}")
async def get_result_by_session(
    session_id: str, redis: aioredis.Redis = Depends(get_redis_client)
):
    """
    Возвращает результат из Redis по `session_id`
    """
    result = await redis.get(session_id)
    if result is None:
        return {"result": "not_found"}
    return {"result": int(result)}


@app.post("/calculate", status_code=status.HTTP_200_OK)
async def get_sum(body: NumList):
    result = await calculate_sum(body.array)
    return {"result": result}
