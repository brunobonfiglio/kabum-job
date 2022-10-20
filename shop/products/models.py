from shop import db
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from flask import Flask, jsonify
import sentry_sdk
sentry_sdk.init(
    "https://e7547433e06143ab9c05a87e576368c3@o464374.ingest.sentry.io/5514931",
    traces_sample_rate=1.0
)


produto_oferta = db.Table('produto_oferta',
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
    db.Column('oferta_codigo', db.String(150), db.ForeignKey('oferta.codigo'))
)

produto_menus = db.Table('produto_menus',
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
    db.Column('menu_codigo', db.Integer, db.ForeignKey('menus.codigo'))
)

produto_familia = db.Table('produto_familias',
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
    db.Column('familias_codigo', db.Integer, db.ForeignKey('familia.codigo'))
)

produto_fabricante = db.Table('produto_fabricantes',
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
    db.Column('fabricantes_codigo', db.Integer, db.ForeignKey('fabricante.codigo'))
)


class Oferta(db.Model):
  
    codigo = db.Column(db.String(150), primary_key=True)
    evento_codigo = db.Column(db.Integer, unique=False, nullable=True)
    data_inicio = db.Column(db.Integer, unique=False, nullable=True)
    data_fim = db.Column(db.Integer, unique=False, nullable=True)
    quantidade = db.Column(db.Integer, unique=False, nullable=True)
    evento = db.Column(db.String(120), unique=False, nullable=True)
    logar = db.Column(db.Integer, unique=False, nullable=True)


class Produto(db.Model):

    id = db.Column(db.Integer, primary_key=True) 
    brinde = db.Column(db.String(120), unique=False, nullable=True)  

    #------------------------------------------------------------------------------------
    produto_oferta = db.relationship('Oferta', secondary=produto_oferta,
            backref=db.backref('ofertas', lazy='dynamic'))
   


    oferta_inicio = db.Column(db.Integer, unique=False, nullable=True)  
    vendedor_nome = db.Column(db.String(120), unique=False, nullable=True)  
    id_oferta = db.Column(db.String(120), unique=False, nullable=True)  
    id_seller = db.Column(db.Integer, unique=False, nullable=True)  
    nova_descricao = db.Column(db.String(120), unique=False, nullable=True)

    #------------------------------------------------------------------------------------
    produto_menus = db.relationship('Menus', secondary=produto_menus,
            backref=db.backref('menus', lazy='dynamic'))


    menu = db.Column(db.String(120), unique=False, nullable=True)  
    codigo = db.Column(db.Integer, unique=False, nullable=True)
    nome = db.Column(db.Text, unique=False, nullable=True)

    #------------------------------------------------------------------------------------
    produto_familia = db.relationship('Familia', secondary=produto_familia,
            backref=db.backref('familias', lazy='dynamic'))


    fotos = db.Column(db.ARRAY(db.String(180)), unique=False, nullable=True)
    disponibilidade = db.Column(db.Boolean, unique=False, nullable=True)
    pre_venda = db.Column(db.Boolean, unique=False, nullable=True)

    #------------------------------------------------------------------------------------
    produto_fabricante = db.relationship('Fabricante', secondary=produto_fabricante,
            backref=db.backref('fabricantes', lazy='dynamic'))


    preco = db.Column(db.Float, unique=False, nullable=True)
    preco_prime = db.Column(db.Float, unique=False, nullable=True)
    preco_desconto = db.Column(db.Float, unique=False, nullable=True)

    preco_desconto_prime = db.Column(db.Float, unique=False, nullable=True)
    preco_antigo = db.Column(db.Float, unique=False, nullable=True)
    economize_prime = db.Column(db.Float, unique=False, nullable=True)
    descricao = db.Column(db.Text, unique=False, nullable=True)
    tag_title = db.Column(db.String(120), unique=False, nullable=True)

    tem_frete_gratis = db.Column(db.Boolean, unique=False, nullable=True)
    frete_gratis_somente_prime = db.Column(db.Boolean, unique=False, nullable=True)
    tag_description = db.Column(db.Text, unique=False, nullable=True)
    avaliacao_numero = db.Column(db.Integer, unique=False, nullable=True)

    avaliacao_nota = db.Column(db.Integer, unique=False, nullable=True)
    desconto = db.Column(db.Integer, unique=False, nullable=True)
    is_openbox = db.Column(db.Boolean, unique=False, nullable=True)
    produto_html = db.Column(db.Text, unique=False, nullable=True)
    dimensao_peso = db.Column(db.Integer, unique=False, nullable=True)

    peso = db.Column(db.String(120), unique=False, nullable=True)
    garantia = db.Column(db.String(120), unique=False, nullable=True)
    codigo_anatel = db.Column(db.String(120), unique=False, nullable=True)
    produto_especie = db.Column(db.Integer, unique=False, nullable=True)

    link_descricao = db.Column(db.Text, unique=False, nullable=True)
    origem = db.Column(db.String(120), unique=False, nullable=True)
    origem_nome = db.Column(db.String(120), unique=False, nullable=True)
    flag_blackfriday = db.Column(db.Integer, unique=False, nullable=True)
    sucesso = db.Column(db.String(120), unique=False, nullable=True)




class Menus(db.Model):

    codigo = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=False, nullable=True)
    amigavel = db.Column(db.String(120), unique=False, nullable=True)
    nome_url = db.Column(db.String(120), unique=False, nullable=True)


class Familia(db.Model):
  
    codigo = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=False, nullable=True)
    titulo = db.Column(db.String(120), unique=False, nullable=True)
    produtos = db.Column(db.ARRAY(db.Integer), unique=False, nullable=True)



class Fabricante(db.Model):

    codigo = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=False, nullable=True)
    img = db.Column(db.String(120), unique=False, nullable=True)


db.create_all()
