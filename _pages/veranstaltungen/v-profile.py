import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
from utils.io import load_sql
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
from reflex_ag_grid import ag_grid

title = 'veranstaltungen'
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

st.subheader("📅 Activities (Veranstaltungen)")

# === 1. Завантаження даних
query = load_sql(f"{title}/sel_v_veranstaltung.sql")
df = conn.execute(query).fetchdf()
# обробляємо пусті дати
for col in df.select_dtypes(include=['datetime']):
    df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
# формуємо датафрейм
cnt_full = len(df)
cnt_filtered = len(df)

# === 2. Обробка Reset Filters ===
col_left, col_center1, col_center2, col_right = st.columns([0.65, 0.15, 0.15, 0.15])
with col_left:
    st.markdown("📋 Click checkbox to view details:")
with col_right:
    if st.button("🔄 Reset filters", use_container_width=True):
        st.session_state["reload_grid"] = True
        st.session_state["reset_grid_key"] = f"grid_{datetime.now().timestamp()}"
        st.rerun()

# === 4. AgGrid відображення
gb = GridOptionsBuilder.from_dataframe(df)

cell_renderer = JsCode("""
                        function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
                        """)

gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=100) #Add pagination
gb.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters') # Add a sidebar
gb.configure_selection(selection_mode="single", use_checkbox=True) # Enable single selection (multiple)
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)

