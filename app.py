from flask import Flask, request
from flask_cors import CORS
from database import conectar_bd


app = Flask(__name__)


# CORS

CORS(app, origins=[
    "http://localhost:5174",
    "http://127.0.0.1:5174"
])



# PRUEBA DE CONEXIÓN


@app.route("/probar", methods=["GET"])
def probar_data():

    conec = None

    try:
        conec = conectar_bd()

        if conec and conec.is_connected():
            return {"mensaje": "Conexion ok"}, 200

        return {
            "mensaje": "No se pudo conectar a la base de datos"
        }, 500

    except Exception as error:

        print("ERROR EN /probar:", error)

        return {
            "mensaje": "Error al conectar con la base de datos",
            "error": str(error)
        }, 500

    finally:

        if conec:
            try:
                conec.close()
            except:
                pass



# REGISTRAR HOJA DE VIDA


@app.route("/api/registrohv", methods=["POST"])
def registrohvida():

    conec = None
    cursor = None

    try:

        datos = request.get_json(silent=True)

        print("Datos recibidos:", datos)

        if not datos:
            return {
                "mensaje": "Debe enviar datos en formato JSON"
            }, 400

        campos = [
            "nombre",
            "edad",
            "ciudad",
            "correo",
            "programa",
            "ficha",
            "jornada"
        ]

        for campo in campos:

            if campo not in datos:
                return {
                    "mensaje": f"Falta el campo: {campo}"
                }, 400

        conec = conectar_bd()

        if conec is None or not conec.is_connected():
            return {
                "mensaje": "No se pudo conectar a la base de datos"
            }, 500

        cursor = conec.cursor()

        # Verificar correo

        cursor.execute(
            """
            SELECT id
            FROM hojas_vida
            WHERE correo = %s
            """,
            (datos["correo"],)
        )

        resultado = cursor.fetchone()

        if resultado:

            return {
                "mensaje": "El correo ya está registrado"
            }, 409

        # Insertar hoja de vida

        sql = """
            INSERT INTO hojas_vida
            (
                nombre,
                edad,
                ciudad,
                correo,
                fotografia,
                programa,
                ficha,
                jornada
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            datos["nombre"],
            datos["edad"],
            datos["ciudad"],
            datos["correo"],
            datos.get("fotografia"),
            datos["programa"],
            datos["ficha"],
            datos["jornada"]
        )

        cursor.execute(sql, valores)

        conec.commit()

        id_generado = cursor.lastrowid

        print("Hoja de vida creada. ID:", id_generado)

        return {
            "mensaje": "Hoja de vida creada",
            "id": id_generado
        }, 201

    except Exception as error:

        print("ERROR REGISTRANDO HOJA DE VIDA:", error)

        if conec:
            try:
                conec.rollback()
            except:
                pass

        return {
            "mensaje": "Error interno del servidor",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            try:
                cursor.close()
            except:
                pass

        if conec:
            try:
                conec.close()
            except:
                pass


# ============================================================
# OBTENER TODAS LAS HOJAS DE VIDA
# ============================================================

@app.route("/api/hojasdevida", methods=["GET"])
def obtener_hojasvida():

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM hojas_vida"
    )

    hojasdevida = cursor.fetchall()

    cursor.close()
    conec.close()

    return hojasdevida, 200


# ============================================================
# OBTENER HOJA DE VIDA POR ID
# ============================================================

@app.route("/api/hojasdevida/<int:id>", methods=["GET"])
def obtener_hojasvidaid(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM hojas_vida
        WHERE id = %s
        """,
        (id,)
    )

    hoja = cursor.fetchone()

    cursor.close()
    conec.close()

    if hoja is None:
        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    return hoja, 200


# ============================================================
# ACTUALIZAR HOJA DE VIDA
# ============================================================

