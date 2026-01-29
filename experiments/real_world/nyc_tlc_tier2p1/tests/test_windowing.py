import pandas as pd

from src.estimators import compute_coherence


def test_coherence_date_ranges_ok_per_window():
    # Construct a Simpson-style level shift:
    # - Within each window: positive monotonic relationship (Spearman rho ~ 1)
    # - Across pooled: ranks invert due to window-level shifts -> pooled rho drops
    n = 40

    dates_pre = pd.date_range("2019-01-01", periods=n, freq="D")
    dates_post = pd.date_range("2020-03-01", periods=n, freq="D")

    x_pre = pd.Series(range(n), dtype=float)
    y_pre = x_pre + 100.0  # shifted up

    x_post = pd.Series(range(n), dtype=float) + 100.0  # shifted up in x
    y_post = pd.Series(range(n), dtype=float)  # shifted down in y

    df = pd.DataFrame(
        {
            "date": list(dates_pre) + list(dates_post),
            "C_congestion": list(x_pre) + list(x_post),
            "C_price_pressure": list(y_pre) + list(y_post),
        }
    )

    prereg = {
        "coherence": {
            "threshold": 0.6,
            "min_points": 10,
            "pairs": [["C_congestion", "C_price_pressure"]],
            "windowing": {
                "type": "date_ranges",
                "aggregate": "all_pass",
                "allow_pooled_fail": True,
                "windows": [
                    {"name": "pre", "start": "2019-01-01", "end": "2019-02-15"},
                    {"name": "post", "start": "2020-03-01", "end": "2020-04-15"},
                ],
            },
        }
    }

    report = compute_coherence(df, prereg)

    assert report["status"] == "OK_PER_WINDOW"
    assert report["windowing"]["type"] == "date_ranges"
    assert len(report["windowing"]["results"]) == 2
    assert all(w["status"] == "OK" for w in report["windowing"]["results"])

