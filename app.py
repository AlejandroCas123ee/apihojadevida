from flask import Flask, request
from database import conectar_bd

app = Flask(__name__)


@app.route("/probar", methods=["GET"])
def probar_data():
    conec = conectar_bd()

    if conec and conec.is_connected():
        conec.close()
        return {"mensaje": "Conexion ok"}, 200

    return {"mensaje": "No se pudo conectar a la base de datos"}, 500

@app.route("/api/registrohv", methods=["POST"])
def registrohvida():
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    campos = ["nombre", "edad", "ciudad", "correo", "programa", "ficha", "jornada"]

    for campo in campos:
        if campo not in datos:
            return {"mensaje": f"Falta el campo: {campo}"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE correo = %s",
        (datos["correo"],)
    )

    resultado = cursor.fetchone()

    if resultado:
        cursor.close()
        conec.close()
        return {"mensaje": "El correo ya está registrado"}, 409

    sql = """
        INSERT INTO hojas_vida
        (nombre, edad, ciudad, correo, fotografia, programa, ficha, jornada)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

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
    }, 201


@app.route("/api/hojasdevida", methods=["GET"])
def obtener_hojasvida():
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hojas_vida")
    hojasdevida = cursor.fetchall()

    cursor.close()
    conec.close()

    return hojasdevida, 200


@app.route("/api/hojasdevida/<int:id>", methods=["GET"])
def obtener_hojasvidaid(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM hojas_vida WHERE id = %s",
        (id,)
    )

    hoja = cursor.fetchone()

    cursor.close()
    conec.close()

    if hoja is None:
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    return hoja, 200


@app.route("/api/actualizarhv/<int:id>", methods=["PUT"])
def actualizar_hv(id):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    campos = ["nombre", "edad", "ciudad", "correo", "programa", "ficha", "jornada"]

    for campo in campos:
        if campo not in datos:
            return {"mensaje": f"Falta el campo: {campo}"}, 400

    conec = conectar_bd()
    cursor = conec.cursor(buffered=True)

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la hoja de vida"}, 404

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE correo = %s AND id != %s",
        (datos["correo"], id)
    )

    if cursor.fetchone() is not None:
        cursor.close()
        conec.close()
        return {"mensaje": "El correo ya está registrado con otra hoja de vida"}, 409

    sql_actualizar = """
        UPDATE hojas_vida
        SET nombre = %s,edad = %s,ciudad = %s,correo = %s,fotografia = %s,programa = %s,ficha = %s,jornada = %s
        WHERE id = %s
    """

    valores = (
        datos["nombre"],datos["edad"],datos["ciudad"],datos["correo"],
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
        "mensaje": "Hoja de vida actualizada",
        "id": id
    }, 200


@app.route("/api/eliminarhv/<int:id>", methods=["DELETE"])
def eliminar_hv(id):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la hoja de vida"}, 404

    cursor.execute(
        "DELETE FROM hojas_vida WHERE id = %s",
        (id,)
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Hoja de vida eliminada",
        "id": id
    }, 200

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
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    sql = """
        SELECT id, hoja_vida_id, nivel, institucion, titulo, anio_graduacion
        FROM estudios
        WHERE hoja_vida_id = %s
    """

    cursor.execute(sql, (id,))
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
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    campos = ["nivel", "institucion", "titulo", "anio_graduacion"]

    for campo in campos:
        if campo not in datos:
            return {"mensaje": f"Falta el campo: {campo}"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    sql = """
        INSERT INTO estudios
        (nivel, institucion, titulo, anio_graduacion, hoja_vida_id)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        datos["nivel"],
        datos["institucion"],
        datos["titulo"],
        datos["anio_graduacion"],
        id
    ))

    id_estudio = cursor.lastrowid
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio registrado para la hoja de vida",
        "id": id_estudio,
        "hoja_vida_id": id
    }, 201


