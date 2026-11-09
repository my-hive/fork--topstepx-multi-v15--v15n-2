# v15n-2 mechanism notes (explorer)

Role: explorer. Budget 30 recorded experiments, 0 sealed slots. Cheapest screen first
(`--null-seeds 0 --mode dev`), provisional nulls only for plausible candidates.

## Mechanism A — pre-open drift continuation (MNQ)

Hypothesis: overnight/European-session order flow (07:00 CT open -> 09:59 CT close)
persists into the US session. Side = sign(09:59 close - 07:00 open); hold 10:00-14:30 CT.

* exp2 (NQ full history 2010-2023, 1 contract): dev 0.063, era blocks -24720/-7208/+32508.
  Edge exists only from 2017 on; 2010-2016 gross PnL of the same rule is negative
  (mean pre-open drift +0.8..+1.2 pt in 2013-2014, negative 2011/2015/2016).
* exp3 (MNQ 2019-05..2023, 1 contract): dev 0.2415, era blocks 1418/2729/1903, 4/5 years.
  MNQ and NQ agree to corr 1.0 and identical gross PnL over the overlap, so this is the
  same rule, not a micro artifact; but MNQ history starts 2019-05 so the 2010-2016 failure
  is invisible in MNQ dev partition. Treat as era-fragile until a longer-history proxy passes.
* exp4 (2 contracts, flat $300/ct declaration): dev 0.2711, era 3523/4018/4828, but
  entry risk 2x300 > 300 fails the risk gate. Sizing must respect the $300 cap.
* exp5 (ATR-scaled size): dev 0.2711 but era2 -7487, 2019 -10090. Small-ATR periods
  oversize the position; volatility-scaled sizing without a stop floor is dangerous.
* exp7 (3 contracts, 45-pt close-based stop, risk 90/ct = 270/entry): dev 0.2988,
  fold 0.0607 (0.062/0.059/0.228/0.103), posyr 0.8, era 8697/9104/646, dev-eligible.
* exp8 (5 contracts, 30-pt stop): dev 0.2364, era2 -1201, posyr 0.4. Scale without stop
  quality destroys year consistency.

Economics: pre-open drift is small (~8-20 NQ points, 3-11 points MNQ) while stressed
round-trip cost is 4.25 (MNQ) / 27.50 (NQ). Edge per trade is a few dollars; the rule
only clears costs because the 10:00-14:30 move is much larger than the signal move.

## Mechanism B — late-session continuation (MNQ)

Sign(09:30 open -> 13:29 close) held 13:30-14:30 CT (exp6): dev 0.2319,
era 455/4326/350, posyr 0.8, folds 0/0/0/0. Independent window from Mechanism A, so
the two are candidates for combination on different symbols.

## Structural findings from 30-minute-bar diagnostics (not screens)

* Equity index 30-min autocorrelation ~0.01 (no short-horizon trend).
* Mid-day -> close correlation: ES/NQ/YM/RTY +0.12 (10:00-13:30 predicts 13:30-15:00);
  CL -0.21 (reversal); FX 6E/6J 30-min lag -0.11/-0.14 (reversion).
* One-lot PnL of every such rule is about equal to its stressed round-trip cost
  (ES 57.5, NQ 27.5, M6E 7.25 per RT), so single-lot versions are unprofitable.
  Micro sizing plus at least 3 contracts is what turns these into positive PnL.
* 60-min intraday momentum on ES loses ~150k/yr; the intraday trend direction is
  anti-persistent at 1-hour scale (exp1).

## Known caveats

* MNQ dev partition covers only 2019-05..2023-12 (5 years); its "three era blocks"
  are 2019-2020 / 2021 / 2022-2023, so era robustness for Mechanism A is untestable
  inside MNQ. NQ is the honest proxy and it fails 2010-2016.
* Fold pass rates stay low because $3,000 in 30 sessions needs >$100/day per account;
  3 MNQ contracts at the observed edge give ~$15/day.
