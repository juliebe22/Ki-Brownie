import os
import re
import uuid
import unicodedata
from functools import wraps
from urllib.parse import quote

from werkzeug.utils import secure_filename
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from config import Config
from services.cache_produtos import invalidar_cache_produtos
from services.supabase_auth import autenticar_admin, obter_usuario
from services.mongo_produtos import (
    criar_produto,
    listar_produtos,
    atualizar_produto,
    desativar_produto,
    reativar_produto,
    excluir_produto
)

app = Flask(__name__)
app.config.from_object(Config)

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "static", "uploads"
)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False  # Apenas para testes locais
)

ADMIN_EMAILS = {
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "").split(",")
    if email.strip()
}


def salvar_imagem(arquivo):
    extensoes_permitidas = {"jpg", "jpeg", "png", "webp"}

    nome_original = secure_filename(arquivo.filename)
    extensao = (
        nome_original.rsplit(".", 1)[-1].lower()
        if "." in nome_original
        else ""
    )

    if extensao not in extensoes_permitidas:
        raise ValueError("Escolha uma imagem JPG, PNG ou WEBP.")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    nome_arquivo = f"{uuid.uuid4().hex}.{extensao}"
    caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_arquivo)

    arquivo.save(caminho)

    return f"/static/uploads/{nome_arquivo}"


def login_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        usuario_id = session.get("admin_id")
        access_token = session.get("access_token")

        if not usuario_id or not access_token:
            return redirect(url_for("login"))

        usuario = obter_usuario(access_token)

        if not usuario or usuario["id"] != usuario_id:
            session.clear()
            flash("Sua sessão expirou. Entre novamente.", "erro")
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return wrapper


def normalizar_texto(texto):
    texto = str(texto or "").strip().casefold()
    texto = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )


def obter_quantidade_minima(produto):
    categoria = normalizar_texto(produto.get("categoria", ""))
    categoria = categoria.replace("-", " ").strip()

    quantidades_minimas = {
        "docinho": 25,
        "docinhos": 25,
        "docinhos premium": 25,
        "cupcake": 8,
        "cupcakes": 8,
        "bem casado": 10,
        "bem casados": 10,
    }

    return quantidades_minimas.get(categoria, 1)

def obter_opcoes_produto(produto):
    nome = normalizar_texto(produto.get("nome", ""))
    categoria = normalizar_texto(produto.get("categoria", ""))

    if "bolo vulcao" in nome:
        correspondencia = re.search(r"(\d{2})\s*cm", nome)
        tamanho = int(correspondencia.group(1)) if correspondencia else None

        return {
            "tipo": "bolo_vulcao",
            "massas": [
                "Branca",
                "Chocolate",
                "Mesclada",
                "Red Velvet",
                "Bolo de cenoura",
            ],
            "coberturas": [
                "Brigadeiro",
                "Brigadeiro Branco",
                "Ninho",
                "Beijinho",
                "Prestígio",
            ],
            "max_coberturas": 2 if tamanho and tamanho > 16 else 1,
        }

    if categoria in ("docinhos", "docinhos premium") and "docinhos" in nome:
       if "personalizados" in nome:
           return {"tipo": "personalizados"}

       if categoria == "docinhos premium":
           return {
            "tipo": "docinhos",
            "sabores": [
                "Ferrero Rocher",
                "Olho de sogra",
            ],
        }

       if "tradicionais" in nome:
           return {
            "tipo": "docinhos",
            "sabores": [
                "Chocolate",
                "Brigadeiro Branco",
                "Beijinho",
                "Ninho",
                "Casadinho",
                "Casadinho Sedução (branco com morango)",
                "Casadinho Sensação (chocolate com morango)",
                "Prestígio",
                "Bicho de pé (morango)",
                "Cajuzinho",
            ],
        }

       if "especiais" in nome:
           return {
            "tipo": "docinhos",
            "sabores": [
                "Capuccino",
                "Chocoball",
                "Ninho com Nutella",
                "Surpresa de uva",
                "Ovomaltine",
                "Castanha",
                "Paçoca",
                "Oreo",
                "Churros",
                "Coco queimado",
                "Confete",
            ],
        }    

    if categoria in ("brownie", "brownies") and "brownie recheado" in nome:
        return {
            "tipo": "brownie",
            "sabores": [
                "Ninho",
                "Dois amores",
                "Chocolate",
                "Coco",
                "Brigadeiro branco",
            ],
        }

    return {"tipo": "nenhum"}

