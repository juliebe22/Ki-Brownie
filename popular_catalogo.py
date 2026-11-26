from services.cache_produtos import invalidar_cache_produtos
from services.mongo_produtos import criar_produto, listar_produtos

# Produtos com preços já informados.
# Cada tamanho ou sabor é cadastrado como um produto separado.
produtos = [
    # Empadão
    ("Empadão de frango com requeijão — P",
     "Serve aproximadamente 10 a 12 pessoas.",
     "Empadão", 110.00),
    ("Empadão de frango com requeijão — M",
     "Serve aproximadamente 16 a 18 pessoas.",
     "Empadão", 160.00),
    ("Empadão de frango com requeijão — G",
     "Serve aproximadamente 24 a 26 pessoas.",
     "Empadão", 220.00),

    # Tranças
    ("Trança de frango — M", "Tamanho médio.", "Tranças", 95.00),
    ("Trança de frango — G", "Tamanho grande.", "Tranças", 130.00),
    ("Trança de carne de sol — M", "Tamanho médio.", "Tranças", 130.00),
    ("Trança de carne de sol — G", "Tamanho grande.", "Tranças", 160.00),
    ("Trança de queijo e presunto — M", "Tamanho médio.", "Tranças", 120.00),
    ("Trança de queijo e presunto — G", "Tamanho grande.", "Tranças", 150.00),
    ("Trança de calabresa com queijo — M", "Tamanho médio.", "Tranças", 95.00),
    ("Trança de calabresa com queijo — G", "Tamanho grande.", "Tranças", 130.00),

    # Fofão
    ("Fofão — P", "Serve aproximadamente 10 fatias.", "Bolos", 90.00),
    ("Fofão — M", "Serve aproximadamente 15 fatias.", "Bolos", 140.00),
    ("Fofão — G", "Serve aproximadamente 25 fatias.", "Bolos", 200.00),
    ("Fofão — GG", "Serve aproximadamente 35 fatias.", "Bolos", 280.00),

    # Sobremesas: pavê
    ("Pavê — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 70.00),
    ("Pavê — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 140.00),
    ("Pavê — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 190.00),

    # Sobremesas: brownie com morangos
    ("Brownie com morangos — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 90.00),
    ("Brownie com morangos — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 140.00),
    ("Brownie com morangos — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 210.00),

    # Torta de brownie
    ("Torta de brownie — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Tortas", 180.00),

    # Mousse de chocolate
    ("Mousse de chocolate ao leite — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 90.00),
    ("Mousse de chocolate ao leite — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 140.00),
    ("Mousse de chocolate ao leite — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 210.00),
    ("Mousse de chocolate branco — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 90.00),
    ("Mousse de chocolate branco — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 140.00),
    ("Mousse de chocolate branco — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 210.00),
    ("Mousse de chocolate meio amargo — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 90.00),
    ("Mousse de chocolate meio amargo — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 140.00),
    ("Mousse de chocolate meio amargo — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 210.00),

    # Mousse de limão com chocolate
    ("Mousse de limão com chocolate — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 50.00),
    ("Mousse de limão com chocolate — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 90.00),
    ("Mousse de limão com chocolate — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 170.00),

    # Mousse de maracujá com chocolate
    ("Mousse de maracujá com chocolate — 8 pessoas", "Porção para aproximadamente 8 pessoas.", "Sobremesas", 60.00),
    ("Mousse de maracujá com chocolate — 15 pessoas", "Porção para aproximadamente 15 pessoas.", "Sobremesas", 100.00),
    ("Mousse de maracujá com chocolate — 25 pessoas", "Porção para aproximadamente 25 pessoas.", "Sobremesas", 180.00),

    # Outros
    ("Brownie recheado — unidade", "Preço por unidade.", "Brownie", 8.00),
    ("Bem-casado — unidade", "Preço por unidade. Encomenda mínima: 10 unidades.", "Bem-casados", 7.00),
    ("Cupcake — unidade", "Preço por unidade. Encomenda mínima: 8 unidades.", "Cupcakes", 7.50),

    # Bolo vulcão
    ("Bolo vulcão — 16 cm", "Serve aproximadamente 6 a 8 fatias.", "Bolos", 50.00),
    ("Bolo vulcão — 18 cm", "Serve aproximadamente 10 a 12 fatias.", "Bolos", 80.00),
    ("Bolo vulcão — 20 cm", "Serve aproximadamente 14 a 16 fatias.", "Bolos", 90.00),
    ("Bolo vulcão — 22 cm", "Serve aproximadamente 18 a 20 fatias.", "Bolos", 110.00),
    ("Bolo vulcão — 24 cm", "Serve aproximadamente 22 a 24 fatias.", "Bolos", 130.00),
    ("Bolo vulcão — 26 cm", "Serve aproximadamente 26 a 28 fatias.", "Bolos", 160.00),

        # Docinhos — preços por unidade; encomenda mínima de 25 unidades
    ("Docinhos tradicionais", "Docinhos tradicionais de 18 g. Encomenda mínima: 25 unidades.", "Docinhos", 1.70),
    ("Docinhos tradicionais personalizados", "Docinhos tradicionais personalizados de 18 g. Encomenda mínima: 25 unidades.", "Docinhos", 1.90),
    ("Docinhos especiais", "Docinhos especiais de 18 g. Encomenda mínima: 25 unidades.", "Docinhos", 1.90),
    ("Docinhos especiais personalizados", "Docinhos especiais personalizados de 18 g. Encomenda mínima: 25 unidades.", "Docinhos", 2.10),
]

# Busca os produtos já cadastrados para não inserir duplicados.
existentes = listar_produtos(apenas_ativos=False)
nomes_existentes = {produto["nome"].strip().casefold() for produto in existentes}

inseridos = 0
ignorados = 0

for nome, descricao, categoria, preco in produtos:
    if nome.strip().casefold() in nomes_existentes:
        print(f"Já existe, pulando: {nome}")
        ignorados += 1
        continue

    criar_produto(
        nome=nome,
        descricao=descricao,
        categoria=categoria,
        preco=preco,
    )

    print(f"Cadastrado: {nome}")
    inseridos += 1

if inseridos > 0:
    invalidar_cache_produtos()

print("\nCadastro finalizado!")
print(f"Novos produtos: {inseridos}")
print(f"Já existentes: {ignorados}")