from flask import (
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from shop import app, db
from .models import (
    Produto,
    Menus,
    produto_menus,
    Oferta,
    produto_oferta,
    Familia,
    produto_familia,
    Fabricante,
    produto_fabricante,
)

# from .forms import Addproducts
import secrets, os, json
from flask import Flask, jsonify
from flask.views import MethodView
from sqlalchemy import and_
from cerberus import Validator
import yaml
from sqlalchemy import text
import sentry_sdk

sentry_sdk.init(
    "https://e7547433e06143ab9c05a87e576368c3@o464374.ingest.sentry.io/5514931",
    traces_sample_rate=1.0,
)


@app.route("/")
def home():

    return render_template("products/index.html", title="Loja", brands="brands")


# ----------------------------------------------------------------------
# PRODUTOS


def get_produtos(request_json=None):
    with open("./shop/products/schemas/produtos.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    exclude = ["oferta", "menus", "familia", "fabricante"]

    def get_table_by_list(key: str, lista: str):
        query_table = and_(
            getattr(Produto, str(f"produto_{key}")).any(
                getattr(eval(key.capitalize()), str(key_value)) == value
            )
            for values in lista
            for key_value, value in values.items()
        )
        return query_table

    def get_table_by_dict(key: str, values: str):
        query_table = and_(
            getattr(Produto, str(f"produto_{key}")).any(
                getattr(eval(key.capitalize()), str(key_value)) == value
            )
            for key_value, value in values.items()
        )
        return query_table

    produtos = (
        db.session.query(*Produto.__table__.columns,)
        .filter(
            and_(
                getattr(Produto, str(key)).ilike(f"%{value}%")
                if isinstance(value, str)
                else getattr(Produto, str(key)) == value
                if key not in exclude
                else get_table_by_list(key, value)
                if isinstance(value, list)
                else get_table_by_dict(key, value)
                for key, value in request_json.items()
            )
        )
        .all()
    )

    k = []
    for produto in produtos:
        d = produto._asdict()
        for excl in exclude:
            x = (
                db.session.query(*eval(excl.capitalize()).__table__.columns)
                .outerjoin(
                    eval(excl.capitalize()), getattr(Produto, str(f"produto_{excl}"))
                )
                .filter(
                    getattr(Produto, str(f"produto_{excl}")).any(Produto.id == d["id"])
                )
                .all()
            )
            x = [z._asdict() for z in x]
            if len(x) == 1:
                d.update({excl: x[0]})
            else:
                d.update({excl: x})
        k.append(d)

    return k


def post_produtos(request_json):
    with open("./shop/products/schemas/produtos_post.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    exclude = ["oferta", "menus", "familia", "fabricante"]

    for key, value in request_json.items():
        if key in exclude:
            if key == "menus":
                menus = Menus.query.filter(
                    getattr(eval(key.capitalize()), str("codigo")).in_(value)
                ).all()
            if key == "oferta":
                oferta = Oferta.query.filter(
                    getattr(eval(key.capitalize()), str("codigo")) == value
                ).all()
            if key == "familia":
                familia = Familia.query.filter(
                    getattr(eval(key.capitalize()), str("codigo")) == value
                ).all()
            if key == "fabricante":
                fabricante = Fabricante.query.filter(
                    getattr(eval(key.capitalize()), str("codigo")) == value
                ).all()

    me = Produto()
    for key, value in request_json.items():
        # print(key)
        if key not in exclude:
            setattr(me, key, value)
        else:
            print(key)
            setattr(me, str("produto_" + key), eval(key))

    db.session.add(me)
    db.session.commit()

    return str(me)


def put_produtos(request_json):
    with open("./shop/products/schemas/produtos_put.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    exclude = ["oferta", "menus", "familia", "fabricante"]

    m = {}
    for key, value in request_json.items():
        if key in exclude:

            if key == "menus":
                menus_del = (
                    Menus.query.outerjoin(Menus, Produto.produto_menus)
                    .filter(
                        getattr(Produto, str(f"produto_menus")).any(
                            Produto.id == request_json["id"]
                        )
                    )
                    .all()
                )
                if menus_del:
                    for i in range(len(menus_del)):
                        produto = (
                            db.session.query(Produto)
                            .filter_by(id=request_json["id"])
                            .first()
                        )
                        produto.produto_menus.remove(menus_del[i])

                    menus = Menus.query.filter(Menus.codigo.in_(value)).all()
                    produto = (
                        db.session.query(Produto)
                        .filter_by(id=request_json["id"])
                        .first()
                    )

                    produto.produto_menus = menus
                    db.session.flush()

            if key == "oferta":
                oferta_del = (
                    Oferta.query.outerjoin(Oferta, Produto.produto_oferta)
                    .filter(
                        getattr(Produto, str(f"produto_oferta")).any(
                            Produto.id == request_json["id"]
                        )
                    )
                    .all()
                )
                if oferta_del:
                    for i in range(len(oferta_del)):
                        produto = (
                            db.session.query(Produto)
                            .filter_by(id=request_json["id"])
                            .first()
                        )
                        produto.produto_oferta.remove(oferta_del[i])

                    oferta = Oferta.query.filter(Oferta.codigo == value).first()
                    produto = (
                        db.session.query(Produto)
                        .filter_by(id=request_json["id"])
                        .first()
                    )

                    produto.produto_oferta = oferta
                    db.session.flush()

            if key == "familia":
                familia_del = (
                    Familia.query.outerjoin(Familia, Produto.produto_familia)
                    .filter(
                        getattr(Produto, str(f"produto_familia")).any(
                            Produto.id == request_json["id"]
                        )
                    )
                    .all()
                )
                if familia_del:
                    for i in range(len(familia_del)):
                        produto = (
                            db.session.query(Produto)
                            .filter_by(id=request_json["id"])
                            .first()
                        )
                        produto.produto_familia.remove(familia_del[i])

                    familia = Familia.query.filter(Familia.codigo == value).first()
                    produto = (
                        db.session.query(Produto)
                        .filter_by(id=request_json["id"])
                        .first()
                    )

                    produto.produto_familia = familia
                    db.session.flush()

            if key == "fabricante":
                fabricante_del = (
                    Fabricante.query.outerjoin(Fabricante, Produto.produto_fabricante)
                    .filter(
                        getattr(Produto, str(f"produto_fabricante")).any(
                            Produto.id == request_json["id"]
                        )
                    )
                    .all()
                )
                if fabricante_del:
                    for i in range(len(fabricante_del)):
                        produto = (
                            db.session.query(Produto)
                            .filter_by(id=request_json["id"])
                            .first()
                        )
                        produto.produto_fabricante.remove(fabricante_del[i])

                    fabricante = Fabricante.query.filter(
                        Fabricante.codigo == value
                    ).first()
                    produto = (
                        db.session.query(Produto)
                        .filter_by(id=request_json["id"])
                        .first()
                    )

                    produto.produto_fabricante = fabricante
                    db.session.flush()
        else:
            m.update({key: value})

    produtos = Produto.query.filter_by(id=request_json["id"]).update(m)
    db.session.commit()
    return str(m)


def delete_produtos(request_json):
    with open("./shop/products/schemas/produtos_delete.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    produtos = Produto.query.filter_by(id=request_json["id"]).first()
    db.session.delete(produtos)
    db.session.commit()
    return str(produtos)


# --------------------------------------------------------------


class ProdutoList(MethodView):
    def get(self):
        values = request.json
        if values == None:
            values = {}
        return jsonify(get_produtos(values))

    def post(self):
        values = request.json
        return jsonify(post_produtos(values))

    def put(self):
        values = request.json
        return jsonify(put_produtos(values))

    def delete(self):
        values = request.json
        return jsonify(delete_produtos(values))


produto_view = ProdutoList.as_view("produto_api")
app.add_url_rule("/api/v1/produto", methods=["GET"], view_func=produto_view)
app.add_url_rule("/api/v1/produto", methods=["POST"], view_func=produto_view)
app.add_url_rule("/api/v1/produto", methods=["PUT", "DELETE"], view_func=produto_view)


# ----------------------------------------------------------------------
# MENUS


def get_menus(request_json):
    with open("./shop/products/schemas/menus.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    x = (
        db.session.query(*Menus.__table__.columns)
        .filter(
            and_(
                getattr(Menus, str(key)).ilike(f"%{value}%")
                if isinstance(value, str)
                else getattr(Menus, str(key)) == value
                for key, value in request_json.items()
            )
        )
        .all()
    )

    return str(x)


def post_menus(request_json):
    with open("./shop/products/schemas/menus_add.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    me = Menus()
    for key, value in request_json.items():
        print(key)
        setattr(me, key, value)

    db.session.add(me)
    db.session.commit()

    return str(me)


def put_menus(request_json):
    with open("./shop/products/schemas/menus_put.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors
    m = {}
    for key, value in request_json.items():
        if key != "codigo":
            m.update({key: value})

    menus = Menus.query.filter_by(codigo=request_json["codigo"]).update(m)
    db.session.commit()
    return str(m)


def delete_menus(request_json):
    with open("./shop/products/schemas/menus_delete.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    menus = Menus.query.filter_by(codigo=request_json["codigo"]).first()
    db.session.delete(menus)
    db.session.commit()
    return str(menus)


# --------------------------------------------------------------


class MenusList(MethodView):
    def get(self):
        values = request.json
        if values == None:
            values = {}
        return jsonify(get_menus(values))

    def post(self):
        values = request.json
        return jsonify(post_menus(values))

    def put(self):
        values = request.json
        return jsonify(put_menus(values))

    def delete(self):
        values = request.json
        return jsonify(delete_menus(values))


menus_view = MenusList.as_view("menus_api")
app.add_url_rule("/api/v1/menus", methods=["GET"], view_func=menus_view)
app.add_url_rule("/api/v1/menus", methods=["POST"], view_func=menus_view)
app.add_url_rule("/api/v1/menus", methods=["PUT", "DELETE"], view_func=menus_view)


# ----------------------------------------------------------------------
# FAMILIA


def get_familia(request_json):
    with open("./shop/products/schemas/familia.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    result = (
        db.session.query(*Familia.__table__.columns)
        .filter(
            and_(
                getattr(Familia, str(key)).ilike(f"%{value}%")
                if isinstance(value, str)
                else getattr(Familia, str(key)) == value
                for key, value in request_json.items()
            )
        )
        .all()
    )

    return result


def post_familia(request_json):
    with open("./shop/products/schemas/familia_add.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    me = Familia()
    for key, value in request_json.items():
        print(key)
        setattr(me, key, value)

    db.session.add(me)
    db.session.commit()

    return str(me)


def put_familia(request_json):
    with open("./shop/products/schemas/familia_put.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors
    m = {}
    for key, value in request_json.items():
        if key != "codigo":
            m.update({key: value})

    familia = Familia.query.filter_by(codigo=request_json["codigo"]).update(m)
    db.session.commit()
    return str(m)


def delete_familia(request_json):
    with open("./shop/products/schemas/familia_delete.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    familia = Familia.query.filter_by(codigo=request_json["codigo"]).first()
    db.session.delete(familia)
    db.session.commit()
    return str(familia)


# --------------------------------------------------------------


class FamiliaList(MethodView):
    def get(self):
        values = request.json
        if values == None:
            values = {}
        return jsonify(get_familia(values))

    def post(self):
        values = request.json
        return jsonify(post_familia(values))

    def put(self):
        values = request.json
        return jsonify(put_familia(values))

    def delete(self):
        values = request.json
        return jsonify(delete_familia(values))


familia_view = FamiliaList.as_view("familia_api")
app.add_url_rule("/api/v1/familia", methods=["GET"], view_func=familia_view)
app.add_url_rule("/api/v1/familia", methods=["POST"], view_func=familia_view)
app.add_url_rule("/api/v1/familia", methods=["PUT", "DELETE"], view_func=familia_view)


# ----------------------------------------------------------------------
# FABRICANTE


def get_fabricante(request_json):
    with open("./shop/products/schemas/fabricante.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    result = (
        db.session.query(*Fabricante.__table__.columns)
        .filter(
            and_(
                getattr(Fabricante, str(key)).ilike(f"%{value}%")
                if isinstance(value, str)
                else getattr(Fabricante, str(key)) == value
                for key, value in request_json.items()
            )
        )
        .all()
    )

    return result


def post_fabricante(request_json):
    with open("./shop/products/schemas/fabricante_add.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    me = Fabricante()
    for key, value in request_json.items():
        print(key)
        setattr(me, key, value)

    db.session.add(me)
    db.session.commit()

    return str(me)


def put_fabricante(request_json):
    with open("./shop/products/schemas/fabricante_put.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors
    m = {}
    for key, value in request_json.items():
        if key != "codigo":
            m.update({key: value})

    fabricante = Fabricante.query.filter_by(codigo=request_json["codigo"]).update(m)
    db.session.commit()
    return str(m)


def delete_fabricante(request_json):
    with open("./shop/products/schemas/fabricante_delete.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    fabricante = Fabricante.query.filter_by(codigo=request_json["codigo"]).first()
    db.session.delete(fabricante)
    db.session.commit()
    return str(fabricante)


# --------------------------------------------------------------


class FabricanteList(MethodView):
    def get(self):
        values = request.json
        if values == None:
            values = {}
        return jsonify(get_fabricante(values))

    def post(self):
        values = request.json
        return jsonify(post_fabricante(values))

    def put(self):
        values = request.json
        return jsonify(put_fabricante(values))

    def delete(self):
        values = request.json
        return jsonify(delete_fabricante(values))


fabricante_view = FabricanteList.as_view("fabricante_api")
app.add_url_rule("/api/v1/fabricante", methods=["GET"], view_func=fabricante_view)
app.add_url_rule("/api/v1/fabricante", methods=["POST"], view_func=fabricante_view)
app.add_url_rule(
    "/api/v1/fabricante", methods=["PUT", "DELETE"], view_func=fabricante_view
)


# ----------------------------------------------------------------------
# OFERTA


def get_oferta(request_json):
    with open("./shop/products/schemas/oferta.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    result = (
        db.session.query(*Oferta.__table__.columns)
        .filter(
            and_(
                getattr(Oferta, str(key)).ilike(f"%{value}%")
                if isinstance(value, str)
                else getattr(Oferta, str(key)) == value
                for key, value in request_json.items()
            )
        )
        .all()
    )

    return result


def post_oferta(request_json):
    with open("./shop/products/schemas/oferta_add.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    me = Oferta()
    for key, value in request_json.items():
        print(key)
        setattr(me, key, value)

    db.session.add(me)
    db.session.commit()

    return str(me)


def put_oferta(request_json):
    with open("./shop/products/schemas/oferta_put.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors
    m = {}
    for key, value in request_json.items():
        if key != "codigo":
            m.update({key: value})

    oferta = Oferta.query.filter_by(codigo=request_json["codigo"]).update(m)
    db.session.commit()
    return str(m)


def delete_oferta(request_json):
    with open("./shop/products/schemas/oferta_delete.yml") as opened_schema:
        schema = yaml.load(opened_schema.read(), Loader=yaml.FullLoader)
    validator = Validator(schema)
    if not validator.validate(request_json):
        return 400, validator.errors

    oferta = Oferta.query.filter_by(codigo=request_json["codigo"]).first()
    db.session.delete(oferta)
    db.session.commit()
    return str(oferta)


# --------------------------------------------------------------


class OfertaList(MethodView):
    def get(self):
        values = request.json
        if values == None:
            values = {}

        return jsonify(get_oferta(values))

    def post(self):
        values = request.json
        return jsonify(post_oferta(values))

    def put(self):
        values = request.json
        return jsonify(put_oferta(values))

    def delete(self):
        values = request.json
        return jsonify(delete_oferta(values))


oferta_view = OfertaList.as_view("oferta_api")
app.add_url_rule("/api/v1/oferta", methods=["GET"], view_func=oferta_view)
app.add_url_rule("/api/v1/oferta", methods=["POST"], view_func=oferta_view)
app.add_url_rule("/api/v1/oferta", methods=["PUT", "DELETE"], view_func=oferta_view)
