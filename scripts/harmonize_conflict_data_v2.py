from pathlib import Path
import pandas as pd


# ---------------------------
# CONFIG
# ---------------------------
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ACLED_FILE = DATA_DIR / "ACLED Data_2026-04-10.csv"
GED_FILES = [
    DATA_DIR / "GEDEvent_v25_01_25_12.csv",
    DATA_DIR / "GEDEvent_v26_0_1.csv",
    DATA_DIR / "GEDEvent_v26_0_2.csv",
]

OUTPUT_FILE = OUTPUT_DIR / "project_ready_conflict_harmonized_v2.csv"


# ---------------------------
# HELPERS
# ---------------------------
def safe_col(df: pd.DataFrame, col: str, default=None):
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def to_datetime_safe(series):
    return pd.to_datetime(series, errors="coerce")


def numeric_safe(series):
    return pd.to_numeric(series, errors="coerce")


def text_clean(series):
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
    )


def add_missing_columns(df: pd.DataFrame, required_cols: list[str]) -> pd.DataFrame:
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df[required_cols]


# ---------------------------
# ACLED HARMONIZATION
# ---------------------------
def harmonize_acled(acled_path: Path) -> pd.DataFrame:
    # Try normal comma-separated read first
    df = pd.read_csv(acled_path, low_memory=False)

    event_date = to_datetime_safe(safe_col(df, "event_date"))

    actor2 = text_clean(safe_col(df, "actor2"))
    actor2_source = pd.Series(
        ["actor2" if pd.notna(x) else pd.NA for x in actor2],
        index=df.index
    )

    out = pd.DataFrame({
        "record_id": [f"ACLED_{i+1}" for i in range(len(df))],
        "event_id": text_clean(safe_col(df, "event_id_cnty")),
        "event_date": event_date.dt.strftime("%Y-%m-%d"),
        "year": numeric_safe(safe_col(df, "year")),
        "actor1": text_clean(safe_col(df, "actor1")),
        "assoc_actor_1": text_clean(safe_col(df, "assoc_actor_1")),
        "inter1": numeric_safe(safe_col(df, "inter1")),
        "actor2": actor2,
        "assoc_actor_2": text_clean(safe_col(df, "assoc_actor_2")),
        "inter2": numeric_safe(safe_col(df, "inter2")),
        "actor2_source": actor2_source,
        "country": text_clean(safe_col(df, "country")),
        "region": text_clean(safe_col(df, "region")),
        "admin1": text_clean(safe_col(df, "admin1")),
        "admin2": text_clean(safe_col(df, "admin2")),
        "admin3": text_clean(safe_col(df, "admin3")),
        "location": text_clean(safe_col(df, "location")),
        "latitude": numeric_safe(safe_col(df, "latitude")),
        "longitude": numeric_safe(safe_col(df, "longitude")),
        "fatalities": numeric_safe(safe_col(df, "fatalities")),
        "notes": text_clean(safe_col(df, "notes")),
        "event_type": text_clean(safe_col(df, "event_type")),
        "sub_event_type": text_clean(safe_col(df, "sub_event_type")),
        "disorder_type": text_clean(safe_col(df, "disorder_type")),
        "interaction": numeric_safe(safe_col(df, "interaction")),
        "civilian_targeting": text_clean(safe_col(df, "civilian_targeting")),
        "source_dataset": "ACLED",
        "source_file": acled_path.name,
        "synthetic_flag": False,
        "harmonization_confidence": "high",
    })

    return out


# ---------------------------
# GED HARMONIZATION
# ---------------------------
GED_TYPE_OF_VIOLENCE_MAP = {
    1: "State-based violence",
    2: "Non-state violence",
    3: "One-sided violence",
}