@app.route("/api/estudios/<int:id>", methods=["GET"])
def consultar_estudio(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, hoja_vida_id, nivel, institucion, titulo, anio_graduacion
        FROM estudios
        WHERE id = %s
    """, (id,))

    estudio = cursor.fetchone()

    cursor.close()
    conec.close()

    if estudio is None:
        return {"mensaje": "Estudio no encontrado"}, 404

    return estudio, 200


@app.route("/api/estudios/<int:id>", methods=["PUT"])
def actualizar_estudio(id):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    campos = ["nivel", "institucion", "titulo", "anio_graduacion"]

    for campo in campos:
        if campo not in datos:
            return {"mensaje": f"Falta el campo: {campo}"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM estudios WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Estudio no encontrado"}, 404

    sql = """
        UPDATE estudios
        SET nivel = %s,
            institucion = %s,
            titulo = %s,
            anio_graduacion = %s
        WHERE id = %s
    """

    cursor.execute(sql, (
        datos["nivel"],datos["institucion"],datos["titulo"],datos["anio_graduacion"],
        id
    ))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio actualizado",
        "id": id
    }, 200


@app.route("/api/estudios/<int:id>", methods=["DELETE"])
def eliminar_estudio(id):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM estudios WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Estudio no encontrado"}, 404

    cursor.execute(
        "DELETE FROM estudios WHERE id = %s",
        (id,)
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio eliminado",
        "id": id
    }, 200


@app.route("/api/HOJAS_VIDA/<int:id>/EXPERIENCIAS", methods=["POST"])
def registrar_experiencia(id):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    campos = ["empresa", "cargo", "tiempo", "funciones"]

    for campo in campos:
        if campo not in datos:
            return {"mensaje": f"Falta el campo: {campo}"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    sql = """
        INSERT INTO experiencias
        (empresa, cargo, tiempo, funciones, hoja_vida_id)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (datos["empresa"],datos["cargo"],datos["tiempo"],datos["funciones"],
        id
    ))

    id_experiencia = cursor.lastrowid
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia registrada para la hoja de vida",
        "id": id_experiencia,
        "hoja_vida_id": id
    }, 201


@app.route("/api/HOJAS_VIDA/<int:id>/EXPERIENCIAS", methods=["GET"])
def consultar_experienciashv(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    sql = """
        SELECT id, hoja_vida_id, empresa, cargo, tiempo, funciones
        FROM experiencias
        WHERE hoja_vida_id = %s
    """

    cursor.execute(sql, (id,))
    experiencias = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida_id": id,
        "experiencias": experiencias
    }, 200


@app.route("/api/EXPERIENCIAS/<int:id>", methods=["GET"])
def consultar_experiencia(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM experiencias WHERE id = %s",
        (id,)
    )

    experiencia = cursor.fetchone()

    cursor.close()
    conec.close()

    if experiencia is None:
        return {"mensaje": "Experiencia no encontrada"}, 404

    return experiencia, 200


@app.route("/api/EXPERIENCIAS/<int:id_hv>/<int:id_exp>", methods=["PUT"])
def actualizar_experiencia(id_hv, id_exp):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    campos = ["empresa", "cargo", "tiempo", "funciones"]

    for campo in campos:
        if campo not in datos:
            return {"mensaje": f"Falta el campo: {campo}"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id_hv,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    cursor.execute("""
        SELECT id FROM experiencias
        WHERE id = %s AND hoja_vida_id = %s
    """, (id_exp, id_hv))

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Experiencia no encontrada en esta hoja de vida"}, 404

    sql = """
        UPDATE experiencias
        SET empresa = %s,
            cargo = %s,
            tiempo = %s,
            funciones = %s
        WHERE id = %s
        AND hoja_vida_id = %s
    """

    cursor.execute(sql, (
        datos["empresa"],
        datos["cargo"],
        datos["tiempo"],
        datos["funciones"],
        id_exp,
        id_hv
    ))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia actualizada",
        "id": id_exp,
        "hoja_vida_id": id_hv
    }, 200


