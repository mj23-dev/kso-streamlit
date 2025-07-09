import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils.io import load_sql
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
from reflex_ag_grid import ag_grid

# === Підключення до бази ===
conn = st.session_state.get("conn")
if conn is None:
    st.warning("You need to upload database file from hauptsite!")
    st.stop()

# === Видалення прапорця перезавантаження після ререндеру ===
if "reload_grid" in st.session_state:
    del st.session_state["reload_grid"]

if "reset_grid_key" not in st.session_state:
    st.session_state["reset_grid_key"] = "grid_default"

title = 'unternehmen'
st.header("🏢 Unternehmen v2")

# === 1. Завантаження даних
query = load_sql(f"{title}/sel_v_uns.sql")
df = conn.execute(query).fetchdf()
cnt_full = len(df)
cnt_filtered = len(df)

# === 2. Обробка Reset Filters ===
col_left, col_center1, col_center2, col_right = st.columns([0.65, 0.15, 0.15, 0.15])
with col_left:
    st.markdown("📋 Click checkbox to view details:")
with col_right:
    if st.button("🔄 Reset filters", use_container_width=True):
        for key in ["name_filter", "selected_land", "selected_bundesland", "selected_form"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["name_filter"] = ""
        st.session_state["selected_land"] = "--All--"
        st.session_state["selected_bundesland"] = "--All--"
        st.session_state["selected_form"] = "--All--"
        st.session_state["reload_grid"] = True
        st.session_state["reset_grid_key"] = f"grid_{datetime.now().timestamp()}"
        st.rerun()

# === 3. Фільтри ===
# expander = st.expander("Use advanced filters 👇", expanded=False)
# col1, col2, col3, col4, col5 = expander.columns([0.2, 0.2, 0.2, 0.2, 0.2])
#
# name_filter = col1.text_input("🔍 vollname_der_firma like '?'", key="name_filter", help='Like statement')
# if name_filter:
#     df = df[df["vollname_der_firma"].str.contains(name_filter, case=False, na=False)]
#     cnt_filtered = len(df)
#
# selected_land = col2.selectbox("🔍 Select Land", ['--All--'] + sorted(df['juradr_land'].dropna().unique()), key="selected_land")
# if selected_land != '--All--':
#     df = df[df['juradr_land'] == selected_land]
#     cnt_filtered = len(df)
#
# selected_bundesland = col2.selectbox("🔍 Select Bundesland", ['--All--'] + sorted(df['juradr_bundesland'].dropna().unique()), key="selected_bundesland")
# if selected_bundesland != '--All--':
#     df = df[df['juradr_bundesland'] == selected_bundesland]
#     cnt_filtered = len(df)
#
# selected_form = col3.selectbox("🔍 Select Rechtsform", ['--All--'] + sorted(df['rechtsform'].dropna().unique()), key="selected_form")
# if selected_form != '--All--':
#     df = df[df['rechtsform'] == selected_form]
#     cnt_filtered = len(df)

# === 4. AgGrid відображення
gb = GridOptionsBuilder.from_dataframe(df)

cell_renderer = JsCode("""
                        function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
                        """)

gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10) #Add pagination
# gb.configure_side_bar(filters_panel=True, columns_panel=True) # Add a sidebar
gb.configure_side_bar(filters_panel=True, columns_panel=True) # Add a sidebar
gb.configure_selection(selection_mode="single", use_checkbox=True) # Enable single selection (multiple)
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_column(field='uns_id', header_name='Id', filter=ag_grid.filters.text, headerCheckboxSelection = True)
gb.configure_column(field='vollname_der_firma', header_name='Vollname', filter=ag_grid.filters.text)
gb.configure_column(field='juradr_land', header_name='Land', filter=ag_grid.filters.text)
gb.configure_column(field='juradr_bundesland', header_name='Bundesland', filter=ag_grid.filters.text)
gb.configure_column(field='rechtsform', header_name='Rechtsform', filter=ag_grid.filters.text)
gb.configure_column(field='product_name_agg', header_name='Product', filter=ag_grid.filters.text)
gb.configure_column(field='registrierungsstatus', header_name='Registrierungsstatus', filter=ag_grid.filters.text)
gb.configure_column(field='akt_titel', header_name='Lasrt aktivitaten', filter=ag_grid.filters.text)
gb.configure_column(field='heaf', header_name='Heaf', filter=ag_grid.filters.text)

