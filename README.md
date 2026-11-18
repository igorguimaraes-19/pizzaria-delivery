# Pizzaria Delivery — Sistema de pedidos online

Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II) — Cruzeiro do Sul Virtual

- **Autor:** Igor Lima Guimarães
- **RGM:** 32906072
- **Back-end:** Python 3 + Flask (padrão MVC)
- **Banco de dados:** PostgreSQL 14+
- **Hospedagem:** Render (aplicação) e Render Postgres (banco)
- **Front-end:** HTML5, CSS3 e JavaScript

> "Pizzaria Delivery" é o nome provisório. Troque pelo nome do seu projeto do PIT I, se houver.

---

## 1. Escopo

### 1.1 Problema
Pizzarias pequenas recebem pedidos por telefone e WhatsApp. Isso gera erros de anotação, pedidos perdidos, dificuldade de acompanhar o que está em preparo e nenhum histórico organizado de pedidos e vendas.

### 1.2 Solução
Aplicação web em que o **cliente** consulta o cardápio, monta o pedido, informa o endereço e acompanha o andamento. A **administração** da pizzaria gerencia o cardápio e atualiza o status dos pedidos.

### 1.3 Dentro do escopo (versão atual)
- Cadastro e login de clientes
- Cardápio por categoria (pizzas, bebidas, sobremesas)
- Carrinho de compras e finalização do pedido
- Endereços de entrega do cliente
- Acompanhamento e cancelamento de pedidos
- Gestão do cardápio e dos pedidos pela administração

### 1.4 Fora do escopo (melhoria contínua / versões futuras)
Pagamento online, rastreamento do entregador em mapa, cupons de desconto, pizza meio a meio, avaliações e aplicativo mobile nativo.

### 1.5 Ajustes feitos nesta revisão (Kaizen)
_(Ajuste esta seção com o que mudou em relação ao PIT I.)_
- Escopo organizado em torno do fluxo principal: cardápio → carrinho → pedido → acompanhamento.
- Modelagem de dados normalizada até a 3FN, com tabela de endereços separada.
- Preço do produto gravado em cada item do pedido, para preservar o histórico quando o cardápio mudar.
- Status do pedido com sequência controlada (diagrama de estados).

---

## 2. Requisitos

### 2.1 Requisitos funcionais

| ID | Requisito | Ator |
|----|-----------|------|
| RF01 | Cadastrar-se informando nome, e-mail, telefone e senha | Cliente |
| RF02 | Entrar e sair do sistema (login/logout) | Cliente, Admin |
| RF03 | Cadastrar, editar, listar e inativar produtos do cardápio | Admin |
| RF04 | Consultar o cardápio filtrando por categoria | Cliente |
| RF05 | Adicionar, alterar a quantidade e remover itens do carrinho | Cliente |
| RF06 | Cadastrar e escolher endereços de entrega | Cliente |
| RF07 | Finalizar o pedido escolhendo endereço e forma de pagamento | Cliente |
| RF08 | Acompanhar o status do pedido | Cliente |
| RF09 | Listar o histórico dos próprios pedidos | Cliente |
| RF10 | Cancelar um pedido que ainda não entrou em preparo | Cliente |
| RF11 | Listar pedidos filtrando por data e status | Admin |
| RF12 | Atualizar o status do pedido | Admin |

### 2.2 Requisitos não funcionais

| ID | Requisito |
|----|-----------|
| RNF01 | **Usabilidade:** interface clara, simples e consistente, com feedback imediato (seção 4) |
| RNF02 | **Segurança:** senhas armazenadas com hash (`werkzeug.security`); rotas protegidas por sessão e perfil |
| RNF03 | **Compatibilidade:** layout responsivo (celular e desktop) |
| RNF04 | **Manutenibilidade:** código separado em Model, View e Controller |
| RNF05 | **Confiabilidade:** erros tratados com mensagens claras, sem expor detalhes técnicos |
| RNF06 | **Testabilidade:** regras de negócio cobertas por testes unitários (pytest) |
| RNF07 | **Portabilidade:** SGBD popular (PostgreSQL) com script de criação versionado |

### 2.3 Regras de negócio

| ID | Regra |
|----|-------|
| RN01 | Todo pedido deve ter pelo menos 1 item, com quantidade entre 1 e 20 |
| RN02 | Pedidos só são aceitos entre 18:00 e 23:30, todos os dias (configurável pelas variáveis `HORARIO_ABERTURA` e `HORARIO_FECHAMENTO`) |
| RN03 | A taxa de entrega é um valor fixo configurável (padrão: R$ 6,00) |
| RN04 | Produto inativo não pode ser adicionado ao pedido |
| RN05 | Valor total = soma de (quantidade × preço unitário) dos itens + taxa de entrega |
| RN06 | O preço de cada item é gravado no pedido no momento da compra |
| RN07 | O status segue a sequência RECEBIDO → EM_PREPARO → SAIU_PARA_ENTREGA → ENTREGUE |
| RN08 | O cliente só cancela enquanto o pedido está RECEBIDO; a administração cancela em RECEBIDO ou EM_PREPARO |
| RN09 | E-mail é único no sistema |
| RN10 | O endereço de entrega deve pertencer ao cliente que fez o pedido |

---

## 3. Modelagem