def harmonize_single_ged(ged_path: Path) -> pd.DataFrame:
    df = pd.read_csv(ged_path, low_memory=False)

    event_date = to_datetime_safe(safe_col(df, "date_start"))
    type_of_violence_num = numeric_safe(safe_col(df, "type_of_violence"))
    disorder_type = type_of_violence_num.map(GED_TYPE_OF_VIOLENCE_MAP)

    out = pd.DataFrame({
        "record_id": [f"{ged_path.stem}_{i+1}" for i in range(len(df))],
        "event_id": text_clean(safe_col(df, "id")),
        "event_date": event_date.dt.strftime("%Y-%m-%d"),
        "year": event_date.dt.year,
        "actor1": text_clean(safe_col(df, "side_a")),
        "assoc_actor_1": pd.NA,
        "inter1": pd.NA,
        "actor2": text_clean(safe_col(df, "side_b")),
        "assoc_actor_2": pd.NA,
        "inter2": pd.NA,
        "actor2_source": "side_b",
        "country": text_clean(safe_col(df, "country")),
        "region": text_clean(safe_col(df, "region")),
        "admin1": text_clean(safe_col(df, "adm_1")),
        "admin2": text_clean(safe_col(df, "adm_2")),
        "admin3": text_clean(safe_col(df, "adm_3")),
        "location": text_clean(safe_col(df, "where_coordinates")),
        "latitude": numeric_safe(safe_col(df, "latitude")),
        "longitude": numeric_safe(safe_col(df, "longitude")),
        "fatalities": numeric_safe(safe_col(df, "best")),
        "notes": text_clean(safe_col(df, "source_headline")),
        "event_type": disorder_type,
        "sub_event_type": text_clean(safe_col(df, "dyad_name")),
        "disorder_type": disorder_type,
        "interaction": type_of_violence_num,
        "civilian_targeting": pd.NA,
        "source_dataset": "GED",
        "source_file": ged_path.name,
        "synthetic_flag": True,
        "harmonization_confidence": "medium",
    })

    return out


def harmonize_all_ged(ged_files: list[Path]) -> pd.DataFrame:
    ged_dfs = []
    for path in ged_files:
        if not path.exists():
            raise FileNotFoundError(f"GED file not found: {path}")
        ged_dfs.append(harmonize_single_ged(path))

    ged = pd.concat(ged_dfs, ignore_index=True)

    # Remove overlaps across GED releases
    ged = ged.drop_duplicates(subset=["event_id"], keep="last").reset_index(drop=True)

    # Rebuild GED record_id after deduplication
    ged["record_id"] = [f"GED_{i+1}" for i in range(len(ged))]

    return ged


# ---------------------------
# MAIN
# ---------------------------
def main():
    if not ACLED_FILE.exists():
        raise FileNotFoundError(f"ACLED file not found: {ACLED_FILE}")

    missing_ged = [p for p in GED_FILES if not p.exists()]
    if missing_ged:
        raise FileNotFoundError(f"Missing GED files: {missing_ged}")

    print("Loading and harmonizing ACLED...")
    acled = harmonize_acled(ACLED_FILE)

    print("Loading and harmonizing GED files...")
    ged = harmonize_all_ged(GED_FILES)

    required_cols = [
        "record_id",
        "event_id",
        "event_date",
        "year",
        "actor1",
        "assoc_actor_1",
        "inter1",
        "actor2",
        "assoc_actor_2",
        "inter2",
        "actor2_source",
        "country",
        "region",
        "admin1",
        "admin2",
        "admin3",
        "location",
        "latitude",
        "longitude",
        "fatalities",
        "notes",
        "event_type",
        "sub_event_type",
        "disorder_type",
        "interaction",
        "civilian_targeting",
        "source_dataset",
        "source_file",
        "synthetic_flag",
        "harmonization_confidence",
    ]

    acled = add_missing_columns(acled, required_cols)
    ged = add_missing_columns(ged, required_cols)

    final_df = pd.concat([acled, ged], ignore_index=True)

    final_df["event_date_dt"] = pd.to_datetime(final_df["event_date"], errors="coerce")
    final_df = (
        final_df.sort_values(
            by=["event_date_dt", "source_dataset", "country", "event_id"],
            na_position="last"
        )
        .drop(columns=["event_date_dt"])
        .reset_index(drop=True)
    )

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\nDone.")
    print(f"Saved harmonized file to: {OUTPUT_FILE}")
    print(f"Rows: {len(final_df):,}")
    print(f"Columns: {len(final_df.columns)}")
    print(f"Date range: {final_df['event_date'].min()} to {final_df['event_date'].max()}")

    print("\nSource breakdown:")
    print(final_df["source_dataset"].value_counts(dropna=False).to_string())

    print("\nMissingness summary:")
    for col in ["actor1", "actor2", "country", "latitude", "longitude", "fatalities", "event_type"]:
        miss = final_df[col].isna().mean() * 100
        print(f"  {col}: {miss:.2f}% missing")


if __name__ == "__main__":
    main()