"""Tests: PyArrow, Pandas, and Streamlit DataFrame Compatibility Suite.

Verifies that NumPy 1.26.4, Pandas 2.2.3, and PyArrow 17.0.0 work seamlessly together
and that Streamlit's Arrow conversion for dataframes and charts functions without errors.
"""
import io
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.ipc as pa_ipc
import streamlit.dataframe_util as df_util

from utils.ui_helpers import get_safe_dataframe
from database.review_repository import ReviewRepository
from services.history_service import HistoryService
from reports.recommendation_formatter import RecommendationFormatter


class TestArrowPandasCompatibility(unittest.TestCase):
    """Test PyArrow, NumPy, Pandas and Streamlit Arrow serialization."""

    def test_dependency_versions(self):
        """Verify exact pinned versions."""
        self.assertEqual(np.__version__, "1.26.4")
        self.assertEqual(pd.__version__, "2.2.3")
        self.assertEqual(pa.__version__, "17.0.0")

    def test_pandas_to_pyarrow_conversion(self):
        """Test DataFrame to PyArrow Table round trip."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "severity": ["CRITICAL", "HIGH", "MEDIUM"],
            "score": [9.8, 8.5, 5.0],
            "active": [True, False, True]
        })
        table = pa.Table.from_pandas(df)
        self.assertEqual(table.num_rows, 3)
        self.assertEqual(table.num_columns, 4)

        df_back = table.to_pandas()
        self.assertEqual(len(df_back), 3)

    def test_pyarrow_ipc_stream(self):
        """Test low-level Apache Arrow IPC stream serialization."""
        df = pd.DataFrame({
            "col_int": np.array([10, 20], dtype=np.int64),
            "col_float": np.array([1.23, 4.56], dtype=np.float64),
            "col_str": ["test1", "test2"]
        })
        table = pa.Table.from_pandas(df)
        sink = io.BytesIO()
        with pa_ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)
        data = sink.getvalue()
        self.assertGreater(len(data), 100)

        reader = pa_ipc.open_stream(data)
        read_table = reader.read_all()
        self.assertEqual(read_table.num_rows, 2)

    def test_streamlit_dataframe_arrow_serialization(self):
        """Test Streamlit's internal convert_pandas_df_to_arrow_bytes function."""
        df = pd.DataFrame({
            "File": ["user_service.py", "safe_calc.py"],
            "Findings": [5, 0],
            "Verdict": ["Changes Requested", "Approved"]
        })
        arrow_bytes = df_util.convert_pandas_df_to_arrow_bytes(df)
        self.assertIsInstance(arrow_bytes, bytes)
        self.assertGreater(len(arrow_bytes), 0)

    def test_dashboard_table_and_chart_arrow_serialization(self):
        """Test Dashboard recent reviews table and severity chart serialization."""
        service = HistoryService()
        metrics = service.get_dashboard_metrics()

        # Recent reviews table
        recent = metrics.get("recent_reviews", [])
        recent_rows = []
        for r in recent:
            recent_rows.append({
                "Review ID": r.get("review_id"),
                "Target File": r.get("filename"),
                "Health Score": f"{r.get('health_score', 0):.1f}/100",
                "Verdict": r.get("pr_status"),
            })
        df_recent = get_safe_dataframe(recent_rows)
        self.assertIsInstance(df_recent, pd.DataFrame)
        arrow_bytes = df_util.convert_pandas_df_to_arrow_bytes(df_recent)
        self.assertGreater(len(arrow_bytes), 0)

        # Severity chart
        sev_dict = {
            "Critical": metrics.get("critical_count", 0),
            "High": metrics.get("high_count", 0),
            "Medium": metrics.get("medium_count", 0),
            "Low": metrics.get("low_count", 0),
        }
        df_sev = pd.DataFrame(list(sev_dict.items()), columns=["Severity", "Count"]).set_index("Severity")
        arrow_chart = df_util.convert_pandas_df_to_arrow_bytes(df_sev)
        self.assertGreater(len(arrow_chart), 0)

    def test_review_history_table_arrow_serialization(self):
        """Test Review History table serialization with real SQLite database records."""
        repo = ReviewRepository()
        all_reviews = repo.get_all_reviews(limit=50)
        self.assertGreater(len(all_reviews), 0)

        history_rows = []
        for r in all_reviews:
            history_rows.append({
                "Review ID": r["review_id"],
                "Target File": r["filename"],
                "Verdict": r.get("pr_status", "N/A"),
                "Score": f"{r.get('health_score', 0):.1f}/100"
            })
        df_hist = get_safe_dataframe(history_rows)
        self.assertIsInstance(df_hist, pd.DataFrame)
        arrow_bytes = df_util.convert_pandas_df_to_arrow_bytes(df_hist)
        self.assertGreater(len(arrow_bytes), 0)

    def test_reports_recommendations_table_arrow_serialization(self):
        """Test Reports recommendations table serialization with real findings."""
        repo = ReviewRepository()
        all_reviews = repo.get_all_reviews(limit=1)
        self.assertGreater(len(all_reviews), 0)

        full_rev = repo.get_review_by_id(all_reviews[0]["review_id"])
        findings = full_rev.get("findings", [])
        rec_table = RecommendationFormatter.format_recommendations_table(findings)
        df_recs = get_safe_dataframe(rec_table)
        self.assertIsInstance(df_recs, pd.DataFrame)
        arrow_bytes = df_util.convert_pandas_df_to_arrow_bytes(df_recs)
        self.assertGreater(len(arrow_bytes), 0)


if __name__ == "__main__":
    unittest.main()
