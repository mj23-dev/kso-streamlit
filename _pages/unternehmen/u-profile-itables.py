import streamlit as st
import pandas as pd
import time, io, base64
from datetime import datetime
from utils.io import load_sql
import itables
from itables.streamlit import interactive_table

from itables import to_html_datatable
from streamlit.components.v1 import html

itables.options.warn_on_undocumented_option=False

# itables.init_notebook_mode(connected=True)

# Описуємо CSS прямо всередині параметра style
# Це додасть стилі безпосередньо в тег <style> всередині iframe таблиці
custom_css = """
table.dataTable thead th {
    background-color: #2E86C1 !important;
    color: white !important;
    font-size: 18px !important;
    font-family: sans-serif !important;
}
table.dataTable tbody td {
    font-size: 18px !important;
    color: #333 !important;
}
"""

itables.init_notebook_mode()
itables.options.maxBytes = 0 #show all rows from sql
itables.options.column_filters = "footer"

# st.markdown("""
# <style>
#     /* Фіксуємо макет усієї таблиці */
#     .itables table {
#         table-layout: fixed !important;
#         width: 100% !important;
#         font-family: 'Courier New', monospace;
#         font-size: 14px;
#     }
#
#     /* Примусово обрізаємо контент у 4-й колонці (nth-child(4)) */
#     /* Якщо у вас відображається індекс Pandas, спробуйте nth-child(5) */
#     .itables td:nth-child(3) {
#         width: 120px !important;
#         max-width: 120px !important;
#         overflow: hidden !important;
#         text-overflow: ellipsis !important;
#         white-space: nowrap !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# Приклад таблиці
# df = pd.DataFrame({'Назва': ['Товар А', 'Товар Б'], 'Ціна': [100, 200]})

# html(
#     to_html_datatable(
#         df,
#         layout={"top1": "searchPanes"},
#         searchPanes={"layout": "columns-3", "cascadePanes": True},
#     ),
#     height=960,  # adjust manually
# )

# interactive_table(
#     df,
#     style=custom_css,
#     classes="display nowrap",
#     width="100%"
# )

# from itables import to_html_datatable
# from streamlit.components.v1 import html
# itables.init_notebook_mode()

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
st.subheader("🏢 Unternehmen (Сompanies)")

# === 1. Завантаження даних
query = load_sql(f"{title}/sel_profile.sql")
df = conn.execute(query).fetchdf()

# обробляємо пусті дати
for col in df.select_dtypes(include=['datetime']):
    df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')


# html(
#     to_html_datatable(
#         df,
#         layout={"top1": "searchPanes"},
#         searchPanes={"layout": "columns-3", "cascadePanes": True},
#     ),
#     height=960,  # adjust manually
# )

# 2. Ваша таблиця з виправленнями
selection = interactive_table(
    df,
    caption='Unternehmen',
    buttons=["pageLength", 'copyHtml5', 'excelHtml5', 'colvis'],
    classes="display stripe cell-border order-column",
    # classes="display nowrap compact cell-border",
    scrollY="700px",
    scrollCollapse=True,
    paging=True,
    # Додаємо autoWidth=False, щоб columnDefs мали пріоритет
    autoWidth=False,
    eval_functions=True,  # ВАЖЛИВО: дозволяє JS-функції
    fixedColumns={"start": 1},
    columnDefs=[
        # {"width": "5%", "targets": [2,3,4,5]},
        # {"width": "100px", "targets": [0]},
        # {"width": "50px", "targets": [2]},
        # {"width": "5px", "targets": [2]},
        {"className": "dt-right", "targets": [2]},
        # {"className": "dt-left", "targets": "_all"},
        {
            "targets": [3],
            "render": itables.JavascriptCode("""
        function (data, type, row) {
            if (type === 'display' && 'www') {
                return '<a href="' + data + '" target="_blank">' + 'www' + '</a>';
            }
            return data;
        }
    """)
        }
    ],
    style="width:100%;margin:auto",
    # scrollX дозволяє гортати таблицю вбік, якщо 120px * к-сть стовпців > ширини екрана
    scrollX=True,
    lengthMenu=[10, 50, 100, 1000, 5000],
    pageLength=100,
    select=True,
    footer=True,
    columnControl=["order", ["orderAsc", "orderDesc", "orderClear", "search", "searchClear", 'searchList']],
    ordering={"indicators": False, "handler": True},
    allow_html=True,
)

# Перевіряємо, чи є вибір і чи він не порожній
if selection and "selected_rows" in selection:
    raw_rows = selection["selected_rows"]

    if raw_rows:
        selected_indices = []
        for item in raw_rows:
            if isinstance(item, str) and ":" in item:
                # Обробка діапазону типу "0:2" -> [0, 1, 2]
                start, end = map(int, item.split(":"))
                selected_indices.extend(range(start, end + 1))
            else:
                # Якщо це просто число
                selected_indices.append(int(item))

        # st.write(f"Ви вибрали {len(selected_indices)} рядків:")
        # st.dataframe(df.iloc[selected_indices])
    else:
        st.info("Будь ласка, виберіть рядки в таблиці вище.")

# st.write(selection)

