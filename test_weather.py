"""Unit tests for weather.py module."""

import pytest
from httputils import requiest_kishou_json
from weather import extract_alerts, get_city_id, get_alerts

@pytest.mark.asyncio
async def test_extract_alerts():
  yokohama = "140010"
  features = await requiest_kishou_json(state=yokohama)
  assert features is not None, "features is None"
  assert 'forecasts' in features and features['forecasts'], "forecasts key missing or empty"
  result = extract_alerts(features['forecasts'][0])
  assert "weather" in result
  assert "wind" in result
  assert "wave" in result
  assert "date" in result

@pytest.mark.asyncio
async def test_get_alerts():
  yokohama = "140010"
  result = await get_alerts(yokohama)
  print(result)
  assert result is not None

@pytest.mark.asyncio
async def test_get_city_id():
  kanagawa = "神奈川県"
  yokohama = "横浜"
  result = await get_city_id(kanagawa, yokohama)
  print(result)
  assert result is not None
  assert isinstance(result, str), "The result should be a string."
  assert len(result) > 0, "The result should not be empty."
  assert result.isdigit(), "The result should be a digit."
  assert len(result) == 6, "The result should be a 6-digit string."
