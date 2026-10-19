"""Shared statistics for the round-6 analyses (note 42).

Index cases are agents infected on trace days 1 to 10 with a known infector. Offspring are
infections they cause on or before day + 14. Moment k is the pooled method of moments with
variance divided by n - 1. Likelihood k is the negative-binomial maximum likelihood with the
mean fixed at the sample mean.
"""

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from analyze_round2 import log_nbinom_pmf  # noqa: E402

UNKNOWN = 4294967295
STEPS = 144
BOOT = 1000
BOOT_SEED = 20261016


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    keys, seen = [], set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    def clean(value):
        if isinstance(value, float):
            return "" if math.isnan(value) else f"{value:.6g}"
        return value

    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: clean(value) for key, value in row.items()} for row in rows])
    print(f"wrote {path.name} ({path.stat().st_size} bytes)", flush=True)


def digamma(x):
    x = float(x)
    result = 0.0
    while x < 6.0:
        result -= 1.0 / x
        x += 1.0
    f = 1.0 / (x * x)
    return result + math.log(x) - 0.5 / x - f * (1 / 12.0 - f * (1 / 120.0 - f * (1 / 252.0 - f * (1 / 240.0 - f / 132.0))))


def trigamma(x):
    x = float(x)
    result = 0.0
    while x < 6.0:
        result += 1.0 / (x * x)
        x += 1.0
    f = 1.0 / (x * x)
    return result + 1.0 / x + 0.5 * f + (1.0 / x) * f * (1 / 6.0 - f * (1 / 30.0 - f * (1 / 42.0 - f / 30.0)))


def gamma_shape_mle(n, total, log_total):
    """Shape of the gamma fit with free scale, from n, sum x and sum log x."""
    if n < 2 or total <= 0:
        return None
    s = math.log(total / n) - log_total / n
    if s <= 0:
        return None
    a = (3 - s + math.sqrt((s - 3) ** 2 + 24 * s)) / (12 * s)
    for _ in range(60):
        step = (math.log(a) - digamma(a) - s) / (1.0 / a - trigamma(a))
        a_new = a - step
        if a_new <= 0:
            a_new = a / 2
        if abs(a_new - a) < 1e-12 * a:
            a = a_new
            break
        a = a_new
    return a


def trait_sufficient(values):
    values = np.asarray(values, dtype=np.float64)
    positive = values[values > 0]
    return {
        "n": int(values.size),
        "sum": float(values.sum()),
        "sumsq": float((values ** 2).sum()),
        "n_pos": int(positive.size),
        "sum_pos": float(positive.sum()),
        "sumlog": float(np.log(positive).sum()),
    }


def pool_sufficient(parts):
    keys = ("n", "sum", "sumsq", "n_pos", "sum_pos", "sumlog")
    return {key: sum(part[key] for part in parts) for key in keys}


def gamma_fit(stat):
    return gamma_shape_mle(stat["n_pos"], stat["sum_pos"], stat["sumlog"])


def cv2(stat):
    if stat["n"] < 2 or stat["sum"] <= 0:
        return None
    mean = stat["sum"] / stat["n"]
    var = (stat["sumsq"] - stat["n"] * mean * mean) / (stat["n"] - 1)
    return var / (mean * mean)


def mean_of(stat):
    return stat["sum"] / stat["n"] if stat["n"] else None


def mom_k(values):
    values = np.asarray(values, dtype=float)
    if values.size < 2:
        return None
    mean = float(values.mean())
    var = float(values.var(ddof=1))
    if mean <= 0:
        return None
    if var <= mean:
        return math.inf
    return mean * mean / (var - mean)


def nb_loglik_arrays(offspring, number, mu, k):
    p = k / (k + mu)
    log_p = math.log(p)
    log_q = math.log(1.0 - p)
    log_k = math.lgamma(k)
    total = 0.0
    for j, c in zip(offspring, number):
        total += c * (math.lgamma(j + k) - log_k - math.lgamma(j + 1) + k * log_p + j * log_q)
    return total


