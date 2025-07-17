import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
from utils.io import load_sql
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
from reflex_ag_grid import ag_grid

title = 'berichte'
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

st.subheader("💼 KSO-Management (KSÖ-Management)")

# === 1. Завантаження даних
query = load_sql(f"{title}/sel_management.sql")
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

gb.configure_column(field='vollname_der_firma', header_name='Supreme structural unit', pinned='left', filter=ag_grid.filters.multi, headerCheckboxSelection = True)
gb.configure_column(field='cnt_pers', header_name='Cnt Pers', pinned='left', filter=ag_grid.filters.number, width=100)
gb.configure_column(field='vor_nachname', header_name='Employee', pinned='left', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='prsd', header_name='Präsidium', filter=ag_grid.filters.multi, width=100)
gb.configure_column(field='vrst', header_name='Vorstand', filter=ag_grid.filters.multi, width=100)
gb.configure_column(field='gnrl', header_name='Generalsekretär', filter=ag_grid.filters.multi, width=100)
gb.configure_column(field='rchn', header_name='Rechnungsprüfer', filter=ag_grid.filters.multi, width=100)
gb.configure_column(field='pos1', header_name='Position1', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='pos2', header_name='Position2', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='email', header_name='Email', filter=ag_grid.filters.multi, width=200)
gb.configure_column(field='juradr_bundesland', header_name='Bundesland', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='juradr_full', header_name='Address', filter=ag_grid.filters.multi, width=250)
gb.configure_column(field='vorname', header_name='Vorname', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='nachname', header_name='Nachname', filter=ag_grid.filters.multi, width=150)
gb.configure_column(field='uns_id', header_name='ID Uns', filter=ag_grid.filters.multi, width=140)
gb.configure_column(field='pers_id', header_name='ID Pers', filter=ag_grid.filters.multi, width=140)

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
    height=360, # = 7 rows
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

    # placeholder_col = st.empty()
    # col_adr, col_form = placeholder_col.columns([0.5, 0.5])
    # with col_adr:
    #     st.markdown(f"🔸**Address:** {selected_df.iloc[0]['rechnungsadr_full']}")
    # with col_form:
    #     if selected_df.iloc[0]['rechtsform']:
    #         st.markdown(f"🔸**Rechtsform:** {selected_df.iloc[0]['rechtsform']}")
    #
    # if selected_df.iloc[0]['onace_code5']:
    #     expander = st.expander(f"**ONACE:** {selected_df.iloc[0]['onace_sh_de5']} ({selected_df.iloc[0]['onace_code5']})", expanded=False)
    #     col_onace1, col_onace2, col_onace3, col_onace4 = expander.columns([0.25, 0.25, 0.25, 0.25])
    #     with col_onace1:
    #         st.write(f"1️⃣{selected_df.iloc[0]['onace_sh_de1']} ({selected_df.iloc[0]['onace_code5'][0:1]})")
    #     with col_onace2:
    #         st.write(f"2️⃣{selected_df.iloc[0]['onace_sh_de2']} ({selected_df.iloc[0]['onace_code5'][0:3]})")
    #     with col_onace3:
    #         st.write(f"3️⃣{selected_df.iloc[0]['onace_sh_de3']} ({selected_df.iloc[0]['onace_code5'][0:5]})")
    #     with col_onace4:
    #         st.write(f"4️⃣{selected_df.iloc[0]['onace_sh_de4']} ({selected_df.iloc[0]['onace_code5'][0:6]})")
    #
    # if selected_df.iloc[0]['product_name_agg'] and selected_df.iloc[0]['tatigkeitsbeschreibung']:
    #     col_prod, col_comm = st.columns([0.5, 0.5])
    # elif selected_df.iloc[0]['product_name_agg']:
    #     col_prod = st.empty()
    # elif selected_df.iloc[0]['tatigkeitsbeschreibung']:
    #     col_comm = st.empty()
    #
    # # col_prod, col_comm = st.columns([0.5, 0.5])
    # try:
    #     with col_prod:
    #         if selected_df.iloc[0]['product_name_agg']:
    #             expander = col_prod.expander(f"**Products and Services:** {selected_df.iloc[0]['product_name_agg'].split('|')[0]} ... ↩️", expanded=False)
    #             expander.write(f"{selected_df.iloc[0]['product_name_agg']}")
    #         else:
    #             expander = col_prod.expander("**Products and Services:** ❌", expanded=False)
    #             expander.write(f"")
    # except:
    #     pass
    #
    # try:
    #     with col_comm:
    #         if selected_df.iloc[0]['tatigkeitsbeschreibung']:
    #             expander = col_comm.expander(f"**Tatigkeitsbeschreibung:** {selected_df.iloc[0]['tatigkeitsbeschreibung'][0:75]}... ↩️", expanded=False)
    #             expander.write(f"{selected_df.iloc[0]['tatigkeitsbeschreibung']}")
    # except:
    #     pass

    st.markdown(f"🔸**Details:**")
    with st.spinner("⏳ Loading ..."):
        # 1. Очистити попередній DataFrame (опціонально — для візуального ефекту)
        placeholder = st.empty()  # створюємо місце, де з'явиться таблиця
        time.sleep(2)  # штучна пауза

        # 2. Наповнюємо вкладки
        selected_pers_id = selected_df.iloc[0]['pers_id']
        selected_uns_id = selected_df.iloc[0]['uns_id']
        selected_pers_vornachname = selected_df.iloc[0]['vor_nachname']
        selected_uns_vollname = selected_df.iloc[0]['vollname_der_firma']

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
                    ORDER BY 3, 2
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

        # query = f"""
        #             SELECT distinct wv.*
        #               from (select wv.datum_titel, case when wv.agenda_link = '-' then null else wv.agenda_link end as agenda_link,
        #                             wv.format, coalesce(wv.bundesland,'-') as bundesland, wv.akt_org, wv.akt_spn,
        #                             wv.adr_full, wv.aktivitaten_id
        #                         from main.w_veranstaltung wv
        #                         group by wv.datum_titel, wv.aktivitaten_id, wv.agenda_link, wv.format, wv.datum_bis_year,
        #                                 wv.bundesland, wv.akt_org, wv.akt_spn, wv.adr_full
        #                     ) wv
        #             INNER JOIN main.w_veranstaltung wv2 on wv.aktivitaten_id = wv2.aktivitaten_id
        #             WHERE wv2.uns_id = '{selected_uns_id}'
        #             ORDER BY 1 desc
        #             """
        # df3 = conn.execute(query).fetchdf()

        # tab1, tab2, tab3 = placeholder.tabs([f"{selected_pers_vornachname} vs Unternehmen ({str(len(df1))})",
        #                                      f"{selected_pers_vornachname} vs Veranstaltung ({str(len(df2))})",
        #                                      f"{selected_uns_vollname} vs Veranstaltung ({str(len(df3))})"
        #                                      ])

        tab1, tab2 = placeholder.tabs([f"{selected_pers_vornachname} vs Unternehmen ({str(len(df1))})",
                                             f"{selected_pers_vornachname} vs Veranstaltung ({str(len(df2))})"
                                             ])

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

            gb1.configure_column(field='vollname_der_firma', header_name='Full Name', pinned='left',
                                filter=ag_grid.filters.multi)
            gb1.configure_column(field='pers_position', header_name='Position', filter=ag_grid.filters.multi, width=200)
            gb1.configure_column(field='uns_id', header_name='Id', filter=ag_grid.filters.multi)
            gb1.configure_column(
                "seite",
                headerName="Link",
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
            gb1.configure_column(field='product_name_agg', header_name='Product Compass', filter=ag_grid.filters.multi)
            gb1.configure_column(field='tatigkeitsbeschreibung', header_name='Tatigkeitsbeschreibung',
                                filter=ag_grid.filters.multi, width=300)
            gb1.configure_column(field='uns_mitg', header_name='Uns Mtg', filter=ag_grid.filters.number, width=100)
            gb1.configure_column(field='uns_mitg_maxd', header_name='Lst Mtg Date', type=["customDateTimeFormat"],
                                custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.date, width=130)
            gb1.configure_column(field='aktivitaten_id', header_name='Lst Akt ID', filter=ag_grid.filters.multi,
                                width=120)
            gb1.configure_column(field='akt_titel', header_name='Lst Akt Titel', filter=ag_grid.filters.multi)
            gb1.configure_column(field='akt_maxd', header_name='Lst Akt Date', type=["customDateTimeFormat"],
                                custom_format_string='yyyy-MM-dd', filter=ag_grid.filters.date, width=130)
            gb1.configure_column(field='heaf', header_name='Heaf', filter=ag_grid.filters.multi, width=80)
            gb1.configure_column(field='hauptunternehmen_id', header_name='ID Haupt', filter=ag_grid.filters.multi,
                                width=120)
            gb1.configure_column(field='rechnungsadr_full', header_name='Address', filter=ag_grid.filters.multi)
            gb1.configure_column(field='kurzbezeichnung', header_name='Short Name', filter=ag_grid.filters.multi)
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
                key='AgGrid1'
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
                key='AgGrid2'
            )

        # with tab3:
        #     dfheight3 = 0 if len(df3) == 0 else 40.7 * min(len(df3) + 3, 10)
        #     # обробляємо пусті дати
        #     for col in df3.select_dtypes(include=['datetime']):
        #         df3[col] = df3[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
        #     # формуємо датафрейм
        #     gb3 = GridOptionsBuilder.from_dataframe(df3)
        #     cell_renderer = JsCode(""" function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`} """)
        #     gb3.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=100)  # Add pagination
        #     gb3.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel='filters')  # Add a sidebar
        #     gb3.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
        #     gb3.configure_column(field='datum_titel', header_name='Datum | Titel', pinned='left', filter=ag_grid.filters.multi, width=250)
        #     gb3.configure_column(field="agenda_link", headerName="Agenda link", width=100,
        #                         cellRenderer=JsCode("""
        #             class UrlCellRenderer {
        #               init(params) {
        #                 this.eGui = document.createElement('a');
        #                 this.eGui.innerText = params.value;
        #                 this.eGui.setAttribute('href', params.value);
        #                 this.eGui.setAttribute('style', "text-decoration:none");
        #                 this.eGui.setAttribute('target', "_blank");
        #               }
        #               getGui() {
        #                 return this.eGui;
        #               }
        #             }
        #         """)
        #                         )
        #     gb3.configure_column(field='format', header_name='Format', filter=ag_grid.filters.multi, width=100)
        #     gb3.configure_column(field='bundesland', header_name='Place', filter=ag_grid.filters.multi, width=150)
        #     gb3.configure_column(field='akt_org', header_name='Organizer', filter=ag_grid.filters.multi, width=300)
        #     gb3.configure_column(field='akt_spn', header_name='Sponsor', filter=ag_grid.filters.multi, width=300)
        #     gb3.configure_column(field='aktivitaten_id', header_name='ID', filter=ag_grid.filters.multi, width=120)
        #     gb3.configure_column(field='adr_full', header_name='Adress', filter=ag_grid.filters.multi, width=300)
        #
        #     grid_options3 = gb3.build()
        #     grid_response3 = AgGrid(
        #         df3,
        #         gridOptions=grid_options3,
        #         # enable_enterprise_modules=True,
        #         update_mode="SELECTION_CHANGED",  # options -> GRID_CHANGED, SELECTION_CHANGED, MODEL_CHANGED
        #         data_return_mode="FILTERED",  # options ->AS_INPUT, FILTERED
        #         theme="blue",  # Add theme color to the table Available options: ['streamlit', 'light', 'dark', 'blue', 'fresh', 'material', 'alpine', 'balham']
        #         pagination_page_size_selector=[20, 50, 100],
        #         height=dfheight3,  # = 7 rows
        #         width='100%',
        #         show_toolbar=True, show_search=False, show_download_button=False,
        #         allow_unsafe_jscode=True,
        #         reload_data=True,
        #         fit_columns_on_grid_load=True,
        #         key='AgGrid3'
        #     )