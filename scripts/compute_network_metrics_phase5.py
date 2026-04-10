from pathlib import Path
import pandas as pd
import networkx as nx


# ---------------------------
# CONFIG
# ---------------------------
EDGE_OVERALL_FILE = Path("output") / "network_outputs" / "actor_actor_edges_overall.csv"
EDGE_BY_PHASE_FILE = Path("output") / "network_outputs" / "actor_actor_edges_by_phase.csv"
OUTPUT_DIR = Path("output") / "network_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------
# HELPERS
# ---------------------------
def build_graph_from_edgelist(df: pd.DataFrame, source_col: str, target_col: str, weight_col: str):
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


def compute_graph_metrics(G: nx.Graph) -> tuple[pd.DataFrame, dict]:
    if G.number_of_nodes() == 0:
        return pd.DataFrame(), {}

    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G, weight="weight", normalized=True)

    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, weight="weight")
    except Exception:
        eigenvector_centrality = {node: pd.NA for node in G.nodes()}

    clustering_coefficient = nx.clustering(G, weight="weight")

    node_metrics = pd.DataFrame({
        "actor": list(G.nodes()),
        "degree": [G.degree(node) for node in G.nodes()],
        "weighted_degree": [G.degree(node, weight="weight") for node in G.nodes()],
        "degree_centrality": [degree_centrality.get(node, pd.NA) for node in G.nodes()],
        "betweenness_centrality": [betweenness_centrality.get(node, pd.NA) for node in G.nodes()],
        "eigenvector_centrality": [eigenvector_centrality.get(node, pd.NA) for node in G.nodes()],
        "clustering_coefficient": [clustering_coefficient.get(node, pd.NA) for node in G.nodes()],
    }).sort_values(
        by=["betweenness_centrality", "weighted_degree", "degree"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    components = list(nx.connected_components(G))
    largest_component_size = max((len(c) for c in components), default=0)

    graph_summary = {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": nx.density(G),
        "connected_components": nx.number_connected_components(G),
        "largest_component_size": largest_component_size,
        "average_clustering": nx.average_clustering(G, weight="weight"),
    }

    return node_metrics, graph_summary


def main():
    if not EDGE_OVERALL_FILE.exists():
        raise FileNotFoundError(f"Missing file: {EDGE_OVERALL_FILE}")
    if not EDGE_BY_PHASE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {EDGE_BY_PHASE_FILE}")

    overall_edges = pd.read_csv(EDGE_OVERALL_FILE, low_memory=False)
    phase_edges = pd.read_csv(EDGE_BY_PHASE_FILE, low_memory=False)

    print(f"Loaded overall edge rows: {len(overall_edges):,}")
    print(f"Loaded phase edge rows: {len(phase_edges):,}")

    # ---------------------------
    # OVERALL GRAPH
    # ---------------------------
    print("\nComputing overall network metrics...")
    G_overall = build_graph_from_edgelist(overall_edges, "node_u", "node_v", "event_count")
    overall_node_metrics, overall_summary = compute_graph_metrics(G_overall)

    overall_node_metrics.to_csv(OUTPUT_DIR / "actor_network_node_metrics_overall.csv", index=False)
    pd.DataFrame([overall_summary]).to_csv(OUTPUT_DIR / "actor_network_summary_overall.csv", index=False)

    # ---------------------------
    # PHASE-WISE GRAPHS
    # ---------------------------
    phase_node_metrics_list = []
    phase_summary_list = []

    print("\nComputing phase-wise network metrics...")
    for phase in sorted(phase_edges["phase"].dropna().unique()):
        phase_df = phase_edges[phase_edges["phase"] == phase].copy()
        G_phase = build_graph_from_edgelist(phase_df, "node_u", "node_v", "event_count")

        node_metrics, summary = compute_graph_metrics(G_phase)
        if not node_metrics.empty:
            node_metrics["phase"] = phase
            phase_node_metrics_list.append(node_metrics)

        summary["phase"] = phase
        phase_summary_list.append(summary)

        print(f"  {phase}: nodes={summary['nodes']}, edges={summary['edges']}")

    actor_network_node_metrics_by_phase = pd.concat(phase_node_metrics_list, ignore_index=True)
    actor_network_summary_by_phase = pd.DataFrame(phase_summary_list)

    actor_network_node_metrics_by_phase.to_csv(
        OUTPUT_DIR / "actor_network_node_metrics_by_phase.csv",
        index=False
    )
    actor_network_summary_by_phase.to_csv(
        OUTPUT_DIR / "actor_network_summary_by_phase.csv",
        index=False
    )

    # ---------------------------
    # REPORT
    # ---------------------------
    print("\nPhase 5 complete.")
    print(f"Saved outputs to: {OUTPUT_DIR}")

    print("\nOverall network summary:")
    for k, v in overall_summary.items():
        print(f"  {k}: {v}")

    print("\nTop 10 actors by betweenness centrality (overall):")
    print(
        overall_node_metrics[
            ["actor", "degree", "weighted_degree", "betweenness_centrality", "eigenvector_centrality"]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()