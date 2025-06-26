# 📊 KSO User Workplace (Streamlit App)

Цей застосунок дозволяє переглядати дані з бази `kso.db` у зручному інтерфейсі Streamlit.

## 📁 Структура
- `hauptseite.py` — головний файл
- `pages/` — окремі сторінки (Unternehmen, Personen, ...)
- `sql/` — SQL-запити
- `utils/` — допоміжні функції

## ⚠️ Увага
База kso.db завантажується вручну на старті застосунку.

## 🚀 Запуск
```bash
streamlit run hauptseite.py