def validar_opcoes_produto(produto, opcoes):
    regras = obter_opcoes_produto(produto)
    tipo = regras["tipo"]

    if tipo == "bolo_vulcao":
        massa = opcoes.get("massa", "")
        coberturas = opcoes.get("coberturas", [])

        if massa not in regras["massas"]:
            raise ValueError("Escolha a massa do bolo.")

        if not isinstance(coberturas, list):
            raise ValueError("Confira as coberturas escolhidas.")

        max_coberturas = regras["max_coberturas"]

        if (
            len(coberturas) < 1
            or len(coberturas) > max_coberturas
            or len(set(coberturas)) != len(coberturas)
            or any(c not in regras["coberturas"] for c in coberturas)
        ):
            if max_coberturas == 1:
                raise ValueError("Escolha uma cobertura para este bolo.")

            raise ValueError(
                "Escolha a primeira cobertura e, se quiser, uma segunda "
                "cobertura diferente."
            )

    elif tipo in ("docinhos", "brownie"):
        sabores_validos = regras["sabores"]
        composicao = opcoes.get("sabores", {})

        if not isinstance(composicao, dict):
            raise ValueError("Confira os sabores escolhidos.")

        if tipo == "brownie":
            sabor = composicao.get("sabor", "")

            if sabor not in sabores_validos:
                raise ValueError("Escolha o sabor do brownie.")

        else:
            if not composicao:
                raise ValueError("Escolha pelo menos um sabor de docinho.")

            for sabor, quantidade in composicao.items():
                if sabor not in sabores_validos:
                    raise ValueError("Um dos sabores selecionados não é válido.")

                try:
                    quantidade = int(quantidade)
                except (TypeError, ValueError):
                    raise ValueError("Informe a quantidade de cada sabor.")

                if quantidade < 25:
                    raise ValueError(
                        f"São necessárias pelo menos 25 unidades de {sabor}."
                    )

def normalizar_item_carrinho(chave, valor):
    # Também aceita itens antigos que ainda estejam salvos na sessão.
    if isinstance(valor, dict):
        return {
            "id_produto": valor.get("id_produto", ""),
            "quantidade": int(valor.get("quantidade", 0)),
            "opcoes": valor.get("opcoes", {}),
            "sabor": valor.get("sabor"),
        }

    return {
        "id_produto": chave,
        "quantidade": int(valor or 0),
        "opcoes": {},
        "sabor": None,
    }


def obter_preco_numerico(produto):
    preco = produto.get("preco", 0)

    if hasattr(preco, "to_decimal"):
        preco = preco.to_decimal()

    return float(preco)


def calcular_preco_item(produto, item):
    preco = obter_preco_numerico(produto)
    opcoes = item.get("opcoes", {})
    sabor = item.get("sabor")

    if sabor and normalizar_texto(sabor) in {
        "ferrero rocher",
        "olho de sogra",
    }:
        preco = 2.10

    if normalizar_texto(opcoes.get("massa", "")) == "bolo de cenoura":
        preco += 12.00

    return preco


def montar_detalhes_item(item):
    opcoes = item.get("opcoes", {})
    detalhes = []

    if opcoes.get("massa"):
        detalhes.append(f"Massa: {opcoes['massa']}")

    if opcoes.get("coberturas"):
        detalhes.append(
            "Coberturas: " + ", ".join(opcoes["coberturas"])
        )

    sabores = opcoes.get("sabores", {})

    if isinstance(sabores, dict):
        for sabor, quantidade in sabores.items():
            if sabor == "sabor":
                detalhes.append(f"Sabor: {quantidade}")
            else:
                detalhes.append(f"{sabor}: {quantidade} unidades")

    if item.get("sabor") and not sabores:
        detalhes.append(f"Sabor: {item['sabor']}")

    return " | ".join(detalhes)


