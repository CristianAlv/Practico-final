from datetime import datetime, date

from flask import Flask, request, render_template, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib


app = Flask(__name__, template_folder="Templado")
app.config.from_pyfile('config.py')

from models import db
from models import Asistencia, Preceptor, Padre, Curso, Estudiante

@app.route('/inicio' , methods = ['GET','POST'])
def inicio():
    return render_template('inicio.html')

@app.route('/index' , methods = ['GET','POST'])
def index():
    return render_template('index.html')
@app.route('/index2', methods = ['GET','POST'])
def index2():
    return render_template('index2.html')

@app.route('/', methods = ['GET','POST'])
def iniciarsesion():
    if request.method == 'POST':
        if not request.form['correo'] or not request.form['clave'] or not request.form['rol']:
            return render_template('error.html',error="Los datos ingresados no son correctos.")
        else:
            rol=request.form['rol']
            if rol == 'Padre':
                actual = Padre.query.filter_by( correo= request.form['correo']).first()
                if actual is None:
                    return render_template('error.html', error='El correo ingresado no existe')
                else:
                    c = request.form['clave']
                    result = hashlib.md5(c.encode()).hexdigest()
                    flask_session['userid'] = actual.id
                    if (actual.clave == result):
                        return render_template('index2.html',padre = actual)
                    else:
                        return render_template('error.html', error="La contraseña no es valida")
                    
            elif rol == 'Preceptor':
                actual = Preceptor.query.filter_by(correo=request.form['correo']).first()
                if actual is None:
                    return render_template('error.html', error='El correo ingresado no existe')
                else:
                    c = request.form['clave']
                    result = hashlib.md5(c.encode()).hexdigest()
                    flask_session['userid'] = actual.id
                    if (actual.clave == result):
                        return render_template('index.html',preceptor = actual)
                    else:
                        return render_template('error.html', error="La contraseña no es valida")
            else:
                return render_template('error.html', error = "El rol seleccionado es erroneo")
    else:
        return render_template('iniciarsesion.html')
    
##FUNCIONALIDAD 2

@app.route('/registrarAsistencia', methods = ['GET', 'POST'])
def registrarAsistencia():
        if request.method == 'POST':
            if not flask_session['curso']:
                curso = request.form['curso']
                flask_session['curso'] = curso
                
                selcurso = Curso.query.filter_by(id=curso).first()
                estudiantes = Estudiante.query.filter_by(idcurso = selcurso.id).order_by(Estudiante.apellido, Estudiante.nombre).all()
                return render_template('cargarestudiantes.html', estudiantes = estudiantes, fecha = date.today())
            else:
                selfecha = request.form['fecha']
                selclase = int(request.form['clase'])
                selcurso = Curso.query.filter_by(id=flask_session['curso']).first()
                estudiantes = Estudiante.query.filter_by(idcurso = selcurso.id).order_by(Estudiante.apellido, Estudiante.nombre).all()
                

                for estudiante in estudiantes:
                    asistencia = Asistencia.query.filter_by(fecha =selfecha, idestudiante = estudiante.id)
                    if asistencia == None:
                        asis = request.form.get(f'asistio-{estudiante.id}')
                        justif = request.form.get(f'justificacion-{estudiante.id}','')
                        asistencia = Asistencia(fecha=datetime.strptime(selfecha, "%Y-%m-%d").date(), codigoclase=selclase,asistio=asis,justificacion=justif,idestudiante=estudiante.id)
                        db.session.add(asistencia)
                        db.session.commit()
                        return render_template('error.html', error = "Asistencia guardada con exito")
                    else:
                        return render_template('error.html', error = "Asistencia existente en la fecha")
        else:
            flask_session['curso'] = None
            preceptoringresado = Preceptor.query.filter_by(id=flask_session['userid']).first()
            cursos=Curso.query.filter_by(idpreceptor=preceptoringresado.id).all()
            return render_template('registrarAsistencia.html', preceptor=preceptoringresado, cursos=cursos)

##Funcionalidad 3
@app.route('/obtener_informe', methods=['GET', 'POST'])
def obtener_informe():
    informe = []
    if 'userid' in flask_session:
        id = flask_session['userid']
        actual = Preceptor.query.get(id)
        if request.method == 'POST':
            if not request.form['curso']:
                return render_template('obtenerinforme.html', cursos=Curso.query.all(), curso_selecc=None, preceptor=actual)
            else:
                curso_id = request.form['curso']
                curso_selecc = Curso.query.get(curso_id)
                estudiantes = Estudiante.query.filter_by(idcurso=curso_selecc.id).all()
                estudiantes.sort()
                for estudiante in estudiantes:
                    cont = 0
                    asistencias = Asistencia.query.filter_by(idestudiante=estudiante.id).all()
                    
                    clases_aula_presentes = sum(1 for asistencia in asistencias if asistencia.asistio=='s' and asistencia.codigoclase == 1)
                    clases_edu_fis_presentes = sum(1 for asistencia in asistencias if asistencia.asistio=='s' and asistencia.codigoclase == 2)
                    clases_aula_aus_justificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 1)    
                    clases_aula_aus_injustificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 1) 
                    clases_edu_aus_justificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 2)    
                    clases_edu_aus_injustificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 2)  
                    for asistencia in asistencias:
                        if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 1:
                            cont+=1
                        if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 1:
                            cont+=1
                        if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 2:
                            cont+=0.5
                        if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 2:
                            cont+=0.5
                        
                    estudiante_info = {
                    'apellido': estudiante.apellido,
                    'nombre': estudiante.nombre,
                    'clases_aula_presentes': clases_aula_presentes,
                    'clases_edu_fis_presentes': clases_edu_fis_presentes,
                    'clases_aula_aus_justificadas': clases_aula_aus_justificadas,
                    'clases_aula_aus_injustificadas':clases_aula_aus_injustificadas,
                    'clases_edu_aus_justificadas':clases_edu_aus_justificadas,
                    'clases_edu_aus_injustificadas':clases_edu_aus_injustificadas,
                    'total_de_inasistencias':cont
                    }

                    informe.append(estudiante_info)

                return render_template('obtenerinforme.html', cursos=None, curso_selecc=curso_selecc, preceptor=actual,informe=informe)
        else:
            return render_template('obtenerinforme.html', cursos=Curso.query.all(), curso_selecc=None, preceptor=actual)
    else:
        return render_template('error.html', error='Debe iniciar sesión como preceptor para acceder a esta página.')    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)