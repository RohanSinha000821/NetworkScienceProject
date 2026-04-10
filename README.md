# NXS PROJECT

A reproducible network-science workflow for analyzing the structural evolution of the **US–Israel–Iran regional conflict system** using event data, actor–actor networks, community detection, bridge-actor analysis, and presentation-ready notebook visualizations.

This project integrates **ACLED** and **UCDP GED** event data, harmonizes them into a common schema, filters the analysis to the core conflict theater, segments the timeline into three historical phases, and builds phase-wise network outputs suitable for quantitative analysis, visualization, and reporting.

---

## 1. Project objective

This project is designed to answer a structural question:

> **How did the present regional escalation emerge from earlier interaction patterns across the conflict system?**

Instead of analyzing the current situation as a single isolated conflict episode, the project models the region as an evolving **multi-actor network** across multiple connected theaters.

The main analytical focus is on:

- growth of the conflict interaction system over time,
- actor–actor interaction structure,
- community formation and fragmentation,
- bridge actors connecting otherwise separate blocs,
- differences between early, transitional, and current escalation phases.

---

## 2. Core analytical goals

The workflow is organized around these goals:

1. **Harmonize** ACLED and GED into one analysis-ready event schema.
2. **Filter** the harmonized data to the strict core theater:
   - Israel
   - Palestine
   - Lebanon
   - Syria
   - Iraq
   - Yemen
   - Iran
   - United States
3. **Segment** the data into three phases:
   - **Phase 1:** 2015–2018 — Transitional Shadow Phase
   - **Phase 2:** 2019–2021 — Escalatory Hybrid Phase
   - **Phase 3:** 2022–2026 — Current Escalation Phase
4. **Construct networks**:
   - actor–actor interaction network
   - event–actor bipartite network
   - phase-wise actor networks
5. **Compute graph metrics** and identify:
   - central actors
   - bridge actors
   - community structure
6. **Generate presentation-ready notebooks and visualizations**.

---

## 3. Project folder structure

The project currently uses the following local structure:

```text
NXS PROJECT/
├── data/
│   ├── ACLED Data_2026-04-10.csv
│   ├── GEDEvent_v25_01_25_12.csv
│   ├── GEDEvent_v26_0_1.csv
│   └── GEDEvent_v26_0_2.csv
├── output/
│   ├── network_outputs/
│   │   ├── actor_actor_edges_by_phase.csv
│   │   ├── actor_actor_edges_overall.csv
│   │   ├── actor_communities_by_phase.csv
│   │   ├── actor_communities_overall.csv
│   │   ├── actor_community_modularity_by_phase.csv
│   │   ├── actor_community_modularity_overall.csv
│   │   ├── actor_community_summary_by_phase.csv
│   │   ├── actor_community_summary_overall.csv
│   │   ├── actor_network_node_metrics_by_phase.csv
│   │   ├── actor_network_node_metrics_overall.csv
│   │   ├── actor_network_summary_by_phase.csv
│   │   ├── actor_network_summary_overall.csv
│   │   ├── actor_nodes_overall.csv
│   │   ├── bridge_actors_by_phase_cleaned.csv
│   │   ├── bridge_actors_by_phase_filtered.csv
│   │   ├── bridge_actors_by_phase.csv
│   │   ├── bridge_actors_overall_cleaned.csv
│   │   ├── bridge_actors_overall_filtered.csv
│   │   ├── bridge_actors_overall.csv
│   │   ├── event_actor_bipartite_edges.csv
│   │   ├── event_nodes_overall.csv
│   │   ├── phase_comparison_table.csv
│   │   ├── report_highlights_table.csv
│   │   ├── top_actors_per_community_by_phase_cleaned.csv
│   │   ├── top_actors_per_community_by_phase.csv
│   │   ├── top_actors_per_community_overall.csv
│   │   └── top10_bridge_actors_by_phase.csv
│   ├── presentation_plots/
│   ├── conflict_filtered_phase2_core_v2.csv
│   ├── conflict_phase3_segmented_v2.csv
│   └── project_ready_conflict_harmonized_v2.csv
├── scripts/
│   ├── add_phase_labels_v2.py
│   ├── build_networks_phase4.py
│   ├── community_bridge_phase6.py
│   ├── compute_network_metrics_phase5.py
│   ├── filter_conflict_scope_strict_v2.py
│   ├── harmonize_conflict_data_v2.py
│   └── phase7_report_tables.py
├── venv/
├── .gitattributes
├── .gitignore
├── conflict_network_visualization_workflow.ipynb
├── NxS_Project_Polished_Visuals.ipynb
├── NxS_Project_Presentation_Visuals_Enhanced.ipynb
├── README.md
└── requirements.txt
```

