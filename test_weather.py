"""Unit tests for weather.py module."""

import pytest
import weather

@pytest.mark.asyncio
async def test_make_nws_request():
  yokohama = "140010"
  result = await weather.make_nws_request(f"{weather.NWS_API_BASE}{yokohama}")
  assert result is not None
