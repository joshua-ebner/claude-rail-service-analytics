"""Run bronze → silver → gold pipeline locally."""

from src.pipelines import bronze_ingest, gold_service_metrics, silver_transform


def main() -> None:
    bronze_df = bronze_ingest.run()
    print(f"Bronze: {len(bronze_df)} rows ingested")

    silver_df = silver_transform.run()
    print(f"Silver: {len(silver_df)} rows transformed")

    gold_df = gold_service_metrics.run()
    print(f"Gold: {len(gold_df)} metric rows aggregated")
    print(f"Locomotives with recommended_review: {gold_df['recommended_review'].sum()}")


if __name__ == "__main__":
    main()
