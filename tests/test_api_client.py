from unittest.mock import Mock, patch

from weather_app.api_client import OpenMeteoClient
from weather_app.models import City


@patch("weather_app.api_client.requests.get")
def test_fetch_weather_uses_mocked_http(
    mock_get: Mock,
) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 18.5,
            "weather_code": 0,
        }
    }

    mock_get.return_value = mock_response

    client = OpenMeteoClient()
    city = City("Van", "TR", 38.5012, 43.373)

    result = client.fetch_weather(city, "metric")

    assert result.temperature == 18.5
    assert result.condition == "Clear Sky"
    assert result.source == "API FETCH"

    mock_get.assert_called_once()