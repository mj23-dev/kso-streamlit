import streamlit as st
import pandas as pd
import time, io, base64
from datetime import datetime
from utils.io import load_sql
import itables
from itables.streamlit import interactive_table

from itables import to_html_datatable
from streamlit.components.v1 import html

itables.init_notebook_mode(connected=True)

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
interactive_table(
    df,
    caption='Unternehmen',
    buttons=["pageLength", 'copyHtml5', 'excelHtml5', 'colvis'],
    classes="display stripe cell-border order-column",
    scrollY="700px",
    scrollCollapse=True,
    paging=True,
    # Додаємо autoWidth=False, щоб columnDefs мали пріоритет
    autoWidth=False,
    eval_functions=True,  # ВАЖЛИВО: дозволяє JS-функції
    fixedColumns={"start": 1},
    columnDefs=[
        # {"width": "5%", "targets": [2,3,4,5]},
        {"width": "50px", "targets": [1]},
        {"width": "50px", "targets": [2]},
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