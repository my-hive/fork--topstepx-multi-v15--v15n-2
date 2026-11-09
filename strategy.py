"""v15n-2 exp7: MNQ pre-open drift continuation, 3 contracts with causal stop.
Side = sign(09:59 close - 07:00 open), held 10:00-14:30 CT.
Flatten if cumulative adverse move from entry close exceeds stop_pts.
Declared risk = stop_pts * 2 ($90/ct, so 3 ct = $270 <= $300 cap)."""
import numpy as np
import pandas as pd

PARAMS = {"ref_sec": 25200, "decide_sec": 35940, "exit_sec": 52200, "contracts": 3, "stop_pts": 45}
SYMBOLS = ("MNQ",)
POINT_VALUE = 2.0


def entry_risk(panel):
    r = float(PARAMS["stop_pts"]) * POINT_VALUE
    return {s: np.full(len(df), r) for s, df in panel.items()}


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol in SYMBOLS:
            sec = df.ct_sec.to_numpy()
            ref = df.open.where(df.ct_sec == PARAMS["ref_sec"]).groupby(df.session, sort=False).transform("first")
            dec = df.close.where(df.ct_sec == PARAMS["decide_sec"]).groupby(df.session, sort=False).transform("first")
            side = np.nan_to_num(np.sign((dec - ref).to_numpy())).astype(np.int64)
            adverse = side * (df.close - dec).to_numpy()
            hold = (sec >= PARAMS["decide_sec"]) & (sec < PARAMS["exit_sec"] - 60)
            hit = hold & (np.nan_to_num(adverse) <= -PARAMS["stop_pts"])
            s_hit = pd.Series(hit, index=df.index).groupby(df.session, sort=False).cummax().to_numpy()
            active = hold & (~s_hit)
            out[active] = PARAMS["contracts"] * side[active]
        result[symbol] = out
    return result
