import os, re

def load_sql(file_name: str) -> str:
    """Завантажує SQL-файл з папки /sql незалежно від місця виклику."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # до папки з app.py
    path = os.path.join(base, "sql", file_name)
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
        sql = re.sub('kso_web.main.', '', sql)
        sql = re.sub('kso.main.', '', sql)
        return sql
