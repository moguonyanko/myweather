"""
PythonでMCPサーバを実装する練習のためのプログラム

## 参考
For Server Developers
https://modelcontextprotocol.io/quickstart/server
天気予報 API（livedoor 天気互換）
https://weather.tsukumijima.net/
"""

from typing import Any
from mcp.server.fastmcp import FastMCP
from httputils import requiest_kishou_json, request_ichijisaibunkuiki_xml

# Initialize FastMCP server
mcp = FastMCP("myweather")

class ForecastException(Exception):
    """
    天気予報を得る過程で発生した例外を表すクラス。
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"天気予報取得で例外発生: {self.message}"
    def __repr__(self) -> str:
        return f"ForecastException({self.message})"
    
class NotFoundPrefException(ForecastException):
    """
    都道府県が見つからない場合の例外を表すクラス。
    """
    def __init__(self, pref_name: str):
        super().__init__(f"都道府県が見つかりません: {pref_name}")
    
class NotFoundCityException(ForecastException):
    """
    市町村が見つからない場合の例外を表すクラス。
    """
    def __init__(self, city_name: str):
        super().__init__(f"地域名が見つかりません: {city_name}")

def extract_alerts(feature: dict[str, Any]) -> dict[str, str]:
    """
    天気予報APIからアラート情報を抽出する関数。
    Args:
        feature (dict[str, Any]): アラートのフィーチャー情報
    例:
        {
            "detail": {
                "weather": "晴れ",
                "wind": "南東の風",
                "wave": "1m"
            },
            "date": "2023-10-01"
        }
 
    Returns:
        dict: アラート情報の辞書
    """
    alerts: dict[str, str] = {}
    # TODO: 返す情報を追加する。
    detail = feature["detail"]
    alerts["weather"] = detail.get("weather", "Unknown")
    alerts["wind"] = detail.get("wind", "Unknown")
    alerts["wave"] = detail.get("wave", "Unknown")

    alerts["date"] = feature.get("date", "Unknown")

    return alerts

def format_alert(feature: dict[str, Any]) -> str:
    """
    天気予報のアラートをフォーマットする関数。
    Args:
        feature (dict[str, Any]): アラートのフィーチャー情報
    Returns:
        str: フォーマットされたアラート情報
    """
    alerts = extract_alerts(feature)

    return f"""
weather: {alerts.get('weather')}
wind: {alerts.get('wind')}
wave: {alerts.get('wave')}
date: {alerts.get("date")}
"""

@mcp.tool()
async def get_city_id(pref_name: str, city_name: str) -> str:
    """
    指定した一次細分区域名から地域IDを取得します。
    例: `get_city_id("福岡県")` で福岡の ID を取得
    Args:
        pref_name: 地域名
        北海道を除き県名と一致する。北海道は「道南」「道央」「道北」「道東」のいずれかを指定する。
        例: "福岡県"
        city_name: 一次細分区域名
        島や湖を除き、「市」を除去した市区町村名と一致する。
        例: "福岡"
    """
    result = await request_ichijisaibunkuiki_xml()
    if not result or "pref" not in result:
        raise ForecastException("地域情報を得るのに失敗しました。")
    if pref_name not in result["pref"]:
        raise NotFoundPrefException(pref_name=pref_name)
    if city_name not in result["pref"][pref_name]:
        raise NotFoundCityException(city_name=city_name)
    city_id = result["pref"][pref_name][city_name]
    if not city_id:
        raise ForecastException("地域 ID が見つかりません。")
    
    return str(city_id)

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    指定した地域IDの天気予報アラートを取得します。
    例: `get_alerts("400010")` で福岡の天気予報を取得

    Args:
        state: 地域別に定義された ID 番号
    Returns:
        str: フォーマットされたアラート情報
    """
    data = await requiest_kishou_json(state=state)

    if not data or "forecasts" not in data:
        raise ForecastException("予報を得るのに失敗しました。")

    if not data["forecasts"]:
        raise ForecastException("予報が空です。")

    alerts = [format_alert(forecast) for forecast in data["forecasts"]]
    return "\n---\n".join(alerts)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