@app.route("/api/actualizarhv/<int:id>", methods=["PUT"])
def actualizar_hv(id):

    datos = request.get_json()

    if not datos:
        return {
            "mensaje": "Debe enviar datos en formato JSON"
        }, 400

    campos = [
        "nombre",
        "edad",
        "ciudad",
        "correo",
        "programa",
        "ficha",
        "jornada"
    ]

    for campo in campos:

        if campo not in datos:
            return {
                "mensaje": f"Falta el campo: {campo}"
            }, 400

    conec = conectar_bd()
    cursor = conec.cursor(buffered=True)

    cursor.execute(
        """
        SELECT id
        FROM hojas_vida
        WHERE id = %s
        """,
        (id,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "No se encontro la hoja de vida"
        }, 404

    cursor.execute(
        """
        SELECT id
        FROM hojas_vida
        WHERE correo = %s
        AND id != %s
        """,
        (datos["correo"], id)
    )

    if cursor.fetchone() is not None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "El correo ya está registrado con otra hoja de vida"
        }, 409

    sql = """
        UPDATE hojas_vida
        SET
            nombre = %s,
            edad = %s,
            ciudad = %s,
            correo = %s,
            fotografia = %s,
            programa = %s,
            ficha = %s,
            jornada = %s
        WHERE id = %s
    """

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

    cursor.execute(sql, valores)

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Hoja de vida actualizada",
        "id": id
    }, 200


# ============================================================
# ELIMINAR HOJA DE VIDA
# ============================================================

@app.route("/api/eliminarhv/<int:id>", methods=["DELETE"])
def eliminar_hv(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        """
        SELECT id
        FROM hojas_vida
        WHERE id = %s
        """,
        (id,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "No se encontro la hoja de vida"
        }, 404

    cursor.execute(
        """
        DELETE FROM hojas_vida
        WHERE id = %s
        """,
        (id,)
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Hoja de vida eliminada",
        "id": id
    }, 200


# ============================================================
# ESTUDIOS
# ============================================================

@app.route("/api/HOJAS_VIDA/<int:id>/estudios", methods=["GET"])
def consultar_estudios(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    cursor.execute(
        """
        SELECT
            id,
            hoja_vida_id,
            nivel,
            institucion,
            titulo,
            anio_graduacion
        FROM estudios
        WHERE hoja_vida_id = %s
        """,
        (id,)
    )

    estudios = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida_id": id,
        "estudios": estudios
    }, 200


@app.route("/api/HOJAS_VIDA/<int:id>/estudios", methods=["POST"])
def registrar_estudio(id):

    datos = request.get_json()

    if not datos:
        return {
            "mensaje": "Debe enviar datos en formato JSON"
        }, 400

    campos = [
        "nivel",
        "institucion",
        "titulo",
        "anio_graduacion"
    ]

    for campo in campos:

        if campo not in datos:
            return {
                "mensaje": f"Falta el campo: {campo}"
            }, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    sql = """
        INSERT INTO estudios
        (
            nivel,
            institucion,
            titulo,
            anio_graduacion,
            hoja_vida_id
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            datos["nivel"],
            datos["institucion"],
            datos["titulo"],
            datos["anio_graduacion"],
            id
        )
    )

    id_estudio = cursor.lastrowid

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio registrado para la hoja de vida",
        "id": id_estudio,
        "hoja_vida_id": id
    }, 201


# ============================================================
# EXPERIENCIAS
# ============================================================

@app.route("/api/HOJAS_VIDA/<int:id>/EXPERIENCIAS", methods=["POST"])
def registrar_experiencia(id):

    datos = request.get_json()

    if not datos:
        return {
            "mensaje": "Debe enviar datos en formato JSON"
        }, 400

    campos = [
        "empresa",
        "cargo",
        "tiempo",
        "funciones"
    ]

    for campo in campos:

        if campo not in datos:
            return {
                "mensaje": f"Falta el campo: {campo}"
            }, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    sql = """
        INSERT INTO experiencias
        (
            empresa,
            cargo,
            tiempo,
            funciones,
            hoja_vida_id
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            datos["empresa"],
            datos["cargo"],
            datos["tiempo"],
            datos["funciones"],
            id
        )
    )

    id_experiencia = cursor.lastrowid

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia registrada para la hoja de vida",
        "id": id_experiencia,
        "hoja_vida_id": id
    }, 201


