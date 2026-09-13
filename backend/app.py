
from flask import Flask, jsonify, request, send_from_directory
import os

import database
import services
from services import RegraDeNegocioError

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

CADASTROS_SIMPLES = {
    "marcas": "marca_id",
    "cores": "cor_id",
    "materiais": "material_id",
}


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------- API generica: Marcas, Cores, Materiais ----------

def registrar_rotas_cadastro_simples(nome_recurso):
    coluna_fk = CADASTROS_SIMPLES[nome_recurso]

    def get_lista():
        return jsonify(services.listar_simples(nome_recurso))

    def post_item():
        dados = request.get_json(force=True)
        try:
            novo_id = services.cadastrar_simples(nome_recurso, dados.get("nome"))
            return jsonify({"id": novo_id}), 201
        except RegraDeNegocioError as e:
            return jsonify({"erro": str(e)}), 400

    def put_item(item_id):
        dados = request.get_json(force=True)
        try:
            services.atualizar_simples(nome_recurso, item_id, dados.get("nome"))
            return "", 204
        except RegraDeNegocioError as e:
            return jsonify({"erro": str(e)}), 400

    def delete_item(item_id):
        try:
            services.remover_simples(nome_recurso, item_id, coluna_fk)
            return "", 204
        except RegraDeNegocioError as e:
            return jsonify({"erro": str(e)}), 400

    app.add_url_rule(f"/api/{nome_recurso}", f"get_{nome_recurso}", get_lista, methods=["GET"])
    app.add_url_rule(f"/api/{nome_recurso}", f"post_{nome_recurso}", post_item, methods=["POST"])
    app.add_url_rule(f"/api/{nome_recurso}/<int:item_id>", f"put_{nome_recurso}", put_item, methods=["PUT"])
    app.add_url_rule(f"/api/{nome_recurso}/<int:item_id>", f"delete_{nome_recurso}", delete_item, methods=["DELETE"])


for recurso in CADASTROS_SIMPLES:
    registrar_rotas_cadastro_simples(recurso)


# ---------- API: Filamentos ----------

@app.route("/api/filamentos", methods=["GET"])
def get_filamentos():
    return jsonify(services.obter_filamentos())


@app.route("/api/filamentos", methods=["POST"])
def post_filamento():
    dados = request.get_json(force=True)
    try:
        novo_id = services.cadastrar_filamento(
            marca_id=dados.get("marca_id"),
            cor_id=dados.get("cor_id"),
            material_id=dados.get("material_id"),
            diametro_mm=dados.get("diametro_mm"),
            peso_rolo_g=dados.get("peso_rolo_g"),
            quantidade_rolos=dados.get("quantidade_rolos"),
        )
        return jsonify({"id": novo_id}), 201
    except RegraDeNegocioError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/filamentos/<int:filamento_id>", methods=["PUT"])
def put_filamento(filamento_id):
    dados = request.get_json(force=True)
    try:
        services.atualizar_filamento(
            filamento_id,
            marca_id=dados.get("marca_id"),
            cor_id=dados.get("cor_id"),
            material_id=dados.get("material_id"),
            diametro_mm=dados.get("diametro_mm"),
            peso_rolo_g=dados.get("peso_rolo_g"),
            quantidade_rolos=dados.get("quantidade_rolos"),
        )
        return "", 204
    except RegraDeNegocioError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/filamentos/<int:filamento_id>", methods=["DELETE"])
def delete_filamento(filamento_id):
    try:
        services.remover_filamento(filamento_id)
        return "", 204
    except RegraDeNegocioError as e:
        return jsonify({"erro": str(e)}), 400


if __name__ == "__main__":
    database.init_db()
    app.run(debug=True, port=5000)
