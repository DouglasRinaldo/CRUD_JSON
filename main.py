from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json
from flask_marshmallow import Marshmallow
from marshmallow import schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/pedidos'

db = SQLAlchemy(app)
ma= Marshmallow(app)
#classes

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_produto = db.Column(db.String(50))
    preco = db.Column(db.Float)
    itens_pedido = db.relationship('Pedido', backref='itens')
    

    def for_json(self):
        return {'id': self.id, 'nome_produto': self.nome_produto, 'preco': self.preco}


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    pedido = db.Column(db.Integer)
    itens_id = db.Column(db.Integer, db.ForeignKey('estoque.id'))


class EstoqueSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Estoque
    id = ma.auto_field()
    nome_produto = ma.auto_field()
    preco = ma.auto_field()
    itens_pedido = ma.auto_field()

class PedidoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Pedido
    id = ma.auto_field()
    nome = ma.auto_field()
    pedido = ma.auto_field()
    itens_id = ma.auto_field()
    
def for_json(id, nome, pedido, itens_id):
    if Pedido.itens_id == Estoque.id:
        return {'id': Pedido.id, 'nome': Pedido.nome, 'pedido': Pedido.pedido, 'itens_id': Estoque.nome_produto}
    else:
        return {'id': Pedido.id, 'nome': Pedido.nome, 'pedido': Pedido.pedido, 'itens_id': Pedido.itens_id}


def dump_all_from_estoque():
    estoque_all = Estoque.query.all()
    for itens in estoque_all:
        estoque_schema = EstoqueSchema()
        output_estoque = estoque_schema.dump(itens)
        print(output_estoque)
    return output_estoque

def dump_all_from_pedidos():
    pedidos_all = Pedido.query.all()
    for pedidos in pedidos_all:
        pedidos_schema = PedidoSchema()
        output_pedidos = pedidos_schema.dump(pedidos)
    return output_pedidos




#Select all
@app.route("/pedidos",methods=['GET'])
def select_all_users():
    pedidos = dump_all_from_pedidos()
    itens = dump_all_from_estoque()
    if pedidos['itens_id'] == itens['id']:
        pedidos['itens_id'] = str(itens['nome_produto'])
    return make_response(200, "pedidos", pedidos)


#Select one
@app.route("/pedido/<id>",methods=["GET"])
def select_one_user(id):
    pedido_one = Pedido.query.filter_by(id=id).first()
    pedidos_schema = PedidoSchema()
    output_pedido = pedidos_schema.dump(pedido_one)
    itens = dump_all_from_estoque()
    if output_pedido['itens_id'] == itens['id']:
        output_pedido['itens_id'] = str(itens['nome_produto'])
    return make_response(200, "pedido", output_pedido)

#Cadastro
@app.route("/pedido",methods=["POST"])
def create_user():
    body = request.get_json()

    try:
        pedido = Pedido(nome = body["nome"], pedido = body["pedido"], itens_id = body["itens_id"])
        db.session.add(pedido)
        db.session.commit()
        return make_response(201, "pedido", pedido.for_json(), "Pedido Criado com Sucesso!")
    except Exception as e:
        return(400, "pedido", {}, "Erro ao cadastrar o pedido")

#Deletar Usuário
@app.route("/pedido/<id>",methods=["DELETE"])
def del_users(id):
    pedido = Pedido.query.filter_by(id=id).first()

    try:
        db.session.delete(pedido)
        db.session.commit()
        return make_response(200,"pedido",pedido.for_json(),"Pedido Deletado com Sucesso!")
    except Exception as e:
        return(400,"pedido",{},"Erro ao identificar o pedido")



#Update
@app.route("/pedido/<id>",methods=["PUT"])
def update_user(id):
    get_pedido = Pedido.query.filter_by(id=id).first()
    body = request.get_json()
    try:
        if 'nome' in body:
            get_pedido.nome = body['nome']
        if 'pedido' in body:
            get_pedido.pedido = body['pedido']
        if 'itens_id' in body:
            get_pedido.itens_id = body['item']
                
        db.session.add(get_pedido)
        db.session.commit()  
        return make_response(200, "pedido", get_pedido.for_json(), "Pedido atualizado com Sucesso.")

    except Exception as e:
        return(400, "pedido", {}, "Erro ao atualizar o pedido")


#gerar resposta
def make_response(status,nome_conteudo,conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo
    if(mensagem):
        body["mensagem"] = mensagem
    return Response(json.dumps(body), status=status,mimetype="aplication/json")

app.run(debug=True)