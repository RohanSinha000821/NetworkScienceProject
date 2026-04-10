from pathlib import Path
import pandas as pd


# ---------------------------
# CONFIG
# ---------------------------
NETWORK_DIR = Path("output") / "network_outputs"
OUTPUT_DIR = NETWORK_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PHASE_SUMMARY_FILE = NETWORK_DIR / "actor_network_summary_by_phase.csv"
PHASE_NODE_METRICS_FILE = NETWORK_DIR / "actor_network_node_metrics_by_phase.csv"
PHASE_MODULARITY_FILE = NETWORK_DIR / "actor_community_modularity_by_phase.csv"
PHASE_BRIDGE_FILE = NETWORK_DIR / "bridge_actors_by_phase_filtered.csv"
OVERALL_BRIDGE_FILE = NETWORK_DIR / "bridge_actors_overall_filtered.csv"
TOP_COMMUNITY_FILE = NETWORK_DIR / "top_actors_per_community_by_phase.csv"


# Extend this list if needed after seeing actor names in your outputs
EXCLUDE_PATTERNS = [
    "civilians",
    "unidentified",
    "rioters",
    "protesters",
    "demonstrators",
    "mob",
    "students",
    "villagers",
    "residents",
    "locals",
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


def exclude_generic(series: pd.Series) -> pd.Series:
    pattern = "|".join(
        pd.Series(EXCLUDE_PATTERNS)
        .str.replace(r"([.^$*+?{}\[\]\\|()])", r"\\\1", regex=True)
        .tolist()
    )
    return normalize_text(series).str.contains(pattern, regex=True, na=False)


def main():
    required_files = [
        PHASE_SUMMARY_FILE,
        PHASE_NODE_METRICS_FILE,
        PHASE_MODULARITY_FILE,
        PHASE_BRIDGE_FILE,
        OVERALL_BRIDGE_FILE,
        TOP_COMMUNITY_FILE,
    ]
    for path in required_files:
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    phase_summary = pd.read_csv(PHASE_SUMMARY_FILE, low_memory=False)
    phase_node_metrics = pd.read_csv(PHASE_NODE_METRICS_FILE, low_memory=False)
    phase_modularity = pd.read_csv(PHASE_MODULARITY_FILE, low_memory=False)
    phase_bridge = pd.read_csv(PHASE_BRIDGE_FILE, low_memory=False)
    overall_bridge = pd.read_csv(OVERALL_BRIDGE_FILE, low_memory=False)
    top_community = pd.read_csv(TOP_COMMUNITY_FILE, low_memory=False)

    print(f"Loaded phase summary rows: {len(phase_summary):,}")
    print(f"Loaded phase node metrics rows: {len(phase_node_metrics):,}")
    print(f"Loaded phase modularity rows: {len(phase_modularity):,}")
    print(f"Loaded phase bridge rows: {len(phase_bridge):,}")
    print(f"Loaded overall bridge rows: {len(overall_bridge):,}")
    print(f"Loaded top community rows: {len(top_community):,}")

    # ---------------------------
    # 1. Phase comparison table
    # ---------------------------
    phase_compare = phase_summary.merge(
        phase_modularity[["phase", "communities", "modularity"]],
        on="phase",
        how="left"
    )

    # Top actor stats by phase
    top_degree = (
        phase_node_metrics.sort_values(["phase", "weighted_degree", "degree"], ascending=[True, False, False])
        .groupby("phase")
        .first()
        .reset_index()[["phase", "actor", "weighted_degree", "betweenness_centrality"]]
        .rename(columns={
            "actor": "top_weighted_degree_actor",
            "weighted_degree": "top_weighted_degree_value",
            "betweenness_centrality": "top_weighted_degree_actor_betweenness"
        })
    )

    top_bridge = (
        phase_bridge[~exclude_generic(phase_bridge["actor"])]
        .sort_values(["phase", "bridge_score", "betweenness_centrality"], ascending=[True, False, False])
        .groupby("phase")
        .first()
        .reset_index()[["phase", "actor", "bridge_score", "betweenness_centrality"]]
        .rename(columns={
            "actor": "top_bridge_actor",
            "bridge_score": "top_bridge_score",
            "betweenness_centrality": "top_bridge_betweenness"
        })
    )

    phase_compare = phase_compare.merge(top_degree, on="phase", how="left")
    phase_compare = phase_compare.merge(top_bridge, on="phase", how="left")

    # Order phases explicitly
    phase_order = {"Phase 1": 1, "Phase 2": 2, "Phase 3": 3}
    phase_compare["phase_order"] = phase_compare["phase"].map(phase_order)
    phase_compare = phase_compare.sort_values("phase_order").drop(columns=["phase_order"])

    # ---------------------------
    # 2. Cleaned bridge tables
    # ---------------------------
    overall_bridge_cleaned = overall_bridge[~exclude_generic(overall_bridge["actor"])].copy()
    overall_bridge_cleaned = overall_bridge_cleaned.sort_values(
        ["bridge_score", "betweenness_centrality", "weighted_degree"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    phase_bridge_cleaned = phase_bridge[~exclude_generic(phase_bridge["actor"])].copy()
    phase_bridge_cleaned = phase_bridge_cleaned.sort_values(
        ["phase", "bridge_score", "betweenness_centrality", "weighted_degree"],
        ascending=[True, False, False, False]
    ).reset_index(drop=True)

    top10_bridge_by_phase = (
        phase_bridge_cleaned.groupby("phase", group_keys=False)
        .head(10)
        .reset_index(drop=True)
    )

    # ---------------------------
    # 3. Top actors per community by phase
    # ---------------------------
    top_community_cleaned = top_community[~exclude_generic(top_community["actor"])].copy()
    top_community_cleaned = top_community_cleaned.sort_values(
        ["phase", "community_id", "rank_in_community"]
    ).reset_index(drop=True)

    # ---------------------------
    # 4. Report-ready highlights table
    # ---------------------------
    highlights_rows = []

    for _, row in phase_compare.iterrows():
        highlights_rows.append({
            "phase": row["phase"],
            "nodes": row["nodes"],
            "edges": row["edges"],
            "density": row["density"],
            "connected_components": row["connected_components"],
            "largest_component_size": row["largest_component_size"],
            "average_clustering": row["average_clustering"],
            "communities": row["communities"],
            "modularity": row["modularity"],
            "top_bridge_actor": row["top_bridge_actor"],
            "top_bridge_score": row["top_bridge_score"],
            "top_weighted_degree_actor": row["top_weighted_degree_actor"],
            "top_weighted_degree_value": row["top_weighted_degree_value"],
        })

    report_highlights = pd.DataFrame(highlights_rows)

    # ---------------------------
    # SAVE
    # ---------------------------
    phase_compare.to_csv(OUTPUT_DIR / "phase_comparison_table.csv", index=False)
    overall_bridge_cleaned.to_csv(OUTPUT_DIR / "bridge_actors_overall_cleaned.csv", index=False)
    phase_bridge_cleaned.to_csv(OUTPUT_DIR / "bridge_actors_by_phase_cleaned.csv", index=False)
    top10_bridge_by_phase.to_csv(OUTPUT_DIR / "top10_bridge_actors_by_phase.csv", index=False)
    top_community_cleaned.to_csv(OUTPUT_DIR / "top_actors_per_community_by_phase_cleaned.csv", index=False)
    report_highlights.to_csv(OUTPUT_DIR / "report_highlights_table.csv", index=False)

    # ---------------------------
    # REPORT
    # ---------------------------
    print("\nPhase 7 complete.")
    print(f"Saved outputs to: {OUTPUT_DIR}")

    print("\nPhase comparison table:")
    print(phase_compare.to_string(index=False))

    print("\nTop 10 overall cleaned bridge actors:")
    print(
        overall_bridge_cleaned[
            ["actor", "community_id", "degree", "weighted_degree", "betweenness_centrality", "bridge_score"]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 bridge actors by phase:")
    print(
        top10_bridge_by_phase[
            ["phase", "actor", "community_id", "degree", "weighted_degree", "betweenness_centrality", "bridge_score"]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()