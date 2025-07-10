import requests
import pandas as pd

def get_hourly_weather_seoul_openmeteo():
    SEOUL_DISTRICTS = [
        {"name": "강남구", "lat": 37.5172, "lon": 127.0473},
        {"name": "강동구", "lat": 37.5301, "lon": 127.1238},
        {"name": "강북구", "lat": 37.6396, "lon": 127.0256},
        {"name": "강서구", "lat": 37.5509, "lon": 126.8495},
        {"name": "관악구", "lat": 37.4784, "lon": 126.9516},
        {"name": "광진구", "lat": 37.5384, "lon": 127.0823},
        {"name": "구로구", "lat": 37.4955, "lon": 126.8878},
        {"name": "금천구", "lat": 37.4604, "lon": 126.9006},
        {"name": "노원구", "lat": 37.6542, "lon": 127.0568},
        {"name": "도봉구", "lat": 37.6688, "lon": 127.0472},
        {"name": "동대문구", "lat": 37.5744, "lon": 127.0396},
        {"name": "동작구", "lat": 37.5124, "lon": 126.9392},
        {"name": "마포구", "lat": 37.5663, "lon": 126.9014},
        {"name": "서대문구", "lat": 37.5791, "lon": 126.9368},
        {"name": "서초구", "lat": 37.4836, "lon": 127.0327},
        {"name": "성동구", "lat": 37.5633, "lon": 127.0364},
        {"name": "성북구", "lat": 37.5894, "lon": 127.0167},
        {"name": "송파구", "lat": 37.5146, "lon": 127.1056},
        {"name": "양천구", "lat": 37.5179, "lon": 126.8666},
        {"name": "영등포구", "lat": 37.5264, "lon": 126.8962},
        {"name": "용산구", "lat": 37.5323, "lon": 126.9909},
        {"name": "은평구", "lat": 37.6027, "lon": 126.9291},
        {"name": "종로구", "lat": 37.5735, "lon": 126.9790},
        {"name": "중구", "lat": 37.5636, "lon": 126.9977},
        {"name": "중랑구", "lat": 37.6065, "lon": 127.0927}
    ]

    result_rows = []
    for gu in SEOUL_DISTRICTS:
        latitude, longitude, name = gu["lat"], gu["lon"], gu["name"]
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&hourly=temperature_2m,precipitation,weathercode,relative_humidity_2m,wind_speed_10m"
            "&forecast_days=8&timezone=Asia%2FSeoul"
        )
        resp = requests.get(url)
        if resp.status_code == 200:
            json_data = resp.json()
            if 'hourly' not in json_data:
                print(f"[경고] {name} 데이터에 'hourly' 없음. 응답: {json_data}")
                continue
            data = json_data['hourly']
            for t, temp, rain, code, rh, wind in zip(
                data['time'],
                data['temperature_2m'],
                data['precipitation'],
                data['weathercode'],
                data['relative_humidity_2m'],
                data['wind_speed_10m'],
            ):
                result_rows.append({
                    "행정구": name,
                    "일시": t,
                    "강수": rain,
                    "습도": rh,
                    "풍속": wind,
                    "기온": temp,
                })
        else:
            print(f"[오류] {name} API 호출 실패: {resp.status_code}")
    df = pd.DataFrame(result_rows)
    return df


if __name__ == "__main__" :
    print(get_hourly_weather_seoul_openmeteo())