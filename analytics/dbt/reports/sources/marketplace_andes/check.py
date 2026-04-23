import duckdb
conn = duckdb.connect('analytics.duckdb')
tables = conn.execute("SHOW ALL TABLES").fetchall()
for t in tables:
    if 'raw' in t[1]:  # solo las del dataset raw
        print(t[2])