gb.configure_column(field='datum_titel', header_name='Datum | Titel', pinned='left', filter=ag_grid.filters.multi, width=400, minWidth=200, maxWidth=1000)
gb.configure_column(field="agenda_link", headerName="Agenda link", width=200, minWidth=100, maxWidth=200,
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
gb.configure_column(field='cnt_pers', header_name='Cnt Pers', filter=ag_grid.filters.number, maxWidth=100)
gb.configure_column(field='cnt_uns', header_name='Cnt Uns', filter=ag_grid.filters.number, maxWidth=100)
gb.configure_column(field='datum_bis_year', header_name='Year Bis', filter=ag_grid.filters.multi, maxWidth=100)
gb.configure_column(field='format', header_name='Format', filter=ag_grid.filters.multi, maxWidth=100)
gb.configure_column(field='bundesland', header_name='Place', filter=ag_grid.filters.multi, width=150, minWidth=100, maxWidth=500)
gb.configure_column(field='akt_org', header_name='Organizer', filter=ag_grid.filters.multi, width=200, minWidth=100, maxWidth=500)
gb.configure_column(field='akt_spn', header_name='Sponsor', filter=ag_grid.filters.multi, width=200, minWidth=100, maxWidth=1000)
gb.configure_column(field='aktivitaten_id', header_name='ID', filter=ag_grid.filters.multi, headerCheckboxSelection = True, maxWidth=125)
gb.configure_column(field='datum_bis', header_name='Datum Bis', type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.date, maxWidth=125)
gb.configure_column(field='titel', header_name='Titel', filter=ag_grid.filters.multi, width=200, minWidth=100, maxWidth=1000)
gb.configure_column(field='adr_full', header_name='Adress', filter=ag_grid.filters.multi, width=200, minWidth=100, maxWidth=500)
# gb.configure_columns(["aktivitaten_id", "datum_titel", "format", "datum_bis_year", "datum_bis", "titel"], filterParams={"buttons": ['apply', 'clear']})

grid_options = gb.build()
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    enable_enterprise_modules=True,
    update_mode="GRID_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
    data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
    fit_columns_on_grid_load=False,
    theme="blue", # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
    pagination_page_size_selector=[20, 50, 100],
    height=285, # = 7 rows
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

# === 6. Деталі вибраного рядка
selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected)
if len(selected_df) > 0:
    placeholder_col = st.empty()
    col_left, col_right = placeholder_col.columns([0.5, 0.5])
    with col_left:
        if selected_df.iloc[0]['akt_org'] != '-':
            st.markdown(f"**Organizer:**")
            for item in selected_df.iloc[0]['akt_org'].split('|'):
                st.text(f"🔸{item.strip()}")
        st.markdown(f"**Address:** {selected_df.iloc[0]['adr_full']}")
    with col_right:
        if selected_df.iloc[0]['akt_spn'] != '-':
            st.markdown(f"**Sponsor:**")
            for item in selected_df.iloc[0]['akt_spn'].split('|'):
                st.text(f"🔹{item.strip()}")

    st.markdown("**Participants:**")
    with st.spinner("⏳ Loading ..."):
        # 1. Очистити попередній DataFrame (опціонально — для візуального ефекту)
        placeholder = st.empty()  # створюємо місце, де з'явиться таблиця
        time.sleep(2)  # штучна пауза

        # 2. Наповнюємо вкладки
        selected_id = selected_df.iloc[0]['aktivitaten_id']
        query1 = f"""
                    SELECT wv.vorname, wv.nachname, wv.anrede, wv.titel_vorne, wv.titel_hinten, wv.pers_rolle, wv.kso_pers_position,
                            concat_ws('; ', wv.email1, wv.email2, wv.email3) as email,
                            wv.pers_mitg, wv.pers_mitg_maxd, 
                            wv.vollname_der_firma, wv.uns_mitg, wv.uns_mitg_maxd,
                            wu.product_name_agg,
                            wv.uns_id, wv.pers_id, wv.aktivitaten_id, wv.datum_titel
                    FROM w_veranstaltung wv
                    LEFT JOIN w_uns wu ON wv.uns_id = wu.uns_id
                    WHERE wv.aktivitaten_id = '{selected_id}'
                    and not(wv.uns_id is null and wv.pers_id is null)
                    ORDER BY wv.vollname_der_firma, wv.nachname, wv.vorname
                    """
        df1 = conn.execute(query1).fetchdf()

        query2 = f"""
                    select distinct
                            wv.vollname_der_firma, wu.seite, wu.email, wu.telefonnummer, wu.rechtsform, wu.product_name_agg, wu.tatigkeitsbeschreibung, 
                            wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id as last_akt_id, strftime(wu.akt_maxd, '%Y-%m-%d') || ' | ' || wu.akt_titel as akt_datum_titel,
                            wu.juradr_land, wu.juradr_bundesland, wu.juradr_plz_ort, wu.juradr_strasse,
                            wu.heaf, wu.uns_id, wu.hauptunternehmen_id, wv.aktivitaten_id, wv.datum_titel
                    from w_veranstaltung wv
                    inner join w_uns wu on wv.uns_id = wu.uns_id
                    where wv.aktivitaten_id = '{selected_id}'
                    order by wv.vollname_der_firma
                """
        df2 = conn.execute(query2).fetchdf()

        tab1, tab2 = placeholder.tabs([f"Personen ({str(len(df1))})", f"Unternehmen ({str(len(df2))})"])
        with tab1:
            dfheight1 = 0 if len(df1) == 0 else 40.7 * min(len(df1),10)
            # обробляємо пусті дати
            for col in df1.select_dtypes(include=['datetime']):
                df1[col] = df1[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
            # формуємо датафрейм
            gb1 = GridOptionsBuilder.from_dataframe(df1)
            gb1.configure_pagination(enabled=True, paginationAutoPageSize=False,paginationPageSize=100)  # Add pagination
            gb1.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters')  # Add a sidebar
            # gb1.configure_selection(selection_mode="single", use_checkbox=True)  # Enable single selection (multiple)
            gb1.configure_column(field='vorname', header_name='Vorname', pinned='left', filter=ag_grid.filters.multi, maxWidth=150)
            gb1.configure_column(field='nachname', header_name='Nachname', pinned='left', filter=ag_grid.filters.multi, maxWidth=150)
            gb1.configure_column(field='anrede', header_name='Anrede', filter=ag_grid.filters.multi, maxWidth=100)
            gb1.configure_column(field='titel_vorne', header_name='Titel vorne', filter=ag_grid.filters.multi, maxWidth=100)
            gb1.configure_column(field='titel_hinten', header_name='Titel Hinten', filter=ag_grid.filters.multi, maxWidth=100)
            gb1.configure_column(field='pers_rolle', header_name='Rolle', filter=ag_grid.filters.multi, maxWidth=100)
            gb1.configure_column(field='kso_pers_position', header_name='KSO Position', filter=ag_grid.filters.multi, maxWidth=150)
            gb1.configure_column(field='email', header_name='Email', filter=ag_grid.filters.multi, maxWidth=500)
            gb1.configure_column(field='pers_mitg', header_name='Pers Mitg', filter=ag_grid.filters.multi, maxWidth=100)
            gb1.configure_column(field='pers_mitg_maxd', header_name='Pers Mitg MaxDatum', type=["customDateTimeFormat"],
                                custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.date, maxWidth=125)
            gb1.configure_column(field='vollname_der_firma', header_name='Vollname der firma', filter=ag_grid.filters.multi, minWidth=200, maxWidth=500)
            gb1.configure_column(field='product_name_agg', header_name='Uns Product', filter=ag_grid.filters.multi, maxWidth=250)
            gb1.configure_column(field='uns_mitg', header_name='Uns Mtg', filter=ag_grid.filters.multi, maxWidth=100)
            gb1.configure_column(field='uns_mitg_maxd', header_name='Uns Mtg MaxDatum', type=["customDateTimeFormat"],
                                custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.date, maxWidth=125)
            gb1.configure_column(field='uns_id', header_name='ID Uns', filter=ag_grid.filters.multi, maxWidth=120)
            gb1.configure_column(field='pers_id', header_name='ID Pers', filter=ag_grid.filters.multi, maxWidth=120)
            gb1.configure_column(field='aktivitaten_id', header_name='ID Akt', filter=ag_grid.filters.multi, maxWidth=120)
            gb1.configure_column(field='datum_titel', header_name='Datum | Titel', filter=ag_grid.filters.multi, minWidth=200, maxWidth=500)

            grid_options1 = gb1.build()
            grid_response1 = AgGrid(
                df1,
                gridOptions=grid_options1,
                enable_enterprise_modules=True,
                update_mode="SELECTION_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
                data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
                theme="blue", # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
                pagination_page_size_selector=[10, 20, 50, 100],
                height=dfheight1,  # = 7 rows
                width='100%',
                header_checkbox_selection_filtered_only=True,
                show_toolbar=True, show_search=False, show_download_button=False,
                allow_unsafe_jscode=True,
                reload_data=True,
            )
        with tab2:
            dfheight2 = 0 if len(df2) == 0 else 40.7 * min(len(df2),10)
            # обробляємо пусті дати
            for col in df2.select_dtypes(include=['datetime']):
                df2[col] = df2[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
            # формуємо датафрейм
            gb2 = GridOptionsBuilder.from_dataframe(df2)
            cell_renderer = JsCode(""" function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`} """)
            gb2.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=100)  # Add pagination
            gb2.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters')  # Add a sidebar
            # gb2.configure_selection(selection_mode="single", use_checkbox=True)  # Enable single selection (multiple)
            gb2.configure_column(field='vollname_der_firma', header_name='Vollname der firma', pinned='left', filter=ag_grid.filters.text, minWidth=400, maxWidth=400)
            gb2.configure_column(
                "seite",
                headerName="Link",
                minWidth=250, maxWidth=500,
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
            gb2.configure_column(field='email', header_name='Email', filter=ag_grid.filters.multi, minWidth=200, maxWidth=500)
            gb2.configure_column(field='juradr_land', header_name='Land', filter=ag_grid.filters.multi, maxWidth=150)
            gb2.configure_column(field='juradr_bundesland', header_name='Bundesland', filter=ag_grid.filters.multi, maxWidth=150)
            gb2.configure_column(field='juradr_plz_ort', header_name='PLZ-Ort', filter=ag_grid.filters.multi, maxWidth=150)
            gb2.configure_column(field='juradr_strasse', header_name='Strasse', filter=ag_grid.filters.multi, maxWidth=150)
            gb2.configure_column(field='rechtsform', header_name='Rechtsform', filter=ag_grid.filters.multi, minWidth=200, maxWidth=500)
            gb2.configure_column(field='product_name_agg', header_name='Product', filter=ag_grid.filters.multi, minWidth=200, maxWidth=1000)
            gb2.configure_column(field='tatigkeitsbeschreibung', header_name='Tatigkeitsbeschreibung', filter=ag_grid.filters.multi, minWidth=200, maxWidth=1000)
            gb2.configure_column(field='last_akt_id', header_name='Last Akt ID', filter=ag_grid.filters.multi, maxWidth=120)
            gb2.configure_column(field='akt_datum_titel', header_name='Last aktivitaten', filter=ag_grid.filters.multi, maxWidth=200)
            gb2.configure_column(field='heaf', header_name='Heaf', filter=ag_grid.filters.multi, maxWidth=100)
            gb2.configure_column(field='product_name_agg', header_name='Uns Product', filter=ag_grid.filters.multi,maxWidth=250)
            gb2.configure_column(field='uns_mitg', header_name='Uns Mitg', filter=ag_grid.filters.multi, maxWidth=100)
            gb2.configure_column(field='uns_mitg_maxd', header_name='Uns Mitg MaxDatum', type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.date, maxWidth=125)
            gb2.configure_column(field='uns_id', header_name='ID uns', filter=ag_grid.filters.multi, maxWidth=120)
            gb2.configure_column(field='hauptunternehmen_id', header_name='ID haup', filter=ag_grid.filters.multi, maxWidth=120)
            gb2.configure_column(field='aktivitaten_id', header_name='ID akt', filter=ag_grid.filters.multi, maxWidth=120)
            gb2.configure_column(field='datum_titel', header_name='Datum | Titel', filter=ag_grid.filters.multi, minWidth=200, maxWidth=500)

            grid_options2 = gb2.build()
            grid_response2 = AgGrid(
                df2,
                gridOptions=grid_options2,
                enable_enterprise_modules=True,
                update_mode="SELECTION_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
                data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
                theme="blue", # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
                pagination_page_size_selector=[10, 20, 50, 100],
                height=dfheight2,  # = 7 rows
                width='100%',
                header_checkbox_selection_filtered_only=True,
                show_toolbar=True, show_search=False, show_download_button=False,
                allow_unsafe_jscode=True,
                reload_data=True,
            )
