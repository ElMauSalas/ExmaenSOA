from spyne import Application, rpc, ServiceBase, Unicode, Iterable, Array, Integer
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import mysql.connector
from wsgiref.simple_server import make_server

# CONFIGURACIÓN BASE DE DATOS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ']C|6pE6}u30Y6d>1d$8VIv5R£r#<P9',  
    'database': 'db_universidad' 
}

# --- MIDDLEWARE CORS (Para que el HTML pueda conectarse) ---
class CorsMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'))
            headers.append(('Access-Control-Allow-Headers', 'Content-Type, SOAPAction'))
            return start_response(status, headers, exc_info)
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            custom_start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'']
        return self.app(environ, custom_start_response)

# --- SERVICIO SOAP ---
class AlumnoService(ServiceBase):
    
    # 1. REGISTRAR
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def registrar_alumno(ctx, matricula, nombre, carrera):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO alumnos (matricula, nombre, carrera) VALUES (%s, %s, %s)"
            cursor.execute(sql, (matricula, nombre, carrera))
            conn.commit()
            return f"Registrado: {nombre}"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # 2. BUSCAR TODOS
    @rpc(_returns=Iterable(Unicode))
    def buscar_todos(ctx):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        resultados = []
        try:
            cursor.execute("SELECT matricula, nombre, carrera FROM alumnos")
            rows = cursor.fetchall()
            for row in rows:
                resultados.append(f"{row[0]} - {row[1]} ({row[2]})")
            return resultados
        except Exception as e:
            return [f"Error: {str(e)}"]
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # 3. BUSCAR UNO
    @rpc(Unicode, _returns=Unicode)
    def buscar_uno(ctx, matricula):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT matricula, nombre, carrera FROM alumnos WHERE matricula = %s", (matricula,))
            row = cursor.fetchone()
            if row:
                return f"Encontrado: {row[0]} - {row[1]} ({row[2]})"
            else:
                return "No encontrado"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # 4. ACTUALIZAR
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def actualizar_alumno(ctx, matricula, nuevo_nombre, nueva_carrera):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            sql = "UPDATE alumnos SET nombre = %s, carrera = %s WHERE matricula = %s"
            cursor.execute(sql, (nuevo_nombre, nueva_carrera, matricula))
            conn.commit()
            if cursor.rowcount > 0:
                return f"Alumno {matricula} actualizado."
            return "No se encontró para actualizar."
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # 5. ELIMINAR UNO
    @rpc(Unicode, _returns=Unicode)
    def eliminar_uno(ctx, matricula):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM alumnos WHERE matricula = %s"
            cursor.execute(sql, (matricula,))
            conn.commit()
            if cursor.rowcount > 0:
                return f"Alumno {matricula} eliminado."
            return "No encontrado."
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # 6. ELIMINAR TODOS
    @rpc(_returns=Unicode)
    def eliminar_todos(ctx):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM alumnos")
            conn.commit()
            return f"Se han eliminado {cursor.rowcount} registros."
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

# Configuración App
application = Application([AlumnoService], 'uav.soap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
wsgi_app = WsgiApplication(application)
wsgi_app_cors = CorsMiddleware(wsgi_app)

if __name__ == '__main__':
    print("SOAP Python corriendo en http://localhost:8000")
    server = make_server('0.0.0.0', 8000, wsgi_app_cors)
    server.serve_forever()