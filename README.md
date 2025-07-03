# 📊 KSO User Workplace (Streamlit App)

Цей застосунок дозволяє переглядати дані з бази `kso.db` у зручному інтерфейсі Streamlit.

## 📁 Структура
- `app.py` — головний файл
- `_pages/` — окремі сторінки (Unternehmen, Personen, ...)
- `sql/` — SQL-запити
- `utils/` — допоміжні функції
- `icon/` — іконки

## ⚠️ Увага
База kso_web.db завантажується вручну на старті застосунку.

## 🚀 Запуск
```bash
streamlit run app.py
