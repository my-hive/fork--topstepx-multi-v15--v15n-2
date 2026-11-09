"""v15n-2 exp5: MNQ pre-open drift continuation, ATR-scaled sizing.
Side = sign(09:59 close - 07:00 open), held to 14:30 CT. Position size = risk_cap / causal
stop distance, capped at max_contracts. Stop distance = atr_mult x 60-min ATR of prior bars."""
import numpy as np

PARAMS = {
    "ref_sec": 25200,        # 07:00 CT
    "decide_sec": 35940,     # 09:59 CT (decision bar, fills 10:00 open)
    "exit_sec": 52200,       # 14:30 CT
    "atr_mult": 3.0,         # stop distance in ATR
    "risk_cap": 300.0,       # max dollars risked per entry (evaluator cap)
    "max_contracts": 10,     # MNQ weight .1 -> <=50 by exposure; this is the binding cap
}
SYMBOLS = ("MNQ",)
ATR_WIN = 60


def _atr(df):
    pc = df.close.groupby(df.session, sort=False).shift(1)
    tr = np.maximum(df.high - df.low, np.maximum(abs(df.high - pc), abs(df.low - pc)))
    return tr.groupby(df.session, sort=False).transform(lambda x: x.rolling(ATR_WIN, min_periods=20).mean())


def entry_risk(panel):
    out = {}
    for s, df in panel.items():
        risk = np.zeros(len(df))
        if s in SYMBOLS:
            stop_pts = PARAMS["atr_mult"] * _atr(df)
            risk = (stop_pts * 10).to_numpy()  # MNQ $2/point, cap handled in size; report per-contract dollars
            risk = np.nan_to_num(risk, nan=PARAMS["risk_cap"], posinf=PARAMS["risk_cap"])
            risk = np.clip(risk, 1.0, PARAMS["risk_cap"])
        out[s] = risk
    return out


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol in SYMBOLS:
            sec = df.ct_sec.to_numpy()
            ref = df.open.where(df.ct_sec == PARAMS["ref_sec"]).groupby(df.session, sort=False).transform("first")
            dec = df.close.where(df.ct_sec == PARAMS["decide_sec"]).groupby(df.session, sort=False).transform("first")
            side = np.nan_to_num(np.sign((dec - ref).to_numpy())).astype(np.int64)
            atr = _atr(df).to_numpy()
            stop_pts = PARAMS["atr_mult"] * atr
            size = np.nan_to_num(PARAMS["risk_cap"] / (stop_pts * 2), posinf=0)
            size = np.clip(size, 1, PARAMS["max_contracts"]).astype(np.int64)
            hold = (sec >= PARAMS["decide_sec"]) & (sec < PARAMS["exit_sec"] - 60)
            out[hold] = size[hold] * side[hold]
        result[symbol] = out
    return result
