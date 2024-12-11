from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
import datetime
import pytz

app = Flask(__name__)

class ControladorExperiencias:
    def __init__(self):
        self.con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
        )

    def check_connection(self):
        if not self.con.is_connected():
            self.con.reconnect()

    def notificarActualizacion(self):
        pusher_client = pusher.Pusher(
            app_id="1766037",
            key="fc838f52101ac3c0e022",
            secret="f9f1bc16656c8d474a72",
            cluster="us2",
            ssl=True
        )

        pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", {})

    def buscar(self):
        self.check_connection()

        cursor = self.con.cursor(dictionary=True)
        cursor.execute("""
        SELECT Id_Experiencia, Nombre_Apellido, Comentario, Calificacion FROM tst0_experiencias
        ORDER BY Id_Experiencia DESC
        LIMIT 10 OFFSET 0
        """)
        registros = cursor.fetchall()

        self.con.close()
        return make_response(jsonify(registros))

    def guardar(self, id, nombre_apellido, comentario, calificacion):
        self.check_connection()

        cursor = self.con.cursor()

        if id:
            sql = """
            UPDATE tst0_experiencias SET
            Nombre_Apellido = %s,
            Comentario = %s,
            Calificacion = %s
            WHERE Id_Experiencia = %s
            """
            val = (nombre_apellido, comentario, calificacion, id)
        else:
            sql = """
            INSERT INTO tst0_experiencias (Nombre_Apellido, Comentario, Calificacion)
            VALUES (%s, %s, %s)
            """
            val = (nombre_apellido, comentario, calificacion)

        cursor.execute(sql, val)
        self.con.commit()
        self.con.close()

        self.notificarActualizacion()

        return make_response(jsonify({}))

    def editar(self, id):
        self.check_connection()

        cursor = self.con.cursor(dictionary=True)
        sql = """
        SELECT Id_Experiencia, Nombre_Apellido, Comentario, Calificacion FROM tst0_experiencias
        WHERE Id_Experiencia = %s
        """
        val = (id,)

        cursor.execute(sql, val)
        registros = cursor.fetchall()

        self.con.close()
        return make_response(jsonify(registros))

    def eliminar(self, id):
        self.check_connection()

        cursor = self.con.cursor()
        sql = """
        DELETE FROM tst0_experiencias
        WHERE Id_Experiencia = %s
        """
        val = (id,)

        cursor.execute(sql, val)
        self.con.commit()
        self.con.close()

        self.notificarActualizacion()

        return make_response(jsonify({}))

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/buscar")
def buscar():
    controlador = ControladorExperiencias()
    return controlador.buscar()

@app.route("/guardar", methods=["POST"])
def guardar():
    id = request.form.get("id")
    nombre_apellido = request.form.get("Nombre_Apellido")
    comentario = request.form.get("Comentario")
    calificacion = request.form.get("Calificacion")

    controlador = ControladorExperiencias()
    return controlador.guardar(id, nombre_apellido, comentario, calificacion)

@app.route("/editar", methods=["GET"])
def editar():
    id = request.args.get("id")

    controlador = ControladorExperiencias()
    return controlador.editar(id)

@app.route("/eliminar", methods=["POST"])
def eliminar():
    id = request.form.get("id")

    controlador = ControladorExperiencias()
    return controlador.eliminar(id)

if __name__ == "__main__":
    app.run(debug=True)
