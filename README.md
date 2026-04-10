# NetworkScienceProject

A reproducible network-science workflow for studying the structural evolution of the **US–Israel–Iran conflict system** through event data, actor interaction networks, community structure, and bridge-actor analysis.

This repository combines **ACLED** and **UCDP GED** event data, harmonizes them into a common schema, filters the study to the core regional theater, segments the timeline into analytically meaningful phases, and builds network outputs suitable for quantitative analysis and visualization.

---

## 1. Project overview

The project asks a structural question:

> **How did the present regional conflict configuration emerge?**

Instead of treating the present escalation as an isolated event, the workflow models the conflict system as an evolving network of actors across multiple theaters. The analysis focuses on:

- actor interaction structure,
- temporal expansion of the conflict system,
- community formation and fragmentation,
- bridge actors connecting otherwise distinct communities,
- phase-wise differences between earlier and current escalation patterns.

The study uses a **multi-source event-data pipeline**:

- **ACLED** for broad historical event coverage and actor-pair structure,
- **UCDP GED** releases for extension into the 2025–2026 period.

---

## 2. Research goals

The repository is organized around five analytical goals:

1. **Harmonize** ACLED and GED into a consistent event schema.
2. **Filter** the dataset to the core theater:
   - Israel
   - Palestine
   - Lebanon
   - Syria
   - Iraq
   - Yemen
   - Iran
   - United States
3. **Segment** the event stream into three phases:
   - **Phase 1:** 2015–2018 — Transitional Shadow Phase
   - **Phase 2:** 2019–2021 — Escalatory Hybrid Phase
   - **Phase 3:** 2022–2026 — Current Escalation Phase
4. **Build actor networks** and derive graph metrics.
5. **Interpret structural change** using centrality, modularity, communities, and bridge actors.

---

## 3. Repository structure

### Current repository layout

```text
NetworkScienceProject/
├── configs/
│   └── config.yaml
├── data/
│   └── (raw and intermediate datasets)
├── notebooks/
│   └── 01_diagnostic_checkpoint.ipynb
├── src/
│   ├── __init__.py
│   ├── analysis/
│   │   └── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── apply_actor_dictionary.py
│   │   ├── audit.py
│   │   ├── build_core_actor_review.py
│   │   ├── build_cross_theater_features_v2.py
│   │   ├── explode_actor_tokens.py
│   │   ├── feature_engineering.py
│   │   ├── load_data.py
│   │   ├── reconstruct_events.py
│   │   ├── scope_filter.py
│   │   ├── scope_filter_refined.py
│   │   └── standardize_actors.py
│   ├── networks/
│   │   ├── __init__.py
│   │   ├── build_multiplex_layers.py
│   │   └── compute_network_metrics.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── .gitattributes
├── .gitignore
├── README.md
└── requirements.txt
```

### What each top-level directory does

#### `configs/`
Contains runtime configuration, dataset locations, thresholds, and experiment settings.

#### `data/`
Stores raw source data and intermediate tabular outputs.
Typical contents during local work include:
- raw ACLED export,
- GED release files,
- harmonized merged files,
- filtered scope files,
- phase-segmented files.

#### `notebooks/`
Notebook-first diagnostics and presentation workflow.
Use this folder for:
- exploratory checks,
- stepwise validation,
- polished presentation notebooks,
- report figure generation.

#### `src/data/`
Data engineering and preprocessing logic:
- loading source files,
- actor cleaning,
- filtering,
- reconstruction,
- feature engineering,
- event standardization.

#### `src/networks/`
Network-construction and metric-computation logic:
- edge construction,
- multiplex layer construction,
- graph statistics.

#### `src/analysis/`
Reserved for higher-level analytical logic and experiment orchestration.

#### `src/utils/`
Reusable helper functions shared across the project.

---

## 4. Expected local working structure

When running the full workflow locally, it is useful to maintain a working structure like this:

