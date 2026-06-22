"""Generación de gráficos técnicos en memoria (PNG).

matplotlib está configurado para headless (Agg backend) para no
requerir un display dentro del contenedor.
"""
import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from app.services.analysis_service import PERIOD_DEFAULT, SMA_WINDOWS, fetch_history


def render_chart_png(symbol: str, period: str = PERIOD_DEFAULT) -> bytes | None:
    """Genera un PNG con cierres + SMAs. None si no hay datos."""
    history = fetch_history(symbol, period)
    if history.empty:
        return None

    closes = history["Close"]
    dates = history.index.to_pydatetime()

    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    ax.plot(dates, closes, label="Close", linewidth=1.5, color="#1f77b4")
    colors = {8: "#ff7f0e", 21: "#2ca02c", 50: "#d62728", 100: "#9467bd"}
    for w in SMA_WINDOWS:
        if len(closes) >= w:
            ax.plot(dates, closes.rolling(window=w).mean(), label=f"SMA{w}",
                    linewidth=1.2, color=colors[w])

    ax.set_title(f"{symbol.upper()} — Close + SMA ({period})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="best", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    ax.grid(True, alpha=0.3)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
