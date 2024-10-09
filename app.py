from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify, make_response

import pusher
import mysql.connector

# Conexión a la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

# Función para verificar la conexión
def check_connection():
    if not con.is_connected():
        con.reconnect()

# Página principal
@app.route("/")
def index():
    con.close()
    return render_template("app.html")

# Función para notificar actualizaciones
def notificarActualizacionTemperaturaHumedad():
    pusher_client = pusher.Pusher(
        app_id='1766037',
        key='fc838f52101ac3c0e022',
        secret='f9f1bc16656c8d474a72',
        cluster='us2',
        ssl=True
    )

    args = {}  # Puedes definir los datos que deseas enviar
    pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", args)

# Ruta para buscar registros
@app.route("/buscar")
def buscar():
    check_connection()

    cursor = con.cursor(dictionary=True)
    cursor.execute("""
    SELECT Id_Experiencia, Nombre_Apellido, Comentario, Calificacion FROM tst0_experiencias
    ORDER BY Id_Experiencia DESC
    LIMIT 10 OFFSET 0
    """)
    registros = cursor.fetchall()

    con.close()
    return make_response(jsonify(registros))

# Ruta para guardar registros (insertar o actualizar)
@app.route("/guardar", methods=["POST"])
def guardar():
    check_connection()

    id = request.form["id"]
    Nombre_Apellido = request.form["Nombre_Apellido"]
    Comentario = request.form["Comentario"]
    Calificacion = request.form["Calificacion"]
    cursor = con.cursor()

    if id:  # Si se proporciona el ID, es una actualización
        sql = """
        UPDATE tst0_experiencias SET
        Nombre_Apellido = %s,
        Comentario     = %s,
        Calificacion   = %s
        WHERE Id_Experiencia = %s
        """
        val = (Nombre_Apellido, Comentario, Calificacion, id)
    else:  # Si no hay ID, es una inserción
        sql = """
        INSERT INTO tst0_experiencias (Nombre_Apellido, Comentario, Calificacion)
        VALUES (%s, %s, %s)
        """
        val = (Nombre_Apellido, Comentario, Calificacion)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))

# Ruta para editar un registro (obtener datos de un registro específico)
@app.route("/editar", methods=["GET"])
def editar():
    check_connection()

    id = request.args["id"]
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT Id_Experiencia, Nombre_Apellido, Comentario, Calificacion FROM tst0_experiencias
    WHERE Id_Experiencia = %s
    """
    val = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()

    con.close()
    return make_response(jsonify(registros))

# Ruta para eliminar un registro
@app.route("/eliminar", methods=["POST"])
def eliminar():
    check_connection()

    id = request.form["id"]
    cursor = con.cursor(dictionary=True)
    sql = """
    DELETE FROM tst0_experiencias
    WHERE Id_Experiencia = %s
    """
    val = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))
