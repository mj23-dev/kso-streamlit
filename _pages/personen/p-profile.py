import streamlit as st
import pandas as pd
import time, io, base64
import streamlit.components.v1 as components
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

title = 'personen'
st.subheader("👤 Personen (Persons)")

# === 1. Завантаження даних
query = load_sql(f"{title}/sel_profile.sql")
df = conn.execute(query).fetchdf()
# обробляємо пусті дати
for col in df.select_dtypes(include=['datetime']):
    df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')

# звязки uns_pers для експорту
query = load_sql(f"{title}/sel_w_links_uns_pers.sql")
df_pers = conn.execute(query).fetchdf()

cnt_full = len(df)
cnt_filtered = len(df)

# === 2. Обробка Reset Filters ===
# col_left, col_center1, col_center2, col_right = st.columns([0.65, 0.15, 0.15, 0.15])
col_left, col_center1, col_right = st.columns([0.55, 0.15, 0.25])
with col_left:
    st.markdown("✔️ Klicken Sie auf das Checkbox, um Details anzuzeigen:")
with col_center1:
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
# gb.configure_side_bar(filters_panel=True, columns_panel=True) # Add a sidebar
gb.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters') # Add a sidebar
gb.configure_selection(selection_mode="single", use_checkbox=True) # Enable single selection (multiple)
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)

gb.configure_column(field='vorname', header_name='Vorname', pinned='left', filter=ag_grid.filters.multi, headerCheckboxSelection = True, width=150)
gb.configure_column(field='nachname', header_name='Nachname', pinned='left', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='pers_id', header_name='ID Pers', filter=ag_grid.filters.multi, width=140)
gb.configure_column(field='pers_mitg', header_name='MG', filter=ag_grid.filters.multi, width=80)
gb.configure_column(field='pers_mitg_maxd', header_name='Letzte MG Data', type=["customDateTimeFormat"],custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.multi, width=120)
gb.configure_column(field='anrede', header_name='Anrede', filter=ag_grid.filters.multi)
gb.configure_column(field='titel_vorne', header_name='Titel Vorne', filter=ag_grid.filters.multi)
gb.configure_column(field='titel_hinten', header_name='Titel Hinten', filter=ag_grid.filters.multi)
gb.configure_column(field='telefonnummer', header_name='Telefonnummer', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='geburtsdatum', header_name='Geburtsdatum', type=["customDateTimeFormat"],custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.multi)
gb.configure_column(field='sprachen', header_name='Sprachen', filter=ag_grid.filters.multi)
gb.configure_column(field='email1', header_name='Email1', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='email2', header_name='Email2', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='email3', header_name='Email3', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='email4', header_name='Email4', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='email5', header_name='Email5', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='rechnungs_email1', header_name='RchnEmail1', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='rechnungs_email2', header_name='RchnEmail2', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='rechnungs_email3', header_name='RchnEmail3', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='domain', header_name='Domain', filter=ag_grid.filters.multi, width=150)

gb.configure_column(field='juradr_land', header_name='Land', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='juradr_bundesland', header_name='Bundesland', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='adr_plz_ort', header_name='Plz-Ort', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='strasse', header_name='Strasse', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='juradr_full', header_name='Adresse', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='akt_maxd', header_name='Letzte Akt Data', type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.multi, width=130)
gb.configure_column(field='akt_titel', header_name='Letzte Akt Titel', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='aktivitaten_id', header_name='ID Akt', filter=ag_grid.filters.multi, width=120)
gb.configure_column(field='cnt_uns', header_name='Cnt Uns', filter=ag_grid.filters.number, width=100)
gb.configure_column(field='vollname_der_firma_aggr', header_name='Uns Voller Name', filter=ag_grid.filters.multi)
gb.configure_column(field='kurzbezeichnung_aggr', header_name='Uns Gekürzter Name', filter=ag_grid.filters.multi)

grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    enable_enterprise_modules=True,
    update_mode="GRID_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
    data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
    theme="blue", # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
    pagination_page_size_selector=[20, 50, 100],
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

