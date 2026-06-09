from pydantic import BaseModel, Field

class SensorRecord(BaseModel):
    """
    ユニットNo、Cycleごとのセンサー状態
    """
    unit_number: int
    time_in_cycles: int
    ope_setting1: float
    ope_setting2: float
    ope_setting3: float
    sensor_ms1: float
    sensor_ms2: float
    sensor_ms3: float
    sensor_ms4: float
    sensor_ms5: float
    sensor_ms6: float
    sensor_ms7: float
    sensor_ms8: float
    sensor_ms9: float
    sensor_ms10: float
    sensor_ms11: float
    sensor_ms12: float
    sensor_ms13: float
    sensor_ms14: float
    sensor_ms15: float
    sensor_ms16: float
    sensor_ms17: float
    sensor_ms18: float
    sensor_ms19: float
    sensor_ms20: float
    sensor_ms21: float

class PredictRequest(BaseModel):
    """
    推論API呼び出し時のリクエストデータ形式
    """
    sequence: list[SensorRecord] = Field(..., min_length=1)
    seq_len: int = 10
    rolling_window: int = 10
    threshold: float = 0.8
    consecutive_window: int = 5

