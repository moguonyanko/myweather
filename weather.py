"""
PythonでMCPサーバを実装する練習のためのプログラム

## 参考
For Server Developers
https://modelcontextprotocol.io/quickstart/server
天気予報 API（livedoor 天気互換）
https://weather.tsukumijima.net/
"""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("myweather")

# Constants
NWS_API_BASE = "https://weather.tsukumijima.net/api/forecast/city/"
USER_AGENT = "my-weather-app/0.0.1"
TIME_OUT = 10.0

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """
    天気予報APIにリクエストを送信し、レスポンスを取得する非同期関数。
    Args:
        url (str): リクエストURL
    Returns:
        dict[str, Any] | None: レスポンスデータ（成功時）またはNone（失敗時）
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=TIME_OUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")
            return None

def extract_alerts(feature: dict) -> dict:
    """
    天気予報APIからアラート情報を抽出する関数。
    Returns:
        dict: アラート情報の辞書
    """
    alerts = {}
    # TODO: 返す情報を追加する。
    detail = feature["detail"]
    alerts["weather"] = detail.get("weather", "Unknown")
    alerts["wind"] = detail.get("wind", "Unknown")
    alerts["wave"] = detail.get("wave", "Unknown")

    alerts["date"] = feature.get("date", "Unknown")

    return alerts

def format_alert(feature: dict) -> str:
    """
    天気予報のアラートをフォーマットする関数。
    Args:
        feature (dict): アラートのフィーチャー情報
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
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific state.
    例: `get_alerts("140010")` で横浜市の天気予報を取得

    Args:
        state: 地域別に定義された ID 番号
    """
    url = f"{NWS_API_BASE}{state}"
    data = await make_nws_request(url)

    if not data or "forecasts" not in data:
        return "予報を得るのに失敗しました。"

    if not data["forecasts"]:
        return "予報が空です。"

    alerts = [format_alert(forecast) for forecast in data["forecasts"]]
    return "\n---\n".join(alerts)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