def adicionar_item_carrinho(id_produto, quantidade, opcoes, sabor=None):
    carrinho_session = session.get("carrinho", {})
    chave_item = uuid.uuid4().hex

    carrinho_session[chave_item] = {
        "id_produto": id_produto,
        "quantidade": quantidade,
        "opcoes": opcoes,
        "sabor": sabor,
    }

    session["carrinho"] = carrinho_session
    session.modified = True


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if email not in ADMIN_EMAILS:
            flash(
                "Este e-mail não tem acesso à administração.",
                "erro"
            )
            return render_template("login.html")

        try:
            usuario = autenticar_admin(email, senha)
        except Exception:
            usuario = None

        if not usuario:
            flash("E-mail ou senha incorretos.", "erro")
            return render_template("login.html")

        session.clear()
        session["admin_id"] = usuario["id"]
        session["access_token"] = usuario["access_token"]

        return redirect(url_for("admin"))

    return render_template("login.html")


@app.route("/admin")
@login_obrigatorio
def admin():
    return render_template("admin.html")


@app.route("/admin/produtos", methods=["GET", "POST"])
@login_obrigatorio
def admin_produtos():
    if request.method == "POST":
        try:
            arquivo = request.files.get("imagem")
            imagem_url = (
                salvar_imagem(arquivo)
                if arquivo and arquivo.filename
                else ""
            )

            criar_produto(
                nome=request.form.get("nome", ""),
                descricao=request.form.get("descricao", ""),
                categoria=request.form.get("categoria", ""),
                preco=request.form.get("preco", ""),
                imagem_url=imagem_url
            )

            invalidar_cache_produtos()
            flash("Produto cadastrado com sucesso!", "sucesso")
            return redirect(url_for("admin_produtos"))

        except ValueError as erro:
            flash(str(erro), "erro")

        except Exception:
            flash(
                "Não foi possível cadastrar o produto. "
                "Confira a conexão com o banco.",
                "erro"
            )

    try:
        produtos = listar_produtos(apenas_ativos=False)

        for produto in produtos:
            produto["preco_formatado"] = (
                f'{produto["preco"].to_decimal():.2f}'
            )

    except Exception:
        produtos = []
        flash(
            "Não foi possível carregar os produtos do banco.",
            "erro"
        )

    return render_template("produtos_admin.html", produtos=produtos)

@app.route("/catalogo")
def catalogo():
    from services.cache_produtos import listar_produtos_com_cache

    try:
        produtos = listar_produtos_com_cache()

        for produto in produtos:
            opcoes = obter_opcoes_produto(produto)
            produto["opcoes"] = opcoes
            produto["max_coberturas"] = opcoes.get("max_coberturas", 1)

    except Exception:
        produtos = []
        flash("Não foi possível carregar o catálogo.", "erro")

    carrinho_session = session.get("carrinho", {})
    total_itens = sum(
        normalizar_item_carrinho(chave, valor)["quantidade"]
        for chave, valor in carrinho_session.items()
    )

    return render_template(
        "catalogo.html",
        produtos=produtos,
        quantidades=carrinho_session,
        total_itens=total_itens
    )


@app.route("/admin/produtos/<id_produto>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar_produto(id_produto):
    from services.mongo_produtos import buscar_produto

    produto = buscar_produto(id_produto)

    if not produto:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("admin_produtos"))

    if request.method == "POST":
        try:
            arquivo = request.files.get("imagem")
            imagem_url = produto.get("imagem_url", "")

            if arquivo and arquivo.filename:
                imagem_url = salvar_imagem(arquivo)

            atualizar_produto(id_produto, {
                "nome": request.form.get("nome", ""),
                "descricao": request.form.get("descricao", ""),
                "categoria": request.form.get("categoria", ""),
                "preco": request.form.get("preco", ""),
                "imagem_url": imagem_url
            })

            invalidar_cache_produtos()
            flash("Produto atualizado!", "sucesso")
            return redirect(url_for("admin_produtos"))

        except ValueError as erro:
            flash(str(erro), "erro")

    produto["preco_formatado"] = (
        f'{produto["preco"].to_decimal():.2f}'
    )

    return render_template("editar_produto.html", produto=produto)


