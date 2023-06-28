from datetime import datetime
from flask import Flask, request, render_template, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib


app = Flask(__name__, template_folder="Templado")
app.config.from_pyfile('config.py')

from models import db
from models import Asistencia, Preceptor, Padre, Curso, Estudiante



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
                        return render_template('index2.html')
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
                        return render_template('index.html')
                    else:
                        return render_template('error.html', error="La contraseña no es valida")
            else:
                return render_template('error.html', error = "El rol seleccionado es erroneo")
    else:
        return render_template('iniciarsesion.html')
    
##FUNCIONALIDAD 2

@app.route('/registrar_asistencia', methods = ['GET', 'POST'])
def registrar_asistencia():
        if request.method == 'POST':
            if not flask_session['curso']:
                curso = request.form['curso']
                flask_session['curso'] = curso
                selcurso = Curso.query.filter_by(id=curso).first()
                estudiantes = Estudiante.query.filter_by(idcurso = selcurso.id).order_by(Estudiante.apellido, Estudiante.nombre).all()
                return render_template('cargarestudiantes.html', estudiantes = estudiantes)
            else:
                selfecha = request.form['fecha']
                selclase = int(request.form['clase'])
                selcurso = Curso.query.filter_by(id=flask_session['curso']).first()
                estudiantes = Estudiante.query.filter_by(idcurso = selcurso.id).order_by(Estudiante.apellido, Estudiante.nombre).all()

                for estudiante in estudiantes:
                    asis = request.form.get(f'asistio-{estudiante.id}')
                    justif = request.form.get(f'justificacion-{estudiante.id}','')
                    asistencia = Asistencia(fecha=datetime.strptime(selfecha, "%Y-%m-%d").date(), codigoclase=selclase,asistio=asis,justificacion=justif,idestudiante=estudiante.id)
                    db.session.add(asistencia)
                db.session.commit()
                return render_template('confirmarregistro.html')
        else:
            flask_session['curso'] = None
            preceptoringresado = Preceptor.query.filter_by(id=flask_session['userid']).first()
            cursos=Curso.query.filter_by(idpreceptor=preceptoringresado.id).all()
            return render_template('registrarAsistencia.html', preceptor=preceptoringresado, cursos=cursos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)