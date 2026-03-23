#!/usr/bin/env python3
"""
Visualize AI evaluation results using Plotly.

Reads evaluation JSONL files from evaluations/ai/ and generates a
self-contained HTML dashboard with three views:
  1. Radar chart — average scores per condition across all criteria
  2. Heatmap     — per-question scores for each condition
  3. Gain chart  — average improvement per criterion (with vs without protocol)

Author: Monica Guimaraes
"""

import json
from pathlib import Path
from typing import Dict, List

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================================
# CONSTANTS
# ============================================================================

CRITERIA_LABELS = {
    "evidence_quality": "Evidence Quality",
    "transparency": "Transparency",
    "reasoning_depth": "Reasoning Depth",
    "actionability": "Actionability",
    "uncertainty_disclosure": "Uncertainty Disclosure",
}

CONDITIONS = ["without-protocol", "with-protocol"]
CONDITION_LABELS = {
    "without-protocol": "Without Protocol",
    "with-protocol": "With Protocol",
}
CONDITION_COLORS = {
    "without-protocol": "#EF553B",
    "with-protocol": "#636EFA",
}


# ============================================================================
# DATA LOADING
# ============================================================================

class EvaluationLoader:
    """
    Loads and aggregates evaluation results from JSONL files.

    Follows Single Responsibility Principle: only handles data loading.
    """

    def __init__(self, evaluations_dir: Path):
        """
        Args:
            evaluations_dir: Path to directory containing evaluation JSONL files.
        """
        self.evaluations_dir = evaluations_dir

    def load(self) -> List[Dict]:
        """
        Load all evaluation records from JSONL files.

        Returns:
            List of evaluation record dicts with valid (non-null) scores.
        """
        records = []
        for criterion_key in CRITERIA_LABELS:
            filepath = self.evaluations_dir / f"{criterion_key}_evaluations.jsonl"
            if not filepath.exists():
                continue
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    if record.get("score") is not None:
                        records.append(record)
        return records


# ============================================================================
# DATA AGGREGATION
# ============================================================================

