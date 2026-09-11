from flask import Flask, request
from database import conectar_bd

app = Flask(__name__)


@app.route("/probar")
def probar_data():
    conec = conectar_bd()

    if conec.is_connected():
        conec.close()

    return {"mensaje": "Conexion ok"}


@app.route("/api/actualizarhv/<int:id>", methods=["PUT"])
def actualizar_hv(id):

    datos = request.get_json()

    conec = conectar_bd()
    cursor = conec.cursor(buffered=True)

    buscar = """SELECT id FROM hojas_vida WHERE id=%s"""

    cursor.execute(buscar, (id,))
    result = cursor.fetchone()

    if result is None:
        cursor.close()
        conec.close()

        return {"mensaje": "No se encontro la hoja de vida"}

    sql_correo = """SELECT id FROM hojas_vida WHERE correo=%s AND id!=%s"""

    cursor.execute(sql_correo, (datos["correo"], id))
    result = cursor.fetchone()

    if result is not None:

        cursor.close()
        conec.close()

        return {"mensaje": "El correo ya está registrado con otra hoja de vida"}

    sql_actualizar = """UPDATE hojas_vida 
                        SET nombre=%s, edad=%s, ciudad=%s, correo=%s, 
                        fotografia=%s, programa=%s, ficha=%s, jornada=%s 
                        WHERE id=%s"""

    valores = (
        datos["nombre"],
        datos["edad"],
        datos["ciudad"],
        datos["correo"],
        datos.get("fotografia"),
        datos["programa"],
        datos["ficha"],
        datos["jornada"],
        id
    )

    cursor.execute(sql_actualizar, valores)

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "Mensaje": "Hoja de vida actualizada",
        "id": id
    }


@app.route("/api/eliminarhv/<int:id>", methods=["DELETE"])
def eliminar_hv(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    buscar = "SELECT id FROM hojas_vida WHERE id = %s"

    cursor.execute(buscar, (id,))
    existe = cursor.fetchone()

    if existe is None:
        cursor.close()
        conec.close()

        return {"mensaje": "No se encontro la hoja de vida"}

    sql_eliminar = """DELETE FROM hojas_vida WHERE id=%s"""

    cursor.execute(sql_eliminar, (id,))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Hoja de vida eliminada",
        "id": id
    }


@app.route("/api/consultahv/<int:id>", methods=["GET"])
def obtener_hvida(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT * FROM hojas_vida WHERE id=%s"""

    cursor.execute(sql, (id,))

    datos = cursor.fetchone()

    cursor.close()
    conec.close()

    if datos is None:
        return {"mensaje": "No se encontro la hoja de vida"}

    return datos


@app.route("/api/registrohv", methods=["POST"])
def registrohvida():

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.get_json()

    cursor.execute(
        "SELECT * FROM hojas_vida WHERE correo = %s",
        (datos['correo'],)
    )

    resultado = cursor.fetchone()

    if resultado:
        cursor.close()
        conec.close()

        return {"mensaje": "El correo ya está registrado"}

    sql = """INSERT INTO hojas_vida 
             (nombre, edad, ciudad, correo, fotografia, programa, ficha, jornada) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    cursor.execute(sql, (
        datos["nombre"],
        datos["edad"],
        datos["ciudad"],
        datos["correo"],
        datos.get("fotografia"),
        datos["programa"],
        datos["ficha"],
        datos["jornada"]
    ))

    id_generado = cursor.lastrowid

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Hoja de vida creada",
        "id": id_generado
    }


@app.route("/")
def inicio():

    return "Api hoja de vida funcionando"


@app.route("/api/hojasdevida/<int:id>")
def obtener_hojasvidaid(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT * FROM hojas_vida WHERE id=%s"""

    cursor.execute(sql, (id,))

    hoja = cursor.fetchone()

    cursor.close()
    conec.close()

    if hoja is None:
        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    return {
        "mensaje": "Hoja de vida encontrada",
        "id": id
    }


@app.route("/api/hojasdevida")
def obtener_hojasvida():

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT * FROM hojas_vida"""

    cursor.execute(sql)

    hojasdevida = cursor.fetchall()

    cursor.close()
    conec.close()

    return hojasdevida
