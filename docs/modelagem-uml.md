# Modelagem UML — Pizzaria Delivery

Os diagramas usam Mermaid e são renderizados automaticamente pelo GitHub.
Se o professor pedir imagens, abra este arquivo no GitHub, tire um print de cada diagrama e salve em `docs/img/`.

---

## 1. Diagrama de Casos de Uso

```mermaid
flowchart LR
    V([Visitante])
    C([Cliente])
    A([Administração])

    subgraph Sistema["Pizzaria Delivery"]
        UC01(UC01 Cadastrar-se)
        UC02(UC02 Fazer login)
        UC03(UC03 Consultar cardápio)
        UC04(UC04 Montar carrinho)
        UC05(UC05 Gerenciar endereços)
        UC06(UC06 Finalizar pedido)
        UC07(UC07 Acompanhar pedido)
        UC08(UC08 Listar meus pedidos)
        UC09(UC09 Cancelar pedido)
        UC10(UC10 Gerenciar cardápio)
        UC11(UC11 Listar pedidos)
        UC12(UC12 Atualizar status do pedido)
    end

    V --> UC01
    V --> UC02
    V --> UC03
    C --> UC02
    C --> UC03
    C --> UC04
    C --> UC05
    C --> UC06
    C --> UC07
    C --> UC08
    C --> UC09
    A --> UC02
    A --> UC09
    A --> UC10
    A --> UC11
    A --> UC12
    UC06 -. include .-> UC04
    UC06 -. include .-> UC05
```

### Caso de uso expandido — UC06 Finalizar pedido

| Item | Descrição |
|------|-----------|
| Ator | Cliente |
| Pré-condição | Cliente autenticado, com pelo menos um item no carrinho |
| Fluxo principal | 1. Cliente abre o carrinho e clica em "Finalizar". 2. Sistema mostra o resumo com itens, taxa e total. 3. Cliente escolhe o endereço de entrega. 4. Cliente escolhe a forma de pagamento. 5. Cliente confirma. 6. Sistema valida horário e disponibilidade dos itens. 7. Sistema grava o pedido com status RECEBIDO e esvazia o carrinho. 8. Sistema exibe a confirmação com o número do pedido. |
| Fluxo alternativo A | No passo 6, a pizzaria está fechada: o sistema informa o horário de funcionamento e mantém o carrinho. |
| Fluxo alternativo B | No passo 6, algum item está inativo: o sistema remove o item, avisa e pede nova confirmação. |
| Fluxo alternativo C | No passo 3, o cliente não tem endereço: o sistema abre o cadastro de endereço. |
| Pós-condição | Pedido e itens gravados; status RECEBIDO |
| Regras | RN01 a RN06 e RN10 |

---

## 2. Diagrama de Classes

```mermaid
classDiagram
    class Perfil {
        <<enumeration>>
        CLIENTE
        ADMIN
    }
    class CategoriaProduto {
        <<enumeration>>
        PIZZA
        BEBIDA
        SOBREMESA
        OUTROS
    }
    class StatusPedido {
        <<enumeration>>
        RECEBIDO
        EM_PREPARO
        SAIU_PARA_ENTREGA
        ENTREGUE
        CANCELADO
    }
    class FormaPagamento {
        <<enumeration>>
        DINHEIRO
        CARTAO
        PIX
    }

    class Usuario {
        -int idUsuario
        -String nome
        -String email
        -String telefone
        -String senhaHash
        -Perfil perfil
        +autenticar(senha) bool
    }
    class Endereco {
        -int idEndereco
        -String logradouro
        -String numero
        -String complemento
        -String bairro
        -String cidade
        -String cep
    }
    class Produto {
        -int idProduto
        -String nome
        -String descricao
        -CategoriaProduto categoria
        -decimal preco
        -bool ativo
    }
    class Pedido {
        -int idPedido
        -datetime dataHora
        -StatusPedido status
        -FormaPagamento formaPagamento
        -decimal taxaEntrega
        -decimal valorTotal
        -String observacao
        +calcularTotal() decimal
        +avancarStatus() void
        +cancelar() void
    }
    class ItemPedido {
        -int quantidade
        -decimal precoUnitario
        +calcularSubtotal() decimal
    }

    Usuario "1" --> "0..*" Endereco : possui
    Usuario "1" --> "0..*" Pedido : realiza
    Endereco "1" --> "0..*" Pedido : recebe
    Pedido "1" *-- "1..*" ItemPedido : é composto por
    Produto "1" --> "0..*" ItemPedido : é pedido em
    Usuario --> Perfil
    Produto --> CategoriaProduto
    Pedido --> StatusPedido
    Pedido --> FormaPagamento
```

---

## 3. Diagrama de Sequência — Finalizar pedido

```mermaid
sequenceDiagram
    actor C as Cliente
    participant V as View (HTML)
    participant K as Controller
    participant M as Model
    participant DB as PostgreSQL

    C->>V: Confirma endereço e forma de pagamento
    V->>K: POST /pedidos
    K->>K: Valida sessão e lê o carrinho da sessão
    K->>M: criar_pedido(usuario, endereco, pagamento, itens)
    M->>M: Valida horário, itens e endereço (RN01, RN02, RN04, RN10)
    M->>DB: SELECT produtos ativos e seus preços
    DB-->>M: produtos
    M->>DB: BEGIN
    M->>DB: INSERT pedido (status RECEBIDO)
    M->>DB: INSERT itens com preço unitário atual
    M->>DB: COMMIT
    alt Tudo válido
        M-->>K: pedido criado
        K->>K: Esvazia o carrinho
        K-->>V: Redireciona para Meus pedidos
        V-->>C: "Pedido nº X recebido!"
    else Fora do horário ou item inválido
        M-->>K: erro de validação
        K-->>V: Reexibe o carrinho com a mensagem
        V-->>C: Mensagem de erro
    end
```

---

## 4. Diagrama de Estados — Pedido

```mermaid
stateDiagram-v2
    [*] --> RECEBIDO : cliente finaliza o pedido
    RECEBIDO --> EM_PREPARO : admin inicia o preparo
    EM_PREPARO --> SAIU_PARA_ENTREGA : admin despacha
    SAIU_PARA_ENTREGA --> ENTREGUE : admin confirma entrega
    RECEBIDO --> CANCELADO : cliente ou admin cancela
    EM_PREPARO --> CANCELADO : somente admin cancela
    ENTREGUE --> [*]
    CANCELADO --> [*]
```

---

## 5. Mapa de navegação (apoio à IHC)

```mermaid
flowchart LR
    L[Login] --> CA[Cardápio]
    L --> R[Cadastro]
    R --> L
    CA --> CR[Carrinho]
    CR --> F[Finalizar pedido]
    F --> E[Meus endereços]
    F --> P[Meus pedidos]
    CA --> P
    L --> AP[Painel de pedidos - Admin]
    AP --> G[Gerenciar cardápio]
```
