import streamlit as st
import pandas as pd
import io

conn = st.session_state.get("conn")
if conn is None:
    st.warning("Спочатку потрібно завантажити базу через головну сторінку.")
    st.stop()

title = 'unternehmen'
st.header("🏢 Unternehmen (v_uns)")

df = conn.execute("SELECT * FROM v_uns").df()

# Фільтри (приклад по одному полю)
name_filter = st.text_input("🔍 Пошук за назвою:", "")
if name_filter:
    df = df[df["vollname_der_firma"].str.contains(name_filter, case=False, na=False)]

st.dataframe(df)

# Експорт
buffer = io.BytesIO()

df.to_excel(f'{title}.xlsx', index=False)
with open(f'{title}.xlsx', "rb") as f:
    st.download_button("⬇️ Export results to XLSX", f, file_name=f'{title}.xlsx', mime="text/csv")

