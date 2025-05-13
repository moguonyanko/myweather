"""Unit tests for weather.py module."""

import pytest
import weather

@pytest.mark.asyncio
async def test_make_nws_request():
  yokohama = "140010"
  result = await weather.make_nws_request(f"{weather.NWS_API_BASE}{yokohama}")
  assert result is not None

@pytest.mark.asyncio
async def test_extract_alerts():
  yokohama = "140010"
  features = await weather.make_nws_request(f"{weather.NWS_API_BASE}{yokohama}")
  result = weather.extract_alerts(features['forecasts'][0])
  assert "weather" in result
  assert "wind" in result
  assert "wave" in result
  assert "date" in result

@pytest.mark.asyncio
async def test_get_alerts():
  yokohama = "140010"
  result = await weather.get_alerts(yokohama)
  print(result)
  assert result is not None