- Diagramas UML (casos de uso, classes, sequência e estados): [`docs/modelagem-uml.md`](docs/modelagem-uml.md)
- Projeto conceitual, lógico normalizado e físico: [`docs/banco-de-dados.md`](docs/banco-de-dados.md)
- Dicionário de dados: [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md)
- Script do banco: [`banco/schema.sql`](banco/schema.sql)

---

## 4. Interface Humano-Computador (IHC)

### 4.1 Telas

| Nº | Tela | Perfil |
|----|------|--------|
| T01 | Login | Todos |
| T02 | Cadastro de cliente | Visitante |
| T03 | Cardápio (com filtro por categoria) | Cliente |
| T04 | Carrinho | Cliente |
| T05 | Finalizar pedido (endereço e pagamento) | Cliente |
| T06 | Meus pedidos e acompanhamento | Cliente |
| T07 | Meus endereços | Cliente |
| T08 | Painel de pedidos | Admin |
| T09 | Gerenciar cardápio | Admin |

### 4.2 Princípios aplicados
- **Clareza:** rótulos diretos ("Adicionar ao carrinho", "Confirmar pedido").
- **Consistência:** mesmo menu, cores e botões em todas as telas.
- **Simplicidade:** finalização em um único passo, com endereço e pagamento já sugeridos.
- **Controle do usuário:** o cliente edita o carrinho livremente antes de confirmar.
- **Feedback:** contador do carrinho sempre visível e mensagens de sucesso e erro em toda ação.
- **Reversibilidade:** itens podem ser removidos e o pedido pode ser cancelado enquanto recebido.
- **Visibilidade do estado:** o status do pedido aparece de forma destacada.

### 4.3 Mensagens do sistema

| Situação | Mensagem |
|----------|----------|
| E-mail repetido no cadastro | "Este e-mail já está cadastrado. Tente entrar ou use outro e-mail." |
| Login inválido | "E-mail ou senha incorretos." |
| Campo obrigatório vazio | "Preencha o campo [nome do campo]." |
| Carrinho vazio ao finalizar | "Seu carrinho está vazio. Adicione pelo menos um item." |
| Fora do horário | "Estamos fechados agora. Recebemos pedidos das 18:00 às 23:30." |
| Produto indisponível | "O item [nome] não está mais disponível e foi removido do carrinho." |
| Endereço não selecionado | "Escolha um endereço de entrega." |
| CEP inválido | "Informe um CEP com 8 números." |
| Pedido criado | "Pedido nº [número] recebido! Acompanhe o andamento em Meus pedidos." |
| Cancelamento fora do prazo | "Este pedido já está em preparo e não pode mais ser cancelado. Entre em contato com a pizzaria." |
| Pedido cancelado | "Pedido cancelado com sucesso." |
| Acesso sem permissão | "Você não tem permissão para acessar esta página." |
| Erro inesperado | "Algo deu errado. Tente novamente em instantes." |

---

## 5. Arquitetura (MVC)

```
pizzaria-delivery/
├── app/
│   ├── __init__.py          # cria a aplicação Flask
│   ├── regras.py            # regras de negócio puras (RN01 a RN10)
│   ├── db.py                # conexão com o PostgreSQL
│   ├── models/              # Model: usuario, endereco, produto, pedido
│   ├── controllers/         # Controller: auth, cardapio, pedidos, admin
│   ├── templates/           # View: HTML (Jinja2)
│   └── static/              # CSS
├── banco/
│   ├── schema.sql
│   └── dados_exemplo.sql
├── docs/
├── tests/                   # testes unitários e de integração (pytest)
├── config.py
├── requirements.txt
└── run.py
```

Fluxo: **Usuário → Rota (Controller) → Model ↔ PostgreSQL → View (HTML) → Usuário**.

### Como o sistema inicia
Na primeira execução, `app/db.py` cria as tabelas, carrega o cardápio de exemplo e cria a conta de administração (variáveis `ADMIN_EMAIL` e `ADMIN_SENHA`). Assim funciona no plano grátis do Render, que não tem terminal.

O carrinho fica na sessão do Flask (não precisa de tabela); só vira dado persistente quando o pedido é finalizado.

---

## 6. Como executar

**Publicado na internet (recomendado):** siga [`docs/publicar-no-render.md`](docs/publicar-no-render.md).

**No seu computador** (precisa de Python 3.12 e PostgreSQL instalados):
```bash
python -m venv venv
venv\Scripts\activate        # Windows  |  no Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
set DATABASE_URL=postgresql://usuario:senha@localhost:5432/pizzaria   # Windows | no Mac/Linux: export ...
python run.py
```
Abra http://127.0.0.1:5000. Administrador padrão: `admin@pizzaria.com` / `admin123` (troque em produção com `ADMIN_EMAIL` e `ADMIN_SENHA`).

**Testes:** veja [`docs/plano-de-testes.md`](docs/plano-de-testes.md).

---

## 7. Organização do repositório Git

| Pasta | Conteúdo | Situação |
|-------|----------|----------|
| `docs/` | Documentação, UML, banco, dicionário, plano de testes, roteiro do vídeo e laudo | 1, 2 e 3 |
| `banco/` | Scripts SQL | 1 |
| `app/` | Código-fonte (front-end e back-end) | 2 |
| `tests/` | Testes automatizados | 2 e 3 |
| `docs/testes-usuarios/` | Formulários dos 5 testadores e evidências | 3 |
