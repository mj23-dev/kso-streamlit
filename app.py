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
        # st.Page("_pages/unternehmen/unternehmen01.py", title="📁 Unternehmen v1"),
        st.Page("_pages/unternehmen/u-profile.py", title="📰 Profile"),
        st.Page("_pages/unternehmen/u-profile-itables.py", title="📰 Profile-test"),
        # st.Page("_pages/unternehmen/u-profile-details.py", title="📰 Profile2"),
        st.Page("_pages/unternehmen/u-member.py", title="💰 Mitglieder"),
        st.Page("_pages/unternehmen/u-onace.py", title="🎯 ÖNACE"),
        st.Page("_pages/unternehmen/u-product.py", title="💶 Compass-Kategorien"),
    ],
    "🧑🏻‍💼Personen": [
        st.Page("_pages/personen/p-profile.py", title="📰 Profile"),
        st.Page("_pages/personen/p-member.py", title="💰 Mitglieder"),
    ],
    "📅 Veranstaltungen": [
        st.Page("_pages/veranstaltungen/v-profile.py", title="🪪 Profile"),
        st.Page("_pages/veranstaltungen/v-participant.py", title="🙋 Participant Plan/Fact"),
    ],
    "📊 KSÖ-OrgStruktur": [
        st.Page("_pages/berichte/b-management.py", title="💼 KSO-Management"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()