-- =====================================================================
-- Pizzaria Delivery — Projeto físico do banco de dados (PostgreSQL 14+)
-- Execute com o banco já criado (no Render, o banco é criado pelo painel).
-- =====================================================================

-- Ordem inversa para permitir recriar as tabelas em desenvolvimento
DROP TABLE IF EXISTS item_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS endereco;
DROP TABLE IF EXISTS usuario;

-- ---------------------------------------------------------------------
-- USUARIO: clientes e administração
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario   INTEGER      GENERATED ALWAYS AS IDENTITY,
    nome         VARCHAR(100) NOT NULL,
    email        VARCHAR(120) NOT NULL,
    telefone     VARCHAR(20)  NOT NULL,
    senha_hash   VARCHAR(255) NOT NULL,
    perfil       VARCHAR(10)  NOT NULL DEFAULT 'CLIENTE',
    criado_em    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_usuario        PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_email  UNIQUE (email),
    CONSTRAINT ck_usuario_perfil CHECK (perfil IN ('CLIENTE', 'ADMIN'))
);

-- ---------------------------------------------------------------------
-- ENDERECO: endereços de entrega de cada cliente
-- ---------------------------------------------------------------------
CREATE TABLE endereco (
    id_endereco  INTEGER      GENERATED ALWAYS AS IDENTITY,
    id_usuario   INTEGER      NOT NULL,
    logradouro   VARCHAR(120) NOT NULL,
    numero       VARCHAR(10)  NOT NULL,
    complemento  VARCHAR(60),
    bairro       VARCHAR(60)  NOT NULL,
    cidade       VARCHAR(60)  NOT NULL,
    cep          CHAR(8)      NOT NULL,
    CONSTRAINT pk_endereco PRIMARY KEY (id_endereco),
    CONSTRAINT fk_endereco_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    CONSTRAINT ck_endereco_cep CHECK (cep ~ '^[0-9]{8}$')
);

-- ---------------------------------------------------------------------
-- PRODUTO: itens do cardápio
-- ---------------------------------------------------------------------
CREATE TABLE produto (
    id_produto  INTEGER       GENERATED ALWAYS AS IDENTITY,
    nome        VARCHAR(100)  NOT NULL,
    descricao   VARCHAR(255),
    categoria   VARCHAR(10)   NOT NULL,
    preco       NUMERIC(8,2)  NOT NULL,
    ativo       BOOLEAN       NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_produto PRIMARY KEY (id_produto),
    CONSTRAINT uq_produto_nome UNIQUE (nome),
    CONSTRAINT ck_produto_categoria CHECK (categoria IN ('PIZZA', 'BEBIDA', 'SOBREMESA', 'OUTROS')),
    CONSTRAINT ck_produto_preco CHECK (preco > 0)
);

-- ---------------------------------------------------------------------
-- PEDIDO
-- ---------------------------------------------------------------------
CREATE TABLE pedido (
    id_pedido       INTEGER       GENERATED ALWAYS AS IDENTITY,
    id_usuario      INTEGER       NOT NULL,
    id_endereco     INTEGER       NOT NULL,
    data_hora       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          VARCHAR(20)   NOT NULL DEFAULT 'RECEBIDO',
    forma_pagamento VARCHAR(10)   NOT NULL,
    taxa_entrega    NUMERIC(6,2)  NOT NULL DEFAULT 0,
    valor_total     NUMERIC(8,2)  NOT NULL,
    observacao      VARCHAR(255),
    CONSTRAINT pk_pedido PRIMARY KEY (id_pedido),
    CONSTRAINT fk_pedido_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario),
    CONSTRAINT fk_pedido_endereco FOREIGN KEY (id_endereco)
        REFERENCES endereco (id_endereco),
    CONSTRAINT ck_pedido_status CHECK (status IN
        ('RECEBIDO', 'EM_PREPARO', 'SAIU_PARA_ENTREGA', 'ENTREGUE', 'CANCELADO')),
    CONSTRAINT ck_pedido_pagamento CHECK (forma_pagamento IN ('DINHEIRO', 'CARTAO', 'PIX')),
    CONSTRAINT ck_pedido_taxa CHECK (taxa_entrega >= 0),
    CONSTRAINT ck_pedido_total CHECK (valor_total >= 0)
);

-- ---------------------------------------------------------------------
-- ITEM_PEDIDO: resolve o relacionamento N:N entre pedido e produto
-- preco_unitario guarda o preço no momento da compra
-- ---------------------------------------------------------------------
CREATE TABLE item_pedido (
    id_pedido       INTEGER       NOT NULL,
    id_produto      INTEGER       NOT NULL,
    quantidade      SMALLINT      NOT NULL,
    preco_unitario  NUMERIC(8,2)  NOT NULL,
    CONSTRAINT pk_item_pedido PRIMARY KEY (id_pedido, id_produto),
    CONSTRAINT fk_item_pedido FOREIGN KEY (id_pedido)
        REFERENCES pedido (id_pedido) ON DELETE CASCADE,
    CONSTRAINT fk_item_produto FOREIGN KEY (id_produto)
        REFERENCES produto (id_produto),
    CONSTRAINT ck_item_quantidade CHECK (quantidade BETWEEN 1 AND 20),
    CONSTRAINT ck_item_preco CHECK (preco_unitario > 0)
);

-- ---------------------------------------------------------------------
-- Índices de apoio às consultas mais frequentes
-- ---------------------------------------------------------------------
CREATE INDEX idx_pedido_usuario  ON pedido (id_usuario, data_hora DESC);
CREATE INDEX idx_pedido_status   ON pedido (status, data_hora);
CREATE INDEX idx_produto_categ   ON produto (categoria) WHERE ativo;
CREATE INDEX idx_endereco_usuario ON endereco (id_usuario);
