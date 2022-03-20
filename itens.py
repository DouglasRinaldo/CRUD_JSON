from flask import Flask, request, Response 
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json
from main import Usuario
from main import Estoque

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/estoque'

db = SQLAlchemy(app)


#Select all
@app.route("/estoques",methods=['GET'])
def select_all_users():
    all_users = Estoque.query.all()
    to_json = [estoques.for_json() for estoques in all_users]
    return make_response(200, "estoques", to_json)


#Select one
@app.route("/estoque/<id>",methods=["GET"])
def select_one_user(id):
    estoque = Estoque.query.filter_by(id=id).first()
    estoque_json = estoque.for_json()
    return make_response(200, "estoque", estoque_json)

#Cadastro
@app.route("/estoque",methods=["POST"])
def create_user():
    body = request.get_json()

    try:
        estoque = Estoque(nome = body["nome"], produto = body["produto"], preco = body["preco"])
        db.session.add(estoque)
        db.session.commit()
        return make_response(201, "estoque", estoque.for_json(), "Usuário Criado com Sucesso!")
    except Exception as e:
        return(400, "estoque", {}, "Erro ao cadastrar")

#Deletar Usuário
@app.route("/estoque/<id>",methods=["DELETE"])
def del_users(id):
    user = Estoque.query.filter_by(id=id).first()

    try:
        db.session.delete(user)
        db.session.commit()
        return make_response(200,"estoque",user.for_json(),"Usuário Deletado com Sucesso!")
    except Exception as e:
        return(400,"estoque",{},"Erro ao identificar o usuário")



#Update
@app.route("/estoque/<id>",methods=["PUT"])
def update_user(id):
    get_user = Estoque.query.filter_by(id=id).first()
    body = request.get_json()
    try:
        if 'nome' in body:
            get_user.nome = body['nome']
        if 'produto' in body:
            get_user.produto = body['produto']
        if 'preco' in body:
            get_user.preco = body['preco']
                
        db.session.add(get_user)
        db.session.commit()  
        return make_response(200, "estoque", get_user.for_json(), "Usuário atualizado com Sucesso.")

    except Exception as e:
        return(400, "estoque", {}, "Erro ao atualizar")


#gerar resposta
def make_response(status,nome_conteudo,conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo
    if(mensagem):
        body["mensagem"] = mensagem
    return Response(json.dumps(body), status=status,mimetype="aplication/json")
