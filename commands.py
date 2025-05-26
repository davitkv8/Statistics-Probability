import argparse, math, sys
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------- #
# ---- parameters you might tweak in one place ------------------------ #
BODY_MU       = math.log(1400)           # მედიანი ≈ 1 400 ₾
BODY_SIGMA    = 0.40                    # CV_body ≈ 0.38
TAIL_SHARE    = 0.003                   # 0.3 % იღებს Pareto კუდს
TAIL_XMIN     = 8_000                   # კუდის დასაწყისი
TAIL_ALPHA    = 2.6                     # სიმკაცრე (დიდი → უფრო იშვიათი ექსტრემი)
SALARY_FLOOR  = 300                     # მინ. ხელფასი კანონით
# --------------------------------------------------------------------- #

# ------------- helper generators ------------------------------------ #
def _gen_salary(rng: np.random.Generator, n: int) -> np.ndarray[int]:
    """Mixture:  (1-TAIL_SHARE)·LogNormal + TAIL_SHARE·Pareto."""
    mask_tail = rng.random(n) < TAIL_SHARE
    body_n    = n - mask_tail.sum()

    # log-normal body
    salaries = np.empty(n, dtype=float)
    salaries[~mask_tail] = rng.lognormal(BODY_MU, BODY_SIGMA, body_n)

    # Pareto tail
    if mask_tail.any():
        u = rng.random(mask_tail.sum())
        salaries[mask_tail] = TAIL_XMIN / (1.0 - u) ** (1.0 / TAIL_ALPHA)

    np.maximum(salaries, SALARY_FLOOR, out=salaries)
    return salaries.round().astype(int)


def _gen_age(s: int, rng: np.random.Generator) -> int:
    r = rng.random()
    if 300 <= s <= 600:                         # low bracket
        if r < 0.70:
            return rng.integers(17, 22) if rng.random() < .5 else rng.integers(55, 66)
        return rng.integers(22, 55)

    if 1_000 <= s <= 2_500:                    # mid bracket
        return rng.integers(25, 36) if r < .80 else rng.integers(18, 66)

    if 4_000 <= s <= 8_000:                    # upper-mid bracket
        if r < .80:
            return rng.integers(23, 29) if rng.random() < .5 else rng.integers(40, 49)
        return rng.integers(18, 66)

    return rng.integers(18, 66)                # fallback


# base industries + weights (sum = 100)
_BASE_INDS = [
    ("IT",                     10),
    ("Medicine & Health Care",  8),
    ("Construction",           12),
    ("Trading",                15),
    ("Agriculture",            10),
    ("Education",              12),
    ("Manufacturing",          15),
    ("Services",               18),
]
_IND_NAMES, _IND_WEIGHTS = zip(*_BASE_INDS)
_IND_WEIGHTS = np.array(_IND_WEIGHTS) / sum(_IND_WEIGHTS)

def _gen_industry(s: int, rng: np.random.Generator) -> str:
    if 4_000 <= s <= 8_000:     # special mix for high earners
        r = rng.random()
        if r < .40: return "IT"
        if r < .50: return "Medicine & Health Care"
        if r < .65: return "Construction"
        if r < .75: return "Trading"
        if r < .80: return "Agriculture"
    return rng.choice(_IND_NAMES, p=_IND_WEIGHTS)


# ------------- main command ----------------------------------------- #
def generate(rows: int, out_path: Path, seed: int | None):
    rng = np.random.default_rng(seed)

    salary = _gen_salary(rng, rows)
    age    = np.fromiter((_gen_age(s, rng)    for s in salary),  int, rows)
    ind    = np.fromiter((_gen_industry(s, rng) for s in salary), '<U24', rows)
    sex    = rng.choice(["Male", "Female"], size=rows)

    df = pd.DataFrame({
        "Salary_GEL": salary,
        "Age":        age,
        "Industry":   ind,
        "Sex":        sex,
    })
    df.to_csv(out_path, index=False)

    print(f"✔ wrote {rows:,} rows → {out_path}")
    print(f"   mean = {salary.mean():.1f} ₾   std = {salary.std(ddof=0):.1f} ₾   "
          f"(CV = {salary.std(ddof=0)/salary.mean():.2f})")


# ------------- CLI --------------------------------------------------- #
def _cli():
    p = argparse.ArgumentParser(description="Synthetic population generator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="create CSV")
    g.add_argument("--rows", type=int, default=10_000, help="number of records")
    g.add_argument("--out",  type=Path, default="population.csv", help="output CSV path")
    g.add_argument("--seed", type=int, help="random seed (omit for fresh data each run)")

    args = p.parse_args()
    if args.cmd == "generate":
        generate(args.rows, args.out, args.seed)

if __name__ == "__main__":
    _cli()