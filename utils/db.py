import duckdb, tempfile, os

def connect_temp_duckdb(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(uploaded_file.read())
        db_path = tmp.name
    try:
        conn = duckdb.connect(db_path, read_only=True)
        return conn, db_path
    except Exception as e:
        if os.path.exists(db_path):
            os.remove(db_path)
        raise e
