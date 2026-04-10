from pathlib import Path
import pandas as pd
import networkx as nx
import community as community_louvain


# ---------------------------
# CONFIG
# ---------------------------
EDGE_OVERALL_FILE = Path("output") / "network_outputs" / "actor_actor_edges_overall.csv"
EDGE_BY_PHASE_FILE = Path("output") / "network_outputs" / "actor_actor_edges_by_phase.csv"
NODE_METRICS_OVERALL_FILE = Path("output") / "network_outputs" / "actor_network_node_metrics_overall.csv"
NODE_METRICS_BY_PHASE_FILE = Path("output") / "network_outputs" / "actor_network_node_metrics_by_phase.csv"

OUTPUT_DIR = Path("output") / "network_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GENERIC_PATTERNS = [
    "civilians",
    "unidentified armed group",
    "unidentified military forces",
    "unidentified communal militia",
    "unidentified gang",
    "unidentified protesters",
    "unidentified rioters",
    "unidentified ethnic militia",
    "unidentified tribal militia",
    "unidentified separatists",
]


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


def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )


def is_generic_actor(series: pd.Series) -> pd.Series:
    pattern = "|".join(
        pd.Series(GENERIC_PATTERNS)
        .str.replace(r"([.^$*+?{}\[\]\\|()])", r"\\\1", regex=True)
        .tolist()
    )
    return normalize_text(series).str.contains(pattern, regex=True, na=False)


def build_graph(df: pd.DataFrame, source_col: str, target_col: str, weight_col: str) -> nx.Graph:
    G = nx.Graph()
    for _, row in df.iterrows():
        u = row[source_col]
        v = row[target_col]
        w = row[weight_col]

        if pd.isna(u) or pd.isna(v):
            continue
        if u == v:
            continue

        G.add_edge(u, v, weight=float(w) if pd.notna(w) else 1.0)

    return G


def add_community_labels(edge_df: pd.DataFrame, node_metrics_df: pd.DataFrame, phase_value=None):
    G = build_graph(edge_df, "node_u", "node_v", "event_count")

    if G.number_of_nodes() == 0:
        return pd.DataFrame(), pd.DataFrame(), {}

    partition = community_louvain.best_partition(G, weight="weight", random_state=42)

    node_comm_df = pd.DataFrame({
        "actor": list(partition.keys()),
        "community_id": list(partition.values())
    })

    if phase_value is not None:
        node_comm_df["phase"] = phase_value

    enriched = node_metrics_df.merge(node_comm_df, on=[c for c in node_comm_df.columns if c in node_metrics_df.columns or c == "actor"], how="left")

    community_summary = (
        enriched.groupby("community_id", dropna=False)
        .agg(
            actor_count=("actor", "nunique"),
            avg_degree=("degree", "mean"),
            avg_weighted_degree=("weighted_degree", "mean"),
            avg_betweenness=("betweenness_centrality", "mean"),
            total_weighted_degree=("weighted_degree", "sum"),
        )
        .reset_index()
        .sort_values(["actor_count", "total_weighted_degree"], ascending=[False, False])
    )

    if phase_value is not None:
        community_summary["phase"] = phase_value

    modularity = community_louvain.modularity(partition, G, weight="weight")

    return enriched, community_summary, {
        "phase": phase_value if phase_value is not None else "Overall",
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "communities": int(node_comm_df["community_id"].nunique()),
        "modularity": modularity,
    }


def compute_bridge_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Higher betweenness + multi-community context + higher degree = stronger bridge intuition
    community_sizes = out.groupby("community_id")["actor"].transform("count")
    out["community_size"] = community_sizes

    out["bridge_score"] = (
        out["betweenness_centrality"].fillna(0) * 0.6
        + out["degree_centrality"].fillna(0) * 0.2
        + (
            out["weighted_degree"].fillna(0) / max(out["weighted_degree"].fillna(0).max(), 1)
        ) * 0.2
    )

    out = out.sort_values(
        ["bridge_score", "betweenness_centrality", "weighted_degree", "degree"],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)

    return out


def top_actors_per_community(df: pd.DataFrame, top_n=10) -> pd.DataFrame:
    ranked = df.sort_values(
        ["community_id", "weighted_degree", "betweenness_centrality", "degree"],
        ascending=[True, False, False, False]
    ).copy()
    ranked["rank_in_community"] = ranked.groupby("community_id").cumcount() + 1
    return ranked[ranked["rank_in_community"] <= top_n].reset_index(drop=True)


