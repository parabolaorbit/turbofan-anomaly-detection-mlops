import requests
import copy


API_URL = "http://localhost:8080/predict"


valid_payload = {
    "sequence": [
        {
            "unit_number": 1,
            "time_in_cycles": i + 1,
            "ope_setting1": -0.0007,
            "ope_setting2": -0.0004,
            "ope_setting3": 100,
            "sensor_ms1": 518.67,
            "sensor_ms2": 641.82,
            "sensor_ms3": 1589.7,
            "sensor_ms4": 1400.6,
            "sensor_ms5": 14.62,
            "sensor_ms6": 21.61,
            "sensor_ms7": 554.36,
            "sensor_ms8": 2388.06,
            "sensor_ms9": 9046.19,
            "sensor_ms10": 1.3,
            "sensor_ms11": 47.47,
            "sensor_ms12": 521.66,
            "sensor_ms13": 2388.02,
            "sensor_ms14": 8138.62,
            "sensor_ms15": 8.4195,
            "sensor_ms16": 0.03,
            "sensor_ms17": 392,
            "sensor_ms18": 2388,
            "sensor_ms19": 100,
            "sensor_ms20": 39.06,
            "sensor_ms21": 23.419,
        }
        for i in range(10)
    ]
}


def post_and_print(name: str, payload: dict):
    response = requests.post(API_URL, json=payload)

    print("=" * 80)
    print(name)
    print("status_code:", response.status_code)

    try:
        print("response:", response.json())
    except Exception:
        print("response text:", response.text)


# 1. 正常系
post_and_print("正常系", valid_payload)


# 2. 欠損カラム
missing_payload = copy.deepcopy(valid_payload)
del missing_payload["sequence"][0]["sensor_ms1"]

post_and_print("欠損カラム: sensor_ms1", missing_payload)


# 3. 型不正
invalid_type_payload = copy.deepcopy(valid_payload)
invalid_type_payload["sequence"][0]["sensor_ms1"] = "invalid"

post_and_print("型不正: sensor_ms1 is string", invalid_type_payload)


# 4. sequenceが空
empty_sequence_payload = {
    "sequence": []
}

post_and_print("異常系: sequence empty", empty_sequence_payload)