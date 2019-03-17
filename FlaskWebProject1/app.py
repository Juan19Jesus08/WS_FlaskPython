from flask import Flask, request, jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import pyodbc
import hashlib
import time
import json

app = Flask(__name__)

@app.route('/getCarrera',methods=['GET'])
def getCarrera():
   
        try:
            print("hola");
            conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=Escuela;'
            'Trusted_Connection=yes;'      
            )
            cur = conn.cursor()
            print("hola2");
            cur.execute("select id_carrera,carrera from Carrera ")
            rows = cur.fetchall()
            array = []
            print("hola3");
            #print(rows[1][1]);
            cont= 0;

            for row in rows:
                data={}
                data['id_carrera'] = str(row[0])
                print(str(row[0]));
                data['carrera'] = str(row[1])
                cont=cont+1;
                print(cont);

                    
                array.append(data)
                print("hola4");
                return jsonify({'carrera':array})
            else:
                return jsonify({'mensaje':'Error de token'})
        except (Exception, pyodbc.DatabaseError) as error:
            print(error)
                                                #METODOS GET
#----------------------------WS PARA LOGIN
@app.route('/sii/login/<nocont>/<pwduser>',methods=['GET'])
def validaUsuario(nocont,pwduser):
   
        conn = None
        try:
            conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
            cur = conn.cursor()
            #pwduser = hashlib.md5(pwduser.encode())
            cur.execute("select * from usuarios where nocont='"+nocont+"' and pwduser = '"+pwduser+"'")
            result = cur.fetchone()
            if len(str(result)) > 0:
                #Insertar Acceso
                token = nocont+pwduser
                #return jsonify({'mensaje':token})
               # token = token.hexdigest()
                cur.execute("insert into accesos(token,fecha_inicio,fecha_fin) values('"+token+"',GETDATE(), DATEADD(minute, 60, GetDate()))")
                conn.commit()
                return jsonify({'nocont':nocont,'token':token,})
            else:
                return jsonify({'mensaje':'Error de nocont o contraseña'})
                cur.close()
        except (Exception, pyodbc.DatabaseError) as error:
            print(error)
