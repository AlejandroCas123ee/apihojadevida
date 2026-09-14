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

@app.route("/api/HOJAS_VIDA/<int:id>/estudios", methods=["GET"])
def consultar_estudios(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, hoja_vida_id, nivel, institucion, titulo,
             anio_graduacion
             FROM estudios
             WHERE hoja_vida_id = %s"""

    cursor.execute(sql, (id,))

    estudios = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida_id": id,
        "estudios": estudios
    }


@app.route("/api/estudios/<int:id>/estudios", methods=["POST"])
def registrar_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    nivel = datos.get("nivel")
    institucion = datos.get("institucion")
    titulo = datos.get("titulo")
    anio_graduacion = datos.get("anio_graduacion")

    sql = """INSERT INTO estudios
             (nivel, institucion, titulo, anio_graduacion, hoja_vida_id)
             VALUES (%s, %s, %s, %s, %s)"""

    cursor.execute(
        sql,
        (
            nivel,
            institucion,
            titulo,
            anio_graduacion,
            id
        )
    )

    conec.commit()

    id_estudio = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio registrado para la hoja de vida",
        "id": id_estudio
    }


@app.route("/api/estudios/<int:id>", methods=["GET"])
def consultar_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, hoja_vida_id, nivel, institucion, titulo,
             anio_graduacion
             FROM estudios
             WHERE id = %s"""

    cursor.execute(sql, (id,))

    estudio = cursor.fetchone()

    cursor.close()
    conec.close()

    if estudio is None:
        return {
            "mensaje": "Estudio no encontrado"
        }, 404

    return estudio, 200


@app.route("/api/estudios/<int:id>/estudios", methods=["PUT"])
def actualizar_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    sql = """UPDATE estudios
             SET nivel = %s,
                 institucion = %s,
                 titulo = %s,
                 anio_graduacion = %s
             WHERE id = %s"""

    cursor.execute(
        sql,
        (
            datos.get("nivel"),
            datos.get("institucion"),
            datos.get("titulo"),
            datos.get("anio_graduacion"),
            id
        )
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio actualizado",
        "id": id
    }


@app.route("/api/estudios/<int:id>", methods=["DELETE"])
def eliminar_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    sql = "DELETE FROM estudios WHERE id = %s"

    cursor.execute(sql, (id,))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio eliminado",
        "id": id
    }, 200

@app.route("/api/EXPERIENCIAS/<int:id>/EXPERIENCIAS", methods=["POST"])
def registrar_experiencia(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    empresa = datos.get("empresa")
    cargo = datos.get("cargo")
    tiempo = datos.get("tiempo")
    funciones = datos.get("funciones")

    sql = """INSERT INTO experiencias
             (empresa, cargo, tiempo, funciones, hoja_vida_id)
             VALUES (%s, %s, %s, %s, %s)"""

    cursor.execute(
        sql,
        (
            empresa,
            cargo,
            tiempo,
            funciones,
            id
        )
    )

    conec.commit()

    id_experiencia = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia registrada para la hoja de vida",
        "id": id_experiencia
    }


@app.route("/api/HOJAS_VIDA/<int:id>/EXPERIENCIAS", methods=["GET"])
def consultar_experienciashv(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, hoja_vida_id, empresa, cargo, tiempo, funciones
             FROM experiencias
             WHERE hoja_vida_id = %s"""

    cursor.execute(sql, (id,))

    experiencias = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida_id": id,
        "experiencias": experiencias
    }


@app.route("/api/EXPERIENCIAS/<int:id>", methods=["GET"])
def consultar_experiencia(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT * FROM experiencias WHERE id = %s"""

    cursor.execute(sql, (id,))

    experiencia = cursor.fetchone()

    cursor.close()
    conec.close()

    if experiencia is None:
        return {
            "mensaje": "Experiencia no encontrada"
        }, 404

    return experiencia, 200


@app.route("/api/EXPERIENCIAS/<int:id_hv>/<int:id_exp>", methods=["PUT"])
def actualizar_experiencia(id_hv, id_exp):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    sql = """UPDATE experiencias
             SET empresa = %s,
                 cargo = %s,
                 tiempo = %s,
                 funciones = %s
             WHERE id = %s
             AND hoja_vida_id = %s"""

    cursor.execute(
        sql,
        (
            datos.get("empresa"),
            datos.get("cargo"),
            datos.get("tiempo"),
            datos.get("funciones"),
            id_exp,
            id_hv
        )
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia actualizada",
        "id": id_exp,
        "hoja_vida_id": id_hv
    }


@app.route("/api/EXPERIENCIAS/<int:id_hv>/<int:id_exp>", methods=["DELETE"])
def eliminar_experiencia(id_hv, id_exp):

    conec = conectar_bd()
    cursor = conec.cursor()

    sql = """DELETE FROM experiencias
             WHERE id = %s
             AND hoja_vida_id = %s"""

    cursor.execute(sql, (id_exp, id_hv))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia eliminada",
        "id": id_exp,
        "hoja_vida_id": id_hv
    }, 200
    
    @app.route("/api/HABILIDADES/<int:id_exp>", methods=["POST"])
def registrar_habilidad(id_exp):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    nombre = datos.get("nombre")

    sql = """INSERT INTO habilidades
             (experiencia_id, nombre)
             VALUES (%s, %s)"""

    cursor.execute(
        sql,
        (
            id_exp,
            nombre
        )
    )

    conec.commit()

    id_habilidades = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad registrada en la experiencia laboral",
        "id": id_habilidades,
        "experiencia_id": id_exp
    }


@app.route("/api/HABILIDADES/<int:id_exp>", methods=["GET"])
def consultar_habilidades(id_exp):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, experiencia_id, nombre
             FROM habilidades
             WHERE experiencia_id = %s"""

    cursor.execute(sql, (id_exp,))

    habilidades = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "habilidades": habilidades
    }


@app.route("/api/HABILIDADES/<int:id_habi>", methods=["PUT"])
def actualizar_habilidad(id_habi):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    nombre = datos.get("nombre")

    sql = """UPDATE habilidades
             SET nombre = %s
             WHERE id = %s"""

    cursor.execute(
        sql,
        (
            nombre,
            id_habi
        )
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad actualizada",
        "id": id_habi
    }, 200


@app.route("/api/HABILIDADES/<int:id_habi>", methods=["DELETE"])
def eliminar_habilidad(id_habi):

    conec = conectar_bd()
    cursor = conec.cursor()

    sql = """DELETE FROM habilidades
             WHERE id = %s"""

    cursor.execute(sql, (id_habi,))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad Eliminada",
        "id": id_habi
    }, 200


@app.route("/api/CURSOS/<int:id_hv>", methods=["POST"])
def registrar_cursos(id_hv):

    conec = conectar_bd()
    cursor = conec.cursor()

    datos = request.json

    nombre = datos.get("nombre")

    sql = """INSERT INTO cursos
             (hoja_vida_id, nombre)
             VALUES (%s, %s)"""

    cursor.execute(
        sql,
        (
            id_hv,
            nombre
        )
    )

    conec.commit()

    id_curso = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Curso registrado en la hoja de vida",
        "id": id_curso,
        "hoja_vida_id": id_hv
    }


@app.route("/api/HOJAS_VIDA/<int:id>/CURSOS", methods=["GET"])
def consultar_cursoshv(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, hoja_vida_id, nombre
             FROM cursos
             WHERE hoja_vida_id = %s"""

    cursor.execute(sql, (id,))

    cursos = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida_id": id,
        "CURSOS": cursos
    }



