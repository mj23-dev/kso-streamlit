import streamlit as st
import duckdb, os
import pandas as pd

from utils.db import connect_temp_duckdb

st.set_page_config(page_title="KSO-Db v1.0",
                page_icon="icon/kso.png",
                layout="wide")

pages = {
    "🏠 Startseite": [st.Page("hauptseite.py", title="🛠️ Set database")],
    "🏢 Unternehmen": [
        st.Page("_pages/unternehmen/unternehmen01.py", title="📁 Unternehmen v1"),
        st.Page("_pages/unternehmen/unternehmen02.py", title="📂 Unternehmen v2"),
        st.Page("_pages/unternehmen/product01.py", title="💶 Products"),
    ],
    "🧑‍💼 Personen": [
        st.Page("_pages/personen/personen01.py", title="👤 Personen"),
    ],
    "📅 Veranstaltungen": [
        st.Page("_pages/veranstaltungen/veranstaltungen01.py", title="🪪 Page 1"),
    ],
    "📊 Berichte": [
        st.Page("_pages/berichte/berichte01.py", title="📈 Page 1"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()
