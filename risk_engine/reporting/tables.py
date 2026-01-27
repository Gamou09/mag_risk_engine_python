"""Tabular outputs (placeholder)."""


def to_dataframe(data):
    """Convert results to pandas DataFrame if available."""
    try:
        import pandas as pd  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        raise ImportError("pandas is required for table exports") from exc

    return pd.DataFrame(data)


# TODO: add schema-aware formatting for risk and pricing results.