class ScoreAggregator:
    """
    Aggregates raw evaluation records into structures needed for plotting.

    Follows Single Responsibility Principle: only handles aggregation logic.
    """

    def __init__(self, records: List[Dict]):
        """
        Args:
            records: List of evaluation record dicts.
        """
        self.records = records

    def average_by_condition_criterion(self) -> Dict[str, Dict[str, float]]:
        """
        Compute average score per (condition, criterion).

        Returns:
            {condition: {criterion: avg_score}}
        """
        totals: Dict[str, Dict[str, List[float]]] = {
            c: {k: [] for k in CRITERIA_LABELS} for c in CONDITIONS
        }
        for r in self.records:
            condition = r.get("condition")
            criterion = r.get("criterion")
            score = r.get("score")
            if condition in totals and criterion in totals[condition]:
                totals[condition][criterion].append(score)

        return {
            condition: {
                criterion: (sum(scores) / len(scores) if scores else 0.0)
                for criterion, scores in criteria.items()
            }
            for condition, criteria in totals.items()
        }

    def scores_by_condition_question_criterion(
        self,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Build per-question score matrix for each condition.

        Returns:
            {condition: {question_id: {criterion: score}}}
        """
        result: Dict[str, Dict[str, Dict[str, float]]] = {
            c: {} for c in CONDITIONS
        }
        for r in self.records:
            condition = r.get("condition")
            qid = r.get("question_id")
            criterion = r.get("criterion")
            score = r.get("score")
            if condition not in result:
                continue
            result[condition].setdefault(qid, {})[criterion] = score
        return result


# ============================================================================
# CHART BUILDERS
# ============================================================================

class RadarChartBuilder:
    """
    Builds a radar chart comparing average scores across conditions.

    Follows Single Responsibility Principle: only handles radar chart creation.
    """

    @staticmethod
    def build(averages: Dict[str, Dict[str, float]]) -> go.Figure:
        """
        Args:
            averages: {condition: {criterion: avg_score}}

        Returns:
            Plotly Figure with radar chart traces.
        """
        criteria_keys = list(CRITERIA_LABELS.keys())
        criteria_display = [CRITERIA_LABELS[k] for k in criteria_keys]
        # Close the polygon
        theta = criteria_display + [criteria_display[0]]

        fig = go.Figure()
        for condition in CONDITIONS:
            values = [averages[condition][k] for k in criteria_keys]
            values_closed = values + [values[0]]
            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=theta,
                fill="toself",
                name=CONDITION_LABELS[condition],
                line_color=CONDITION_COLORS[condition],
                fillcolor=CONDITION_COLORS[condition],
                opacity=0.35,
                hovertemplate=(
                    "<b>%{theta}</b><br>Score: %{r:.2f}<extra>"
                    + CONDITION_LABELS[condition] + "</extra>"
                ),
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], tickfont_size=11),
            ),
            showlegend=True,
            title=dict(text="Average Scores by Condition", font_size=16, x=0.5),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=60, b=60, l=60, r=60),
        )
        return fig


class HeatmapBuilder:
    """
    Builds side-by-side heatmaps showing per-question scores per condition.

    Follows Single Responsibility Principle: only handles heatmap creation.
    """

    @staticmethod
    def build(matrix: Dict[str, Dict[str, Dict[str, float]]]) -> go.Figure:
        """
        Args:
            matrix: {condition: {question_id: {criterion: score}}}

        Returns:
            Plotly Figure with two heatmap subplots.
        """
        criteria_keys = list(CRITERIA_LABELS.keys())
        criteria_display = [CRITERIA_LABELS[k] for k in criteria_keys]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[CONDITION_LABELS[c] for c in CONDITIONS],
            horizontal_spacing=0.12,
        )

        for col_idx, condition in enumerate(CONDITIONS, start=1):
            question_ids = sorted(matrix[condition].keys())
            z = []
            for qid in question_ids:
                row = [matrix[condition][qid].get(k, 0) for k in criteria_keys]
                z.append(row)

            text = [[str(v) for v in row] for row in z]

            fig.add_trace(
                go.Heatmap(
                    z=z,
                    x=criteria_display,
                    y=question_ids,
                    text=text,
                    texttemplate="%{text}",
                    textfont=dict(size=13, color="white"),
                    colorscale="Blues",
                    zmin=0,
                    zmax=5,
                    showscale=(col_idx == 2),
                    colorbar=dict(title="Score", tickvals=[0, 1, 2, 3, 4, 5]),
                    hovertemplate="<b>%{y} | %{x}</b><br>Score: %{z}<extra></extra>",
                ),
                row=1, col=col_idx,
            )

        fig.update_layout(
            title=dict(text="Scores by Question and Criterion", font_size=16, x=0.5),
            margin=dict(t=80, b=60, l=60, r=60),
        )
        fig.update_xaxes(tickangle=-30, tickfont_size=11)
        return fig


class GainChartBuilder:
    """
    Builds a horizontal bar chart showing average gain per criterion.

    Follows Single Responsibility Principle: only handles gain chart creation.
    """

    @staticmethod
    def build(averages: Dict[str, Dict[str, float]]) -> go.Figure:
        """
        Args:
            averages: {condition: {criterion: avg_score}}

        Returns:
            Plotly Figure with horizontal bar chart.
        """
        criteria_keys = list(CRITERIA_LABELS.keys())
        criteria_display = [CRITERIA_LABELS[k] for k in criteria_keys]

        gains = [
            averages["with-protocol"][k] - averages["without-protocol"][k]
            for k in criteria_keys
        ]
        bar_colors = ["#2ecc71" if g >= 0 else "#e74c3c" for g in gains]

        fig = go.Figure(go.Bar(
            x=gains,
            y=criteria_display,
            orientation="h",
            marker_color=bar_colors,
            text=[f"+{g:.2f}" if g >= 0 else f"{g:.2f}" for g in gains],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Gain: %{x:.2f}<extra></extra>",
        ))

        fig.add_vline(x=0, line_width=1.5, line_color="grey")

        fig.update_layout(
            title=dict(
                text="Average Score Gain: With Protocol vs Without Protocol",
                font_size=16, x=0.5,
            ),
            xaxis=dict(title="Score Gain (0–5 scale)", range=[-1, 5.5]),
            yaxis=dict(autorange="reversed"),
            margin=dict(t=60, b=60, l=180, r=80),
            showlegend=False,
        )
        return fig


# ============================================================================
# DASHBOARD ASSEMBLER
# ============================================================================

class DashboardAssembler:
    """
    Assembles individual charts into a single self-contained HTML dashboard.

    Follows Single Responsibility Principle: only handles HTML assembly.
    """

    @staticmethod
    def assemble(
        radar: go.Figure,
        heatmap: go.Figure,
        gain: go.Figure,
        output_path: Path,
    ) -> None:
        """
        Write a single HTML file containing all three charts.

        Args:
            radar: Radar chart figure.
            heatmap: Heatmap figure.
            gain: Gain bar chart figure.
            output_path: Path to write the HTML file.
        """
        radar_html = radar.to_html(full_html=False, include_plotlyjs="cdn")
        heatmap_html = heatmap.to_html(full_html=False, include_plotlyjs=False)
        gain_html = gain.to_html(full_html=False, include_plotlyjs=False)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Grounding Lab — Evaluation Results</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Segoe UI", system-ui, sans-serif;
      background: #f4f6fb;
      color: #1a1a2e;
      padding: 2rem;
    }}
    header {{
      text-align: center;
      margin-bottom: 2.5rem;
    }}
    header h1 {{
      font-size: 2rem;
      font-weight: 700;
      color: #1a1a2e;
    }}
    header p {{
      margin-top: 0.5rem;
      color: #555;
      font-size: 1rem;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    .card {{
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      padding: 1.25rem;
    }}
    .card-full {{
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      padding: 1.25rem;
      margin-bottom: 1.5rem;
    }}
    .plotly-graph-div {{ width: 100% !important; }}
  </style>
</head>
<body>
  <header>
    <h1>AI Grounding Lab — Evaluation Results</h1>
    <p>Scientific Grounding Protocol &nbsp;|&nbsp; AI Rubric Scores (0–5) &nbsp;|&nbsp; Evaluator: gpt-4o-mini</p>
  </header>

  <div class="grid-2">
    <div class="card">{radar_html}</div>
    <div class="card">{gain_html}</div>
  </div>

  <div class="card-full">{heatmap_html}</div>

</body>
</html>"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Load data, build charts, and write the dashboard HTML."""
    evaluations_dir = Path("evaluations/ai")
    output_path = Path("evaluations/results_dashboard.html")

    print("Loading evaluation records...")
    records = EvaluationLoader(evaluations_dir).load()
    print(f"  {len(records)} valid records loaded")

    aggregator = ScoreAggregator(records)
    averages = aggregator.average_by_condition_criterion()
    matrix = aggregator.scores_by_condition_question_criterion()

    print("Building charts...")
    radar = RadarChartBuilder.build(averages)
    heatmap = HeatmapBuilder.build(matrix)
    gain = GainChartBuilder.build(averages)

    print(f"Writing dashboard to {output_path}...")
    DashboardAssembler.assemble(radar, heatmap, gain, output_path)
    print(f"Done. Open: {output_path.resolve()}")


if __name__ == "__main__":
    main()
