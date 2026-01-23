import streamlit as st
import duckdb
import pandas as pd
from utils.db import connect_temp_duckdb
# from streamlit_option_menu import option_menu

# st.set_page_config(page_title="KSO-Db v1.0", layout="wide")

# === КРОК 1: Завантаження файлу бази ===
st.title("KSO DataWarehouse ⚡")

st.header("To continue work with DB - please upload local database file 'kso_web.db':")

expander = st.expander("🔌 DB connection:", expanded=True)
uploaded_file = expander.file_uploader("Upload database file (kso_web.db)", type=["db"])
if not uploaded_file:
    # st.warning("⬅️ Upload local database file 'kso.db'.")
    st.stop()
else:
    pass

# === КРОК 2: Підключення до тимчасового duckdb ===
conn, db_path = connect_temp_duckdb(uploaded_file)

st.session_state["conn"] = conn
st.session_state["db_path"] = db_path

if conn:
    st.header("Use menu to navigate data: Unternehmen, Personen, ...")
