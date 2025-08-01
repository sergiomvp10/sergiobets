import os
import psycopg2

def connect_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER", "admin"),  # si no cambiaste el user, por defecto es admin
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def create_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pronosticos (
            id SERIAL PRIMARY KEY,
            partido VARCHAR(255),
            liga VARCHAR(255),
            pronostico TEXT,
            cuota DECIMAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabla creada correctamente.")

if __name__ == "__main__":
    create_table()
