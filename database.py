import mysql.connector

def conectar_bd():
    conexion = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        database="hojas_de_vida"
    )

    return conexion