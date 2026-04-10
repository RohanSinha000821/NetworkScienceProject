from pathlib import Path
import pandas as pd


# ---------------------------
# CONFIG
# ---------------------------
INPUT_FILE = Path("output") / "project_ready_conflict_harmonized_v2.csv"
OUTPUT_FILE = Path("output") / "conflict_filtered_phase2_core_v2.csv"

TARGET_COUNTRIES = [
    "Israel",
    "Palestine",
    "Lebanon",
    "Syria",
    "Iraq",
    "Yemen",
    "Iran",
    "United States",
]


# ---------------------------
# HELPERS
# ---------------------------
def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Loaded rows: {len(df):,}")
    print(f"Loaded columns: {len(df.columns)}")

    # Normalize country names
    df["country_norm"] = normalize_text(df["country"])
    target_countries_norm = {c.lower() for c in TARGET_COUNTRIES}

    # Strict country-only filter
    filtered = df[df["country_norm"].isin(target_countries_norm)].copy()

    # Drop helper column
    filtered = filtered.drop(columns=["country_norm"], errors="ignore")

    # Sort by date
    filtered["event_date_dt"] = pd.to_datetime(filtered["event_date"], errors="coerce")
    filtered = (
        filtered.sort_values(
            by=["event_date_dt", "source_dataset", "country", "event_id"],
            na_position="last"
        )
        .drop(columns=["event_date_dt"])
        .reset_index(drop=True)
    )

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(OUTPUT_FILE, index=False)

    # Reporting
    print("\nStrict Phase 2 filtering complete.")
    print(f"Saved filtered file to: {OUTPUT_FILE}")
    print(f"Filtered rows: {len(filtered):,}")
    print(f"Rows removed: {len(df) - len(filtered):,}")

    print("\nSource breakdown:")
    print(filtered["source_dataset"].value_counts(dropna=False).to_string())

    print("\nCountry breakdown:")
    print(filtered["country"].value_counts(dropna=False).to_string())

    print("\nDate range:")
    print(f"{filtered['event_date'].min()} to {filtered['event_date'].max()}")

    print("\nActor coverage:")
    for col in ["actor1", "actor2", "assoc_actor_1", "assoc_actor_2"]:
        miss = filtered[col].isna().mean() * 100
        print(f"  {col}: {miss:.2f}% missing")

    print("\nInteraction coverage:")
    for col in ["inter1", "inter2", "interaction"]:
        miss = filtered[col].isna().mean() * 100
        print(f"  {col}: {miss:.2f}% missing")

    print("\nSanity checks:")
    print(f"  Unique countries: {filtered['country'].nunique(dropna=True)}")
    print(f"  Unique actor1 values: {filtered['actor1'].nunique(dropna=True):,}")
    print(f"  Unique actor2 values: {filtered['actor2'].nunique(dropna=True):,}")
    print(f"  Unique assoc_actor_1 values: {filtered['assoc_actor_1'].nunique(dropna=True):,}")
    print(f"  Unique assoc_actor_2 values: {filtered['assoc_actor_2'].nunique(dropna=True):,}")


if __name__ == "__main__":
    main()