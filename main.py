"""Adaptive-volatility quantile forecaster for Polymarket's Next CEO of NVIDIA?

For every market in a case, the forecast centres on the checkpoint price
(the last price given) and widens with horizon. The width is set per
market from how much that market actually moved recently: the root-mean-
square of its one-minute price changes over the last 120 minutes,
floored and capped so quiet markets stay narrow and jumpy ones stay
wide. Spreads grow as h**0.30, slower than a random walk, because
measured price moves over 240 minutes are much smaller than sqrt(h)
would predict. The five quantiles use widened normal offsets, and all
centres are pulled slightly toward the mutually-exclusive sum of 1.

Standard library only, deterministic, no network, no clock, no random
numbers. Reads every *.in file in $MAKEFUN_INPUT_DIR (else /input) and
writes one <id>.out per case to $MAKEFUN_OUTPUT_DIR (else /output).
"""

import json
import math
import os
from pathlib import Path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

QUANTILES = [0.05, 0.25, 0.5, 0.75, 0.95]
# Normal quantiles, outer pair stretched by 1.3 and inner pair shrunk
# by 0.8 (measured on the backtest cuts: wider tails, tighter shoulders).
Z = [-2.138310, -0.539592, 0.0, 0.539592, 2.138310]

VOL_WINDOW = 120          # minutes of recent history used for sigma
VOL_FLOOR = 0.0005        # minimum per-minute sigma
VOL_CAP = 0.02            # maximum per-minute sigma
GROWTH = 0.30             # spread grows as h ** GROWTH
SUM_PULL = 0.25           # fraction of the sum-to-one correction applied


def clean(value):
    """Clamp to [0, 1], round to 6 decimals, and never return -0.0."""
    return round(min(1.0, max(0.0, value)), 6) + 0.0


def recent_sigma(prices):
    """RMS of one-minute price differences over the last 120 minutes."""
    if len(prices) < 2:
        return VOL_FLOOR
    # 120 one-minute differences need the last 121 prices; fewer
    # prices means use everything available.
    tail = prices[-121:] if len(prices) > 121 else prices
    total = 0.0
    count = 0
    for prev, cur in zip(tail, tail[1:]):
        diff = cur - prev
        total += diff * diff
        count += 1
    if count == 0:
        return VOL_FLOOR
    sigma = math.sqrt(total / count)
    return min(VOL_CAP, max(VOL_FLOOR, sigma))


def forecast_market(center, sigma, horizon):
    """240 rows of five quantiles around `center` for one market."""
    rows = []
    for h in range(1, horizon + 1):
        spread = sigma * (h ** GROWTH)
        rows.append([clean(center + z * spread) for z in Z])
    return rows


def forecast_case(case):
    if case["quantiles"] != QUANTILES:
        raise ValueError(
            "quantiles %r do not match expected %r"
            % (case["quantiles"], QUANTILES)
        )
    horizon = case["horizon_minutes"]
    markets = case["markets"]

    last_prices = [m["prices"][-1] for m in markets]
    total = sum(last_prices)
    # The 24 outcomes are mutually exclusive, so their Yes prices
    # should sum to about 1; pull each centre a quarter of the way
    # toward that constraint.
    pull = 1.0 - SUM_PULL * (total - 1.0) / total if total > 0 else 1.0

    forecasts = []
    for market in markets:
        if not market["prices"]:
            raise ValueError("market %s has no prices" % market["id"])
        centre = market["prices"][-1] * pull
        sigma = recent_sigma(market["prices"])
        forecasts.append(
            {"id": market["id"], "q": forecast_market(centre, sigma, horizon)}
        )
    return {"forecasts": forecasts}


def main():
    in_dir = Path(INPUT_DIR)
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(p.name for p in in_dir.glob("*.in")):
        case = json.loads((in_dir / name).read_text(encoding="utf-8"))
        result = forecast_case(case)
        out_path = out_dir / (name[:-3] + ".out")
        out_path.write_text(
            json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
