import streamlit as st
import pandas as pd
import time, io, base64
import streamlit.components.v1 as components
from datetime import datetime
from utils.io import load_sql
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
# from reflex_ag_grid import ag_grid

title = 'export'
st.set_page_config(page_title=f"KSO-Db v1.0 - {title}", layout="wide")

conn = st.session_state.get("conn")
if conn is None:
    st.warning("You need to upload database file from hauptsite!")
    st.stop()

# === Видалення прапорця перезавантаження після ререндеру ===
if "reload_grid" in st.session_state:
    del st.session_state["reload_grid"]

if "reset_grid_key" not in st.session_state:
    st.session_state["reset_grid_key"] = "grid_default"

st.subheader("🏢 Unternehmen (Сompanies)")

# =============================================================== 1.1 Профіль
query = load_sql(f"{title}/u-profile.sql")
df11 = conn.execute(query).fetchdf()
# обробляємо пусті дати
for col in df11.select_dtypes(include=['datetime']):
    df11[col] = df11[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')

# Create an in-memory buffer to hold the binary Excel data
buffer = io.BytesIO()

# Write the DataFrame to the buffer using openpyxl engine
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df11.to_excel(writer, index=False, sheet_name='Export')

# Reset buffer pointer to the beginning so it can be read completely
buffer.seek(0)

st.download_button(
    label="⬇️ Download file: Profile",
    data=buffer,
    file_name = f"u-profile_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================================== 1.2 звязки uns_pers
query = load_sql(f"{title}/u-links_uns_pers.sql")
df12 = conn.execute(query).fetchdf()

# Create an in-memory buffer to hold the binary Excel data
buffer12 = io.BytesIO()


merged_df = pd.merge(df11, df12, on='uns_id', how='left')
insert_after_column = 'compass_id'  # додаємо нову колонку після
col_index = merged_df.columns.get_loc(insert_after_column)
merged_df.insert(col_index + 1, 'dtype', 'PersLinked ->')
towrite = io.BytesIO()

# Write the DataFrame to the buffer using openpyxl engine
with pd.ExcelWriter(buffer12, engine='openpyxl') as writer:
    merged_df.to_excel(writer, index=False, sheet_name='Export')

# Reset buffer pointer to the beginning so it can be read completely
buffer12.seek(0)

st.download_button(
    label="⬇️ Download file: Profile + Personen",
    data=buffer12,
    file_name = f"u-links_personen_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================================== 3.1 onace
query = load_sql(f"{title}/u-onace.sql")
df31 = conn.execute(query).fetchdf()

# Create an in-memory buffer to hold the binary Excel data
buffer31 = io.BytesIO()

# Write the DataFrame to the buffer using openpyxl engine
with pd.ExcelWriter(buffer31, engine='openpyxl') as writer:
    df31.to_excel(writer, index=False, sheet_name='Export')

# Reset buffer pointer to the beginning so it can be read completely
buffer31.seek(0)

st.download_button(
    label="⬇️ Download file: ÖNACE",
    data=buffer31,
    file_name = f"u-onace_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================================== 4.1 onace
query = load_sql(f"{title}/u-product.sql")
df41 = conn.execute(query).fetchdf()

# Create an in-memory buffer to hold the binary Excel data
buffer41 = io.BytesIO()

# Write the DataFrame to the buffer using openpyxl engine
with pd.ExcelWriter(buffer41, engine='openpyxl') as writer:
    df41.to_excel(writer, index=False, sheet_name='Export')

# Reset buffer pointer to the beginning so it can be read completely
buffer41.seek(0)

st.download_button(
    label="⬇️ Download file: Compass-Kategorien",
    data=buffer41,
    file_name = f"u-product_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)