@app.route("/api/EXPERIENCIAS/<int:id_hv>/<int:id_exp>", methods=["DELETE"])
def eliminar_experiencia(id_hv, id_exp):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute("""
        SELECT id FROM experiencias
        WHERE id = %s AND hoja_vida_id = %s
    """, (id_exp, id_hv))

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Experiencia no encontrada en esta hoja de vida"}, 404

    cursor.execute("""
        DELETE FROM experiencias
        WHERE id = %s AND hoja_vida_id = %s
    """, (id_exp, id_hv))

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
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    if "nombre" not in datos:
        return {"mensaje": "Falta el campo: nombre"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM experiencias WHERE id = %s",
        (id_exp,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Experiencia no encontrada"}, 404

    sql = """
        INSERT INTO habilidades
        (experiencia_id, nombre)
        VALUES (%s, %s)
    """

    cursor.execute(sql, (
        id_exp,
        datos["nombre"]
    ))

    id_habilidad = cursor.lastrowid
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad registrada en la experiencia laboral",
        "id": id_habilidad,
        "experiencia_id": id_exp
    }, 201


@app.route("/api/HABILIDADES/<int:id_exp>", methods=["GET"])
def consultar_habilidades(id_exp):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM experiencias WHERE id = %s",
        (id_exp,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Experiencia no encontrada"}, 404

    cursor.execute("""
        SELECT id, experiencia_id, nombre
        FROM habilidades
        WHERE experiencia_id = %s
    """, (id_exp,))

    habilidades = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "experiencia_id": id_exp,
        "habilidades": habilidades
    }, 200


@app.route("/api/HABILIDADES/<int:id_habi>", methods=["PUT"])
def actualizar_habilidad(id_habi):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    if "nombre" not in datos:
        return {"mensaje": "Falta el campo: nombre"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM habilidades WHERE id = %s",
        (id_habi,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Habilidad no encontrada"}, 404

    cursor.execute("""
        UPDATE habilidades
        SET nombre = %s
        WHERE id = %s
    """, (
        datos["nombre"],
        id_habi
    ))

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

    cursor.execute(
        "SELECT id FROM habilidades WHERE id = %s",
        (id_habi,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Habilidad no encontrada"}, 404

    cursor.execute(
        "DELETE FROM habilidades WHERE id = %s",
        (id_habi,)
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad eliminada",
        "id": id_habi
    }, 200

@app.route("/api/CURSOS/<int:id_hv>", methods=["POST"])
def registrar_curso(id_hv):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    if "nombre" not in datos:
        return {"mensaje": "Falta el campo: nombre"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id_hv,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    sql = """
        INSERT INTO cursos
        (hoja_vida_id, nombre)
        VALUES (%s, %s)
    """

    cursor.execute(sql, (
        id_hv,
        datos["nombre"]
    ))

    id_curso = cursor.lastrowid
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Curso registrado en la hoja de vida",
        "id": id_curso,
        "hoja_vida_id": id_hv
    }, 201


@app.route("/api/HOJAS_VIDA/<int:id>/CURSOS", methods=["GET"])
def consultar_cursoshv(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM hojas_vida WHERE id = %s",
        (id,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    cursor.execute("""
        SELECT id, hoja_vida_id, nombre
        FROM cursos
        WHERE hoja_vida_id = %s
    """, (id,))

    cursos = cursor.fetchall()

    cursor.close()
    conec.close()

    return {
        "hoja_de_vida_id": id,
        "cursos": cursos
    }, 200


@app.route("/api/CURSOS/<int:id>", methods=["GET"])
def consultar_curso(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM cursos WHERE id = %s",
        (id,)
    )

    curso = cursor.fetchone()

    cursor.close()
    conec.close()

    if curso is None:
        return {"mensaje": "Curso no encontrado"}, 404

    return curso, 200


@app.route("/api/CURSOS/<int:id_CUR>", methods=["PUT"])
def actualizar_curso(id_CUR):
    datos = request.get_json()

    if not datos:
        return {"mensaje": "Debe enviar datos en formato JSON"}, 400

    if "nombre" not in datos:
        return {"mensaje": "Falta el campo: nombre"}, 400

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM cursos WHERE id = %s",
        (id_CUR,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Curso no encontrado"}, 404

    cursor.execute("""
        UPDATE cursos
        SET nombre = %s
        WHERE id = %s
    """, (
        datos["nombre"],
        id_CUR
    ))

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Curso actualizado",
        "id": id_CUR
    }, 200


@app.route("/api/CURSOS/<int:id_CUR>", methods=["DELETE"])
def eliminar_curso(id_CUR):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM cursos WHERE id = %s",
        (id_CUR,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Curso no encontrado"}, 404

    cursor.execute(
        "DELETE FROM cursos WHERE id = %s",
        (id_CUR,)
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Curso eliminado",
        "id": id_CUR
    }, 200

@app.route("/api/HOJAS_VIDA/<int:id>/completa", methods=["GET"])
def consultar_hoja_vida_completa(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    # 1. Datos personales
    cursor.execute(
        "SELECT * FROM hojas_vida WHERE id = %s",
        (id,)
    )

    hoja_vida = cursor.fetchone()

    if hoja_vida is None:
        cursor.close()
        conec.close()
        return {"mensaje": "Hoja de vida no encontrada"}, 404

    # 2. Estudios
    cursor.execute("""
        SELECT *
        FROM estudios
        WHERE hoja_vida_id = %s
    """, (id,))

    estudios = cursor.fetchall()

    # 3. Cursos
    cursor.execute("""
        SELECT *
        FROM cursos
        WHERE hoja_vida_id = %s
    """, (id,))

    cursos = cursor.fetchall()

    # 4. Experiencias
    cursor.execute("""
        SELECT *
        FROM experiencias
        WHERE hoja_vida_id = %s
    """, (id,))

    experiencias = cursor.fetchall()

    # 5. Habilidades de cada experiencia
    for experiencia in experiencias:
        cursor.execute("""
            SELECT id, experiencia_id, nombre
            FROM habilidades
            WHERE experiencia_id = %s
        """, (experiencia["id"],))

        experiencia["habilidades"] = cursor.fetchall()

    cursor.close()
    conec.close()

    respuesta_completa = {
        "hoja_de_vida": hoja_vida,
        "estudios": estudios,
        "cursos": cursos,
        "experiencias": experiencias
    }

    return respuesta_completa, 200

@app.route("/", methods=["GET"])
def inicio():
    return "Api hoja de vida funcionando"


if __name__ == "__main__":
    app.run(debug=True)