# === 5. Експорт
with col_right:
    with st.popover("⬇️ Export XLS", use_container_width=True):
        col_left_exp, col_right_exp = st.columns([0.5,0.5])
        with col_left_exp:
            if st.button("🔄 Pers", use_container_width=True):
                file_exp1 = f"p-profile_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx"
                towrite = io.BytesIO()
                filtered_df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                data1 = towrite.read()
                b64 = base64.b64encode(data1).decode()
                st.session_state['excel_file_name1'] = file_exp1
                st.session_state['excel_file_data1'] = b64

            if 'excel_file_name1' in st.session_state and 'excel_file_data1' in st.session_state:
                # Генеруємо HTML-кнопку з JS, яка ховається після кліку
                download_html1 = f"""
                <html>
                <head>
                <script>
                function hideButton() {{
                    var btn = document.getElementById('download-btn1');
                    btn.style.display = 'none';
                }}
                </script>
                </head>
                <body>
                <a id="download-btn1" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{st.session_state['excel_file_data1']}" 
                   download="{file_exp1}" 
                   onclick="hideButton()"
                   style="display: inline-block; padding: 8px 12px; background-color: #e7e7e7; color: black; text-decoration: none; border-radius: 5px; font-family: sans-serif; font-size:14px; ">
                   ⬇️ Download
                </a>
                </body>
                </html>
                """
                components.html(download_html1, height=50, width=190)
                if 'excel_file_name1' in st.session_state:
                    del st.session_state['excel_file_name1']
        with col_right_exp:
            file_exp2 = f"p-profile_uns_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx"
            if st.button("🔄 Pers+Uns", use_container_width=True):
                merged_df = pd.merge(filtered_df, df_pers, on='pers_id', how='left')
                insert_after_column = 'kurzbezeichnung_aggr' # додаємо нову колонку після
                col_index = merged_df.columns.get_loc(insert_after_column)
                merged_df.insert(col_index + 1, 'dtype', 'UnsLinked ->')
                towrite = io.BytesIO()
                merged_df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                data2 = towrite.read()
                b64 = base64.b64encode(data2).decode()
                st.session_state['excel_file_name2'] = file_exp2
                st.session_state['excel_file_data2'] = b64
            if 'excel_file_name2' in st.session_state and 'excel_file_data2' in st.session_state:
                # Генеруємо HTML-кнопку з JS, яка ховається після кліку
                download_html2 = f"""
                    <html>
                    <head>
                    <script>
                    function hideButton() {{
                        var btn = document.getElementById('download-btn2');
                        btn.style.display = 'none';
                    }}
                    </script>
                    </head>
                    <body>
                    <a id="download-btn2" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{st.session_state['excel_file_data2']}" 
                       download="{file_exp2}" 
                       onclick="hideButton()"
                       style="display: inline-block; padding: 8px 12px; background-color: #e7e7e7; color: black; text-decoration: none; border-radius: 5px; font-family: sans-serif; font-size:14px; ">
                       ⬇️ Download
                    </a>
                    </body>
                    </html>
                    """
                components.html(download_html2, height=50, width=190)
                if 'excel_file_name2' in st.session_state:
                    del st.session_state['excel_file_name2']

