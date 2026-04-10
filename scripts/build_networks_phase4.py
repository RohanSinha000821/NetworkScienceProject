from pathlib import Path
import pandas as pd


# ---------------------------
# CONFIG
# ---------------------------
INPUT_FILE = Path("output") / "conflict_phase3_segmented_v2.csv"
OUTPUT_DIR = Path("output") / "network_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------
# HELPERS
# ---------------------------
def clean_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Loaded rows: {len(df):,}")
    print(f"Loaded columns: {len(df.columns)}")

    # Clean key fields
    df["event_id"] = clean_text(df["event_id"])
    df["actor1"] = clean_text(df["actor1"])
    df["actor2"] = clean_text(df["actor2"])
    df["phase"] = clean_text(df["phase"])
    df["country"] = clean_text(df["country"])
    df["event_date"] = clean_text(df["event_date"])
    df["fatalities"] = pd.to_numeric(df["fatalities"], errors="coerce").fillna(0)

    # ---------------------------
    # 1. ACTOR-ACTOR EDGE LIST
    # ---------------------------
    actor_pairs = df[
        df["actor1"].notna() &
        df["actor2"].notna() &
        df["event_id"].notna()
    ].copy()

    # Optional canonical ordering for undirected network
    actor_pairs["node_u"] = actor_pairs[["actor1", "actor2"]].min(axis=1)
    actor_pairs["node_v"] = actor_pairs[["actor1", "actor2"]].max(axis=1)

    actor_actor_edges_overall = (
        actor_pairs.groupby(["node_u", "node_v"], dropna=False)
        .agg(
            event_count=("event_id", "nunique"),
            row_count=("event_id", "size"),
            total_fatalities=("fatalities", "sum"),
            phases=("phase", lambda x: "|".join(sorted(set(x.dropna().astype(str))))),
            countries=("country", lambda x: "|".join(sorted(set(x.dropna().astype(str))))),
            first_event_date=("event_date", "min"),
            last_event_date=("event_date", "max"),
        )
        .reset_index()
        .sort_values(["event_count", "total_fatalities"], ascending=[False, False])
    )

    actor_actor_edges_by_phase = (
        actor_pairs.groupby(["phase", "node_u", "node_v"], dropna=False)
        .agg(
            event_count=("event_id", "nunique"),
            row_count=("event_id", "size"),
            total_fatalities=("fatalities", "sum"),
            countries=("country", lambda x: "|".join(sorted(set(x.dropna().astype(str))))),
            first_event_date=("event_date", "min"),
            last_event_date=("event_date", "max"),
        )
        .reset_index()
        .sort_values(["phase", "event_count", "total_fatalities"], ascending=[True, False, False])
    )

    # ---------------------------
    # 2. EVENT-ACTOR BIPARTITE EDGE LIST
    # ---------------------------
    actor1_edges = df[df["event_id"].notna() & df["actor1"].notna()].copy()
    actor1_edges = actor1_edges.assign(
        event_node=actor1_edges["event_id"],
        actor_node=actor1_edges["actor1"],
        actor_role="actor1"
    )[
        ["event_node", "actor_node", "actor_role", "phase", "country", "event_date", "fatalities"]
    ]

    actor2_edges = df[df["event_id"].notna() & df["actor2"].notna()].copy()
    actor2_edges = actor2_edges.assign(
        event_node=actor2_edges["event_id"],
        actor_node=actor2_edges["actor2"],
        actor_role="actor2"
    )[
        ["event_node", "actor_node", "actor_role", "phase", "country", "event_date", "fatalities"]
    ]

    event_actor_bipartite_edges = pd.concat([actor1_edges, actor2_edges], ignore_index=True)

    # ---------------------------
    # 3. NODE TABLES
    # ---------------------------
    actor_nodes = pd.concat([
        df[["actor1"]].rename(columns={"actor1": "actor"}),
        df[["actor2"]].rename(columns={"actor2": "actor"})
    ], ignore_index=True)

    actor_nodes = actor_nodes.dropna().drop_duplicates().reset_index(drop=True)
    actor_nodes["node_type"] = "actor"

    actor_participation = (
        event_actor_bipartite_edges.groupby("actor_node")
        .agg(
            event_count=("event_node", "nunique"),
            total_fatalities=("fatalities", "sum"),
            phases=("phase", lambda x: "|".join(sorted(set(x.dropna().astype(str))))),
            countries=("country", lambda x: "|".join(sorted(set(x.dropna().astype(str))))),
        )
        .reset_index()
        .rename(columns={"actor_node": "actor"})
        .sort_values(["event_count", "total_fatalities"], ascending=[False, False])
    )

    actor_nodes_overall = actor_nodes.merge(actor_participation, on="actor", how="left")

    event_nodes_overall = (
        df[df["event_id"].notna()][["event_id", "event_date", "phase", "country", "fatalities", "event_type", "sub_event_type"]]
        .drop_duplicates(subset=["event_id"])
        .rename(columns={"event_id": "event_node"})
        .reset_index(drop=True)
    )
    event_nodes_overall["node_type"] = "event"

    # ---------------------------
    # SAVE
    # ---------------------------
    actor_actor_edges_overall.to_csv(OUTPUT_DIR / "actor_actor_edges_overall.csv", index=False)
    actor_actor_edges_by_phase.to_csv(OUTPUT_DIR / "actor_actor_edges_by_phase.csv", index=False)
    event_actor_bipartite_edges.to_csv(OUTPUT_DIR / "event_actor_bipartite_edges.csv", index=False)
    actor_nodes_overall.to_csv(OUTPUT_DIR / "actor_nodes_overall.csv", index=False)
    event_nodes_overall.to_csv(OUTPUT_DIR / "event_nodes_overall.csv", index=False)

    # ---------------------------
    # REPORT
    # ---------------------------
    print("\nPhase 4 complete.")
    print(f"Saved outputs to: {OUTPUT_DIR}")

    print("\nOutput sizes:")
    print(f"  actor_actor_edges_overall: {len(actor_actor_edges_overall):,}")
    print(f"  actor_actor_edges_by_phase: {len(actor_actor_edges_by_phase):,}")
    print(f"  event_actor_bipartite_edges: {len(event_actor_bipartite_edges):,}")
    print(f"  actor_nodes_overall: {len(actor_nodes_overall):,}")
    print(f"  event_nodes_overall: {len(event_nodes_overall):,}")

    print("\nSanity checks:")
    print(f"  Events with actor1+actor2 pairs: {len(actor_pairs):,}")
    print(f"  Unique phases in pair network: {actor_pairs['phase'].nunique(dropna=True)}")
    print(f"  Unique countries in pair network: {actor_pairs['country'].nunique(dropna=True)}")


if __name__ == "__main__":
    main()