---

## 4. What each folder and file does

### `data/`
Stores the raw source datasets used in the project.

Files:
- `ACLED Data_2026-04-10.csv`  
  Main ACLED export containing native actor interaction fields such as `actor1`, `actor2`, `assoc_actor_1`, `assoc_actor_2`, `inter1`, and `inter2`.

- `GEDEvent_v25_01_25_12.csv`  
  GED event data for the 2025 release window.

- `GEDEvent_v26_0_1.csv`
- `GEDEvent_v26_0_2.csv`  
  GED event releases extending coverage into 2026.

These are the raw inputs for the harmonization pipeline.

---

### `scripts/`
Contains the full execution pipeline, organized phase by phase.

#### `harmonize_conflict_data_v2.py`
Phase 1. Reads ACLED + GED source files and creates the harmonized merged dataset:

- standardizes column names,
- preserves actor and geography fields,
- keeps provenance information,
- deduplicates overlapping GED events.

Output:
- `output/project_ready_conflict_harmonized_v2.csv`

#### `filter_conflict_scope_strict_v2.py`
Phase 2. Restricts the harmonized dataset to the strict core theater:

- Israel
- Palestine
- Lebanon
- Syria
- Iraq
- Yemen
- Iran
- United States

Output:
- `output/conflict_filtered_phase2_core_v2.csv`

#### `add_phase_labels_v2.py`
Phase 3. Adds:
- `phase`
- `phase_label`

using the three historical periods defined for the project.

Output:
- `output/conflict_phase3_segmented_v2.csv`

#### `build_networks_phase4.py`
Phase 4. Constructs the network-ready datasets:

- overall actor–actor edge list,
- phase-wise actor–actor edge list,
- event–actor bipartite edge list,
- actor node table,
- event node table.

Outputs go to:
- `output/network_outputs/`

#### `compute_network_metrics_phase5.py`
Phase 5. Computes network metrics, including:

- degree,
- weighted degree,
- degree centrality,
- betweenness centrality,
- eigenvector centrality,
- clustering coefficient,
- density,
- connected components,
- largest component size.

Outputs:
- network summaries
- node-metric tables

#### `community_bridge_phase6.py`
Phase 6. Performs:

- Louvain community detection,
- modularity calculation,
- community summaries,
- bridge-actor scoring,
- cleaned and filtered bridge-actor tables.

#### `phase7_report_tables.py`
Phase 7. Creates report-ready tables:

- phase comparison table,
- report highlights table,
- cleaned bridge-actor outputs,
- community summary tables.

---

### `output/`
Stores all generated outputs from the pipeline.

#### Main processed datasets
- `project_ready_conflict_harmonized_v2.csv`  
  Harmonized ACLED + GED merged dataset.

- `conflict_filtered_phase2_core_v2.csv`  
  Strictly filtered core-theater dataset.

- `conflict_phase3_segmented_v2.csv`  
  Final event-level dataset used for the phase-wise network analysis.

#### `output/network_outputs/`
Stores all network-analysis outputs.

Key files include:

##### Edge lists
- `actor_actor_edges_overall.csv`
- `actor_actor_edges_by_phase.csv`
- `event_actor_bipartite_edges.csv`

##### Node tables
- `actor_nodes_overall.csv`
- `event_nodes_overall.csv`

