import dados
from flask import Flask, request, jsonify, render_template, redirect

app = Flask(__name__)
dados.init_db()


@app.route("/")
def index():
    livros = dados.executar("SELECT * FROM livros")
    return render_template("index.html", livros=livros)


@app.route("/livros", methods=["GET", "POST"])
@app.route("/livros/buscar", methods=["GET"])
@app.route("/livros/<isbn>", methods=["PUT"])
def livros(isbn=None):
    if request.path == "/livros/buscar":
        termo = request.args.get("q", "").lower()
        resultado = dados.executar(
            "SELECT * FROM livros WHERE LOWER(titulo) LIKE ? OR isbn = ?",
            (f"%{termo}%", termo)
        )
        return jsonify(resultado)

    if request.method == "GET":
        return jsonify(dados.executar("SELECT * FROM livros"))

    if request.method == "POST":
        novo = request.get_json()

        existe = dados.executar("SELECT isbn FROM livros WHERE isbn = ?", (novo["isbn"],))
        if existe:
            return jsonify({"erro": "ISBN já cadastrado!"}), 400

        status = novo.get("status", "disponivel")
        dados.executar(
            "INSERT INTO livros (isbn, titulo, autor, ano_publicacao, genero, status) VALUES (?, ?, ?, ?, ?, ?)",
            (novo["isbn"], novo["titulo"], novo["autor"], novo["ano_publicacao"], novo["genero"], status)
        )
        novo["status"] = status
        return jsonify({"mensagem": "Livro cadastrado com sucesso!", "livro": novo}), 201

    resultado = dados.executar("SELECT * FROM livros WHERE isbn = ?", (isbn,))
    if not resultado:
        return jsonify({"erro": "Livro não encontrado."}), 404

    livro = resultado[0]
    alteracoes = request.get_json()
    livro.update(alteracoes)
    dados.executar(
        "UPDATE livros SET titulo=?, autor=?, ano_publicacao=?, genero=?, status=? WHERE isbn=?",
        (livro["titulo"], livro["autor"], livro["ano_publicacao"], livro["genero"], livro["status"], isbn)
    )
    return jsonify({"mensagem": "Livro atualizado!", "livro": livro})


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        isbn = request.form["isbn"]

        existe = dados.executar("SELECT isbn FROM livros WHERE isbn = ?", (isbn,))
        if existe:
            return render_template("cadastro.html", erro="ISBN já cadastrado!")

        dados.executar(
            "INSERT INTO livros (isbn, titulo, autor, ano_publicacao, genero, status) VALUES (?, ?, ?, ?, ?, ?)",
            (
                isbn,
                request.form["titulo"],
                request.form["autor"],
                int(request.form["ano_publicacao"]),
                request.form["genero"],
                "disponivel"
            )
        )
        return redirect("/")

    return render_template("cadastro.html")


@app.route("/editar/<isbn>", methods=["GET", "POST"])
def editar(isbn):
    resultado = dados.executar("SELECT * FROM livros WHERE isbn = ?", (isbn,))
    if not resultado:
        return "Livro não encontrado.", 404

    livro = resultado[0]

    if request.method == "POST":
        dados.executar(
            "UPDATE livros SET titulo=?, autor=?, ano_publicacao=?, genero=?, status=? WHERE isbn=?",
            (
                request.form["titulo"],
                request.form["autor"],
                int(request.form["ano_publicacao"]),
                request.form["genero"],
                request.form["status"],
                isbn
            )
        )
        return redirect("/")

    return render_template("editar.html", livro=livro)


if __name__ == "__main__":
    app.run(debug=True)