# === 6. Деталі вибраного рядка
selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected)
if len(selected_df) > 0:

    st.markdown("🔸**Details:**")
    with st.spinner("⏳ Loading ..."):
        # 1. Очистити попередній DataFrame (опціонально — для візуального ефекту)
        placeholder = st.empty()  # створюємо місце, де з'явиться таблиця
        time.sleep(2)  # штучна пауза

        # 2. Наповнюємо вкладки
        selected_pers_id = selected_df.iloc[0]['pers_id']

        query = f"""
                    SELECT wu.vollname_der_firma, wlup.pers_position, wu.uns_id, 
                            case when wu.seite not like 'http%' and wu.seite not like 'www%' then null else wu.seite end as seite, 
                            wu.email, wu.telefonnummer, 
                            wu.rechnungsadr_land, wu.rechnungsadr_bundesland, wu.rechnungsadr_plz_ort, 
                            wu.rechtsform, 
                            wu.code5 as onace_code5, wu.onace_sh_de1, wu.onace_sh_de2, wu.onace_sh_de3, wu.onace_sh_de4, wu.onace_sh_de5,
                            wu.product_name_agg, wu.tatigkeitsbeschreibung,
                            wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id, wu.akt_titel, wu.akt_maxd,
                            wu.heaf, wu.hauptunternehmen_id, wu.kurzbezeichnung, wu.rechnungsadr_full, wu.registrierungsstatus, wu.compass_id,
                            wp.pers_id
                    FROM main.w_pers wp
                    INNER join main.w_links_uns_pers wlup on wlup.pers_id = wp.pers_id
                    INNER join main.w_uns wu on wu.uns_id = wlup.uns_id
                    WHERE wp.pers_id = '{selected_pers_id}'
                    ORDER BY 2
                    """
        df1 = conn.execute(query).fetchdf()

        query = f"""
                    SELECT distinct wv.*
                      from (select wv.datum_titel, case when wv.agenda_link = '-' then null else wv.agenda_link end as agenda_link, 
                                    wv.format, coalesce(wv.bundesland,'-') as bundesland, wv.akt_org, wv.akt_spn,
                                    wv.adr_full, wv.aktivitaten_id
                                from main.w_veranstaltung wv 
                                group by wv.datum_titel, wv.aktivitaten_id, wv.agenda_link, wv.format, wv.datum_bis_year, 
                                        wv.bundesland, wv.akt_org, wv.akt_spn, wv.adr_full
                            ) wv
                    INNER JOIN main.w_veranstaltung wv2 on wv.aktivitaten_id = wv2.aktivitaten_id
                    WHERE wv2.pers_id = '{selected_pers_id}'
                    ORDER BY 1 desc
                    """
        df2 = conn.execute(query).fetchdf()

        tab1, tab2 = placeholder.tabs([f"Unternehmen ({str(len(df1))})", f"Veranstaltung ({str(len(df2))})"])
        with tab1:
            # Поза межами spinner — вивід даних
            dfheight1 = 0 if len(df1) == 0 else 40.7 * min(len(df1) + 3, 10)
            # обробляємо пусті дати
            for col in df1.select_dtypes(include=['datetime']):
                df1[col] = df1[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
            # формуємо датафрейм
            gb1 = GridOptionsBuilder.from_dataframe(df1)

            cell_renderer = JsCode("""
                                    function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
                                    """)

            gb1.configure_pagination(enabled=True, paginationAutoPageSize=False,
                                    paginationPageSize=5000)  # Add pagination
            # gb1.configure_side_bar(filters_panel=True, columns_panel=True) # Add a sidebar
            gb1.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters')  # Add a sidebar
            gb1.configure_selection(selection_mode="single")  # Enable single selection (multiple)
            gb1.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)

            gb1.configure_column(field='vollname_der_firma', header_name='Voller Name', pinned='left',
                                filter=ag_grid.filters.multi)
            gb1.configure_column(field='pers_position', header_name='Position', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='uns_id', header_name='Id', filter=ag_grid.filters.multi)
            gb1.configure_column(
                "seite",
                headerName="Link zur Website",
                width=200,
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
            gb1.configure_column(field='email', header_name='Email', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='telefonnummer', header_name='Telefonnummer', filter=ag_grid.filters.multi,
                                width=150)
            gb1.configure_column(field='rechnungsadr_land', header_name='Land', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='rechnungsadr_bundesland', header_name='Bundesland', filter=ag_grid.filters.multi,
                                width=200)
            gb1.configure_column(field='rechnungsadr_plz_ort', header_name='Plz-Ort', filter=ag_grid.filters.multi,
                                width=200)
            gb1.configure_column(field='rechtsform', header_name='Rechtsform', filter=ag_grid.filters.multi)
            gb1.configure_column(field='onace_code5', header_name='ONACE', filter=ag_grid.filters.multi, width=100)
            gb1.configure_column(field='onace_sh_de1', header_name='ONACE L1', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='onace_sh_de2', header_name='ONACE L2', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='onace_sh_de3', header_name='ONACE L3', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='onace_sh_de4', header_name='ONACE L4', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='onace_sh_de5', header_name='ONACE L5', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='product_name_agg', header_name="Produkte von 'Compass'", filter=ag_grid.filters.multi)
            gb1.configure_column(field='tatigkeitsbeschreibung', header_name='Tatigkeitsbeschreibung',
                                filter=ag_grid.filters.multi, width=300)
            gb1.configure_column(field='uns_mitg', header_name='Uns MG', filter=ag_grid.filters.number, width=100)
            gb1.configure_column(field='uns_mitg_maxd', header_name='Letzte MG Data', type=["customDateTimeFormat"],
                                custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.multi, width=130)
            gb1.configure_column(field='aktivitaten_id', header_name='Letzte Akt ID', filter=ag_grid.filters.multi,
                                width=120)
            gb1.configure_column(field='akt_titel', header_name='Letzte Akt Titel', filter=ag_grid.filters.multi)
            gb1.configure_column(field='akt_maxd', header_name='Letzte Akt Data', type=["customDateTimeFormat"],
                                custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.multi, width=130)
            gb1.configure_column(field='heaf', header_name='Heaf', filter=ag_grid.filters.multi, width=80)
            gb1.configure_column(field='hauptunternehmen_id', header_name='ID Haupt', filter=ag_grid.filters.multi,
                                width=120)
            gb1.configure_column(field='rechnungsadr_full', header_name='Adresse', filter=ag_grid.filters.multi)
            gb1.configure_column(field='kurzbezeichnung', header_name='Gekürzter Name', filter=ag_grid.filters.multi)
            gb1.configure_column(field='registrierungsstatus', header_name='Status', filter=ag_grid.filters.multi,
                                width=100)
            gb1.configure_column(field='compass_id', header_name='ID Compass', filter=ag_grid.filters.multi, width=120)

            grid_options1 = gb1.build()

            grid_response1 = AgGrid(
                df1,
                gridOptions=grid_options1,
                enable_enterprise_modules=True,
                update_mode="SELECTION_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
                data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
                theme="blue",
                # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
                pagination_page_size_selector=[20, 50, 100],
                height=dfheight1,
                width='100%',
                header_checkbox_selection_filtered_only=True,
                show_toolbar=True, show_search=False, show_download_button=False,
                allow_unsafe_jscode=True,
                reload_data=True,
            )

        with tab2:
            dfheight2 = 0 if len(df2) == 0 else 40.7 * min(len(df2) + 3, 10)
            # обробляємо пусті дати
            for col in df2.select_dtypes(include=['datetime']):
                df2[col] = df2[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
            # формуємо датафрейм
            gb2 = GridOptionsBuilder.from_dataframe(df2)
            cell_renderer = JsCode(""" function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`} """)
            gb2.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=100)  # Add pagination
            gb2.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters')  # Add a sidebar
            gb2.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
            gb2.configure_column(field='datum_titel', header_name='Datum | Titel', pinned='left', filter=ag_grid.filters.multi, width=250)
            gb2.configure_column(field="agenda_link", headerName="Agenda link", width=100,
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
            gb2.configure_column(field='format', header_name='Format', filter=ag_grid.filters.multi, width=100)
            gb2.configure_column(field='bundesland', header_name='Place', filter=ag_grid.filters.multi, width=150)
            gb2.configure_column(field='akt_org', header_name='Organizer', filter=ag_grid.filters.multi, width=300)
            gb2.configure_column(field='akt_spn', header_name='Sponsor', filter=ag_grid.filters.multi, width=300)
            gb2.configure_column(field='aktivitaten_id', header_name='ID', filter=ag_grid.filters.multi, width=120)
            gb2.configure_column(field='adr_full', header_name='Adress', filter=ag_grid.filters.multi, width=300)

            grid_options2 = gb2.build()
            grid_response2 = AgGrid(
                df2,
                gridOptions=grid_options2,
                # enable_enterprise_modules=True,
                update_mode="SELECTION_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
                data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
                theme="blue",  # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
                pagination_page_size_selector=[20, 50, 100],
                height=dfheight2,  # = 7 rows
                width='100%',
                show_toolbar=True, show_search=False, show_download_button=False,
                allow_unsafe_jscode=True,
                reload_data=True,
                fit_columns_on_grid_load=True,
            )
