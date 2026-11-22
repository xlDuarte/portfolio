"""Export observed FastF1 lap telemetry for the corner comparison tool.
Install fastf1; python export_fastf1.py 2024 Bahrain R VER --lap 5
Distance is integrated by FastF1, not surveyed circuit distance.
"""
import argparse
import json
from pathlib import Path
import fastf1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('year', type=int)
    parser.add_argument('event')
    parser.add_argument('session')
    parser.add_argument('driver')
    parser.add_argument('--lap', type=int)
    parser.add_argument('--output', default='fastf1-corner.csv')
    args = parser.parse_args()
    session = fastf1.get_session(args.year, args.event, args.session)
    session.load()
    laps = session.laps.pick_drivers(args.driver)
    if args.lap is None:
        lap = laps.pick_fastest()
    else:
        selected = laps[laps.LapNumber == args.lap]
        if len(selected) != 1:
            raise ValueError('Lap not found or ambiguous')
        lap = selected.iloc[0]
    if lap is None:
        raise ValueError('No valid lap available')
    telemetry = lap.get_car_data().add_distance()
    data = telemetry[['Time', 'Distance', 'Speed']].copy()
    data['Time'] = data['Time'].dt.total_seconds()
    data.columns = ['time_s', 'distance_m', 'speed_kmh']
    data = data.dropna()
    if len(data) < 3 or not (data.time_s.diff().dropna() > 0).all() or not (data.distance_m.diff().dropna() > 0).all():
        raise ValueError('Non-monotonic telemetry; cannot export')
    data.distance_m -= data.distance_m.iloc[0]
    output = Path(args.output)
    data.to_csv(output, index=False)
    output.with_suffix('.metadata.json').write_text(json.dumps({
        'provider': 'FastF1', 'year': args.year, 'event': args.event,
        'session': args.session, 'driver': args.driver, 'lap': int(lap.LapNumber),
        'distance_method': 'integrated speed; zero at first telemetry sample',
        'limitation': 'Check spatial alignment between drivers before comparing corners.'
    }, indent=2))


if __name__ == '__main__':
    main()
