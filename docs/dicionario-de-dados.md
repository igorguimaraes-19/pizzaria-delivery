# Dicionário de Dados — Pizzaria Delivery

Legenda: **PK** = chave primária, **FK** = chave estrangeira, **UK** = chave única, **AI** = identidade (`GENERATED ALWAYS AS IDENTITY`, auto incremento).

---

## Tabela `usuario`
Clientes e administração.

| Campo | Tipo | Nulo | Chave | Padrão | Descrição e domínio |
|-------|------|------|-------|--------|---------------------|
| id_usuario | INTEGER | Não | PK, AI | — | Identificador do usuário |
| nome | VARCHAR(100) | Não | — | — | Nome completo |
| email | VARCHAR(120) | Não | UK | — | E-mail usado no login; único no sistema |
| telefone | VARCHAR(20) | Não | — | — | Telefone com DDD |
| senha_hash | VARCHAR(255) | Não | — | — | Hash da senha; nunca a senha em texto |
| perfil | VARCHAR(10) | Não | — | CLIENTE | Domínio: `CLIENTE`, `ADMIN` |
| criado_em | TIMESTAMP | Não | — | CURRENT_TIMESTAMP | Data e hora do cadastro |

## Tabela `endereco`
Endereços de entrega cadastrados pelos clientes.

| Campo | Tipo | Nulo | Chave | Padrão | Descrição e domínio |
|-------|------|------|-------|--------|---------------------|
| id_endereco | INTEGER | Não | PK, AI | — | Identificador do endereço |
| id_usuario | INTEGER | Não | FK | — | Dono do endereço; referencia `usuario.id_usuario` |
| logradouro | VARCHAR(120) | Não | — | — | Rua, avenida etc. |
| numero | VARCHAR(10) | Não | — | — | Número (aceita "S/N") |
| complemento | VARCHAR(60) | Sim | — | — | Apartamento, bloco, referência |
| bairro | VARCHAR(60) | Não | — | — | Bairro |
| cidade | VARCHAR(60) | Não | — | — | Cidade |
| cep | CHAR(8) | Não | — | — | CEP com 8 dígitos numéricos, sem hífen |

## Tabela `produto`
Itens do cardápio.

| Campo | Tipo | Nulo | Chave | Padrão | Descrição e domínio |
|-------|------|------|-------|--------|---------------------|
| id_produto | INTEGER | Não | PK, AI | — | Identificador do produto |
| nome | VARCHAR(100) | Não | UK | — | Nome, incluindo o tamanho quando houver (ex.: "Pizza Calabresa (Grande)") |
| descricao | VARCHAR(255) | Sim | — | — | Ingredientes ou detalhes |
| categoria | VARCHAR(10) | Não | — | — | Domínio: `PIZZA`, `BEBIDA`, `SOBREMESA`, `OUTROS` |
| preco | NUMERIC(8,2) | Não | — | — | Preço atual em reais; maior que 0 |
| ativo | BOOLEAN | Não | — | TRUE | Domínio: `TRUE` disponível, `FALSE` indisponível |

## Tabela `pedido`
Pedidos feitos pelos clientes.

| Campo | Tipo | Nulo | Chave | Padrão | Descrição e domínio |
|-------|------|------|-------|--------|---------------------|
| id_pedido | INTEGER | Não | PK, AI | — | Número do pedido |
| id_usuario | INTEGER | Não | FK | — | Cliente; referencia `usuario.id_usuario` |
| id_endereco | INTEGER | Não | FK | — | Endereço de entrega; referencia `endereco.id_endereco` |
| data_hora | TIMESTAMP | Não | — | CURRENT_TIMESTAMP | Momento em que o pedido foi feito |
| status | VARCHAR(20) | Não | — | RECEBIDO | Domínio: `RECEBIDO`, `EM_PREPARO`, `SAIU_PARA_ENTREGA`, `ENTREGUE`, `CANCELADO` |
| forma_pagamento | VARCHAR(10) | Não | — | — | Domínio: `DINHEIRO`, `CARTAO`, `PIX` |
| taxa_entrega | NUMERIC(6,2) | Não | — | 0 | Taxa cobrada; maior ou igual a 0 |
| valor_total | NUMERIC(8,2) | Não | — | — | Soma dos itens + taxa, gravada no momento do pedido |
| observacao | VARCHAR(255) | Sim | — | — | Observações do cliente (ex.: "sem cebola") |

## Tabela `item_pedido`
Itens de cada pedido (relação N:N entre pedido e produto).

| Campo | Tipo | Nulo | Chave | Padrão | Descrição e domínio |
|-------|------|------|-------|--------|---------------------|
| id_pedido | INTEGER | Não | PK, FK | — | Referencia `pedido.id_pedido` |
| id_produto | INTEGER | Não | PK, FK | — | Referencia `produto.id_produto` |
| quantidade | SMALLINT | Não | — | — | Entre 1 e 20 |
| preco_unitario | NUMERIC(8,2) | Não | — | — | Preço cobrado por unidade na compra; maior que 0 |

---

## Resumo das restrições

| Restrição | Tabela | Regra |
|-----------|--------|-------|
| uq_usuario_email | usuario | E-mail único (RN09) |
| ck_usuario_perfil | usuario | Perfil em `CLIENTE`, `ADMIN` |
| ck_endereco_cep | endereco | CEP com exatamente 8 dígitos |
| uq_produto_nome | produto | Nome único |
| ck_produto_categoria | produto | Categoria dentro do domínio |
| ck_produto_preco | produto | Preço maior que 0 |
| ck_pedido_status | pedido | Status dentro do domínio (RN07) |
| ck_pedido_pagamento | pedido | Forma de pagamento dentro do domínio |
| ck_pedido_taxa / ck_pedido_total | pedido | Valores não negativos |
| pk_item_pedido | item_pedido | Mesmo produto não se repete no pedido |
| ck_item_quantidade | item_pedido | Quantidade entre 1 e 20 (RN01) |
| ck_item_preco | item_pedido | Preço unitário maior que 0 |
| fk_* | várias | Integridade referencial entre as tabelas |

## Regras que ficam na aplicação (Model)
Algumas regras não cabem em restrições de coluna e são validadas no código e cobertas por testes: horário de funcionamento (RN02), pedido com pelo menos um item (RN01), cálculo do total (RN05), sequência de status (RN07), cancelamento conforme o perfil (RN08) e endereço pertencente ao cliente (RN10).
