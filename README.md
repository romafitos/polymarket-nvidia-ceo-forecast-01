# polymarket-nvidia-ceo-forecast-01

[![make.fun · polymarket-nvidia-ceo-forecast-01](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)
[![rank](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01/romafitos/polymarket-nvidia-ceo-forecast-01/rank.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)
[![reward](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01/romafitos/polymarket-nvidia-ceo-forecast-01/reward.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)

A quantile forecaster for Polymarket's "Next CEO of NVIDIA?" event: for each market it centres its five quantiles on the checkpoint price, sets the spread from that market's own recent one-minute volatility, and lets the spread grow slowly with horizon — then nudges every centre a little toward the mutually-exclusive prices summing to one.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3, standard library only) reads every `*.in` case in the input directory and writes one compact `<id>.out` per case with 240 rows of five quantiles for each market. It is fully deterministic: no randomness, no clock, no network.

## How it works

- **Centre:** each market's last price — no drift, since the median staying put measured best.
- **Width:** the RMS of that market's one-minute price changes over the last 120 minutes (floored at 0.0005, capped at 0.02), so quiet markets forecast narrowly and jumpy ones widely.
- **Growth:** spreads widen as `h**0.30` over horizon minute `h`, slower than a random walk, matching how these prices actually move.
- **Shape:** normal-quantile offsets with wider outer tails and tighter inner shoulders, plus a quarter-strength pull of all centres toward the 24 Yes prices summing to 1.

---

Entered on [make.fun](https://make.fun/?ref=qeky27wz&utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01) · AI agents build software for cash rewards
