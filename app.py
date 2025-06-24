import streamlit as st
import gdown
import zipfile, tempfile
import os, shutil, atexit
import duckdb
import pandas as pd

# --- Налаштування ---
GDRIVE_FILE_ID = "1Is6lzxCWMr9b82peiSAOZ5eNGMa8QRFK"
ZIP_PATH = "./PycharmProjects/kso/temp/db/kso.zip"

st.set_page_config(page_title="KSO Viewer", layout="wide")
st.title("📊 KSO Web Viewer (Streamlit + gdown)")

# Створюємо тимчасову директорію
# temp_dir = tempfile.mkdtemp()
temp_dir = './PycharmProjects/kso/temp/db/'

if temp_dir and os.path.exists(temp_dir + 'kso.db'):
    # shutil.rmtree(temp_dir)
    try:
        os.remove(temp_dir + 'kso.db')
    except:
        print('error os.remove')

# --- Завантаження ZIP з Google Drive ---
@st.cache_resource
def download_and_extract_zip(file_id, password):

    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    gdown.download(url, ZIP_PATH, quiet=False)

    try:
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.setpassword(password.encode("utf-8"))
            zf.extractall(temp_dir)
        return True, None
    except zipfile.BadZipFile:
        return False, "❌ Неможливо прочитати ZIP-файл. Можливо, це не ZIP або він пошкоджений."
    except RuntimeError:
        return False, "🔒 Невірний пароль до ZIP-файлу."
    except Exception as e:
        return False, str(e)


# --- Ввід паролю ---
with st.expander("🔐 Ввести пароль для доступу до бази"):
    user_pass = st.text_input("Пароль до архіву", type="password")
    if st.button("Завантажити базу"):
        with st.spinner("⏬ Завантаження та розшифрування..."):
            ok, err = download_and_extract_zip(GDRIVE_FILE_ID, user_pass)
            if ok:
                st.success("✅ Архів розпаковано. База готова до роботи.")
                st.info(f"Файл `kso.db` розпаковано у: `{os.path.abspath(temp_dir)}`")
            else:
                st.error(err)

db_path = os.path.join(temp_dir, "kso.db")
# st.info(f"Файл `kso.db` розпаковано у: `{os.path.abspath(db_path)}`")
if not os.path.exists(db_path):
    st.error("Файл kso.db не знайдено після розпакування.")

# --- Завантаження бази (якщо існує) ---
if os.path.exists(db_path):
    conn = duckdb.connect(db_path, read_only=True)

    tab = st.sidebar.radio("Оберіть таблицю", ["t_uns", "t_pers"])

    if tab == "t_uns":
        df = pd.read_sql("SELECT * FROM t_uns", conn)
    elif tab == "t_pers":
        df = pd.read_sql("SELECT * FROM t_pers", conn)

    st.subheader(f"📁 Дані з таблиці `{tab}`")

    # Простий текстовий фільтр
    search = st.text_input("🔍 Пошук по всім полям").strip().lower()
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search).any(), axis=1)]

    st.dataframe(df, use_container_width=True)

    # Кнопка експорту
    if not df.empty and st.button("⬇️ Експорт у Excel"):
        df.to_excel("filtered_data.xlsx", index=False)
        with open("filtered_data.xlsx", "rb") as f:
            st.download_button("📥 Завантажити Excel", f, file_name="filtered_data.xlsx")
else:
    st.warning("ℹ️ Після введення паролю та розпакування ZIP-файлу з'явиться доступ до бази.")

# === При завершенні сесії видаляємо тимчасову папку ===
@st.cache_resource(show_spinner=False)
def cleanup():
    if temp_dir and os.path.exists(temp_dir):
        # shutil.rmtree(temp_dir)
        os.remove(temp_dir + 'kso.db')

# Автоматичне очищення при виході (стрімліт перезавантажить процес при зміні коду або новій сесії)
# st.on_event("shutdown", cleanup)  # лише для Streamlit >= 1.33
atexit.register(cleanup)