```text
NetworkScienceProject/
├── configs/
├── data/
│   ├── ACLED Data_2026-04-10.csv
│   ├── GEDEvent_v25_01_25_12.csv
│   ├── GEDEvent_v26_0_1.csv
│   └── GEDEvent_v26_0_2.csv
├── notebooks/
│   ├── 01_diagnostic_checkpoint.ipynb
│   ├── conflict_network_visualization_workflow.ipynb
│   ├── NxS_Project_Polished_Visuals.ipynb
│   └── NxS_Project_Presentation_Visuals_Enhanced.ipynb
├── output/
│   ├── project_ready_conflict_harmonized_v2.csv
│   ├── conflict_filtered_phase2_core_v2.csv
│   ├── conflict_phase3_segmented_v2.csv
│   ├── network_outputs/
│   │   ├── actor_actor_edges_overall.csv
│   │   ├── actor_actor_edges_by_phase.csv
│   │   ├── event_actor_bipartite_edges.csv
│   │   ├── actor_network_node_metrics_overall.csv
│   │   ├── actor_network_node_metrics_by_phase.csv
│   │   ├── actor_network_summary_overall.csv
│   │   ├── actor_network_summary_by_phase.csv
│   │   ├── actor_communities_overall.csv
│   │   ├── actor_communities_by_phase.csv
│   │   ├── bridge_actors_overall_cleaned.csv
│   │   ├── bridge_actors_by_phase_cleaned.csv
│   │   └── ...
│   └── presentation_plots/
├── src/
└── requirements.txt
```

The `output/` directory is not required to exist before the first run; it is created as the pipeline executes.

---

## 5. Data sources

This project relies on conflict event data from:

- **ACLED** for coded event records and actor interaction fields,
- **UCDP GED** releases for event continuity into 2025–2026.

### Local input files used in the current workflow

The local analysis described in this repository used:

- `ACLED Data_2026-04-10.csv`
- `GEDEvent_v25_01_25_12.csv`
- `GEDEvent_v26_0_1.csv`
- `GEDEvent_v26_0_2.csv`


---

## 6. Processing pipeline

The full workflow follows these stages.

### Phase 1 — Harmonization
ACLED and GED are mapped into a unified schema with consistent names for:
- event ID,
- event date,
- actor fields,
- geographic fields,
- fatalities,
- notes,
- event-type fields,
- provenance metadata.

Key point:
- the revised ACLED export includes native `actor2`, `assoc_actor_2`, and `inter2`,
  which makes actor–actor analysis methodologically stronger than the earlier proxy-based version.

### Phase 2 — Scope filtering
The harmonized dataset is restricted to the core theater:

- Israel
- Palestine
- Lebanon
- Syria
- Iraq
- Yemen
- Iran
- United States

This creates the **main analysis dataset** used for the reported results.

### Phase 3 — Phase segmentation
Rows are labeled by historical phase:

- **Phase 1:** 2015–2018  
- **Phase 2:** 2019–2021  
- **Phase 3:** 2022–2026  

This enables phase-wise network comparison.

### Phase 4 — Network construction
The pipeline builds:

- **actor–actor edge lists**
- **event–actor bipartite edge lists**
- **phase-wise actor–actor networks**

### Phase 5 — Network metrics
Graph metrics are computed, including:

- degree,
- weighted degree,
- degree centrality,
- betweenness centrality,
- eigenvector centrality,
- clustering coefficient,
- density,
- connected components,
- largest connected component size.

### Phase 6 — Community and bridge-actor analysis
Community structure is detected using **Louvain modularity optimization**, followed by bridge-actor ranking.

### Phase 7 — Report-ready outputs
Phase-wise comparison tables, cleaned bridge-actor tables, and presentation-ready figures are generated.

---

## 7. Main results snapshot

The current strict core-theater analysis produced a phase-segmented dataset of **546,300 events**.

### Actor–actor network growth across phases

| Phase | Nodes | Edges | Communities | Connected Components | Largest Component | Density | Modularity |
|------|------:|------:|------------:|---------------------:|------------------:|--------:|-----------:|
| Phase 1 | 754 | 1,893 | 54 | 48 | 652 | 0.006668 | 0.640777 |
| Phase 2 | 1,111 | 2,455 | 125 | 107 | 883 | 0.003981 | 0.727473 |
| Phase 3 | 1,628 | 3,363 | 179 | 156 | 1,290 | 0.002539 | 0.693744 |

### Overall network summary

