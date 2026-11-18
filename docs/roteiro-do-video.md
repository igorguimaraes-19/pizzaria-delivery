# Roteiro do vídeo narrado (até 5 minutos)

Dica: grave a tela do computador com a voz (Gravador do Windows com Win+G, QuickTime no Mac, ou OBS) e suba no YouTube como **não listado**. Antes de gravar, confira se as variáveis `HORARIO_ABERTURA` e `HORARIO_FECHAMENTO` estão configuradas no Render (veja `docs/publicar-no-render.md`), senão o sistema recusa pedidos fora das 18:00 às 23:30.

| Tempo | O que mostrar | O que falar (adapte com suas palavras) |
|-------|---------------|----------------------------------------|
| 0:00 | Tela do repositório no GitHub | "Meu nome é ___. Este é o meu projeto: um sistema de pedidos para pizzaria. O código está aberto no GitHub." |
| 0:30 | Pastas `app`, `docs`, `banco`, `tests` | "O back-end é em Python com Flask, no padrão MVC: models, controllers e templates. O banco é PostgreSQL." |
| 1:00 | `docs/banco-de-dados.md` com o diagrama | "Modelei o banco com 5 tabelas, normalizadas até a 3FN, e fiz o dicionário de dados." |
| 1:30 | Site publicado: cadastro e login | "Aqui o cliente se cadastra e entra." |
| 2:00 | Cardápio, filtro e carrinho | "Ele escolhe os itens por categoria e monta o carrinho." |
| 2:30 | Endereço e confirmação do pedido | "Cadastra o endereço, escolhe o pagamento e confirma. O sistema calcula o total com a taxa de entrega." |
| 3:00 | Meus pedidos e cancelamento | "O cliente acompanha o status e pode cancelar enquanto o pedido está recebido." |
| 3:30 | Painel do administrador | "A administração vê os pedidos do dia, avança o status e gerencia o cardápio." |
| 4:00 | Terminal ou GitHub com os testes (`58 passed`) | "Escrevi testes automatizados para as regras de negócio: horário, total, status e cancelamento." |
| 4:30 | Formulários dos testadores | "Cinco colegas testaram o sistema. Corrigi os problemas que encontraram e documentei no laudo." |

## Vídeo da solução atualizada (Situação 3)
Mostre, em até 5 minutos, **cada erro que os colegas encontraram**: o erro, a correção feita e o resultado funcionando agora.
