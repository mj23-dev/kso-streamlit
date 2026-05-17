import streamlit as st
import pandas as pd
import time, io, base64
import streamlit.components.v1 as components
from datetime import datetime
from utils.io import load_sql
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
# from reflex_ag_grid import ag_grid
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
data = df.to_dict('records')  # ✅ SlickGrid формат
data = add_tree_info(
    data,
    tree_fields=["vorname", "nachname", "id", "pers_mitg", "pers_mitg_maxd", "anrede", "titel_vorne", "titel_hinten", "domain", "telefonnummer", "geburtsdatum", "sprachen", "email1", "email2", "email3", "email4", "email5", "rechnungs_email1", "rechnungs_email2", "rechnungs_email3", "juradr_land", "juradr_bundesland", "adr_plz_ort", "strasse", "juradr_full", "akt_titel", "akt_maxd", "aktivitaten_id", "cnt_uns", "vollname_der_firma_aggr", "kurzbezeichnung_aggr"],
    join_fields_as="title",
    id_field="id",)

# звязки uns_pers для експорту
query = load_sql(f"{title}/sel_w_links_uns_pers.sql")
df_pers = conn.execute(query).fetchdf()

cnt_full = len(df)
cnt_filtered = len(df)

# === 2. Обробка Reset Filters ===
# col_left, col_center1, col_center2, col_right = st.columns([0.65, 0.15, 0.15, 0.15])
col_left, col_center1, col_right = st.columns([0.55, 0.15, 0.25])
with col_left:
    st.markdown("👆 Klicken Sie auf den Eintrag, um Details anzuzeigen:")
with col_center1:
    if st.button("🔄 Reset filters", use_container_width=True):
        st.session_state["reload_grid"] = True
        st.session_state["reset_grid_key"] = f"grid_{datetime.now().timestamp()}"
        st.rerun()

