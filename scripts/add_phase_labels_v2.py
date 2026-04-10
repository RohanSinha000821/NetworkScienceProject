from pathlib import Path
import pandas as pd


# ---------------------------
# CONFIG
# ---------------------------
INPUT_FILE = Path("output") / "conflict_filtered_phase2_core_v2.csv"
OUTPUT_FILE = Path("output") / "conflict_phase3_segmented_v2.csv"


# ---------------------------
# HELPERS
# ---------------------------
def assign_phase(year):
    if pd.isna(year):
        return pd.NA

    year = int(year)

    if 2015 <= year <= 2018:
        return "Phase 1"
    elif 2019 <= year <= 2021:
        return "Phase 2"
    elif 2022 <= year <= 2026:
        return "Phase 3"
    else:
        return pd.NA


def assign_phase_label(year):
    if pd.isna(year):
        return pd.NA

    year = int(year)

    if 2015 <= year <= 2018:
        return "2015-2018 | Transitional Shadow Phase"
    elif 2019 <= year <= 2021:
        return "2019-2021 | Escalatory Hybrid Phase"
    elif 2022 <= year <= 2026:
        return "2022-2026 | Current Escalation Phase"
    else:
        return pd.NA


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Loaded rows: {len(df):,}")
    print(f"Loaded columns: {len(df.columns)}")

    # Ensure year is numeric
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Add phase columns
    df["phase"] = df["year"].apply(assign_phase)
    df["phase_label"] = df["year"].apply(assign_phase_label)

    # Count rows outside the intended phase range
    outside_range = df["phase"].isna().sum()

    # Sort by phase and date
    df["event_date_dt"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = (
        df.sort_values(
            by=["phase", "event_date_dt", "source_dataset", "country", "event_id"],
            na_position="last"
        )
        .drop(columns=["event_date_dt"])
        .reset_index(drop=True)
    )

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    # Reporting
    print("\nPhase 3 segmentation complete.")
    print(f"Saved file to: {OUTPUT_FILE}")

    print("\nPhase breakdown:")
    print(df["phase"].value_counts(dropna=False).sort_index().to_string())

    print("\nPhase label breakdown:")
    print(df["phase_label"].value_counts(dropna=False).to_string())

    print("\nSource breakdown by phase:")
    print(pd.crosstab(df["phase"], df["source_dataset"]))

    print("\nCountry breakdown by phase:")
    print(pd.crosstab(df["phase"], df["country"]))

    print("\nActor coverage by phase:")
    actor_cov = df.groupby("phase")[["actor1", "actor2", "assoc_actor_1", "assoc_actor_2"]].apply(
        lambda g: pd.Series({
            "actor1_missing_pct": g["actor1"].isna().mean() * 100,
            "actor2_missing_pct": g["actor2"].isna().mean() * 100,
            "assoc_actor_1_missing_pct": g["assoc_actor_1"].isna().mean() * 100,
            "assoc_actor_2_missing_pct": g["assoc_actor_2"].isna().mean() * 100,
        })
    )
    print(actor_cov.round(2).to_string())

    print("\nSanity checks:")
    print(f"  Rows outside defined phase ranges: {outside_range}")
    print(f"  Unique phases: {df['phase'].nunique(dropna=True)}")
    print(f"  Date range: {df['event_date'].min()} to {df['event_date'].max()}")


if __name__ == "__main__":
    main()