@app.route("/admin/produtos/<id_produto>/desativar", methods=["POST"])
@login_obrigatorio
def admin_desativar_produto(id_produto):
    try:
        desativar_produto(id_produto)
        invalidar_cache_produtos()
        flash("Produto desativado.", "sucesso")
    except ValueError as erro:
        flash(str(erro), "erro")
    except Exception:
        flash("Não foi possível desativar o produto.", "erro")

    return redirect(url_for("admin_produtos"))


@app.route("/admin/produtos/<id_produto>/reativar", methods=["POST"])
@login_obrigatorio
def admin_reativar_produto(id_produto):
    try:
        reativar_produto(id_produto)
        invalidar_cache_produtos()
        flash("Produto reativado com sucesso!", "sucesso")
    except ValueError as erro:
        flash(str(erro), "erro")
    except Exception:
        flash("Não foi possível reativar o produto.", "erro")

    return redirect(url_for("admin_produtos"))


@app.route("/admin/produtos/<id_produto>/excluir", methods=["POST"])
@login_obrigatorio
def admin_excluir_produto(id_produto):
    try:
        excluiu = excluir_produto(id_produto)

        if excluiu:
            invalidar_cache_produtos()
            flash("Produto excluído permanentemente.", "sucesso")
        else:
            flash("Produto não encontrado.", "erro")

    except ValueError as erro:
        flash(str(erro), "erro")
    except Exception:
        flash("Não foi possível excluir o produto.", "erro")

    return redirect(url_for("admin_produtos"))


@app.route("/carrinho/adicionar/<id_produto>", methods=["POST"])
def adicionar_ao_carrinho(id_produto):
    from services.mongo_produtos import buscar_produto

    produto = buscar_produto(id_produto)

    if not produto or not produto.get("ativo", False):
        flash("Esse produto não está disponível.", "erro")
        return redirect(url_for("catalogo"))

    regras = obter_opcoes_produto(produto)
    tipo = regras["tipo"]
    opcoes = {}
    sabor = None

    try:
        quantidade = int(request.form.get("quantidade", ""))
    except (TypeError, ValueError):
        flash("Informe uma quantidade válida.", "erro")
        return redirect(url_for("catalogo"))

    quantidade_minima = obter_quantidade_minima(produto)

    if quantidade < quantidade_minima:
        flash(
            f"A quantidade mínima deste produto é {quantidade_minima}.",
            "erro"
        )
        return redirect(url_for("catalogo"))

    if tipo == "bolo_vulcao":
        cobertura1 = request.form.get("cobertura1", "").strip()
        cobertura2 = request.form.get("cobertura2", "").strip()

        coberturas = [cobertura for cobertura in [cobertura1, cobertura2]
                  if cobertura and cobertura != "Nenhuma"]

        opcoes = {
             "massa": request.form.get("massa", "").strip(),
             "coberturas": coberturas,
        }

    elif tipo == "docinhos":
        sabor = request.form.get("sabor", "").strip()

        opcoes = {
            "sabores": {
                sabor: quantidade
            }
        }
    elif tipo == "personalizados":
        opcoes = {}    

    elif tipo == "brownie":
        sabor = request.form.get("sabor", "").strip()

        opcoes = {
            "sabores": {
                "sabor": sabor
            }
        }

    try:
        validar_opcoes_produto(produto, opcoes)
    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("catalogo"))

    # Adiciona o item depois que todas as validações passam.
    adicionar_item_carrinho(
        id_produto=id_produto,
        quantidade=quantidade,
        opcoes=opcoes,
        sabor=sabor
    )

    flash("Produto adicionado ao carrinho!", "sucesso")
    return redirect(url_for("carrinho"))


@app.route("/carrinho")
def carrinho():
    from services.mongo_produtos import buscar_produto

    carrinho_session = session.get("carrinho", {})
    itens = []
    total = 0
    carrinho_corrigido = {}

    for chave_item, valor in carrinho_session.items():
        item = normalizar_item_carrinho(chave_item, valor)
        produto = buscar_produto(item["id_produto"])

        if not produto or not produto.get("ativo", False):
            continue

        quantidade = item["quantidade"]
        preco = calcular_preco_item(produto, item)
        subtotal = preco * quantidade
        total += subtotal

        itens.append({
            "id_item": chave_item,
            "id_produto": item["id_produto"],
            "nome": produto.get("nome", "Produto"),
            "preco": preco,
            "quantidade": quantidade,
            "subtotal": subtotal,
            "detalhes_opcoes": montar_detalhes_item(item)
        })

        carrinho_corrigido[chave_item] = item

    session["carrinho"] = carrinho_corrigido
    session.modified = True

    return render_template(
        "carrinho.html",
        itens=itens,
        total=total
    )


