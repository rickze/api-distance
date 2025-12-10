
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("gps_cache.db")  # ficheiro na mesma pasta do main.py
# DB_PATH = Path(r"C:\APIs\GPS_DISTANCE\data\gps_cache.db") #

def init_db():
    #DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # cria pasta se não existir
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cep_distance_cache (
            cep_origem      TEXT    NOT NULL,
            cep_destino     TEXT    NOT NULL,
            vehicle_type    TEXT    NOT NULL,
            distance_km     REAL    NOT NULL,
            time_min        REAL    NOT NULL,
            distance_unit   TEXT    NOT NULL,
            time_unit       TEXT    NOT NULL,
            created_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_used_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            hit_count       INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (cep_origem, cep_destino, vehicle_type)
        );
    """)
    conn.commit()
    conn.close()

def get_from_cache(cep_origem: str, cep_destino: str, vehicle_type: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT distance_km, time_min, distance_unit, time_unit
          FROM cep_distance_cache
         WHERE cep_origem = ?
           AND cep_destino = ?
           AND vehicle_type = ?
    """, (cep_origem, cep_destino, vehicle_type))
    row = cur.fetchone()
    if row:
        # atualizar hit_count e last_used_at
        cur.execute("""
            UPDATE cep_distance_cache
               SET hit_count   = hit_count + 1,
                   last_used_at = CURRENT_TIMESTAMP
             WHERE cep_origem = ?
               AND cep_destino = ?
               AND vehicle_type = ?
        """, (cep_origem, cep_destino, vehicle_type))
        conn.commit()
        conn.close()
        return {
            "distance_km": row[0],
            "time_min": row[1],
            "distance_unit": row[2],
            "time_unit": row[3],
        }
    conn.close()
    return None


def save_to_cache(cep_origem: str,
                  cep_destino: str,
                  vehicle_type: str,
                  distance_km: float,
                  time_min: float,
                  distance_unit: str,
                  time_unit: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO cep_distance_cache (
            cep_origem, cep_destino, vehicle_type,
            distance_km, time_min, distance_unit, time_unit,
            created_at, last_used_at, hit_count
        )
        VALUES (
            ?, ?, ?,
            ?, ?, ?, ?,
            COALESCE(
              (SELECT created_at FROM cep_distance_cache
                WHERE cep_origem = ? AND cep_destino = ? AND vehicle_type = ?),
              CURRENT_TIMESTAMP
            ),
            CURRENT_TIMESTAMP,
            COALESCE(
              (SELECT hit_count FROM cep_distance_cache
                WHERE cep_origem = ? AND cep_destino = ? AND vehicle_type = ?),
              1
            )
        );
    """, (
        cep_origem, cep_destino, vehicle_type,
        distance_km, time_min, distance_unit, time_unit,
        cep_origem, cep_destino, vehicle_type,
        cep_origem, cep_destino, vehicle_type
    ))
    conn.commit()
    conn.close()