- **Nodes:** 2,520
- **Edges:** 6,145
- **Connected components:** 221
- **Largest connected component:** 2,024 nodes
- **Density:** 0.001936
- **Average clustering:** 0.000136
- **Communities (overall):** 253
- **Overall modularity:** 0.714908

### Interpreting these results

The main structural trend is clear:

- the conflict system **expands** strongly from Phase 1 to Phase 3,
- the number of communities increases substantially,
- density decreases over time, indicating **expansion and fragmentation** rather than convergence into one dense block,
- modularity remains high across all phases, showing a persistent **community/bloc structure**.

### Top bridge actors (overall, cleaned)

The cleaned bridge-actor list is dominated by actors with cross-theater or structurally linking roles, including:

- Islamic State in Iraq and the Levant (ISIL)
- Military Forces of Yemen (2017–) Houthi
- Military Forces of Israel (2022–)
- Military Forces of Syria (2000–2024)
- Military Forces of Turkey (2016–)
- Syrian Democratic Forces
- PKK
- Hadi-aligned Yemeni forces

### Top bridge actor by phase

- **Phase 1:** ISIL
- **Phase 2:** Military Forces of Yemen (2017–) Houthi
- **Phase 3:** Military Forces of Israel (2022–)

This phase shift is one of the central substantive findings of the project.

---

## 8. How to clone and run locally

### Step 1 — Clone the repository

```bash
git clone https://github.com/RohanSinha000821/NetworkScienceProject.git
cd NetworkScienceProject
```

### Step 2 — Create and activate a virtual environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Add raw input data

Place the required CSV files inside the `data/` directory:

```text
data/
├── ACLED Data_2026-04-10.csv
├── GEDEvent_v25_01_25_12.csv
├── GEDEvent_v26_0_1.csv
└── GEDEvent_v26_0_2.csv
```

### Step 5 — Launch Jupyter

```bash
jupyter lab
```

or

```bash
jupyter notebook
```

### Step 6 — Run the notebook(s)

Start with:

```text
notebooks/01_diagnostic_checkpoint.ipynb
```

If you have the presentation notebooks locally, run them from the same repository root so all relative paths resolve correctly.

---

## 9. Recommended local execution order

For reproducible end-to-end execution, the recommended order is:

1. **Diagnostic notebook**
   - verify data availability and schema,
   - confirm that paths in `config.yaml` are correct.

2. **Harmonization**
   - merge ACLED and GED into a common format.

3. **Scope filtering**
   - restrict to the strict core-theater dataset.

4. **Phase segmentation**
   - create phase labels.

5. **Network construction**
   - build overall and phase-wise edge lists.

6. **Metric computation**
   - compute node-level and graph-level network statistics.

7. **Community + bridge analysis**
   - detect communities and rank bridge actors.

8. **Visualization notebooks**
   - create presentation-quality plots.

---

## 10. Configuration notes

The repository includes:

```text
configs/config.yaml
```

Use this file for:
- raw data paths,
- output paths,
- filtering thresholds,
- notebook/runtime parameters.

If you move datasets or change local folder names, update the configuration accordingly.

---

## 11. Reproducibility notes

To keep the analysis reproducible:

- use the same raw ACLED and GED files throughout one run,
- keep a consistent `data/` structure,
- do not mix old harmonized outputs with new ACLED exports,
- regenerate all downstream outputs whenever the ACLED source file changes,
- keep notebook execution order fixed.

---

## 12. Typical generated outputs

After a successful run, you should expect outputs such as:

### Tabular outputs
- harmonized event dataset,
- strict filtered core-theater dataset,
- phase-segmented dataset,
- actor–actor edge lists,
- bipartite event–actor edge lists,
- network metric tables,
- community assignments,
- bridge-actor rankings,
- report-ready comparison tables.

### Visual outputs
- source-data composition plots,
- preprocessing retention plots,
- country and phase composition charts,
- network growth plots,
- bridge-actor charts,
- community distribution charts,
- phase-wise network visualizations.

---

## 13. Future extensions

The repository can be extended in several directions:

- richer event reconstruction for cross-theater linkages,
- multiplex or multilayer network analysis,
- geographic overlays and map-based visualization,
- temporal cascade networks,
- robustness checks under alternative actor dictionaries,
- community-comparison methods beyond Louvain,
- more formal hypothesis testing on phase transitions.