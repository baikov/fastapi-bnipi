from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app

from src.main import calculate_sum

client = TestClient(app)


class TestApi:
    async def test_calculate_sum(self):
        assert await calculate_sum(["1", "2", "3", None, "4"]) == 10
        assert await calculate_sum(["1", "2", "3"]) == 6
        try:
            await calculate_sum([1, 2, 3, None, "a"])
        except HTTPException as e:
            assert e.status_code == 400
            assert (
                "Некоторые элементы массива невозможно привести к целому типу"
                in e.detail
            )

    def test_calculate_sum_handler_with_invalid_array(self):
        with patch("main.get_redis_client") as mock_redis:
            mock_redis.return_value = MagicMock()

            response = client.post(
                "/async-calculate",
                json={
                    "array": ["1", "2", "invalid"],
                },
            )

            assert response.status_code == 400
            assert response.json() == {
                "detail": "Некоторые элементы массива невозможно привести к целому типу"
            }
            mock_redis.return_value.set.assert_not_called()
