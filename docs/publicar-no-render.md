# Como publicar o sistema no Render (passo a passo)

Os nomes dos botões podem variar um pouco, mas o caminho é este. Tempo estimado: 20 a 30 minutos.

## Antes de começar
- O repositório no GitHub precisa conter a pasta `app/` e os arquivos `run.py`, `config.py` e `requirements.txt` **na raiz** (não dentro de outra pasta).
- Você precisa estar logado no Render com a conta do GitHub.

## Passo 1 — Criar o banco de dados
1. No painel do Render, clique em **New +** e depois em **PostgreSQL**.
2. **Name:** `pizzaria-db`. Deixe o restante como está e escolha o plano **Free**.
3. Clique em **Create Database** e espere o status ficar **Available**.
4. Na página do banco, procure **Internal Database URL** e clique em copiar. Guarde esse texto.

## Passo 2 — Criar o serviço web
1. Clique em **New +** e depois em **Web Service**.
2. Escolha o repositório `pizzaria-delivery` (se não aparecer, clique em configurar o acesso do GitHub e autorize o repositório).
3. Preencha:
   - **Name:** `pizzaria-delivery`
   - **Language:** Python 3
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
   - **Instance Type:** Free

## Passo 3 — Variáveis de ambiente
Na seção **Environment Variables**, adicione:

| Nome | Valor |
|------|-------|
| `DATABASE_URL` | a Internal Database URL copiada no passo 1 |
| `SECRET_KEY` | uma frase longa e aleatória (ex.: `pizza-rapida-2026-trocar-por-algo-seu-8f3k2`) |
| `ADMIN_EMAIL` | o e-mail que você quer usar como administrador |
| `ADMIN_SENHA` | uma senha sua para o administrador (mínimo 6 caracteres) |
| `PYTHON_VERSION` | `3.12.8` |
| `HORARIO_ABERTURA` | `00:00` (só durante os testes e a gravação do vídeo; o padrão do sistema é `18:00`) |
| `HORARIO_FECHAMENTO` | `23:59` (idem; o padrão é `23:30`) |

## Passo 4 — Publicar
1. Clique em **Create Web Service** e acompanhe o log. Na primeira vez leva alguns minutos.
2. Quando aparecer "Your service is live", clique no endereço no topo da página (algo como `https://pizzaria-delivery-xxxx.onrender.com`). **Esse é o link da solução em funcionamento.**
3. No primeiro acesso, o sistema cria sozinho as tabelas, o cardápio de exemplo e a conta de administrador.

## Passo 5 — Conferir
1. Abra o link e veja o cardápio.
2. Entre com `ADMIN_EMAIL` e `ADMIN_SENHA` e confira o painel de pedidos.
3. Faça um cadastro de cliente, cadastre um endereço e faça um pedido de teste.
4. Atenção ao horário: por padrão o sistema só aceita pedidos das **18:00 às 23:30** (horário de Brasília) e, fora disso, mostra "Estamos fechados agora". Por isso, durante os testes dos colegas e a gravação do vídeo, use as variáveis `HORARIO_ABERTURA=00:00` e `HORARIO_FECHAMENTO=23:59` (o Render reinicia o serviço sozinho ao salvar). Depois da entrega você pode apagá-las para voltar ao horário real.

## Cuidados do plano grátis
- Depois de 15 minutos sem acesso, o site "dorme". O primeiro acesso seguinte demora cerca de 1 minuto. Avise os testadores.
- O banco grátis expira 30 dias depois de criado. Guarde os prints e o vídeo.

## Se der erro
- **Build falhou:** abra o log e veja a última linha vermelha. Confira se `requirements.txt` está na raiz do repositório.
- **Application error ao abrir o site:** confira se `DATABASE_URL` foi colada inteira e se o banco está **Available**.