# === 4. Slickgrid відображення
columns = [
            # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
    {"id": "vorname", "name": "Vorname", "field": "vorname", "sortable": True, "filterable": True, "minWidth": 150},
    {"id": "nachname", "name": "Nachname", "field": "nachname", "sortable": True, "filterable": True, "minWidth": 150},
    {"id": "id", "name": "ID Pers", "field": "id", "sortable": True, "filterable": True, "minWidth": 150},
    {"id": "pers_mitg", "name": "MG", "field": "pers_mitg", "sortable": True, "filterable": True, "minWidth": 50},
    {"id": "pers_mitg_maxd", "name": "Letzte MG Data", "field": "pers_mitg_maxd", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "anrede", "name": "Anrede", "field": "anrede", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "titel_vorne", "name": "Titel Vorne", "field": "titel_vorne", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "titel_hinten", "name": "Titel Hinten", "field": "titel_hinten", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "domain", "name": "Plz-Ort", "field": "domain", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "telefonnummer", "name": "Telefonnummer", "field": "telefonnummer", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "geburtsdatum", "name": "Geburtsdatum", "field": "geburtsdatum", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "sprachen", "name": "Sprachen", "field": "sprachen", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "email1", "name": "Email1", "field": "email1", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "email2", "name": "Email2", "field": "email2", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "email3", "name": "Email3", "field": "email3", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "email4", "name": "Email4", "field": "email4", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "email5", "name": "Email5", "field": "email5", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "rechnungs_email1", "name": "RchnEmail1", "field": "rechnungs_email1", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "rechnungs_email2", "name": "RchnEmail2", "field": "rechnungs_email2", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "rechnungs_email3", "name": "RchnEmail3", "field": "rechnungs_email3", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "juradr_land", "name": "Land", "field": "juradr_land", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "juradr_bundesland", "name": "Bundesland", "field": "juradr_bundesland", "sortable": True,
     "filterable": True, "minWidth": 100},
    {"id": "adr_plz_ort", "name": "Plz-Ort", "field": "adr_plz_ort", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "strasse", "name": "Strasse", "field": "strasse", "sortable": True, "filterable": True, "minWidth": 100},
    {"id": "juradr_full", "name": "Adresse", "field": "juradr_full", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "akt_titel", "name": "Letzte Akt Data", "field": "akt_titel", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "akt_maxd", "name": "Letzte Akt Titel", "field": "akt_maxd", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "aktivitaten_id", "name": "ID Akt", "field": "aktivitaten_id", "sortable": True, "filterable": True,
     "minWidth": 100},
    {"id": "cnt_uns", "name": "Cnt Uns", "field": "cnt_uns", "sortable": True, "filterable": True, "minWidth": 50},
    {"id": "vollname_der_firma_aggr", "name": "Uns Voller Name", "field": "vollname_der_firma_aggr", "sortable": True,
     "filterable": True, "minWidth": 100},
    {"id": "kurzbezeichnung_aggr", "name": "Uns Gekürzter Name", "field": "kurzbezeichnung_aggr", "sortable": True,
     "filterable": True, "minWidth": 100},
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

out = slickgrid(
        data,  # ✅ list of dicts
        columns,
        options,
        key=st.session_state["reset_grid_key"],
        on_click = "rerun"
    )

@st.dialog("Details", width="large")
def show_dialog(item):
    # st.write("Congrats! You clicked on the row below:")
    st.write(item)

if out is not None:
    row, col = out
    selected_uns_id = out[0]
    # print(selected_uns_id)
    selected_df = df[df['id'] == row]
    selected_df_tr = selected_df.transpose()
    # st.dataframe(selected_df_tr, use_container_width=True)
    # show_dialog(selected_df_tr)

# filtered_df = pd.DataFrame(grid_response['data'])
# cnt_filtered = len(filtered_df)

# === 6. Деталі вибраного рядка
# selected = grid_response['selected_rows']
# selected_df = pd.DataFrame(selected)

if out is not None:
    if len(selected_df) > 0:

        # @st.cache_data(ttl=300)  # Кеш 5 хв
        def load_details_data(conn, selected_uns_id):
            query1 = f"""
                        SELECT wu.vollname_der_firma, wlup.pers_position, wu.uns_id as id,
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
                        WHERE wv2.pers_id = '{selected_pers_id}'
                        ORDER BY 1 desc
                        """
            df2 = conn.execute(query2).fetchdf()

            return df1, df2

        selected_pers_id = selected_df.iloc[0]['id']
        df1, df2 = load_details_data(conn, selected_pers_id)

        st.markdown("🔸**Details:**")

        with st.expander(f"🏢 **Unternehmen** ({str(len(df1))})", expanded=True if len(df1) != 0 else False):

            dfheight1 = 0 if len(df1) == 0 else 40.7 * min(len(df1) + 3, 10)
            # обробляємо пусті дати
            for col in df1.select_dtypes(include=['datetime']):
                df1[col] = df1[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
            # формуємо датафрейм

            columns1 = [
                # {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True, "filterable": True, "formatter": Formatters.tree, "exportCustomFormatter": Formatters.treeExport, "minWidth": 450},
                {"id": "vollname_der_firma", "name": "Voller Name", "field": "vollname_der_firma", "sortable": True,
                 "filterable": True, "minWidth": 450},
                {"id": "pers_position", "name": "Position", "field": "pers_position", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "id", "name": "ID", "field": "id", "sortable": True, "filterable": True,
                 "minWidth": 150},
                {"id": "seite", "name": "Link zur Website", "field": "seite", "sortable": True, "filterable": True,
                 "minWidth": 200, "formatter": Formatters.hyperlink},
                {"id": "email", "name": "Email", "field": "email", "sortable": True, "filterable": True,
                 "minWidth": 200},
                {"id": "telefonnummer", "name": "Telefonnummer", "field": "telefonnummer", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "rechnungsadr_land", "name": "Land", "field": "rechnungsadr_land", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "rechnungsadr_bundesland", "name": "Bundesland", "field": "rechnungsadr_bundesland",
                 "sortable": True, "filterable": True, "minWidth": 200},
                {"id": "rechnungsadr_plz_ort", "name": "Plz-Ort", "field": "rechnungsadr_plz_ort", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "rechtsform", "name": "Rechtsform", "field": "rechtsform", "sortable": True, "filterable": True,
                 "minWidth": 200},
                {"id": "onace_code5", "name": "ONACE", "field": "onace_code5", "sortable": True, "filterable": True,
                 "minWidth": 100},
                {"id": "onace_sh_de1", "name": "ONACE L1", "field": "onace_sh_de1", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "onace_sh_de2", "name": "ONACE L2", "field": "onace_sh_de2", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "onace_sh_de3", "name": "ONACE L3", "field": "onace_sh_de3", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "onace_sh_de4", "name": "ONACE L4", "field": "onace_sh_de4", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "onace_sh_de5", "name": "ONACE L5", "field": "onace_sh_de5", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "product_name_agg", "name": "Produkte von 'Compass'", "field": "product_name_agg",
                 "sortable": True, "filterable": True, "minWidth": 200},
                {"id": "tatigkeitsbeschreibung", "name": "Tatigkeitsbeschreibung", "field": "tatigkeitsbeschreibung",
                 "sortable": True, "filterable": True, "minWidth": 200},
                {"id": "uns_mitg", "name": "Uns MG", "field": "uns_mitg", "sortable": True, "filterable": True,
                 "type": FieldType.number, "minWidth": 50},
                {"id": "uns_mitg_maxd", "name": "Letzte MG Data", "field": "uns_mitg_maxd", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "aktivitaten_id", "name": "Letzte Akt ID", "field": "aktivitaten_id", "sortable": True,
                 "filterable": True, "minWidth": 120},
                {"id": "akt_titel", "name": "Letzte Akt Titel", "field": "akt_titel", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "akt_maxd", "name": "Letzte Akt Data", "field": "akt_maxd", "sortable": True, "filterable": True,
                 "minWidth": 100},
                {"id": "heaf", "name": "Heaf", "field": "heaf", "sortable": True, "filterable": True, "minWidth": 50},
                {"id": "hauptunternehmen_id", "name": "ID Haupt", "field": "hauptunternehmen_id", "sortable": True,
                 "filterable": True, "minWidth": 120},
                {"id": "kurzbezeichnung", "name": "Gekürzter Name", "field": "kurzbezeichnung", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "rechnungsadr_full", "name": "Adresse", "field": "rechnungsadr_full", "sortable": True,
                 "filterable": True, "minWidth": 200},
                {"id": "registrierungsstatus", "name": "Status", "field": "registrierungsstatus", "sortable": True,
                 "filterable": True, "minWidth": 100},
                {"id": "compass_id", "name": "ID Compass", "field": "compass_id", "sortable": True, "filterable": True,
                 "type": FieldType.number, "minWidth": 100},
                {"id": "id", "name": "Row ID", "field": "id", "sortable": True, "filterable": True,
                 "type": FieldType.number, "minWidth": 100},
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
                # "autoResize": {"minHeight": 450,},
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
                "enableCellNavigation": True,
                # True allows cell selection visualization (enableRowSelection must be False)
            }

            data1 = df1.to_dict('records')  # ✅ SlickGrid формат
            data1 = add_tree_info(
                data1,
                tree_fields=["vollname_der_firma", "pers_position", "uns_id", "seite", "email", "telefonnummer", "rechnungsadr_land", "rechnungsadr_bundesland", "rechnungsadr_plz_ort", "rechtsform", "onace_code5", "onace_sh_de1", "onace_sh_de2", "onace_sh_de3", "onace_sh_de4", "onace_sh_de5", "product_name_agg", "tatigkeitsbeschreibung", "uns_mitg", "uns_mitg_maxd", "aktivitaten_id", "akt_titel", "akt_maxd", "heaf", "hauptunternehmen_id", "kurzbezeichnung", "rechnungsadr_full", "registrierungsstatus", "compass_id", "id"],
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
