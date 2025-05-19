from typing import Any, Optional
import xml.etree.ElementTree as ET
import requests
import httpx
import json

config = json.load(open("config.json", "r", encoding="utf-8"))

async def do_request(url: str, accept: str) -> bytes | None:
    """
    天気予報APIにリクエストを送信し、レスポンスを取得する非同期関数。
    引数:
        url (str): リクエストURL
    戻り値:
        bytes | None: レスポンスデータ（成功時）またはNone（失敗時）
    """
    headers: dict[str, str] = {
        "User-Agent": config["user_agent"],
        "Accept": accept
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=config["time_out"])
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"データの取得中にエラーが発生しました: {url}: {e}")
            return None

async def requiest_kishou_json(state: str) -> dict[str, Any] | None:
    """
    天気予報APIにリクエストを送信し、JSONレスポンスを取得する非同期関数。
    引数:
        state (str): 地域名や都道府県名
    戻り値:
        dict[str, Any] | None: レスポンスデータ（成功時）またはNone（失敗時）
    """
    nws_url = f"{config["nws_api_base"]}{state}"
    response_bytes = await do_request(nws_url, "application/json")
    if response_bytes is not None:
        try:
            return json.loads(response_bytes.decode("utf-8"))
        except Exception as e:
            print(f"JSONレスポンスのデコードに失敗しました: {e}")
            return None
    return None

def set_city_ids(pref_element: ET.Element, 
                 output_json: dict[str, dict[str, dict[str, Optional[str]]]], 
                 pref_title: str):
    """
    都道府県要素から市町村のIDを抽出して辞書に格納する関数。
    Args:
        pref_element (ET.Element): 都道府県要素
        output_json (dict): 出力用の辞書
        pref_title (str): 都道府県名
    """
    # 都道府県名をキーにして辞書を初期化
    for city_element in pref_element.findall('./city'):
        city_title = city_element.get('title')
        city_id = city_element.get('id')
        if city_title is not None:
            output_json["pref"][pref_title][city_title] = city_id

async def request_ichijisaibunkuiki_xml() -> dict[str, dict[str, dict[str, Optional[str]]]]:
    """
    気象庁の防災情報XMLをパースして、一次細分区域の名称とコード（もしあれば）を抽出する関数。

    戻り値:
        dict[str, dict[str, dict[str, Optional[str]]]]: 一次細分区域の名称とコード（またはNone）を格納した辞書。
    """

    output_json: dict[str, dict[str, dict[str, Optional[str]]]] = {"pref": {}}
    xml_source = config["ichijisaibunkuiki_xml"]
    try:
        response = await do_request(url=xml_source, accept="application/xml")
        if response is not None:
            root = ET.fromstring(response.decode("utf-8"))

            for pref_element in root.findall('.//pref'):
                pref_title = pref_element.get('title')
                if pref_title is not None:
                    if pref_title not in output_json["pref"]:                        
                        output_json["pref"][pref_title] = {}
                    set_city_ids(pref_element, output_json, pref_title)
        else:
            print(f"エラー: XMLデータの取得に失敗しました: {xml_source}")

    except requests.exceptions.RequestException as e:
        print(f"エラー: URL '{xml_source}' へのアクセスに失敗しました: {e}")
    except ET.ParseError as e:
        print(f"エラー: XMLのパースに失敗しました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

    return output_json
