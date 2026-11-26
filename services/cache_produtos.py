import json

import redis

from config import Config
from services.mongo_produtos import listar_produtos


CHAVE_CACHE_PRODUTOS = "ki-brownie:produtos"
TEMPO_CACHE = 300  # 5 minutos


def criar_cliente_redis():
    if not Config.REDIS_URL:
        raise RuntimeError("REDIS_URL não está configurada no .env")

    return redis.Redis.from_url(
        Config.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3
    )


def listar_produtos_com_cache():
    try:
        cliente = criar_cliente_redis()
        dados_cache = cliente.get(CHAVE_CACHE_PRODUTOS)

        if dados_cache:
            print("CACHE HIT: produtos carregados do Redis")
            return json.loads(dados_cache)

    except Exception as erro:
        print(f"Redis indisponível; buscando no MongoDB: {erro}")

    print("CACHE MISS: produtos carregados do MongoDB")

    produtos = listar_produtos()
    produtos_catalogo = []

    for produto in produtos:
        categoria = produto.get("categoria", "")
        eh_docinho = categoria.strip().casefold() == "docinhos"

        produtos_catalogo.append({
            "_id": str(produto["_id"]),
            "nome": produto["nome"],
            "descricao": produto.get("descricao", ""),
            "categoria": categoria,
            "preco_formatado": f'{produto["preco"].to_decimal():.2f}',
            "imagem_url": produto.get("imagem_url", ""),
            "quantidade_minima": 25 if eh_docinho else 1,
            "incremento_quantidade": 1
        })

    try:
        cliente = criar_cliente_redis()
        cliente.set(
            CHAVE_CACHE_PRODUTOS,
            json.dumps(produtos_catalogo, ensure_ascii=False),
            ex=TEMPO_CACHE
        )
    except Exception as erro:
        print(f"Não foi possível salvar no Redis: {erro}")

    return produtos_catalogo


def invalidar_cache_produtos():
    try:
        cliente = criar_cliente_redis()
        cliente.delete(CHAVE_CACHE_PRODUTOS)
        print("Cache de produtos invalidado")
    except Exception as erro:
        print(f"Não foi possível limpar o cache: {erro}")