selected_df = df.iloc[selected_indices]
if len(selected_df) > 0:

    st.markdown(f"🔸**Voller Name:** {selected_df.iloc[0]['vollname_der_firma']}")

    placeholder_col = st.empty()
    col_adr, col_form = placeholder_col.columns([0.5, 0.5])
    with col_adr:
        st.markdown(f"🔸**Adresse:** {selected_df.iloc[0]['rechnungsadr_full']}")
    with col_form:
        if selected_df.iloc[0]['rechtsform']:
            st.markdown(f"🔸**Rechtsform:** {selected_df.iloc[0]['rechtsform']}")

    if selected_df.iloc[0]['onace_code5']:
        expander = st.expander(f"**ONACE:** {selected_df.iloc[0]['onace_sh_de5']} ({selected_df.iloc[0]['onace_code5']})", expanded=False)
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
                expander = col_prod.expander(f"**Produkte von 'Compass':** {selected_df.iloc[0]['product_name_agg'].split('|')[0]} ... ↩️", expanded=False)
                expander.write(f"{selected_df.iloc[0]['product_name_agg']}")
            else:
                expander = col_prod.expander("**Produkte von 'Compass':** ❌", expanded=False)
                expander.write(f"")
    except:
        pass

    try:
        with col_comm:
            if selected_df.iloc[0]['tatigkeitsbeschreibung']:
                expander = col_comm.expander(f"**Tatigkeitsbeschreibung:** {selected_df.iloc[0]['tatigkeitsbeschreibung'][0:75]}... ↩️", expanded=False)
                expander.write(f"{selected_df.iloc[0]['tatigkeitsbeschreibung']}")
    except:
        pass


    # @st.cache_data(ttl=300)  # Кеш 5 хв
    def load_details_data(conn, selected_uns_id):
        query1 = f"""
                    SELECT wlup.pers_id, wp.vorname, wp.nachname,
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
                      from (select wv.datum_titel, case when wv.agenda_link = '-' then null else wv.agenda_link end as agenda_link,
                                    wv.format, coalesce(wv.bundesland,'-') as bundesland, wv.akt_org, wv.akt_spn,
                                    wv.adr_full, wv.aktivitaten_id
                                from main.w_veranstaltung wv
                                group by wv.datum_titel, wv.aktivitaten_id, wv.agenda_link, wv.format, wv.datum_bis_year,
                                        wv.bundesland, wv.akt_org, wv.akt_spn, wv.adr_full
                            ) wv
                    INNER JOIN main.w_veranstaltung wv2 on wv.aktivitaten_id = wv2.aktivitaten_id
                    WHERE wv2.uns_id = '{selected_uns_id}'
                    ORDER BY 1 desc
                    """  # твій запит2
        df2 = conn.execute(query2).fetchdf()

        return df1, df2

    st.markdown("🔸**Other details:**")

    # ✅ БЕЗ spinner + sleep
    selected_uns_id = selected_df.iloc[0]['uns_id']
    df1, df2 = load_details_data(conn, selected_uns_id)

    # interactive_table(df1,
    #                   caption='df1',
    #                   select=True,
    #                   # selected_rows=[0, 1, 2, 100, 207],
    #                   buttons=['copyHtml5', 'csvHtml5', 'excelHtml5', 'colvis'])
    #
    # st.dataframe(df1, use_container_width=True)
    # st.dataframe(df2, use_container_width=True)

    # ✅ СТАТИЧНІ ТАБЛИЦІ (без placeholder)
    tab1, tab2 = st.tabs([f"Personen ({len(df1)})", f"Veranstaltung ({len(df2)})"])

    with tab1:
        interactive_table(
            df1,
            # caption='Unternehmen',
            # buttons=["pageLength", 'copyHtml5', 'excelHtml5', 'colvis'],
            classes="display stripe cell-border order-column",
            # classes="display nowrap compact cell-border",
            scrollY="700px",
            scrollCollapse=True,
            paging=True,
            # Додаємо autoWidth=False, щоб columnDefs мали пріоритет
            autoWidth=False,
            eval_functions=True,  # ВАЖЛИВО: дозволяє JS-функції
            fixedColumns={"start": 3},
            style="width:100%;margin:auto",
            # scrollX дозволяє гортати таблицю вбік, якщо 120px * к-сть стовпців > ширини екрана
            scrollX=True,
            pageLength=10,
            select=False,
            # footer=True,
            columnControl=["order", ["orderAsc", "orderDesc", "orderClear", "search", "searchClear", 'searchList']],
            ordering={"indicators": False, "handler": True},
            allow_html=True,
        )

    with tab2:
        interactive_table(
            df2,
            # caption='Unternehmen',
            # buttons=["pageLength", 'copyHtml5', 'excelHtml5', 'colvis'],
            classes="display stripe cell-border order-column",
            # classes="display nowrap compact cell-border",
            scrollY="700px",
            scrollCollapse=True,
            paging=True,
            # Додаємо autoWidth=False, щоб columnDefs мали пріоритет
            autoWidth=False,
            eval_functions=True,  # ВАЖЛИВО: дозволяє JS-функції
            fixedColumns={"start": 1},
            style="width:100%;margin:auto",
            # scrollX дозволяє гортати таблицю вбік, якщо 120px * к-сть стовпців > ширини екрана
            scrollX=True,
            pageLength=10,
            select=True,
            # footer=True,
            columnControl=["order", ["orderAsc", "orderDesc", "orderClear", "search", "searchClear", 'searchList']],
            ordering={"indicators": False, "handler": True},
            allow_html=True,
            columnDefs=[
                {
                    "targets": [1],
                    "render": itables.JavascriptCode("""
            function (data, type, row) {
                if (type === 'display' && 'www') {
                    return '<a href="' + data + '" target="_blank">' + 'www' + '</a>';
                }
                return data;
            }
        """)
                }
            ],
        )