def ml_k(values):
    """Maximum-likelihood negative-binomial k with the mean fixed at the sample mean."""
    values = np.asarray(values, dtype=np.int64)
    if values.size < 2:
        return None
    mu = float(values.mean())
    if mu <= 0:
        return None
    counts = Counter(values.tolist())
    offspring = list(counts.keys())
    number = [counts[j] for j in offspring]
    grid = np.geomspace(1e-3, 200.0, 60)
    scores = [nb_loglik_arrays(offspring, number, mu, float(k)) for k in grid]
    best = int(np.argmax(scores))
    if best == len(grid) - 1:
        return math.inf
    lo = float(grid[max(best - 1, 0)])
    hi = float(grid[min(best + 1, len(grid) - 1)])
    for _ in range(45):
        a = math.exp((2 * math.log(lo) + math.log(hi)) / 3)
        b = math.exp((math.log(lo) + 2 * math.log(hi)) / 3)
        if nb_loglik_arrays(offspring, number, mu, a) < nb_loglik_arrays(offspring, number, mu, b):
            lo = a
        else:
            hi = b
    return math.exp(0.5 * (math.log(lo) + math.log(hi)))


def nb_pmf(mu, k, j):
    p = k / (k + mu)
    return math.exp(log_nbinom_pmf(j, k, p))


def nb_sf_at_least(mu, k, threshold):
    if threshold <= 0:
        return 1.0
    p = k / (k + mu)
    log_q = math.log(1.0 - p)
    logpmf = log_nbinom_pmf(threshold, k, p)
    logs = [logpmf]
    j = threshold
    while j < threshold + 200000:
        j += 1
        logpmf += math.log(j - 1 + k) - math.log(j) + log_q
        logs.append(logpmf)
        if logpmf < logs[0] - 45 and logpmf < max(logs) - 45:
            break
    peak = max(logs)
    return math.exp(peak) * sum(math.exp(item - peak) for item in logs)


def nb_zero(mu, k):
    if k is None or not math.isfinite(k):
        return math.exp(-mu)
    return (k / (k + mu)) ** k


def nb_shares(mu, k):
    keys = ("share_0", "share_1_to_5", "share_above_5", "share_at_least_20", "share_at_least_50")
    if mu is None or k is None or mu <= 0:
        return {key: None for key in keys}
    if not math.isfinite(k):
        # Poisson limit
        p0 = math.exp(-mu)
        mid = sum(math.exp(-mu + j * math.log(mu) - math.lgamma(j + 1)) for j in range(1, 6))
        cdf = lambda t: 1.0 - sum(math.exp(-mu + j * math.log(mu) - math.lgamma(j + 1)) for j in range(t))
        return {"share_0": p0, "share_1_to_5": mid, "share_above_5": cdf(6), "share_at_least_20": cdf(20), "share_at_least_50": cdf(50)}
    p0 = nb_pmf(mu, k, 0)
    mid = sum(nb_pmf(mu, k, j) for j in range(1, 6))
    above5 = nb_sf_at_least(mu, k, 6)
    return {
        "share_0": p0,
        "share_1_to_5": mid,
        "share_above_5": above5,
        "share_at_least_20": nb_sf_at_least(mu, k, 20),
        "share_at_least_50": nb_sf_at_least(mu, k, 50),
    }


