from typing import Any
import xml.etree.ElementTree as ET
import requests
import httpx
import json

config = json.load(open("config.json", "r", encoding="utf-8"))

# async def do_request(url: str, accept: str) -> dict[str, Any] | None:
#     """
#     天気予報APIにリクエストを送信し、レスポンスを取得する非同期関数。
#     Args:
#         url (str): リクエストURL
#     Returns:
#         dict[str, Any] | None: レスポンスデータ（成功時）またはNone（失敗時）
#     """
#     headers = {
#         "User-Agent": config["user_agent"],
#         "Accept": accept
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=config["time_out"])
#             response.raise_for_status()
#             return response.content
#         except Exception as e:
#             print(f"Error fetching data from {url}: {e}")
#             return None


# async def make_nws_request(url: str) -> dict[str, Any] | None:
#     """
#     天気予報APIにリクエストを送信し、レスポンスを取得する非同期関数。
#     Args:
#         url (str): リクエストURL
#     Returns:
#         dict[str, Any] | None: レスポンスデータ（成功時）またはNone（失敗時）
#     """
#     headers = {
#         "User-Agent": USER_AGENT,
#         "Accept": "application/json"
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=TIME_OUT)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"Error fetching data from {url}: {e}")
#             return None


async def request_kishou_xml(xml_source):
    """
    気象庁の防災情報XMLをパースして、一次細分区域の名称とコード（もしあれば）を抽出する関数。

    Args:
        xml_source (str): XMLファイルのパスまたはURL。

    Returns:
        list: 一次細分区域の名称とコード（またはNone）のタプルのリスト。
    """
    output_json = {"pref": {}}
    async with httpx.AsyncClient() as client:
      try:
          headers = {
              "User-Agent": config.get("user_agent"),
              "Accept": "application/xml"
          }
          response = await client.get(xml_source, headers=headers, timeout=config.get("time_out", 10))
          response.raise_for_status()
          root = ET.fromstring(response.content)

          for pref_element in root.findall('.//pref'):
              pref_title = pref_element.get('title')
              output_json["pref"][pref_title] = {}
              for city_element in pref_element.findall('./city'):
                  city_title = city_element.get('title')
                  city_id = city_element.get('id')
                  output_json["pref"][pref_title][city_title] = city_id

      except requests.exceptions.RequestException as e:
          print(f"エラー: URL '{xml_source}' へのアクセスに失敗しました: {e}")
      except ET.ParseError as e:
          print(f"エラー: XMLのパースに失敗しました: {e}")
      except Exception as e:
          print(f"予期せぬエラーが発生しました: {e}")

    return output_json
