"""Unit tests for weather.py module."""

import pytest
from httputils import requiest_kishou_json, request_ichijisaibunkuiki_xml

@pytest.mark.asyncio
async def test_make_nws_request():
  yokohama = "140010"
  result = await requiest_kishou_json(state=yokohama)
  assert result is not None

@pytest.mark.asyncio
async def test_request_kishou_xml():
  result = await request_ichijisaibunkuiki_xml()

  assert isinstance(result, dict), "The result should be a dictionary."
  assert "pref" in result, "The result should contain 'pref' key."
  assert isinstance(result["pref"], dict), "'pref' should be a dictionary."
  assert len(result["pref"]) > 0, "'pref' should not be empty."

  for pref, cities in result["pref"].items():
    assert isinstance(cities, dict), f"Cities for {pref} should be a dictionary."
    assert len(cities) > 0, f"Cities for {pref} should not be empty."
    for city, city_id in cities.items():
      assert isinstance(city, str), f"City name should be a string."
      assert city_id is None or isinstance(city_id, str), f"City ID should be a string or None."
      assert len(city) > 0, f"City name should not be empty."
      if city_id is not None:
        assert len(city_id) > 0, f"City ID should not be empty."
      assert city in cities, f"City {city} should be in the cities dictionary."
      assert city_id in cities.values(), f"City ID {city_id} should be in the cities dictionary values."
      assert city in result["pref"][pref], f"City {city} should be in the pref dictionary."
      assert result["pref"][pref][city] == city_id, f"City ID for {city} should be {city_id}."
      assert pref in result["pref"], f"Prefecture {pref} should be in the result."
      
  print(result)
