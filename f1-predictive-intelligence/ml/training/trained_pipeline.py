"""Leakage-resistant F1 finishing-order models (research on simulated races).

Input protocol: historical events carry event_timestamp_utc, entries with only pre-race
features, and results. Training features are computed exclusively from prior events.
No official F1 data, track-specific telemetry, or externally calibrated probabilities.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path

FEATURES = (
    'grid_pos', 'driver_mean_prior', 'driver_starts_prior', 'team_mean_prior',
    'team_starts_prior', 'clean_air_delta_s', 'weather_skill_delta_s',
)
MODEL_NAMES = (
    'Baseline_Grid', 'Baseline_Standings', 'Ridge_Regularized',
    'RandomForest_Ensemble', 'GradientBoosting_Regressor',
    'XGBoost_Calibrated', 'LightGBM_Ranker', 'CatBoost_Probabilistic',
)


def timestamp(value):
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError('timestamp must be an ISO-8601 string with timezone') from exc
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError('timezone is required')
    return d


def _validate_entries(entries):
    if not isinstance(entries, list) or len(entries) < 2:
        raise ValueError('at least two race entries required')
    seen = set()
    for row in entries:
        code = row.get('driver_code')
        if not code or code in seen or not row.get('constructor'):
            raise ValueError('duplicate/missing driver or constructor')
        seen.add(code)
        grid = float(row.get('grid_pos', 0))
        if not math.isfinite(grid) or not 1 <= grid <= len(entries):
            raise ValueError('grid_pos outside starter count')
        for k in ('clean_air_delta_s', 'weather_skill_delta_s'):
            value = float(row.get(k, 0.0))
            if not math.isfinite(value):
                raise ValueError('non-finite feature ' + k)
    return seen


def features_for(entries, prior_events):
    _validate_entries(entries)
    driver = defaultdict(list)
    teams = defaultdict(list)
    for event in prior_events:
        for result in event['results']:
            v = float(result['finish_pos'])
            if not math.isfinite(v) or v < 1:
                raise ValueError('invalid finish_pos')
            driver[result['driver_code']].append(v)
            teams[result['constructor']].append(v)
    count = len(entries)
    global_prior = (count + 1) / 2
    out = []
    for e in entries:
        dh = driver[e['driver_code']]
        th = teams[e['constructor']]
        out.append([
            float(e['grid_pos']),
            sum(dh)/len(dh) if dh else global_prior,
            float(len(dh)),
            sum(th)/len(th) if th else global_prior,
            float(len(th)),
            float(e.get('clean_air_delta_s', 0.0)),
            float(e.get('weather_skill_delta_s', 0.0)),
        ])
    return out


def _ordered_events(events, as_of=None):
    result = sorted(events, key=lambda e: timestamp(e['event_timestamp_utc']))
    seen = set()
    for e in result:
        t = timestamp(e['event_timestamp_utc'])
        if as_of is not None and t >= as_of:
            raise ValueError('look-ahead: training event at or after prediction cutoff')
        if e.get('event_id') in seen:
            raise ValueError('duplicate event_id')
        seen.add(e.get('event_id'))
        codes = _validate_entries(e['entries'])
        ranks = [int(r['finish_pos']) for r in e['results']]
        if set(r['driver_code'] for r in e['results']) != codes:
            raise ValueError('results/entries driver mismatch')
        if sorted(ranks) != list(range(1, len(codes)+1)):
            raise ValueError('results must contain a unique, complete finishing order')
        if timestamp(e['snapshot_timestamp_utc']) > t:
            raise ValueError('snapshot cannot be newer than race result')
    return result


def build_temporal_rows(events):
    """Create per-race feature groups, using *only* strictly earlier completed races."""
    evs = _ordered_events(events)
    groups = []
    prior = []
    for e in evs:
        # Skip first race: it has no observed prior form and would be pure grid baseline.
        if prior:
            values = features_for(e['entries'], prior)
            ranks = {r['driver_code']: int(r['finish_pos']) for r in e['results']}
            groups.append((e['event_id'], values,
                           [ranks[e['driver_code']] for e in e['entries']]))
        prior.append(e)
    return groups


def _fit(name, x, y, groups, seed=41):
    if name.startswith('Baseline_'):
        return None
    from sklearn.linear_model import Ridge
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    if name == 'Ridge_Regularized':
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        obj = make_pipeline(StandardScaler(), Ridge(alpha=10))
    elif name == 'RandomForest_Ensemble':
        obj = RandomForestRegressor(n_estimators=75, min_samples_leaf=2, random_state=seed, n_jobs=1)
    elif name == 'GradientBoosting_Regressor':
        obj = GradientBoostingRegressor(n_estimators=65, max_depth=2, random_state=seed)
    elif name == 'XGBoost_Calibrated':
        from xgboost import XGBRegressor
        obj = XGBRegressor(n_estimators=65, max_depth=2, learning_rate=0.08,
                           objective='reg:squarederror', random_state=seed, n_jobs=1)
    elif name == 'LightGBM_Ranker':
        from lightgbm import LGBMRanker
        obj = LGBMRanker(objective='lambdarank', n_estimators=55,
                        num_leaves=10, min_child_samples=3, verbosity=-1, random_state=seed)
        relevance = [max(0, 25-int(z)) for z in y]
        obj.fit(x, relevance, group=groups)
        return obj
    elif name == 'CatBoost_Probabilistic':
        from catboost import CatBoostRegressor
        obj = CatBoostRegressor(iterations=75, depth=4, learning_rate=0.08, verbose=False,
                                thread_count=1, random_seed=seed)
    else:
        raise ValueError('unknown model ' + name)
    obj.fit(x, y)
    return obj


def _predict(name, model, x):
    import numpy as np
    a = np.asarray(x, dtype=float)
    if name == 'Baseline_Grid':
        return a[:, 0].tolist()
    if name == 'Baseline_Standings':
        return a[:, 1].tolist()
    scores = model.predict(a)
    if name == 'LightGBM_Ranker':
        # Higher relevance means better finish; translate to low-score-is-best.
        return (-scores).tolist()
    return [float(z) for z in scores]


def _rank_error(predictions, actual):
    # Invariant to different model output scales (regression and ranking).
    order = sorted(range(len(predictions)), key=lambda i: float(predictions[i]))
    assigned = [0] * len(order)
    for rank, idx in enumerate(order, 1):
        assigned[idx] = rank
    return sum(abs(a-b) for a,b in zip(assigned, actual)) / len(actual)


def _pl_rank_probabilities(scores, seed=41, simulations=3000, temperature=3.5):
    if not scores or not all(math.isfinite(float(s)) for s in scores):
        raise ValueError('invalid scores')
    smin, smax = min(scores), max(scores)
    span = max(float(smax)-float(smin), 0.5)
    weights = [math.exp(-temperature*(float(s)-smin)/span) for s in scores]
    rng = random.Random(seed)
    counts = [[0,0,0] for _ in scores]
    for _ in range(simulations):
        order = sorted(range(len(scores)), key=lambda i: rng.expovariate(max(weights[i], 1e-14)))
        for pos, i in enumerate(order):
            if pos == 0: counts[i][0] += 1
            if pos < 3: counts[i][1] += 1
            if pos < 10: counts[i][2] += 1
    return [[c/simulations for c in row] for row in counts]


def fit_and_evaluate(history, target_event, as_of_timestamp, models=None,
                     calibration_fraction=0.25):
    """Train on chronological events, validate only on *later* events, predict target.

    This is an evaluation example, NOT a production model or a calibration claim.
    Metric is rank MAE on held-out *events*, not in-sample scores.
    """
    import numpy as np
    asof = timestamp(as_of_timestamp)
    ordered = _ordered_events(history, asof)
    if timestamp(target_event['snapshot_timestamp_utc']) > asof:
        raise ValueError('look-ahead: target snapshot after as-of')
    if target_event.get('event_timestamp_utc') and timestamp(target_event['event_timestamp_utc']) < asof:
        raise ValueError('target event cannot predate as-of')
    _validate_entries(target_event['entries'])
    if len(ordered) < 7:
        raise ValueError('at least seven historical races required for temporal evaluation')
    groups = build_temporal_rows(ordered)
    n_val = max(2, math.ceil(len(groups)*calibration_fraction))
    if n_val >= len(groups)-2:
        raise ValueError('insufficient prior races for train/validation split')
    train_groups, val_groups = groups[:-n_val], groups[-n_val:]
    xx = np.asarray([x for _, vals, _ in train_groups for x in vals], dtype=float)
    yy = np.asarray([z for _, _, ys in train_groups for z in ys], dtype=float)
    sizes = [len(rows) for _, rows, _ in train_groups]
    names = tuple(models or MODEL_NAMES)
    if not names or len(set(names))!=len(names) or any(n not in MODEL_NAMES for n in names):
        raise ValueError('unsupported or duplicate model')
    target_x = features_for(target_event['entries'], ordered)
    results = {}
    fitted = {}
    for name in names:
        try:
            estimator = _fit(name, xx, yy, sizes)
        except ImportError as ex:
            results[name] = {'status':'MISSING_DEPENDENCY', 'error':type(ex).__name__}
            continue
        errors = []
        # Direct fixed-origin evaluation uses train event history, never validation labels.
        for _, xv, yv in val_groups:
            errors.append(_rank_error(_predict(name, estimator, xv), yv))
        # Actual temperature tuning on the later validation races. This is *not*
        # independently calibrated: the tuning races must not be described as an unseen test set.
        temperatures = (0.5, 1., 2., 3.5, 5., 7.)
        def win_logloss(temp):
            total = 0.0
            for _, xv, yv in val_groups:
                field = _predict(name, estimator, xv)
                lo, hi = min(field), max(field)
                scale = max(hi-lo, 0.5)
                weights = [math.exp(-temp*(z-lo)/scale) for z in field]
                winner = yv.index(1)
                total -= math.log(max(weights[winner]/sum(weights), 1e-12))
            return total/len(val_groups)
        temperature = min(temperatures, key=win_logloss)
        results[name] = {'status':'EVALUATED', 'holdout_event_rank_mae':round(sum(errors)/len(errors),5),
                         'validation_win_logloss_tuned':round(win_logloss(temperature),5),
                         'softmax_temperature':temperature,
                         'validation_events':len(val_groups), 'training_events':len(train_groups),
                         'kind':'baseline' if estimator is None else 'trained'}
        fitted[name] = estimator
    candidates = [(v['holdout_event_rank_mae'], name) for name,v in results.items() if v['status']=='EVALUATED']
    if not candidates:
        raise RuntimeError('no usable model; install sklearn and requested optional dependencies')
    # Model selection is in-sample to the holdout used for scoring; this is research,
    # not an unbiased final generalization metric. External test is still required.
    winner = min(candidates)[1]
    scores = _predict(winner, fitted[winner], target_x)
    probabilities = _pl_rank_probabilities(scores, temperature=results[winner]['softmax_temperature'])
    predictions = []
    for i, entry in enumerate(target_event['entries']):
        predictions.append({
            'driver_code':entry['driver_code'],
            'constructor':entry['constructor'],
            'ranking_score':round(float(scores[i]),4),
            'win_prob':probabilities[i][0], 'podium_prob':probabilities[i][1],
            'points_prob':probabilities[i][2],
        })
    predictions.sort(key=lambda row:row['ranking_score'])
    for pos,row in enumerate(predictions, 1): row['predicted_rank'] = pos
    return {'event_id':target_event['event_id'], 'as_of_timestamp':as_of_timestamp,
            'features':list(FEATURES), 'model_results':results, 'selected_model':winner,
            'predictions':predictions, 'limitations':[
                'Synthetic demo or user-supplied history; no official F1 datasets bundled',
                'Monte Carlo probabilities are not empirically calibrated',
                'Selected-model holdout scores are biased by model selection; require untouched test season',
                'Softmax temperature fitted on validation events, not externally calibrated',
                'Missing framework dependencies are reported, not silently simulated',
            ]}


def make_synthetic_events(n=16, drivers=12):
    """Deterministic artificial season fixture; never call it real F1 telemetry."""
    import random
    from datetime import timedelta, timezone
    rng = random.Random(41)
    start = datetime(2024,1,1,tzinfo=timezone.utc)
    events=[]
    codes=[f'D{i:02d}' for i in range(drivers)]
    for k in range(n):
        timestamp_ = start + timedelta(days=14*k)
        strengths={c:i for i,c in enumerate(codes)}
        shuffled=codes[:]; rng.shuffle(shuffled)
        grid={c:i+1 for i,c in enumerate(shuffled)}
        entries=[{'driver_code':c,'constructor':f'T{i//2:02d}', 'grid_pos':grid[c],
                  'clean_air_delta_s':round((i-drivers/2)*0.01,3)} for i,c in enumerate(codes)]
        race=sorted(codes,key=lambda c:0.5*grid[c]+0.35*strengths[c]+rng.gauss(0,2.3))
        events.append({'event_id':f'SIM{k:03d}','event_timestamp_utc':timestamp_.isoformat(),
                       'snapshot_timestamp_utc':(timestamp_-timedelta(hours=4)).isoformat(),
                       'entries':entries,
                       'results':[{'driver_code':c,'constructor':entries[int(c[1:])]['constructor'],
                                   'finish_pos':i+1} for i,c in enumerate(race)]})
    return events


if __name__ == '__main__':
    p=argparse.ArgumentParser(description='Research walk-forward ranking models; no official F1 data bundled')
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--synthetic-demo',action='store_true',help='Use deterministic fabricated race events only')
    source.add_argument('--events-json',help='JSON array of authorized, chronologically annotated historical race events')
    p.add_argument('--target-json',help='JSON object with entries and pre-race snapshot timestamp')
    p.add_argument('--as-of',help='ISO timestamp with timezone; mandatory for --events-json')
    p.add_argument('--output',default=None)
    args=p.parse_args()
    if args.synthetic_demo:
        ev=make_synthetic_events()
        target=ev[-1].copy()
        target['event_id']='SIM_NEXT'
        target['event_timestamp_utc']='2025-01-01T12:00:00+00:00'
        target['snapshot_timestamp_utc']='2024-12-31T18:00:00+00:00'
        cutoff='2024-12-31T20:00:00+00:00'
    else:
        if not args.target_json or not args.as_of:
            p.error('--events-json requires both --target-json and --as-of')
        ev=json.loads(Path(args.events_json).read_text(encoding='utf-8'))
        target=json.loads(Path(args.target_json).read_text(encoding='utf-8'))
        cutoff=args.as_of
    res=fit_and_evaluate(ev,target,cutoff)
    serialized=json.dumps(res,indent=2,ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(serialized+'\n',encoding='utf-8')
    else:
        print(serialized)
