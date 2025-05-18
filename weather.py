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

def extract_alerts(feature: dict[str, Any]) -> dict[str, str]:
    """
    天気予報APIからアラート情報を抽出する関数。
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
    """Get the city ID for a given city name.
    例: `get_city_id("横浜市")` で横浜市の ID を取得
    Args:
        city_name: 地域名
    """
    result = await request_ichijisaibunkuiki_xml()
    if not result or "pref" not in result:
        return "地域情報を得るのに失敗しました。"
    if pref_name not in result["pref"]:
        return "県名が見つかりません。"
    if city_name not in result["pref"][pref_name]:
        return "地域名が見つかりません。"
    # Get the city ID
    city_id = result["pref"][pref_name][city_name]
    if not city_id:
        return "地域 ID が見つかりません。"
    
    return str(city_id)

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific state.
    例: `get_alerts("140010")` で横浜市の天気予報を取得

    Args:
        state: 地域別に定義された ID 番号
    """
    data = await requiest_kishou_json(state=state)

    if not data or "forecasts" not in data:
        return "予報を得るのに失敗しました。"

    if not data["forecasts"]:
        return "予報が空です。"

    alerts = [format_alert(forecast) for forecast in data["forecasts"]]
    return "\n---\n".join(alerts)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
