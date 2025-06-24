import streamlit as st
import duckdb
import pandas as pd
import tempfile
import os

st.set_page_config(page_title="KSO Viewer", layout="wide")

st.title("📂 KSO Viewer")

# === КРОК 1: Завантаження файлу бази ===
uploaded_file = st.file_uploader("Завантажте базу даних (kso.db)", type=["db"])

if uploaded_file:
    # === КРОК 2: Збереження у тимчасовий файл ===
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(uploaded_file.read())
        db_path = tmp.name

    # === КРОК 3: Підключення до бази ===
    try:
        conn = duckdb.connect(db_path)
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]
    except Exception as e:
        st.error(f"Помилка при підключенні до бази: {e}")
        os.remove(db_path)
        st.stop()

    # === КРОК 4: Вибір таблиці та перегляд ===
    st.sidebar.header("📋 Таблиці")
    selected_table = st.sidebar.selectbox("Оберіть таблицю:", table_names)

    df = conn.execute(f"SELECT * FROM {selected_table}").df()
    st.markdown(f"### 🔎 Дані з таблиці `{selected_table}`")
    st.dataframe(df, use_container_width=True)

    # === КРОК 5: Експорт у CSV ===
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Експортувати у CSV", csv, file_name=f"{selected_table}.csv", mime="text/csv")

    # === КРОК 6: Очищення після завершення ===
    @st.cache_resource(show_spinner=False)
    def cleanup_duckdb(path):
        def _clean():
            if os.path.exists(path):
                os.remove(path)
        return _clean

    cleanup_duckdb(db_path)

else:
    st.info("👈 Завантажте локальний `.duckdb` файл для перегляду вмісту.")
