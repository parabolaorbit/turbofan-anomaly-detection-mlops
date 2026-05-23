import requests
import pandas as pd
from pathlib import Path


API_URL = "http://localhost:8080/predict"

INPUT_CSV = Path("data/test_sequence.csv")
OUTPUT_CSV = Path("results/batch_predictions.csv")


def build_payload(df_unit: pd.DataFrame) -> dict:
    records = df_unit.to_dict(orient="records")

    return {
        "sequence": records
    }


def main():
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV)

    results = []

    grouped = df.groupby("unit_number")

    for unit_number, df_unit in grouped:

        payload = build_payload(df_unit)

        response = requests.post(API_URL, json=payload)

        if response.status_code != 200:
            print(f"[ERROR] unit={unit_number}")
            print(response.text)
            continue

        result = response.json()

        results.append(result)

        print(
            f"[OK] unit={unit_number} "
            f"score={result['error']:.4f} "
            f"severity={result['severity']}"
        )

    results_df = pd.DataFrame(results)

    results_df.to_csv(OUTPUT_CSV, index=False)

    print()
    print(f"saved: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()