gb.configure_columns(["uns_id", "vollname_der_firma", "juradr_land", "juradr_bundesland", "rechtsform", "product_name_agg", "registrierungsstatus", "akt_titel", "heaf"], filterParams={"buttons": ['apply', 'clear']})
gb.configure_column(
    "seite",
    headerName="link",
    # width=100,
    cellRenderer=JsCode("""
        class UrlCellRenderer {
          init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = params.value;
            this.eGui.setAttribute('href', params.value);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
          }
          getGui() {
            return this.eGui;
          }
        }
    """)
)

grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    enable_enterprise_modules=True,
    update_mode="GRID_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
    data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
    theme="blue", # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
    pagination_page_size_selector=[10, 20, 50, 100, 1000],
    height=375,
    width='100%',
    header_checkbox_selection_filtered_only=True,
    show_toolbar=True, show_search=False, show_download_button=False,
    allow_unsafe_jscode=True,
    reload_data=True,
    # key=f"grid_{datetime.now().timestamp()}" if st.session_state.get("reload_grid") else "grid_default"
    key=st.session_state["reset_grid_key"]
)

filtered_df = pd.DataFrame(grid_response['data'])
cnt_filtered = len(filtered_df)

# with col_center1:
#     st.markdown(f"📊 Records: {cnt_filtered}/{cnt_full}")

# === 5. Експорт
# with col_right:
#     file_exp = f"{title}_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx"
#     # filtered_df.to_excel(file_exp, index=False)
#     df.to_excel(file_exp, index=False)
#     with open(file_exp, "rb") as f:
#         st.download_button(
#             label="⬇️ Export XLSX",
#             data=f,
#             file_name=file_exp,
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             # help=f"Records: {len(filtered_df)}/{cnt_full}",
#             use_container_width=True
#         )

# === 6. Деталі вибраного рядка
selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected)
if len(selected_df) > 0:
    with st.spinner("⏳ Loading ..."):
        # 1. Очистити попередній DataFrame (опціонально — для візуального ефекту)
        placeholder = st.empty()  # створюємо місце, де з'явиться таблиця
        time.sleep(2)  # штучна пауза

        # 2. Наповнюємо вкладки
        tab1, tab2 = placeholder.tabs(["Personen", "Full details"])
        with tab1:
            selected_uns_id = selected_df.iloc[0]['uns_id']
            query = f"""
                SELECT wlup.pers_id, wp.vorname, wp.nachname, 
                       concat_ws('; ', wlup.email1, wlup.email2, wlup.email3, wlup.email4, wlup.email5) as email,
                       wlup.pers_kategorie, wlup.pers_position,
                       wp.anrede, wp.titel_vorne, wp.titel_hinten, 
                       wu.uns_id
                FROM w_uns wu
                INNER JOIN main.w_links_uns_pers wlup ON wu.uns_id = wlup.uns_id
                INNER JOIN main.w_pers wp ON wlup.pers_id = wp.pers_id
                WHERE wu.uns_id = '{selected_uns_id}'
                ORDER BY 3,2
            """
            df1 = conn.execute(query).fetchdf()

            # Поза межами spinner — вивід даних
            st.dataframe(
                df1,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "pers_id": st.column_config.Column(width=50),
                    "uns_id": st.column_config.Column(width=50),
                    "email": st.column_config.Column(width="medium")
                }
            )
        with tab2:
            selected_uns_id = selected_df.iloc[0]['uns_id']
            query = f"SELECT * FROM w_uns WHERE uns_id = '{selected_uns_id}'"
            df2 = conn.execute(query).fetchdf()

            stacked = (
                df2.stack()
                .reset_index()
                .rename(columns={"level_1": "Field", 0: "Value"})
                .drop(columns=["level_0"])
            )
            stacked["Value"] = stacked["Value"].astype(str)

            st.dataframe(
                stacked,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Field": st.column_config.Column(width="small"),
                    "Value": st.column_config.Column(width="large")
                }
            )