#------------------------WS PARA KARDEX
@app.route('/sii/kardex/<nocont>/<token>',methods=['GET'])
def kardex(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select cvemat,opor,calificacion from kardex where nocont = '"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['cvemat'] = str(row[0])
                data['opor'] = str(row[1])
                data['calificacion'] = str(row[2])
                #Oportunidad
                cur.execute("select descripcion from oportunidad where opor = "+data['opor'])
                oportunidad = cur.fetchall()
                for r in oportunidad:
                    data['oportunidad'] = {'descripcion':str(r[0])}
                #Materia
                cur.execute("select nombre,creditos from materias where cvemat = '"+data['cvemat']+"'")
                materia = cur.fetchall()
                for r in materia:
                    data['materia'] = {'nombre':str(r[0]),'creditos':str(r[1])}
                array.append(data)
            return jsonify({'kardex':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#----------------------------WS PARA ALUMNO
@app.route('/sii/alumno/<nocont>/<token>',methods=['GET'])
def alumno(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select nombre,cveesp,sexo,email,telefono,direccion from alumnos where nocont = '"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['nombre'] = str(row[0])
                data['cveesp'] = str(row[1])
                data['sexo'] = str(row[2])
                data['email'] = str(row[3])
                data['telefono'] = str(row[4])
                data['direccion'] = str(row[5])
                cur.execute("select nombre from especialidades where cveesp = '"+data['cveesp']+"'")
                especialidad = cur.fetchall()
                for r in especialidad:
                    data['especialidad'] = {'nombre':str(r[0])}
                array.append(data)
            return jsonify({'alumno':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)
#-------------------------WS PARA CARGA
@app.route('/sii/carga/<nocont>/<token>', methods=['GET'])
def carga(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #Verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select cvemat,nogpo from listas where nocont = '"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['cvemat'] = str(row[0])
                data['nogpo'] = str(row[1])
               
                cur.execute("select cvemae,horario,salon from grupos where cvemat = '"+data['cvemat']+"'")
                grupo = cur.fetchall()
                for r in grupo:
                    data['grupo'] = {'cvemae':str(r[0]),'horario':str(r[1]),'salon':str(r[2])}
                #Maestro
                cur.execute("select nombre from materias where cvemat = '"+data['cvemat']+"'")
                materia = cur.fetchall()
                for r in materia:
                    data['materia'] = {'nombre':str(r[0])}
                array.append(data)
            return jsonify({'carga':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#-------------------------WS PARA ORDEN DE ENTRADA
@app.route('/sii/orden/<nocont>/<token>',methods=['GET'])
def orden(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select fecha_ins,idorden from orden_entrada where nocont = '"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['fecha_ins'] = str(row[0])
                data['idorden'] = str(row[1])
              
               
                array.append(data)
            return jsonify({'orden':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#----------------WS PARA ACTIVIDADES EXTRAESCOLARES
@app.route('/sii/actividadext/<nocont>/<token>',methods=['GET'])
def actividadext(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select actividad,rama,grupo,lugar,responsable from actividades_extra")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['actividad'] = str(row[0])
                data['rama'] = str(row[1])
                data['grupo'] = str(row[2])
                data['lugar'] = str(row[3])
                data['responsable'] = str(row[4])
              
               
                array.append(data)
            return jsonify({'actividadext':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#-----------------------WS PARA ACTIVIDADES COMPLEMENTARIAS
@app.route('/sii/complemento/<nocont>/<token>',methods=['GET'])
def complemento(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select actividad_complementaria,creditos,situacion from complementaria where nocont = '"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['actividad_complementaria'] = str(row[0])
                data['creditos'] = str(row[1])
                data['situacion'] = str(row[2])
                array.append(data)
            return jsonify({'complemento':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#---------------------------------WS LISTA DE MATERIAS  ******CHECAR
@app.route('/sii/lista/<nocont>/<token>', methods=['GET'])
def lista(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #Verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select cvemat,nogpo,calificacion1,calificacion2,cal3,calificacion4 from listas where nocont = '"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['cvemat'] = str(row[0])
                data['nogpo'] = str(row[1])
                data['calificacion1'] = str(row[2])
                data['calificacion2'] = str(row[3])
                data['cal3'] = str(row[4])
                data['calificacion4'] = str(row[5])
                cur.execute("select nombre from materias where cvemat = '"+data['cvemat']+"'")
                materia = cur.fetchall()
                for r in materia:
                    data['materia'] = {'nombre':str(r[0])}
                array.append(data)
            return jsonify({'lista':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#-------------------WS CORREO
@app.route('/sii/correo/<nocont>/<token>',methods=['GET'])
def correo(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select distinct maestros.email as correo,maestros.nombre as nombre "+
            	        "from reticula inner join maestros on reticula.cveesp=maestros.cveesp inner join "+ 
						"listas on listas.cvemat=reticula.cvemat where nocont='"+nocont+"'")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['correo'] = str(row[0])
                data['nombre'] = str(row[1])
                array.append(data)
            return jsonify({'correo':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#-----------------WS LIST MAT
@app.route('/sii/listmat/<nocont>/<token>',methods=['GET'])
def listmat(nocont,token):
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        #verificar token
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("select materias.nombre as nombre_mat,materias.cvemat as clave_mat,grupos.nogpo as clave_grupo,grupos.horario as horas "+
            	        "from materias inner join grupos on materias.cvemat=grupos.cvemat ")
            rows = cur.fetchall()
            array = []
            for row in rows:
                data={}
                data['nombre_mat'] = str(row[0])
                data['clave_mat'] = str(row[1])
                data['clave_grupo'] = str(row[2])
                data['horas'] = str(row[3])
                array.append(data)
            return jsonify({'listmat':array})
        else:
            return jsonify({'mensaje':'Error de token'})
    except (Exception, pyodbc.DatabaseError) as error:
        print(error)

#-----------------------------METODO POST

@app.route('/sii/envio/<token>', methods=['POST'])
def envio(token):
    #Validar Token
    data = request.get_json()
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("insert into quejas (queja,descripcion,email)"
                    + " values ('"+data['queja']+"',"
                    + "'"+data['descripcion']+"',"
                    + "'"+data['email']+"')")
            #return jsonify({'mensaje':'valido'})
            conn.commit()
            return jsonify({'mensaje':'envio insertado'})
            return ''
        else:
    	    return jsonify({'mensaje':'token invalido'})
    except (Exception, pyodbc.DatabaseError) as error:
    	print(error)

#------------------------WS INSCRIBIR


@app.route('/sii/inscribir/<token>', methods=['POST'])
def inscribir(token):
    #Validar Token
    data = request.get_json()
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 4:
            cur.execute("insert into listas (cvemat, nogpo, nocont, calificacion1, calificacion2, calificacion4)"
                    + " values ('"+data['cvemat']+"',"
                    + "'"+data['nogpo']+"',"
                    + "'"+data['nocont']+"',"
                    + ""+data['calificacion1']+","
                     + ""+data['calificacion2']+","
                   
                     ""+data['calificacion4']+")")
            #return jsonify({'mensaje':'valido'})
            conn.commit()
            return jsonify({'mensaje':'envio insertado'})
            return ''
        else:
    	    return jsonify({'mensaje':'token invalido'})
    except (Exception, pyodbc.DatabaseError) as error:
    	print(error)

#--------------------METODO PUT

@app.route('/sii/updalumno/<nocont>/<token>', methods=['PUT'])
def updalumno(nocont,token):
    #Validar Token
    data = request.get_json()
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'SERVER=DESKTOP-RPDFJP3\SQLEXPRESS;'
            'DATABASE=itc;'
            'Trusted_Connection=yes;'      
            )
        cur = conn.cursor()
        cur.execute("select * from accesos where token = '"+token+"' and GETDATE() between fecha_inicio and fecha_fin")
        result = cur.fetchone()
        if len(str(result)) > 0:
            #Insertar alumno
            #insert into alumno (nombre,apaterno,amaterno,email,nocontrol,idcarrera) values('alejandra','lopez','aguilar','')
            #return jsonify({'mensaje':'valido'})
            cur.execute("update alumnos set " 
                    + "email = '"+data['email']+"',"
                    + "telefono = '"+data['telefono']+"',"
                    + "direccion = '"+data['direccion']+"' "
                    + "where nocont = '"+nocont+"'")

            
            #return jsonify({'mensaje':'valido'})
            conn.commit()
            return jsonify({'mensaje':'alumno actualizado'})
        else:
    	    return jsonify({'mensaje':'token invalido'})
    except (Exception, pyodbc.DatabaseError) as error:
    	print(error)


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0')