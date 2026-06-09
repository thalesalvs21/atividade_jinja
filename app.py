import json
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
arquivo = "arquivos/livros.json"


def ler_livros():
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_livros(lista):
    os.makedirs("arquivos", exist_ok=True)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)


@app.route("/")
def index():
    livros = ler_livros()
    return render_template("index.html", livros=livros)


@app.route("/livros", methods=["GET", "POST"])
@app.route("/livros/buscar", methods=["GET"])
@app.route("/livros/<isbn>", methods=["PUT"])
def livros(isbn=None):
    livros = ler_livros()

    if request.path == "/livros/buscar":
        termo = request.args.get("q", "").lower()
        return jsonify([l for l in livros if termo in l["titulo"].lower() or termo == l["isbn"]])

    if request.method == "GET":
        return jsonify(livros)

    if request.method == "POST":
        novo = request.get_json()
        if any(l["isbn"] == novo["isbn"] for l in livros):
            return jsonify({"erro": "ISBN já cadastrado!"}), 400
        novo.setdefault("status", "disponivel")
        livros.append(novo)
        salvar_livros(livros)
        return jsonify({"mensagem": "Livro cadastrado com sucesso!", "livro": novo}), 201

    alteracoes = request.get_json()
    for livro in livros:
        if livro["isbn"] == isbn:
            livro.update(alteracoes)
            salvar_livros(livros)
            return jsonify({"mensagem": "Livro atualizado!", "livro": livro})
    return jsonify({"erro": "Livro não encontrado."}), 404


if __name__ == "__main__":
    app.run(debug=True)
