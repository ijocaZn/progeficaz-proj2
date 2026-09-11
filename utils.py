import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def conectar_banco():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca=os.getenv("DB_SSL_CA"),
        port=int(os.getenv("DB_PORT"))
    )
    return conn

def listar_imoveis():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imoveis")
    imoveis = cursor.fetchall()
    cursor.close()
    conn.close()
    return imoveis

def listar_imovel_por_id(id):
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
    imovel = cursor.fetchone()
    cursor.close()
    conn.close()
    return imovel