def index_table(trace_path, events=None, event_agents=None):
    """Return agent ids, day, total offspring and event offspring of every index case."""
    day = {}
    location = {}
    known = set()
    children = defaultdict(list)
    with open(trace_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            agent = int(parts[col["agent"]])
            infector = int(parts[col["infector"]])
            d = int(parts[col["timestamp"]]) // STEPS
            loc = int(parts[col["location"]])
            day[agent] = d
            location[agent] = loc
            if infector != UNKNOWN:
                known.add(agent)
                children[infector].append((d, loc, agent))
    ids, total, event = [], [], []
    for agent, d in day.items():
        if agent not in known or not (1 <= d <= 10):
            continue
        n = e = 0
        limit = d + 14
        for child_day, child_loc, child_agent in children.get(agent, ()):
            if child_day <= limit:
                n += 1
                if events and (child_loc, child_day) in events:
                    e += 1
                elif event_agents and child_agent in event_agents:
                    e += 1
        ids.append(agent)
        total.append(n)
        event.append(e)
    return (np.asarray(ids, dtype=np.int64), np.asarray(total, dtype=np.int32), np.asarray(event, dtype=np.int32))


def load_events(path):
    found = set()
    with open(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                continue
            found.add((int(parts[col["location_index"]]), int(parts[col["day"]])))
    return found


def load_event_agents(path):
    """Agents infected at a closed-group event: one per row of <eventGroupLog>.infections."""
    found = set()
    with open(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = header.index("agent")
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > col:
                found.add(int(parts[col]))
    return found


def pack(total, event, nb=True):
    total = np.asarray(total)
    event = np.asarray(event)
    n = int(total.size)
    if n == 0:
        return None
    mean = float(total.mean())
    k_mom = mom_k(total)
    k_ml = ml_k(total)
    nonempty = total[total >= 1]
    out = {
        "index_cases": n,
        "early_R": mean,
        "k_mom": k_mom,
        "k_ml": k_ml,
        "share_0": float(np.mean(total == 0)),
        "share_1_to_5": float(np.mean((total >= 1) & (total <= 5))),
        "share_above_5": float(np.mean(total > 5)),
        "share_at_least_20": float(np.mean(total >= 20)),
        "share_at_least_50": float(np.mean(total >= 50)),
        "maximum": int(total.max()),
        "event_offspring_share": (float(event.sum()) / float(total.sum())) if total.sum() else None,
        "event_mean_if_any": float(event[event >= 1].mean()) if np.any(event >= 1) else None,
        "nonempty_median": float(np.median(nonempty)) if nonempty.size else None,
        "nonempty_p90": float(np.quantile(nonempty, 0.9)) if nonempty.size else None,
        "zero_ratio_mom_over_ml": None,
    }
    if nb:
        for tag, k in (("mom", k_mom), ("ml", k_ml)):
            shares = nb_shares(mean, k)
            for key, value in shares.items():
                out[f"nb_{tag}_{key}"] = value
    return out


def pack_fast(total, event):
    """Statistics used inside bootstrap loops. Skips the tail negative-binomial sums."""
    total = np.asarray(total)
    event = np.asarray(event)
    mean = float(total.mean())
    k_mom = mom_k(total)
    k_ml = ml_k(total)
    nonempty = total[total >= 1]
    return {
        "early_R": mean,
        "k_mom": k_mom,
        "k_ml": k_ml,
        "share_0": float(np.mean(total == 0)),
        "share_1_to_5": float(np.mean((total >= 1) & (total <= 5))),
        "share_above_5": float(np.mean(total > 5)),
        "share_at_least_20": float(np.mean(total >= 20)),
        "share_at_least_50": float(np.mean(total >= 50)),
        "event_offspring_share": (float(event.sum()) / float(total.sum())) if total.sum() else None,
        "nb_mom_share_0": nb_zero(mean, k_mom),
        "nb_ml_share_0": nb_zero(mean, k_ml),
        "nonempty_median": float(np.median(nonempty)) if nonempty.size else None,
        "nonempty_p90": float(np.quantile(nonempty, 0.9)) if nonempty.size else None,
    }


def interval(samples):
    values = np.asarray([v for v in samples if v is not None and np.isfinite(v)], dtype=float)
    if values.size == 0:
        return None, None
    return float(np.quantile(values, 0.05)), float(np.quantile(values, 0.95))


def bootstrap_pack(reps, draws=BOOT, seed=BOOT_SEED, extra=None):
    """Replicate bootstrap of pack_fast. reps is a list of (total, event). extra maps name -> f(list of reps)."""
    rng = np.random.default_rng(seed)
    n = len(reps)
    columns = defaultdict(list)
    for _ in range(draws):
        pick = rng.integers(0, n, size=n)
        total = np.concatenate([reps[i][0] for i in pick])
        event = np.concatenate([reps[i][1] for i in pick])
        stats = pack_fast(total, event)
        for key, value in stats.items():
            columns[key].append(value)
        if extra:
            for key, func in extra.items():
                columns[key].append(func([reps[i] for i in pick]))
    return {key: interval(values) for key, values in columns.items()}


def flatten_row(label, point, intervals):
    row = {"cell": label}
    for key, value in point.items():
        row[key] = value
        if key in intervals and intervals[key][0] is not None:
            row[f"{key}_low"] = intervals[key][0]
            row[f"{key}_high"] = intervals[key][1]
    return row
