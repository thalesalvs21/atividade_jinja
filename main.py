import json
import os
from flask import Flask, request, jsonify, render_template, redirect

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

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        novo = {
            "isbn": request.form["isbn"],
            "titulo": request.form["titulo"],
            "autor": request.form["autor"],
            "ano_publicacao": int(request.form["ano_publicacao"]),
            "genero": request.form["genero"],
            "status": "disponivel"
        }

        livros = ler_livros()

        if any(l["isbn"] == novo["isbn"] for l in livros):
            return render_template("cadastro.html", erro="ISBN já cadastrado!")

        livros.append(novo)
        salvar_livros(livros)
        return redirect("/")

    return render_template("cadastro.html")

@app.route("/editar/<isbn>", methods=["GET", "POST"])
def editar(isbn):
    livros = ler_livros()
    livro = next((l for l in livros if l["isbn"] == isbn), None)
    print("ISBN recebido na URL:", repr(isbn))
    print("Livro encontrado:", livro)

    if livro is None:
        return "Livro não encontrado.", 404

    if request.method == "POST":
        print("Dados do formulário:", dict(request.form))

        livro["titulo"] = request.form["titulo"]
        livro["autor"] = request.form["autor"]
        livro["ano_publicacao"] = int(request.form["ano_publicacao"])
        livro["genero"] = request.form["genero"]
        livro["status"] = request.form["status"]

        print("Livro depois de atualizar:", livro)

        salvar_livros(livros)
        print("Salvou em:", os.path.abspath(arquivo))
        return redirect("/")

    return render_template("editar.html", livro=livro)

if __name__ == "__main__":
    app.run(debug=True)
