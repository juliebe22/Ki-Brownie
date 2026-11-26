import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from bson import ObjectId
from bson.decimal128 import Decimal128
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "ki_brownie")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI não encontrada no arquivo .env")

cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
banco = cliente[MONGO_DATABASE]
colecao_produtos = banco["produtos"]


def testar_conexao():
    try:
        cliente.admin.command("ping")
        print("Conexão com MongoDB realizada com sucesso!")
        return True
    except Exception as erro:
        print(f"Erro ao conectar com MongoDB: {erro}")
        return False


def criar_produto(nome, descricao, categoria, preco, imagem_url=""):
    nome = nome.strip()
    descricao = descricao.strip()
    categoria = categoria.strip()

    if not nome:
        raise ValueError("O nome do produto é obrigatório.")

    if not categoria:
        raise ValueError("A categoria é obrigatória.")

    try:
        preco_decimal = Decimal(str(preco).replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError("Informe um preço válido.")

    if not preco_decimal.is_finite() or preco_decimal <= 0:
        raise ValueError("O preço deve ser maior que zero.")

    agora = datetime.now(timezone.utc)

    produto = {
        "nome": nome,
        "descricao": descricao,
        "categoria": categoria,
        "preco": Decimal128(preco_decimal),
        "imagem_url": imagem_url.strip(),
        "disponivel": True,
        "ativo": True,
        "criado_em": agora,
        "atualizado_em": agora
    }

    resultado = colecao_produtos.insert_one(produto)
    return str(resultado.inserted_id)


def listar_produtos(apenas_ativos=True):
    filtro = {"ativo": True} if apenas_ativos else {}

    return list(colecao_produtos.find(filtro).sort("nome", 1))


def buscar_produto(id_produto):
    if not ObjectId.is_valid(id_produto):
        return None

    return colecao_produtos.find_one({"_id": ObjectId(id_produto)})


def atualizar_produto(id_produto, dados):
    if not ObjectId.is_valid(id_produto):
        raise ValueError("ID de produto inválido.")

    campos_permitidos = {
        "nome", "descricao", "categoria", "preco",
        "imagem_url", "disponivel", "ativo"
    }

    atualizacao = {
        campo: valor
        for campo, valor in dados.items()
        if campo in campos_permitidos
    }

    if not atualizacao:
        raise ValueError("Nenhum campo válido foi informado.")

    if "nome" in atualizacao:
        atualizacao["nome"] = atualizacao["nome"].strip()
        if not atualizacao["nome"]:
            raise ValueError("O nome não pode ficar vazio.")

    if "preco" in atualizacao:
        try:
            preco = Decimal(str(atualizacao["preco"]).replace(",", "."))
        except (InvalidOperation, ValueError):
            raise ValueError("Informe um preço válido.")

        if not preco.is_finite() or preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")

        atualizacao["preco"] = Decimal128(preco)

    atualizacao["atualizado_em"] = datetime.now(timezone.utc)

    resultado = colecao_produtos.update_one(
        {"_id": ObjectId(id_produto)},
        {"$set": atualizacao}
    )

    return resultado.matched_count > 0


def desativar_produto(id_produto):
    if not ObjectId.is_valid(id_produto):
        raise ValueError("ID de produto inválido.")

    resultado = colecao_produtos.update_one(
        {"_id": ObjectId(id_produto)},
        {
            "$set": {
                "ativo": False,
                "atualizado_em": datetime.now(timezone.utc)
            }
        }
    )

    return resultado.matched_count > 0

def reativar_produto(id_produto):
    if not ObjectId.is_valid(id_produto):
        raise ValueError("ID de produto inválido.")

    resultado = colecao_produtos.update_one(
        {"_id": ObjectId(id_produto)},
        {
            "$set": {
                "ativo": True,
                "atualizado_em": datetime.now(timezone.utc)
            }
        }
    )

    return resultado.matched_count > 0

def excluir_produto(id_produto):
    if not ObjectId.is_valid(id_produto):
        raise ValueError("ID de produto inválido.")

    resultado = colecao_produtos.delete_one(
        {"_id": ObjectId(id_produto)}
    )

    return resultado.deleted_count > 0

if __name__ == "__main__":
    if testar_conexao():
        print("Total de produtos cadastrados:", colecao_produtos.count_documents({}))

    cliente.close()