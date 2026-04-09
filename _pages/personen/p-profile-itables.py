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

title = 'personen'
st.subheader("👤 Personen (Persons)")

# === 1. Завантаження даних
query = load_sql(f"{title}/sel_profile.sql")
df = conn.execute(query).fetchdf()

# обробляємо пусті дати
for col in df.select_dtypes(include=['datetime']):
    df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')

# 2. Ваша таблиця з виправленнями
selection = interactive_table(
    df,
    caption='Personen',
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
        selected_indices = []
        st.info("Будь ласка, виберіть рядки в таблиці вище.")
else:
    selected_indices = []
# st.write(selection)

try:
    selected_df = df.iloc[selected_indices]
except:
    selected_df = None

if len(selected_df) > 0:

    sst.markdown("🔸**Details:**")

    # @st.cache_data(ttl=300)  # Кеш 5 хв
    def load_details_data(conn, selected_pers_id):
        query1 = f"""
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
                    WHERE wv2.pers_id = '{selected_pers_id}'
                    ORDER BY 1 desc
                    """
        df2 = conn.execute(query2).fetchdf()

        return df1, df2

    st.markdown("🔸**Other details:**")

    # ✅ БЕЗ spinner + sleep
    selected_pers_id = selected_df.iloc[0]['pers_id']
    df1, df2 = load_details_data(conn, selected_pers_id)

    # interactive_table(df1,
    #                   caption='df1',
    #                   select=True,
    #                   # selected_rows=[0, 1, 2, 100, 207],
    #                   buttons=['copyHtml5', 'csvHtml5', 'excelHtml5', 'colvis'])
    #
    # st.dataframe(df1, use_container_width=True)
    # st.dataframe(df2, use_container_width=True)

    # ✅ СТАТИЧНІ ТАБЛИЦІ (без placeholder)
    tab1, tab2 = st.tabs([f"Unternehmen ({str(len(df1))})", f"Veranstaltung ({str(len(df2))})"])

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