@app.route("/carrinho/quantidade/<id_item>", methods=["POST"])
def alterar_quantidade_carrinho(id_item):
    from services.mongo_produtos import buscar_produto

    carrinho_session = session.get("carrinho", {})
    valor = carrinho_session.get(id_item)

    if valor is None:
        flash("Item não encontrado no carrinho.", "erro")
        return redirect(url_for("carrinho"))

    item = normalizar_item_carrinho(id_item, valor)
    produto = buscar_produto(item["id_produto"])

    if not produto or not produto.get("ativo", False):
        flash("Esse produto não está disponível.", "erro")
        return redirect(url_for("carrinho"))

    quantidade_minima = obter_quantidade_minima(produto)
    quantidade_atual = item["quantidade"]
    acao = request.form.get("acao")

    if acao == "mais":
        item["quantidade"] = quantidade_atual + 1

    elif acao == "menos":
        if quantidade_atual <= quantidade_minima:
            flash(
                f"A quantidade mínima é {quantidade_minima}. "
                "Use Remover para tirar o item do carrinho.",
                "erro"
            )
        else:
            item["quantidade"] = quantidade_atual - 1

    carrinho_session[id_item] = item
    session["carrinho"] = carrinho_session
    session.modified = True

    return redirect(url_for("carrinho"))


@app.route("/carrinho/remover/<id_item>", methods=["POST"])
def remover_do_carrinho(id_item):
    carrinho_session = session.get("carrinho", {})
    carrinho_session.pop(id_item, None)

    session["carrinho"] = carrinho_session
    session.modified = True

    flash("Item removido do carrinho.", "sucesso")
    return redirect(url_for("carrinho"))


@app.route("/carrinho/finalizar", methods=["GET", "POST"])
def finalizar_pedido():
    from services.mongo_produtos import buscar_produto

    observacao = request.form.get("observacao", "").strip()

    carrinho_session = session.get("carrinho", {})
    linhas_pedido = []
    total = 0

    for chave_item, valor in carrinho_session.items():
        item = normalizar_item_carrinho(chave_item, valor)
        produto = buscar_produto(item["id_produto"])

        if not produto or not produto.get("ativo", False):
            continue

        quantidade = item["quantidade"]
        preco = calcular_preco_item(produto, item)
        subtotal = preco * quantidade
        total += subtotal

        detalhes = montar_detalhes_item(item)
        subtotal_formatado = f"{subtotal:.2f}".replace(".", ",")

        texto_item = f"{produto.get('nome', 'Produto')}\n"

        if detalhes:
            texto_item += f"{detalhes}\n"

        texto_item += (
            f"Quantidade: {quantidade}\n"
            f"Subtotal: R$ {subtotal_formatado}"
        )

        linhas_pedido.append(texto_item)

    if not linhas_pedido:
        flash("Seu carrinho está vazio.", "erro")
        return redirect(url_for("carrinho"))

    total_formatado = f"{total:.2f}".replace(".", ",")

    observacao = request.form.get("observacao", "").strip()

    mensagem = (
           "Ki-Brownie | Pedido de encomenda\n\n"
           "Olá! Gostaria de fazer esta encomenda:\n\n"
           + "\n\n".join(linhas_pedido)
           + f"\n\nTotal do pedido: R$ {total_formatado}"
           )

    if observacao:
           mensagem += f"\n\nObservações do pedido: {observacao}"

    mensagem += (
           "\n\nData desejada: a combinar"
           "\nEntrega ou retirada: a combinar"
           "\n\nPodemos combinar os detalhes?"
    )

    numero_whatsapp = "5586999432705"
    link_whatsapp = (
        f"https://wa.me/{numero_whatsapp}?text={quote(mensagem, safe='')}"
    )

    return redirect(link_whatsapp)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "main":
    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "Configure FLASK_SECRET_KEY no arquivo .env"
        )

    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)    