# ============================================================
# HABILIDADES
# ============================================================

@app.route("/api/HABILIDADES/<int:id_exp>", methods=["POST"])
def registrar_habilidad(id_exp):

    datos = request.get_json()

    if not datos:
        return {
            "mensaje": "Debe enviar datos en formato JSON"
        }, 400

    if "nombre" not in datos:
        return {
            "mensaje": "Falta el campo: nombre"
        }, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM experiencias WHERE id = %s",
        (id_exp,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "Experiencia no encontrada"
        }, 404

    cursor.execute(
        """
        INSERT INTO habilidades
        (
            experiencia_id,
            nombre
        )
        VALUES (%s, %s)
        """,
        (
            id_exp,
            datos["nombre"]
        )
    )

    id_habilidad = cursor.lastrowid

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad registrada en la experiencia laboral",
        "id": id_habilidad,
        "experiencia_id": id_exp
    }, 201


# ============================================================
# CURSOS
# ============================================================

@app.route("/api/CURSOS/<int:id_hv>", methods=["POST"])
def registrar_curso(id_hv):

    datos = request.get_json()

    if not datos:
        return {
            "mensaje": "Debe enviar datos en formato JSON"
        }, 400

    if "nombre" not in datos:
        return {
            "mensaje": "Falta el campo: nombre"
        }, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id_hv,)
    )

    if cursor.fetchone() is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    cursor.execute(
        """
        INSERT INTO cursos
        (
            hoja_vida_id,
            nombre
        )
        VALUES (%s, %s)
        """,
        (
            id_hv,
            datos["nombre"]
        )
    )

    id_curso = cursor.lastrowid

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Curso registrado en la hoja de vida",
        "id": id_curso,
        "hoja_vida_id": id_hv
    }, 201


# ============================================================
# HOJA DE VIDA COMPLETA
# ============================================================

@app.route("/api/HOJAS_VIDA/<int:id>/completa", methods=["GET"])
def consultar_hoja_vida_completa(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    # Datos personales

    cursor.execute(
        "SELECT * FROM hojas_vida WHERE id = %s",
        (id,)
    )

    hoja_vida = cursor.fetchone()

    if hoja_vida is None:

        cursor.close()
        conec.close()

        return {
            "mensaje": "Hoja de vida no encontrada"
        }, 404

    # Estudios

    cursor.execute(
        """
        SELECT *
        FROM estudios
        WHERE hoja_vida_id = %s
        """,
        (id,)
    )

    estudios = cursor.fetchall()

    # Cursos

    cursor.execute(
        """
        SELECT *
        FROM cursos
        WHERE hoja_vida_id = %s
        """,
        (id,)
    )

    cursos = cursor.fetchall()

    # Experiencias

    cursor.execute(
        """
        SELECT *
        FROM experiencias
        WHERE hoja_vida_id = %s
        """,
        (id,)
    )

    experiencias = cursor.fetchall()

    # Habilidades

    for experiencia in experiencias:

        cursor.execute(
            """
            SELECT id, experiencia_id, nombre
            FROM habilidades
            WHERE experiencia_id = %s
            """,
            (experiencia["id"],)
        )

        experiencia["habilidades"] = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida": hoja_vida,
        "estudios": estudios,
        "cursos": cursos,
        "experiencias": experiencias
    }, 200


# ============================================================
# INICIO
# ============================================================

@app.route("/", methods=["GET"])
def inicio():

    return "Api hoja de vida funcionando"


# ============================================================
# EJECUTAR FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