# ---------------------------
# MAIN
# ---------------------------
def main():
    required_files = [
        EDGE_OVERALL_FILE,
        EDGE_BY_PHASE_FILE,
        NODE_METRICS_OVERALL_FILE,
        NODE_METRICS_BY_PHASE_FILE,
    ]
    for path in required_files:
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    edge_overall = pd.read_csv(EDGE_OVERALL_FILE, low_memory=False)
    edge_by_phase = pd.read_csv(EDGE_BY_PHASE_FILE, low_memory=False)
    node_metrics_overall = pd.read_csv(NODE_METRICS_OVERALL_FILE, low_memory=False)
    node_metrics_by_phase = pd.read_csv(NODE_METRICS_BY_PHASE_FILE, low_memory=False)

    # Clean actor fields
    for df in [edge_overall, edge_by_phase, node_metrics_overall, node_metrics_by_phase]:
        for col in df.columns:
            if "actor" in col or "node_" in col or col == "phase":
                df[col] = clean_text(df[col])

    print(f"Loaded overall edges: {len(edge_overall):,}")
    print(f"Loaded phase edges: {len(edge_by_phase):,}")
    print(f"Loaded overall node metrics: {len(node_metrics_overall):,}")
    print(f"Loaded phase node metrics: {len(node_metrics_by_phase):,}")

    # ---------------------------
    # OVERALL COMMUNITY DETECTION
    # ---------------------------
    print("\nComputing overall communities...")
    overall_nodes_with_communities, overall_community_summary, overall_modularity_summary = add_community_labels(
        edge_overall,
        node_metrics_overall
    )

    overall_bridge = compute_bridge_scores(overall_nodes_with_communities)
    overall_bridge["is_generic_actor"] = is_generic_actor(overall_bridge["actor"])

    overall_bridge_filtered = overall_bridge[~overall_bridge["is_generic_actor"]].copy()

    overall_top_per_community = top_actors_per_community(overall_nodes_with_communities, top_n=10)

    # ---------------------------
    # PHASE-WISE COMMUNITY DETECTION
    # ---------------------------
    print("\nComputing phase-wise communities...")
    phase_nodes_list = []
    phase_community_summary_list = []
    phase_modularity_list = []
    phase_bridge_list = []
    phase_bridge_filtered_list = []
    phase_top_per_community_list = []

    for phase in sorted(edge_by_phase["phase"].dropna().unique()):
        print(f"  Processing {phase} ...")
        phase_edge_df = edge_by_phase[edge_by_phase["phase"] == phase].copy()
        phase_node_df = node_metrics_by_phase[node_metrics_by_phase["phase"] == phase].copy()

        nodes_with_communities, community_summary, modularity_summary = add_community_labels(
            phase_edge_df,
            phase_node_df,
            phase_value=phase
        )

        if len(nodes_with_communities) == 0:
            continue

        bridge_df = compute_bridge_scores(nodes_with_communities)
        bridge_df["phase"] = phase
        bridge_df["is_generic_actor"] = is_generic_actor(bridge_df["actor"])

        bridge_filtered_df = bridge_df[~bridge_df["is_generic_actor"]].copy()

        top_comm_df = top_actors_per_community(nodes_with_communities, top_n=10)
        top_comm_df["phase"] = phase

        phase_nodes_list.append(nodes_with_communities)
        phase_community_summary_list.append(community_summary)
        phase_modularity_list.append(modularity_summary)
        phase_bridge_list.append(bridge_df)
        phase_bridge_filtered_list.append(bridge_filtered_df)
        phase_top_per_community_list.append(top_comm_df)

    phase_nodes_with_communities = pd.concat(phase_nodes_list, ignore_index=True)
    phase_community_summary = pd.concat(phase_community_summary_list, ignore_index=True)
    phase_modularity_summary = pd.DataFrame(phase_modularity_list)
    phase_bridge = pd.concat(phase_bridge_list, ignore_index=True)
    phase_bridge_filtered = pd.concat(phase_bridge_filtered_list, ignore_index=True)
    phase_top_per_community = pd.concat(phase_top_per_community_list, ignore_index=True)

    # ---------------------------
    # SAVE OUTPUTS
    # ---------------------------
    overall_nodes_with_communities.to_csv(
        OUTPUT_DIR / "actor_communities_overall.csv", index=False
    )
    overall_community_summary.to_csv(
        OUTPUT_DIR / "actor_community_summary_overall.csv", index=False
    )
    pd.DataFrame([overall_modularity_summary]).to_csv(
        OUTPUT_DIR / "actor_community_modularity_overall.csv", index=False
    )
    overall_bridge.to_csv(
        OUTPUT_DIR / "bridge_actors_overall.csv", index=False
    )
    overall_bridge_filtered.to_csv(
        OUTPUT_DIR / "bridge_actors_overall_filtered.csv", index=False
    )
    overall_top_per_community.to_csv(
        OUTPUT_DIR / "top_actors_per_community_overall.csv", index=False
    )

    phase_nodes_with_communities.to_csv(
        OUTPUT_DIR / "actor_communities_by_phase.csv", index=False
    )
    phase_community_summary.to_csv(
        OUTPUT_DIR / "actor_community_summary_by_phase.csv", index=False
    )
    phase_modularity_summary.to_csv(
        OUTPUT_DIR / "actor_community_modularity_by_phase.csv", index=False
    )
    phase_bridge.to_csv(
        OUTPUT_DIR / "bridge_actors_by_phase.csv", index=False
    )
    phase_bridge_filtered.to_csv(
        OUTPUT_DIR / "bridge_actors_by_phase_filtered.csv", index=False
    )
    phase_top_per_community.to_csv(
        OUTPUT_DIR / "top_actors_per_community_by_phase.csv", index=False
    )

    # ---------------------------
    # REPORT
    # ---------------------------
    print("\nPhase 6 complete.")
    print(f"Saved outputs to: {OUTPUT_DIR}")

    print("\nOverall community summary:")
    print(f"  communities: {overall_modularity_summary['communities']}")
    print(f"  modularity: {overall_modularity_summary['modularity']:.6f}")

    print("\nTop 10 bridge actors overall:")
    print(
        overall_bridge[
            ["actor", "community_id", "degree", "weighted_degree", "betweenness_centrality", "bridge_score"]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 filtered bridge actors overall:")
    print(
        overall_bridge_filtered[
            ["actor", "community_id", "degree", "weighted_degree", "betweenness_centrality", "bridge_score"]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nPhase-wise modularity summary:")
    print(phase_modularity_summary.to_string(index=False))


if __name__ == "__main__":
    main()