##### Network metrics
- `actor_network_node_metrics_overall.csv`
- `actor_network_node_metrics_by_phase.csv`
- `actor_network_summary_overall.csv`
- `actor_network_summary_by_phase.csv`

##### Community analysis
- `actor_communities_overall.csv`
- `actor_communities_by_phase.csv`
- `actor_community_modularity_overall.csv`
- `actor_community_modularity_by_phase.csv`
- `actor_community_summary_overall.csv`
- `actor_community_summary_by_phase.csv`

##### Bridge actor outputs
- `bridge_actors_overall.csv`
- `bridge_actors_overall_filtered.csv`
- `bridge_actors_overall_cleaned.csv`
- `bridge_actors_by_phase.csv`
- `bridge_actors_by_phase_filtered.csv`
- `bridge_actors_by_phase_cleaned.csv`
- `top10_bridge_actors_by_phase.csv`

##### Report-ready tables
- `phase_comparison_table.csv`
- `report_highlights_table.csv`
- `top_actors_per_community_overall.csv`
- `top_actors_per_community_by_phase.csv`
- `top_actors_per_community_by_phase_cleaned.csv`

#### `output/presentation_plots/`
Stores saved plots generated for presentations and reporting.

---

### Notebook files in project root

#### `conflict_network_visualization_workflow.ipynb`
Step-by-step workflow notebook used to present the full process:
- raw data,
- preprocessing,
- phase segmentation,
- network construction,
- metrics,
- communities,
- bridge actors.

#### `NxS_Project_Polished_Visuals.ipynb`
More presentation-oriented notebook with cleaner figures and summary visuals.

#### `NxS_Project_Presentation_Visuals_Enhanced.ipynb`
Most visualization-heavy notebook. Contains more colorful and denser plots for presentation and viva use.

---

### Environment and metadata files

#### `venv/`
Local Python virtual environment.

#### `requirements.txt`
Dependency list used to recreate the project environment.

#### `.gitignore`
Git ignore rules.

#### `.gitattributes`
Git attributes and file-handling metadata.

---

## 5. Data-processing pipeline

The project is executed in the following order.

### Phase 1 — Harmonization
Merge ACLED and GED into one standardized dataset.

Important details:
- uses real ACLED `actor2` and `assoc_actor_2`,
- keeps actor provenance and geography fields,
- resolves overlapping GED event IDs.

Output:
- `project_ready_conflict_harmonized_v2.csv`

### Phase 2 — Strict theater filtering
Restrict the study to the core theater countries only.

Output:
- `conflict_filtered_phase2_core_v2.csv`

### Phase 3 — Historical phase labeling
Assign each event to:
- Phase 1,
- Phase 2,
- Phase 3.

Output:
- `conflict_phase3_segmented_v2.csv`

### Phase 4 — Network construction
Build:
- actor–actor edge lists,
- event–actor bipartite edge lists,
- node tables.

### Phase 5 — Network metrics
Compute:
- degree,
- weighted degree,
- betweenness,
- eigenvector centrality,
- clustering,
- density,
- connected components.

### Phase 6 — Communities and bridge actors
Detect communities and rank bridge actors.

### Phase 7 — Report outputs
Create tables and cleaned outputs for interpretation and presentation.

---

## 6. Main results summary

The strict phase-segmented dataset used for the final analysis contains:

- **546,300 events**

### Phase-wise actor–actor network growth

| Phase | Nodes | Edges | Communities | Connected Components | Largest Component | Density | Modularity |
|------|------:|------:|------------:|---------------------:|------------------:|--------:|-----------:|
| Phase 1 | 754 | 1,893 | 54 | 48 | 652 | 0.006668 | 0.640777 |
| Phase 2 | 1,111 | 2,455 | 125 | 107 | 883 | 0.003981 | 0.727473 |
| Phase 3 | 1,628 | 3,363 | 179 | 156 | 1,290 | 0.002539 | 0.693744 |

### Overall network summary

