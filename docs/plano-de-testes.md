# Plano de Testes — Pizzaria Delivery

## 1. Estratégia (Modelo V)

| Etapa de desenvolvimento (verificação) | Teste correspondente (validação) | Como foi feito |
|----------------------------------------|----------------------------------|----------------|
| Requisitos e regras de negócio | Teste de aceitação | 5 testadores externos usando o formulário de `docs/testes-usuarios/` |
| Análise e UML | Teste de sistema | Roteiro manual de ponta a ponta (seção 4) |
| Arquitetura (MVC) | Teste de integração | `tests/test_integracao.py` (rotas + PostgreSQL) |
| Código | Teste unitário | `tests/test_regras.py` (regras de negócio isoladas) |

Verificação também inclui revisão do código e conferência das regras do README contra as funções de `app/regras.py`.

## 2. Como executar os testes automatizados

```bash
pip install -r requirements.txt

# Testes unitários (não precisam de banco)
pytest

# Testes unitários + integração (precisam de um banco PostgreSQL VAZIO de testes)
DATABASE_URL_TESTE=postgresql://usuario:senha@localhost:5432/pizzaria_teste pytest
```

Os testes de integração apagam e recriam as tabelas do banco informado. **Nunca aponte para o banco de produção.**

## 3. Resultado da última execução

| Suíte | Testes | Resultado |
|-------|--------|-----------|
| Unitários (`test_regras.py`) | 39 | Todos passaram |
| Integração (`test_integracao.py`) | 19 | Todos passaram |
| **Total** | **58** | **58 aprovados, 0 falhas** |

## 4. Cobertura por regra de negócio

| Regra | Teste |
|-------|-------|
| RN01 quantidade e carrinho vazio | `test_quantidade_*`, `test_pedido_com_carrinho_vazio`, `test_quantidade_acima_do_limite_e_recusada` |
| RN02 horário de funcionamento | `test_horario_de_funcionamento`, `test_pedido_fora_do_horario` |
| RN04 produto inativo | `test_produto_inativo_nao_pode_ser_pedido` |
| RN05 cálculo do total | `test_total_*`, `test_pedido_completo` |
| RN06 preço gravado no item | `test_preco_do_item_nao_muda_quando_o_cardapio_muda` |
| RN07 sequência de status | `test_sequencia_de_status`, `test_sequencia_completa_de_status` |
| RN08 cancelamento | `test_quem_pode_cancelar`, `test_cliente_cancela_*`, `test_cliente_nao_cancela_*`, `test_admin_cancela_*` |
| RN09 e-mail único | `test_cadastro_e_email_duplicado` |
| RN10 endereço do cliente | `test_endereco_de_outro_cliente_e_recusado` |
| Segurança (RNF02) | `test_senha_fica_com_hash`, `test_rotas_protegidas`, `test_cliente_nao_acessa_pedido_de_outro` |

## 5. Roteiro manual de ponta a ponta (teste de sistema)

| Nº | Passo | Resultado esperado |
|----|-------|--------------------|
| 0 | Confirmar que a pizzaria está aberta (ou ajustar `HORARIO_ABERTURA`/`HORARIO_FECHAMENTO`) | Cardápio sem o aviso "Estamos fechados" |
| 1 | Cadastrar um cliente | Redireciona para o login com mensagem de sucesso |
| 2 | Tentar cadastrar o mesmo e-mail | Mensagem "Este e-mail já está cadastrado..." |
| 3 | Entrar com senha errada | Mensagem "E-mail ou senha incorretos." |
| 4 | Entrar com os dados corretos | Cardápio aparece e o menu mostra "Sair (nome)" |
| 5 | Filtrar o cardápio por categoria | Só os itens da categoria aparecem |
| 6 | Adicionar 2 pizzas e 1 bebida | Contador do carrinho mostra 3 |
| 7 | Alterar a quantidade e remover um item | Totais atualizam |
| 8 | Finalizar sem endereço | Pede o cadastro de endereço |
| 9 | Cadastrar endereço com CEP inválido | Mensagem "Informe um CEP com 8 números." |
| 10 | Cadastrar endereço válido e confirmar o pedido | Mensagem "Pedido nº X recebido!" |
| 11 | Abrir Meus pedidos | Pedido aparece como "Recebido" |
| 12 | Entrar como administrador e avançar o status | Cliente vê o novo status |
| 13 | Cliente tenta cancelar pedido "Em preparo" | Mensagem de que não pode mais cancelar |
| 14 | Administrador cria, edita e inativa um produto | Cardápio do cliente reflete a mudança |

## 6. Registro de erros encontrados e correções (alimenta o Laudo de Qualidade)

_Preencha durante os testes dos colegas. Anexe um print de cada erro em `docs/testes-usuarios/evidencias/`._

| Nº | Erro encontrado | Quem encontrou | Evidência | Correção feita | Situação |
|----|-----------------|----------------|-----------|----------------|----------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
