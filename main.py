import email
from flask import Flask, request, Response 
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/cadastro'

db = SQLAlchemy(app)

#classe
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    
    def for_json(self):
        return {'id': self.id, 'nome': self.nome, 'email': self.email}

#Select all
@app.route("/usuarios",methods=['GET'])
def select_all_users():
    all_users = Usuario.query.all()
    to_json = [usuarios.for_json() for usuarios in all_users]
    return make_response(200, "usuarios", to_json)


#Select one
@app.route("/usuario/<id>",methods=["GET"])
def select_one_user(id):
    usuario = Usuario.query.filter_by(id=id).first()
    usuario_json = usuario.for_json()
    return make_response(200, "usuario", usuario_json)

#Cadastro
@app.route("/usuario",methods=["POST"])
def create_user():
    body = request.get_json()

    try:
        usuario = Usuario(nome = body["nome"], email = body["email"])
        db.session.add(usuario)
        db.session.commit()
        return make_response(201, "usuario", usuario.for_json(), "Usuário Criado com Sucesso!")
    except Exception as e:
        return(400, "usuario", {}, "Erro ao cadastrar")

#Deletar Usuário
@app.route("/usuario/<id>",methods=["DELETE"])
def del_users(id):
    user = Usuario.query.filter_by(id=id).first()

    try:
        db.session.delete(user)
        db.session.commit()
        return make_response(200,"usuario",user.for_json(),"Usuário Deletado com Sucesso!")
    except Exception as e:
        return(400,"usuario",{},"Erro ao identificar o usuário")



#Update
@app.route("/usuario/<id>",methods=["PUT"])
def update_user(id):
    get_user = Usuario.query.filter_by(id=id).first()
    body = request.get_json()
    try:
        if 'nome' in body:
            get_user.nome = body['nome']
        if 'email' in body:
            get_user.email = body['email']
                
        db.session.add(get_user)
        db.session.commit()  
        return make_response(200, "usuario", get_user.for_json(), "Usuário atualizado com Sucesso.")

    except Exception as e:
        return(400, "usuario", {}, "Erro ao atualizar")


#gerar resposta
def make_response(status,nome_conteudo,conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo
    if(mensagem):
        body["mensagem"] = mensagem
    return Response(json.dumps(body), status=status,mimetype="aplication/json")


app.run()