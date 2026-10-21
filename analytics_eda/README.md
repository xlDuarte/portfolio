# EDA 011–020

10 different domain datasets generated with fixed NumPy seeds. All are SYNTHETIC and explicitly not real business, F1, jobs or equity data.

```bash
pip install -r requirements-eda.txt
python -m analytics_eda.generate
python -m analytics_eda.engine 011 --report-dir /tmp/eda11
python -m unittest discover -s tests -v
```

Tools executed: Pandas, NumPy, sqlite3 SQL, Seaborn, Matplotlib, Plotly. Plotly interactivity from exported HTML requires external CDN; static SVG is always present.
