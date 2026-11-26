
# 🍫 Ki-Brownie

### Um cantinho doce para encomendar momentos especiais.

O **Ki-Brownie** é uma aplicação web de catálogo e gerenciamento de encomendas para uma confeitaria. O projeto foi desenvolvido para facilitar a visualização dos produtos, a montagem dos pedidos e a administração do catálogo, com uma experiência delicada e acolhedora.

---

## 🧁 Sobre o projeto

A plataforma permite que os clientes explorem os produtos da confeitaria, escolham suas opções e organizem os itens em um carrinho antes de solicitar a encomenda pelo WhatsApp.

O sistema trabalha com **produtos feitos sob encomenda**, com opções de **entrega ou retirada**. A aplicação também conta com uma área administrativa para gerenciar os produtos do catálogo.

## 🎥 Vídeo de demonstração

Assista à demonstração do sistema para conhecer suas principais funcionalidades e a experiência de navegação.

**Link do vídeo:** [Inserir link do vídeo de demonstração aqui](COLE_O_LINK_DO_VIDEO_AQUI)

## 🌐 Link do site publicado

https://ki-brownie.onrender.com

## ✨ Funcionalidades

### Para os clientes
- Visualização do catálogo de produtos por categoria.
- Consulta de informações e preços dos produtos.
- Seleção de quantidades e opções disponíveis para cada produto.
- Carrinho para organizar os itens da encomenda.
- Solicitação do pedido pelo WhatsApp.
- Opções de entrega ou retirada.

### Para a administração
- Acesso à área administrativa com autenticação.
- Cadastro, edição e gerenciamento dos produtos do catálogo.
- Organização dos produtos por categoria.
- Armazenamento dos dados dos produtos e pedidos.

## 🍰 Categorias do catálogo

- Bolos
- Docinhos
- Brownies
- Cupcakes
- Tortas
- Pães e salgados

As opções e quantidades mínimas podem variar conforme o produto, respeitando as especificações de cada encomenda.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação no projeto |
|---|---|
| Python | Linguagem principal da aplicação |
| Flask | Desenvolvimento da aplicação web e das rotas |
| MongoDB Atlas | Banco de dados para produtos e pedidos |
| Supabase Auth | Autenticação da área administrativa |
| Redis | Cache para otimizar o acesso aos dados do catálogo |
| HTML e CSS | Estrutura e apresentação das páginas |
| JavaScript | Interações da interface |

## 🗂️ Estrutura do projeto

```text
Ki-Brownie/
├── app.py
├── config.py
├── popular_catalogo.py
├── requirements.txt
├── package.json
├── package-lock.json
├── services/
│   ├── cache_produtos.py
│   ├── mongo_pedidos.py
│   ├── mongo_produtos.py
│   └── supabase_auth.py
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
└── templates/
    ├── admin.html
    ├── base.html
    ├── carrinho.html
    ├── catalogo.html
    ├── editar_produto.html
    ├── index.html
    ├── login.html
    └── produtos_admin.html
```

## 🚀 Como executar localmente

### Pré-requisitos

- Python instalado
- Acesso a uma instância MongoDB
- Credenciais configuradas para os serviços utilizados pelo projeto

### Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/juliebe22/Ki-Brownie.git
   ```

2. Entre na pasta do projeto:

   ```bash
   cd Ki-Brownie
   ```

3. Crie e ative um ambiente virtual:

   **Windows (PowerShell):**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **Linux ou macOS:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

5. Configure as variáveis de ambiente seguindo o arquivo `.env.example`. Use suas próprias credenciais e mantenha o arquivo `.env` fora do repositório.

6. Inicie a aplicação:

   ```bash
   python app.py
   ```

Acesse o endereço local indicado pelo Flask no terminal.

## 🔐 Configuração e segurança

As credenciais e configurações sensíveis devem ser armazenadas em variáveis de ambiente no arquivo `.env`, que não deve ser enviado ao GitHub. O arquivo `.env.example` serve como referência para a configuração do ambiente.

## 🎯 Objetivo

O Ki-Brownie busca reunir, em uma única aplicação, a apresentação dos produtos, a organização das encomendas e o gerenciamento do catálogo da confeitaria, utilizando tecnologias de desenvolvimento web e serviços de banco de dados, autenticação e cache.


