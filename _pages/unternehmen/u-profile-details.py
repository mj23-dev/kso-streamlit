# pages/u-profile-details.py
import streamlit as st
import urllib.parse
import pandas as pd

st.set_page_config(page_title="KSO - Компанія деталі", layout="wide")

# Читаємо параметри з URL
query_params = st.query_params
uns_id = query_params.get('uns_id', [''])[0]
company_name = urllib.parse.unquote(query_params.get('company', [''])[0])

if not uns_id:
    st.error("❌ Відкрий через чекбокс на u-profile!")
    st.stop()

st.title(f"🏢 {company_name}")
st.caption(f"ID: {uns_id}")

# Твоя логіка підключення до DuckDB
conn = st.session_state.get("conn")
if conn is None:
    st.warning("Завантаж базу з головної!")
    st.stop()

# Завантажуємо повні деталі (твій SQL запит)
query = f"""
SELECT * FROM w_uns WHERE uns_id = '{uns_id}'
"""
df_company = conn.execute(query).fetchdf()
st.dataframe(df_company, use_container_width=True)

if st.button("❌ Закрити вкладку"):
    st.components.v1.html("<script>window.close();</script>", height=0)