import streamlit as st
import pandas as pd
import io
from utils.io import load_sql

conn = st.session_state.get("conn")
if conn is None:
    st.warning("Спочатку потрібно завантажити базу через головну сторінку.")
    st.stop()

title = 'personen'
st.header("👨‍💼 Personen")

# виконуємо запит
query = load_sql(f"{title}/sel_v_pers.sql")
df = conn.execute(query).fetchdf()

# Фільтри (приклад по одному полю)
name_filter = st.text_input("🔍 Пошук за назвою:", "")
if name_filter:
    df = df[df["nachname"].str.contains(name_filter, case=False, na=False)]

# відображаємо результат
st.dataframe(df)

# Експорт
buffer = io.BytesIO()

df.to_excel(f'{title}.xlsx', index=False)
with open(f'{title}.xlsx', "rb") as f:
    st.download_button("⬇️ Export results to XLSX", f, file_name=f'{title}.xlsx', mime="text/csv")

