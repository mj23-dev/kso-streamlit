import streamlit as st
import pandas as pd
import time
import io
import base64
from datetime import datetime
from utils.io import load_sql
from streamlit_slickgrid import (
    add_tree_info,
    slickgrid,
    Formatters,
    Filters,
    FieldType,
    OperatorType,
    ExportServices,
    StreamlitSlickGridFormatters,
    StreamlitSlickGridSorters,)

# Inject custom CSS to target the dialog container
st.markdown(
    """
    <style>
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 80vw;
        height: 50vw;
        max-width: 80vw;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ SlickGrid замість st_aggrid
# st.set_page_config(page_title="KSO - Unternehmen Profile", layout="wide")

title = 'unternehmen'
st.subheader("🏢 Unternehmen (Сompanies)")

# Connection (без змін)
conn = st.session_state.get("conn")
if conn is None:
    st.warning("❌ You need to upload database file from hauptseite!")
    st.stop()

# Reload logic (без змін)
if "reload_grid" in st.session_state:
    del st.session_state["reload_grid"]
if "reset_grid_key" not in st.session_state:
    st.session_state["reset_grid_key"] = "grid_default"

# ✅ df1 — основна таблиця (без змін)
query = load_sql(f"{title}/sel_profile.sql")
df = conn.execute(query).fetchdf()

# Форматування дат (без змін)
for col in df.select_dtypes(include=['datetime']):
    df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
data = df.to_dict('records')  # ✅ SlickGrid формат
data = add_tree_info(
    data,
    tree_fields=["vollname_der_firma", "kurzbezeichnung", "uns_id", "cnt_pers", "seite", "email", "telefonnummer", "rechnungsadr_land", "rechnungsadr_bundesland", "rechnungsadr_plz_ort", "rechtsform", "onace_code5", "onace_sh_de1", "onace_sh_de2", "onace_sh_de3", "onace_sh_de4", "onace_sh_de5", "product_name_agg", "tatigkeitsbeschreibung", "uns_mitg", "uns_mitg_maxd", "aktivitaten_id", "akt_titel", "akt_maxd", "heaf", "hauptunternehmen_id", "rechnungsadr_full", "registrierungsstatus", "compass_id"],
    join_fields_as="title",
    id_field="id",)

# dfpers (без змін)
query_pers = load_sql(f"{title}/sel_w_links_uns_pers.sql")
df_pers = conn.execute(query_pers).fetchdf()

cnt_full = len(df)
cnt_filtered = cnt_full

# st.subheader(f"**Unternehmen** ({cnt_full})")

columns = [
            # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
            {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "minWidth": 450},
            {"id": "kurzbezeichnung", "name": "Gekürzter Name", "field": "kurzbezeichnung", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "uns_id", "name": "ID", "field": "uns_id", "sortable": True, "filterable": True, "minWidth": 150},
            {"id": "cnt_pers", "name": "Cnt Pers", "field": "cnt_pers", "type": FieldType.number, "sortable": True, "filterable": True, "minWidth": 50},
            {"id": "seite", "name": "Link zur Website", "field": "seite", "sortable": True, "filterable": True, "minWidth": 200, "formatter": Formatters.hyperlink},
            {"id": "email", "name": "Email", "field": "email", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "telefonnummer", "name": "Telefonnummer", "field": "telefonnummer", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "rechnungsadr_land", "name": "Land", "field": "rechnungsadr_land", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "rechnungsadr_bundesland", "name": "Bundesland", "field": "rechnungsadr_bundesland", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "rechnungsadr_plz_ort", "name": "Plz-Ort", "field": "rechnungsadr_plz_ort", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "rechtsform", "name": "Rechtsform", "field": "rechtsform", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "onace_code5", "name": "ONACE", "field": "onace_code5", "sortable": True, "filterable": True, "minWidth": 100},
            {"id": "onace_sh_de1", "name": "ONACE L1", "field": "onace_sh_de1", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "onace_sh_de2", "name": "ONACE L2", "field": "onace_sh_de2", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "onace_sh_de3", "name": "ONACE L3", "field": "onace_sh_de3", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "onace_sh_de4", "name": "ONACE L4", "field": "onace_sh_de4", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "onace_sh_de5", "name": "ONACE L5", "field": "onace_sh_de5", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "product_name_agg", "name": "Produkte von 'Compass'", "field": "product_name_agg", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "tatigkeitsbeschreibung", "name": "Tatigkeitsbeschreibung", "field": "tatigkeitsbeschreibung", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "uns_mitg", "name": "Uns MG", "field": "uns_mitg", "sortable": True, "filterable": True, "type": FieldType.number, "minWidth": 50},
            {"id": "uns_mitg_maxd", "name": "Letzte MG Data", "field": "uns_mitg_maxd", "sortable": True, "filterable": True, "minWidth": 100},
            {"id": "aktivitaten_id", "name": "Letzte Akt ID", "field": "aktivitaten_id", "sortable": True, "filterable": True, "minWidth": 120},
            {"id": "akt_titel", "name": "Letzte Akt Titel", "field": "akt_titel", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "akt_maxd", "name": "Letzte Akt Data", "field": "akt_maxd", "sortable": True, "filterable": True, "minWidth": 100},
            {"id": "heaf", "name": "Heaf", "field": "heaf", "sortable": True, "filterable": True, "minWidth": 50},
            {"id": "hauptunternehmen_id", "name": "ID Haupt", "field": "hauptunternehmen_id", "sortable": True, "filterable": True, "minWidth": 120},
            {"id": "rechnungsadr_full", "name": "Adresse", "field": "rechnungsadr_full", "sortable": True, "filterable": True, "minWidth": 200},
            {"id": "registrierungsstatus", "name": "Status", "field": "registrierungsstatus", "sortable": True, "filterable": True, "minWidth": 100},
            {"id": "compass_id", "name": "ID Compass", "field": "compass_id", "sortable": True, "filterable": True, "type": FieldType.number, "minWidth": 100},
    ]

options={
    #
    # Allow filtering (based on column filter* properties)
    "enableFiltering": True,
    # --
    #
    # Debounce/throttle the input text filter if you have lots of data
    # filterTypingDebounce: 250,
    # --
    #
    # Set up export options.
    "enableTextExport": True,
    "enableExcelExport": True,
    "enableGridMenu": True, 
    "explicitInitialization": True,
    "excelExportOptions": {"sanitizeDataExport": True},
    "textExportOptions": {"sanitizeDataExport": True},
    "externalResources": [
        ExportServices.ExcelExportService,
        ExportServices.TextExportService,
    ],
    # --
    #
    # Pin columns.
    "frozenColumn": 0,
    # --
    #
    # Pin rows.
    # "frozenRow": 0,
    # --
    #
    # Don't scroll table when too big. Instead, just let it grow.
    # "autoHeight": True,
    # --
    #
    "autoResize": {
        "minHeight": 450,
    },
    # --
    #
    # Set up tree.
    "enableTreeData": True,
    "multiColumnSort": False,
    "treeDataOptions": {
        "columnId": "title",
        "indentMarginLeft": 15,
        "initiallyCollapsed": True,
        # This is a field that add_tree_info() inserts in your data:
        "parentPropName": "__parent",
        # This is a field that add_tree_info() inserts in your data:
        "levelPropName": "__depth",
        #
        # If you're building your own tree (without add_tree_info),
        # you should configure the props above accordingly.
        #
        # See below for more info:
        # - https://ghiscoding.github.io/slickgrid-react-demos/#/example27
        # - https://ghiscoding.github.io/slickgrid-react-demos/#/example28
    },
    # Enables row or cell selection highlight behavior
    "enableRowSelection": True,  # True enables row selection (requires enableCellNavigation=True)
    "enableCellNavigation": True,  # True allows cell selection visualization (enableRowSelection must be False)
}

# ✅ UI Controls (без змін)
# col_left, col_center1, col_right = st.columns([0.55, 0.15, 0.25])
col_left, col_center1, col_right = st.columns([1,0.01,0.01])
with col_left:
    st.markdown("**👆 Klicken Sie auf den Eintrag, um Details anzuzeigen**")
# with col_center1:
#     if st.button("🔄 Reset filters", use_container_width=True):
#         st.session_state["reload_grid"] = True
#         st.session_state["reset_grid_key"] = f"grid_{datetime.now().timestamp()}"
#         st.rerun()
# === 5. Експорт
# with col_right:
#     with st.popover("⬇️ Export XLS", use_container_width=True):
#         col_left_exp, col_right_exp = st.columns([0.5,0.5])
#         with col_left_exp:
#             if st.button("🔄 Uns", use_container_width=True):
#                 file_exp1 = f"u-profile_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx"
#                 towrite = io.BytesIO()
#                 filtered_df.to_excel(towrite, index=False, engine='openpyxl')
#                 towrite.seek(0)
#                 data1 = towrite.read()
#                 b64 = base64.b64encode(data1).decode()
#                 st.session_state['excel_file_name1'] = file_exp1
#                 st.session_state['excel_file_data1'] = b64
#
#             if 'excel_file_name1' in st.session_state and 'excel_file_data1' in st.session_state:
#                 # Генеруємо HTML-кнопку з JS, яка ховається після кліку
#                 download_html1 = f"""
#                 <html>
#                 <head>
#                 <script>
#                 function hideButton() {{
#                     var btn = document.getElementById('download-btn1');
#                     btn.style.display = 'none';
#                 }}
#                 </script>
#                 </head>
#                 <body>
#                 <a id="download-btn1" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{st.session_state['excel_file_data1']}"
#                    download="{file_exp1}"
#                    onclick="hideButton()"
#                    style="display: inline-block; padding: 8px 12px; background-color: #e7e7e7; color: black; text-decoration: none; border-radius: 5px; font-family: sans-serif; font-size:14px; ">
#                    ⬇️ Download
#                 </a>
#                 </body>
#                 </html>
#                 """
#                 components.html(download_html1, height=50, width=190)
#                 if 'excel_file_name1' in st.session_state:
#                     del st.session_state['excel_file_name1']
#         with col_right_exp:
#             file_exp2 = f"u-profile_pers_" + datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".xlsx"
#             if st.button("🔄 Uns+Pers", use_container_width=True):
#                 merged_df = pd.merge(filtered_df, df_pers, on='uns_id', how='left')
#                 insert_after_column = 'compass_id'  # додаємо нову колонку після
#                 col_index = merged_df.columns.get_loc(insert_after_column)
#                 merged_df.insert(col_index + 1, 'dtype', 'PersLinked ->')
#                 towrite = io.BytesIO()
#                 merged_df.to_excel(towrite, index=False, engine='openpyxl')
#                 towrite.seek(0)
#                 data2 = towrite.read()
#                 b64 = base64.b64encode(data2).decode()
#                 st.session_state['excel_file_name2'] = file_exp2
#                 st.session_state['excel_file_data2'] = b64
#             if 'excel_file_name2' in st.session_state and 'excel_file_data2' in st.session_state:
#                 # Генеруємо HTML-кнопку з JS, яка ховається після кліку
#                 download_html2 = f"""
#                     <html>
#                     <head>
#                     <script>
#                     function hideButton() {{
#                         var btn = document.getElementById('download-btn2');
#                         btn.style.display = 'none';
#                     }}
#                     </script>
#                     </head>
#                     <body>
#                     <a id="download-btn2" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{st.session_state['excel_file_data2']}"
#                        download="{file_exp2}"
#                        onclick="hideButton()"
#                        style="display: inline-block; padding: 8px 12px; background-color: #e7e7e7; color: black; text-decoration: none; border-radius: 5px; font-family: sans-serif; font-size:14px; ">
#                        ⬇️ Download
#                     </a>
#                     </body>
#                     </html>
#                     """
#                 components.html(download_html2, height=50, width=190)
#                 if 'excel_file_name2' in st.session_state:
#                     del st.session_state['excel_file_name2']
#

# ✅ Callback для вибору рядка
def on_row_selected(event):
    """Callback при виборі рядка"""
    if event.get("rows"):
        row_idx = event["rows"][0]
        selected_row = df.iloc[row_idx].to_dict()
        st.session_state.selected_uns_id = selected_row.get("uns_id")
        st.session_state.selected_row_data = selected_row
        st.success(f"✅ Вибрано: {selected_row.get('vollname_der_firma', 'N/A')}")

# ✅ SlickGrid (замість AgGrid)
# with col_left:
out = slickgrid(
    data,  # ✅ list of dicts
    columns,
    options,
    key=st.session_state["reset_grid_key"],
    on_click = "rerun"
)


# if out:
#     print(out)
#     filtered_df = pd.DataFrame(out)
#     cnt_filtered = len(filtered_df)
#     print(cnt_filtered)
# else:
#     print('error')


@st.dialog("Details", width="large")
def show_dialog(item):
    # st.write("Congrats! You clicked on the row below:")
    st.write(item)

if out is not None:
    row, col = out
    selected_uns_id = out[0]
    # print(selected_uns_id)
    selected_df = df[df['uns_id'] == row]
    # show_dialog(selected_df.transpose())

if out is not None:
    if len(selected_df) > 0:

        placeholder_col = st.empty()
        col_name, col_link = placeholder_col.columns([0.5, 0.5])
        with col_name:
            st.markdown(f"🔸**Voller Name:** {selected_df.iloc[0]['vollname_der_firma']}")
        with col_link:
            st.markdown(f"🔸**Link zur Website:** {selected_df.iloc[0]['seite']}")

        placeholder_col = st.empty()
        col_adr, col_form = placeholder_col.columns([0.5, 0.5])
        with col_adr:
            st.markdown(f"🔸**Adresse:** {selected_df.iloc[0]['rechnungsadr_full']}")
        with col_form:
            if selected_df.iloc[0]['rechtsform']:
                st.markdown(f"🔸**Rechtsform:** {selected_df.iloc[0]['rechtsform']}")

        if selected_df.iloc[0]['onace_code5']:
            expander = st.expander(
                f"**ONACE:** {selected_df.iloc[0]['onace_sh_de5']} ({selected_df.iloc[0]['onace_code5']})", expanded=False)
            col_onace1, col_onace2, col_onace3, col_onace4 = expander.columns([0.25, 0.25, 0.25, 0.25])
            with col_onace1:
                st.write(f"1️⃣{selected_df.iloc[0]['onace_sh_de1']} ({selected_df.iloc[0]['onace_code5'][0:1]})")
            with col_onace2:
                st.write(f"2️⃣{selected_df.iloc[0]['onace_sh_de2']} ({selected_df.iloc[0]['onace_code5'][0:3]})")
            with col_onace3:
                st.write(f"3️⃣{selected_df.iloc[0]['onace_sh_de3']} ({selected_df.iloc[0]['onace_code5'][0:5]})")
            with col_onace4:
                st.write(f"4️⃣{selected_df.iloc[0]['onace_sh_de4']} ({selected_df.iloc[0]['onace_code5'][0:6]})")

        if selected_df.iloc[0]['product_name_agg'] and selected_df.iloc[0]['tatigkeitsbeschreibung']:
            col_prod, col_comm = st.columns([0.5, 0.5])
        elif selected_df.iloc[0]['product_name_agg']:
            col_prod = st.empty()
        elif selected_df.iloc[0]['tatigkeitsbeschreibung']:
            col_comm = st.empty()

        # col_prod, col_comm = st.columns([0.5, 0.5])
        try:
            with col_prod:
                if selected_df.iloc[0]['product_name_agg']:
                    expander = col_prod.expander(
                        f"**Produkte von 'Compass':** {selected_df.iloc[0]['product_name_agg'].split('|')[0]} ... ↩️",
                        expanded=False)
                    expander.write(f"{selected_df.iloc[0]['product_name_agg']}")
                else:
                    expander = col_prod.expander("**Produkte von 'Compass':** ❌", expanded=False)
                    expander.write(f"")
        except:
            pass

        try:
            with col_comm:
                if selected_df.iloc[0]['tatigkeitsbeschreibung']:
                    expander = col_comm.expander(
                        f"**Tatigkeitsbeschreibung:** {selected_df.iloc[0]['tatigkeitsbeschreibung'][0:75]}... ↩️",
                        expanded=False)
                    expander.write(f"{selected_df.iloc[0]['tatigkeitsbeschreibung']}")
        except:
            pass


        # @st.cache_data(ttl=300)  # Кеш 5 хв
        def load_details_data(conn, selected_uns_id):
            query1 = f"""
                        SELECT wlup.pers_id as id, wp.vorname, wp.nachname,
                               concat_ws('; ', wlup.email1, wlup.email2, wlup.email3, wlup.email4, wlup.email5) as email,
                               wlup.pers_kategorie, wlup.pers_position, wp.telefonnummer,
                               wp.pers_mitg, wp.pers_mitg_maxd, wp.aktivitaten_id, wp.akt_titel, wp.akt_maxd,
                               wu.kurzbezeichnung, wu.uns_id
                        FROM w_uns wu
                        INNER JOIN main.w_links_uns_pers wlup ON wu.uns_id = wlup.uns_id
                        INNER JOIN main.w_pers wp ON wlup.pers_id = wp.pers_id
                        WHERE wu.uns_id = '{selected_uns_id}'
                        ORDER BY 3,2
                        """  # твій запит1
            df1 = conn.execute(query1).fetchdf()

            query2 = f"""
                        SELECT distinct wv.*
                          from (select wv.datum_titel, wv.agenda_link,
                                        wv.format, coalesce(wv.bundesland,'-') as bundesland, wv.akt_org, wv.akt_spn,
                                        wv.adr_full, wv.aktivitaten_id as id
                                    from main.w_veranstaltung wv
                                    group by wv.datum_titel, wv.aktivitaten_id, wv.agenda_link, wv.format, wv.datum_bis_year,
                                            wv.bundesland, wv.akt_org, wv.akt_spn, wv.adr_full
                                ) wv
                        INNER JOIN main.w_veranstaltung wv2 on wv.id = wv2.aktivitaten_id
                        WHERE wv2.uns_id = '{selected_uns_id}'
                        ORDER BY 1 desc
                        """  # твій запит2
            df2 = conn.execute(query2).fetchdf()

            return df1, df2

        st.markdown("🔸**Other details:**")

        # ✅ БЕЗ spinner + sleep
        selected_uns_id = selected_df.iloc[0]['uns_id']
        df1, df2 = load_details_data(conn, selected_uns_id)

        # ✅ СТАТИЧНІ ТАБЛИЦІ (без placeholder)
        # tab1, tab2 = st.tabs([f"Personen ({len(df1)})", f"Veranstaltung ({len(df2)})"])

        # with tab1:
        #     dfheight1 = 0 if len(df1) == 0 else 40.7 * min(len(df1) + 3, 10)
        #     # обробляємо пусті дати
        #     for col in df1.select_dtypes(include=['datetime']):
        #         df1[col] = df1[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
        #     # формуємо датафрейм
        #
        #     columns1 = [
        #         # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
        #         {"id": "vorname", "name": "Vorname", "field": "vorname", "sortable": True, "filterable": True, "minWidth": 140},
        #         {"id": "nachname", "name": "Nachname", "field": "nachname", "sortable": True, "filterable": True, "minWidth": 140},
        #         {"id": "id", "name": "ID Pers", "field": "id", "sortable": True, "filterable": True, "minWidth": 75},
        #         {"id": "email", "name": "Email", "field": "email", "sortable": True, "filterable": True, "minWidth": 200},
        #         {"id": "pers_kategorie", "name": "Kategorie", "field": "pers_kategorie", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "pers_position", "name": "Position", "field": "pers_position", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "telefonnummer", "name": "Telefonnummer", "field": "telefonnummer", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "pers_mitg", "name": "MG", "field": "pers_mitg", "sortable": True, "filterable": True, "minWidth": 20},
        #         {"id": "pers_mitg_maxd", "name": "Letzte MG Data", "field": "pers_mitg_maxd", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "aktivitaten_id", "name": "ID Akt", "field": "aktivitaten_id", "sortable": True, "filterable": True, "minWidth": 75},
        #         {"id": "akt_titel", "name": "Letzte Akt Titel", "field": "akt_titel", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "akt_maxd", "name": "Letzte Akt Data", "field": "akt_maxd", "sortable": True, "filterable": True, "minWidth": 50},
        #         {"id": "kurzbezeichnung", "name": "Gekürzter Name", "field": "kurzbezeichnung", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "uns_id", "name": "ID Uns", "field": "uns_id", "sortable": True, "filterable": True, "minWidth": 100},
        #     ]
        #
        #     options1 = {
        #         #
        #         # Allow filtering (based on column filter* properties)
        #         "enableFiltering": True,
        #         # --
        #         #
        #         # Debounce/throttle the input text filter if you have lots of data
        #         # filterTypingDebounce: 250,
        #         # --
        #         #
        #         # Set up export options.
        #         "enableTextExport": True,
        #         "enableExcelExport": True,
        #         "excelExportOptions": {"sanitizeDataExport": True},
        #         "textExportOptions": {"sanitizeDataExport": True},
        #         "externalResources": [
        #             ExportServices.ExcelExportService,
        #             ExportServices.TextExportService,
        #         ],
        #         # --
        #         #
        #         # Pin columns.
        #         "frozenColumn": 1,
        #         # --
        #         #
        #         # Pin rows.
        #         # "frozenRow": 0,
        #         # --
        #         #
        #         # Don't scroll table when too big. Instead, just let it grow.
        #         "autoHeight": True,
        #         # --
        #         #
        #         # "autoResize": {"minHeight": 300,},
        #         # --
        #         #
        #         # Set up tree.
        #         "enableTreeData": True,
        #         "multiColumnSort": False,
        #         "treeDataOptions": {
        #             "columnId": "title",
        #             "indentMarginLeft": 15,
        #             "initiallyCollapsed": True,
        #             # This is a field that add_tree_info() inserts in your data:
        #             "parentPropName": "__parent",
        #             # This is a field that add_tree_info() inserts in your data:
        #             "levelPropName": "__depth",
        #             #
        #             # If you're building your own tree (without add_tree_info),
        #             # you should configure the props above accordingly.
        #             #
        #             # See below for more info:
        #             # - https://ghiscoding.github.io/slickgrid-react-demos/#/example27
        #             # - https://ghiscoding.github.io/slickgrid-react-demos/#/example28
        #         },
        #         # Enables row or cell selection highlight behavior
        #         # "enableRowSelection": False,  # True enables row selection (requires enableCellNavigation=True)
        #         # "enableCellNavigation": False,  # True allows cell selection visualization (enableRowSelection must be False)
        #     }
        #
        #     data1 = df1.to_dict('records')  # ✅ SlickGrid формат
        #     data1 = add_tree_info(
        #             data1,
        #             tree_fields=["vorname", "nachname", "id", "email", "pers_kategorie", "pers_position", "telefonnummer", "pers_mitg", "pers_mitg_maxd", "aktivitaten_id", "akt_titel", "akt_maxd", "kurzbezeichnung", "uns_id"],
        #             join_fields_as="title",
        #             id_field="id", )
        #
        #     out1 = slickgrid(
        #         data1,  # ✅ list of dicts
        #         columns1,
        #         options1,
        #         # key=st.session_state["profile_det1_key"],
        #         # on_click="rerun"
        #     )
        #
        # with tab2:
        #     dfheight2 = 0 if len(df2) == 0 else 40.7 * min(len(df2) + 3, 10)
        #     # обробляємо пусті дати
        #     for col in df2.select_dtypes(include=['datetime']):
        #         df2[col] = df2[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
        #
        #     columns2 = [
        #         # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
        #         {"id": "datum_titel", "name": "Datum | Titel", "field": "datum_titel", "sortable": True, "filterable": True, "minWidth": 200},
        #         {"id": "agenda_link", "name": "Agenda link", "field": "agenda_link", "sortable": True, "filterable": True, "minWidth": 300},
        #         {"id": "format", "name": "Format", "field": "format", "sortable": True, "filterable": True, "minWidth": 75},
        #         {"id": "bundesland", "name": "Place", "field": "bundesland", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "akt_org", "name": "Organizer", "field": "akt_org", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "akt_spn", "name": "Sponsor", "field": "akt_spn", "sortable": True, "filterable": True, "minWidth": 100},
        #         {"id": "id", "name": "ID", "field": "id", "sortable": True, "filterable": True, "minWidth": 75},
        #         {"id": "adr_full", "name": "Adress", "field": "adr_full", "sortable": True, "filterable": True, "minWidth": 100},
        #     ]
        #
        #     options2 = {
        #         #
        #         # Allow filtering (based on column filter* properties)
        #         "enableFiltering": True,
        #         # --
        #         #
        #         # Debounce/throttle the input text filter if you have lots of data
        #         # filterTypingDebounce: 250,
        #         # --
        #         #
        #         # Set up export options.
        #         "enableTextExport": True,
        #         "enableExcelExport": True,
        #         "excelExportOptions": {"sanitizeDataExport": True},
        #         "textExportOptions": {"sanitizeDataExport": True},
        #         "externalResources": [
        #             ExportServices.ExcelExportService,
        #             ExportServices.TextExportService,
        #         ],
        #         # --
        #         #
        #         # Pin columns.
        #         "frozenColumn": 0,
        #         # --
        #         #
        #         # Pin rows.
        #         # "frozenRow": 0,
        #         # --
        #         #
        #         # Don't scroll table when too big. Instead, just let it grow.
        #         "autoHeight": True,
        #         # --
        #         #
        #         # "autoResize": {"minHeight": 300,},
        #         # --
        #         #
        #         # Set up tree.
        #         "enableTreeData": True,
        #         "multiColumnSort": False,
        #         "treeDataOptions": {
        #             "columnId": "title",
        #             "indentMarginLeft": 15,
        #             "initiallyCollapsed": True,
        #             # This is a field that add_tree_info() inserts in your data:
        #             "parentPropName": "__parent",
        #             # This is a field that add_tree_info() inserts in your data:
        #             "levelPropName": "__depth",
        #             #
        #             # If you're building your own tree (without add_tree_info),
        #             # you should configure the props above accordingly.
        #             #
        #             # See below for more info:
        #             # - https://ghiscoding.github.io/slickgrid-react-demos/#/example27
        #             # - https://ghiscoding.github.io/slickgrid-react-demos/#/example28
        #         },
        #         # Enables row or cell selection highlight behavior
        #         # "enableRowSelection": False,  # True enables row selection (requires enableCellNavigation=True)
        #         # "enableCellNavigation": False,  # True allows cell selection visualization (enableRowSelection must be False)
        #     }
        #
        #     data2 = df2.to_dict('records')  # ✅ SlickGrid формат
        #     data2 = add_tree_info(
        #         data2,
        #         tree_fields=["datum_titel", "agenda_link", "format", "bundesland", "akt_org", "akt_spn", "id", "adr_full"],
        #         # join_fields_as="title",
        #         id_field="id", )
        #
        #     out2 = slickgrid(
        #         data2,  # ✅ list of dicts
        #         columns2,
        #         options2,
        #         # key=st.session_state["profile_det2_key"],
        #         # on_click="rerun"
        #     )

        with st.expander(f"👥 **Personen** ({len(df1)})", expanded=True if len(df1) != 0 else False):

            dfheight1 = 0 if len(df1) == 0 else 40.7 * min(len(df1) + 3, 10)
            # обробляємо пусті дати
            for col in df1.select_dtypes(include=['datetime']):
                df1[col] = df1[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
            # формуємо датафрейм

            columns1 = [
                # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
                {"id": "vorname", "name": "Vorname", "field": "vorname", "sortable": True, "filterable": True,
                 "minWidth": 140},
                {"id": "nachname", "name": "Nachname", "field": "nachname", "sortable": True, "filterable": True,
                 "minWidth": 140},
                {"id": "id", "name": "ID Pers", "field": "id", "sortable": True, "filterable": True, "minWidth": 75},
                {"id": "email", "name": "Email", "field": "email", "sortable": True, "filterable": True, "minWidth": 200},
                {"id": "pers_kategorie", "name": "Kategorie", "field": "pers_kategorie", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "pers_position", "name": "Position", "field": "pers_position", "sortable": True, "filterable": True,
                 "minWidth": 100},
                {"id": "telefonnummer", "name": "Telefonnummer", "field": "telefonnummer", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "pers_mitg", "name": "MG", "field": "pers_mitg", "sortable": True, "filterable": True,
                 "minWidth": 20},
                {"id": "pers_mitg_maxd", "name": "Letzte MG Data", "field": "pers_mitg_maxd", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "aktivitaten_id", "name": "ID Akt", "field": "aktivitaten_id", "sortable": True, "filterable": True,
                 "minWidth": 75},
                {"id": "akt_titel", "name": "Letzte Akt Titel", "field": "akt_titel", "sortable": True, "filterable": True,
                 "minWidth": 100},
                {"id": "akt_maxd", "name": "Letzte Akt Data", "field": "akt_maxd", "sortable": True, "filterable": True,
                 "minWidth": 50},
                {"id": "kurzbezeichnung", "name": "Gekürzter Name", "field": "kurzbezeichnung", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "uns_id", "name": "ID Uns", "field": "uns_id", "sortable": True, "filterable": True,
                 "minWidth": 100},
            ]

            options1 = {
                #
                # Allow filtering (based on column filter* properties)
                "enableFiltering": True,
                # --
                #
                # Debounce/throttle the input text filter if you have lots of data
                # filterTypingDebounce: 250,
                # --
                #
                # Set up export options.
                "enableTextExport": True,
                "enableExcelExport": True,
                "excelExportOptions": {"sanitizeDataExport": True},
                "textExportOptions": {"sanitizeDataExport": True},
                "externalResources": [
                    ExportServices.ExcelExportService,
                    ExportServices.TextExportService,
                ],
                # --
                #
                # Pin columns.
                "frozenColumn": 1,
                # --
                #
                # Pin rows.
                # "frozenRow": 0,
                # --
                #
                # Don't scroll table when too big. Instead, just let it grow.
                "autoHeight": True,
                # --
                #
                # "autoResize": {"minHeight": 300,},
                # --
                #
                # Set up tree.
                "enableTreeData": True,
                "multiColumnSort": False,
                "treeDataOptions": {
                    "columnId": "title",
                    "indentMarginLeft": 15,
                    "initiallyCollapsed": True,
                    # This is a field that add_tree_info() inserts in your data:
                    "parentPropName": "__parent",
                    # This is a field that add_tree_info() inserts in your data:
                    "levelPropName": "__depth",
                    #
                    # If you're building your own tree (without add_tree_info),
                    # you should configure the props above accordingly.
                    #
                    # See below for more info:
                    # - https://ghiscoding.github.io/slickgrid-react-demos/#/example27
                    # - https://ghiscoding.github.io/slickgrid-react-demos/#/example28
                },
                # Enables row or cell selection highlight behavior
                # "enableRowSelection": False,  # True enables row selection (requires enableCellNavigation=True)
                # "enableCellNavigation": False,  # True allows cell selection visualization (enableRowSelection must be False)
            }

            data1 = df1.to_dict('records')  # ✅ SlickGrid формат
            data1 = add_tree_info(
                data1,
                tree_fields=["vorname", "nachname", "id", "email", "pers_kategorie", "pers_position", "telefonnummer",
                             "pers_mitg", "pers_mitg_maxd", "aktivitaten_id", "akt_titel", "akt_maxd", "kurzbezeichnung",
                             "uns_id"],
                join_fields_as="title",
                id_field="id", )

            out1 = slickgrid(
                data1,  # ✅ list of dicts
                columns1,
                options1,
                # key=st.session_state["profile_det1_key"],
                # on_click="rerun"
            )

        with st.expander(f"📅 **Veranstaltungen** ({len(df2)})", expanded=True if len(df2) != 0 else False):
            dfheight2 = 0 if len(df2) == 0 else 40.7 * min(len(df2) + 3, 10)
            # обробляємо пусті дати
            for col in df2.select_dtypes(include=['datetime']):
                df2[col] = df2[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')

            columns2 = [
                # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
                {"id": "datum_titel", "name": "Datum | Titel", "field": "datum_titel", "sortable": True, "filterable": True,
                 "minWidth": 200},
                {"id": "agenda_link", "name": "Agenda link", "field": "agenda_link", "sortable": True, "filterable": True,
                 "minWidth": 100, "formatter": Formatters.hyperlink},
                {"id": "format", "name": "Format", "field": "format", "sortable": True, "filterable": True, "minWidth": 75},
                {"id": "bundesland", "name": "Place", "field": "bundesland", "sortable": True, "filterable": True,
                 "minWidth": 75},
                {"id": "akt_org", "name": "Organizer", "field": "akt_org", "sortable": True, "filterable": True,
                 "minWidth": 200},
                {"id": "akt_spn", "name": "Sponsor", "field": "akt_spn", "sortable": True, "filterable": True,
                 "minWidth": 200},
                {"id": "id", "name": "ID", "field": "id", "sortable": True, "filterable": True, "minWidth": 75},
                {"id": "adr_full", "name": "Adress", "field": "adr_full", "sortable": True, "filterable": True,
                 "minWidth": 100},
            ]

            options2 = {
                #
                # Allow filtering (based on column filter* properties)
                "enableFiltering": True,
                # --
                #
                # Debounce/throttle the input text filter if you have lots of data
                # filterTypingDebounce: 250,
                # --
                #
                # Set up export options.
                "enableTextExport": True,
                "enableExcelExport": True,
                "excelExportOptions": {"sanitizeDataExport": True},
                "textExportOptions": {"sanitizeDataExport": True},
                "externalResources": [
                    ExportServices.ExcelExportService,
                    ExportServices.TextExportService,
                ],
                # --
                #
                # Pin columns.
                "frozenColumn": 0,
                # --
                #
                # Pin rows.
                # "frozenRow": 0,
                # --
                #
                # Don't scroll table when too big. Instead, just let it grow.
                "autoHeight": True,
                # --
                #
                # "autoResize": {"minHeight": 300,},
                # --
                #
                # Set up tree.
                "enableTreeData": True,
                "multiColumnSort": False,
                "treeDataOptions": {
                    "columnId": "title",
                    "indentMarginLeft": 15,
                    "initiallyCollapsed": True,
                    # This is a field that add_tree_info() inserts in your data:
                    "parentPropName": "__parent",
                    # This is a field that add_tree_info() inserts in your data:
                    "levelPropName": "__depth",
                    #
                    # If you're building your own tree (without add_tree_info),
                    # you should configure the props above accordingly.
                    #
                    # See below for more info:
                    # - https://ghiscoding.github.io/slickgrid-react-demos/#/example27
                    # - https://ghiscoding.github.io/slickgrid-react-demos/#/example28
                },
                # Enables row or cell selection highlight behavior
                # "enableRowSelection": False,  # True enables row selection (requires enableCellNavigation=True)
                # "enableCellNavigation": False,  # True allows cell selection visualization (enableRowSelection must be False)
            }

            data2 = df2.to_dict('records')  # ✅ SlickGrid формат
            data2 = add_tree_info(
                data2,
                tree_fields=["datum_titel", "agenda_link", "format", "bundesland", "akt_org", "akt_spn", "id", "adr_full"],
                # join_fields_as="title",
                id_field="id", )

            out2 = slickgrid(
                data2,  # ✅ list of dicts
                columns2,
                options2,
                # key=st.session_state["profile_det2_key"],
                # on_click="rerun"
            )