- **Nodes:** 2,520
- **Edges:** 6,145
- **Connected components:** 221
- **Largest connected component:** 2,024
- **Density:** 0.001936
- **Average clustering:** 0.000136
- **Communities (overall):** 253
- **Overall modularity:** 0.714908

### Bridge-actor findings

#### Top bridge actor by phase
- **Phase 1:** Islamic State in Iraq and the Levant (ISIL)
- **Phase 2:** Military Forces of Yemen (2017–) Houthi
- **Phase 3:** Military Forces of Israel (2022–)

#### Overall cleaned bridge actors
The overall cleaned bridge list prominently includes:

- Islamic State in Iraq and the Levant (ISIL)
- Military Forces of Yemen (2017–) Houthi
- Military Forces of Israel (2022–)
- Military Forces of Syria (2000–2024)
- Military Forces of Turkey (2016–)
- Military Forces of Yemen (2012–2022) Hadi
- QSD / Syrian Democratic Forces
- PKK

### Structural interpretation
The network results show that:

- the conflict system grows substantially across phases,
- the number of communities rises sharply,
- density declines over time, indicating expansion with fragmentation,
- modularity remains high, showing persistent bloc structure,
- bridge actors shift over time from ISIL to Houthi forces to Israeli military forces.

This supports the argument that the present escalation emerged through a broader regional structural transformation rather than a single isolated trigger.

---

## 7. How to clone and run locally

Clone the repository:

```bash
git clone https://github.com/RohanSinha000821/NetworkScienceProject.git
cd NetworkScienceProject
```

---

## 8. Environment setup

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 9. Required input data

Place the raw datasets in the `data/` directory exactly like this:

```text
data/
├── ACLED Data_2026-04-10.csv
├── GEDEvent_v25_01_25_12.csv
├── GEDEvent_v26_0_1.csv
└── GEDEvent_v26_0_2.csv
```

These raw CSV files are required before running the scripts.

---

## 10. How to run the full pipeline

Run the scripts in this order from the project root.

### Step 1 — Harmonization
```bash
python scripts\harmonize_conflict_data_v2.py
```

### Step 2 — Strict filtering
```bash
python scripts\filter_conflict_scope_strict_v2.py
```

### Step 3 — Phase segmentation
```bash
python scripts\add_phase_labels_v2.py
```

### Step 4 — Network construction
```bash
python scripts\build_networks_phase4.py
```

### Step 5 — Network metrics
```bash
python scripts\compute_network_metrics_phase5.py
```

### Step 6 — Community and bridge analysis
```bash
python scripts\community_bridge_phase6.py
```

### Step 7 — Report-ready tables
```bash
python scripts\phase7_report_tables.py
```

After these steps, the main outputs will appear in:

- `output/`
- `output/network_outputs/`

---

## 11. Running the notebooks

You can launch Jupyter using:

```bash
jupyter notebook
```

or

```bash
jupyter lab
```

Then open one of the following root-level notebooks:

- `conflict_network_visualization_workflow.ipynb`
- `NxS_Project_Polished_Visuals.ipynb`
- `NxS_Project_Presentation_Visuals_Enhanced.ipynb`

### Recommended usage
- use `conflict_network_visualization_workflow.ipynb` to explain the full pipeline,
- use `NxS_Project_Polished_Visuals.ipynb` for cleaner presentation figures,
- use `NxS_Project_Presentation_Visuals_Enhanced.ipynb` for the most colorful and visually rich presentation flow.

---

## 12. Reproducibility notes

To keep the pipeline reproducible:

- do not mix outputs from old ACLED exports with new ones,
- regenerate downstream outputs whenever the ACLED source file changes,
- keep the raw file names and locations consistent,
- run the scripts in the order documented above,
- use the same environment and dependency versions whenever possible.

---

## 13. Requirements

The main Python stack includes:

- pandas
- matplotlib
- networkx
- python-louvain
- jupyter

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

## 14. Future extensions

Possible future extensions include:

- multiplex network analysis,
- temporal cascade networks,
- geo-spatial mapping,
- actor-dictionary refinement,
- stronger robustness checks across actor categories,
- additional policy-oriented visualization layers.