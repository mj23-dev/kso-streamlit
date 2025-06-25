import streamlit as st
import pandas as pd
import io

def show(conn):
    title = 'personen'
    st.header("🏢 Personen (v_pers)")
    df = conn.execute("SELECT * FROM v_pers").df()

    # Фільтри (приклад по одному полю)
    name_filter = st.text_input("🔍 Пошук за назвою:", "")
    if name_filter:
        df = df[df["nachname"].str.contains(name_filter, case=False, na=False)]

    st.dataframe(df)

    # Експорт
    df.to_excel(f'{title}.xlsx', index=False)
    with open(f'{title}.xlsx', "rb") as f:
        st.download_button("⬇️ Export results to XLSX", f, file_name=f'{title}.xlsx', mime="text/csv")
