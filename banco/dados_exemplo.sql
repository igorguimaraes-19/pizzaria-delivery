-- Dados de exemplo para desenvolvimento e testes
-- Usuários (cliente e administração) devem ser criados pela aplicação,
-- pois a senha precisa ser gravada com hash.

INSERT INTO produto (nome, descricao, categoria, preco) VALUES
    ('Pizza Mussarela (Grande)',   'Molho de tomate, mussarela e orégano',                'PIZZA',     48.00),
    ('Pizza Calabresa (Grande)',   'Calabresa fatiada, cebola e mussarela',               'PIZZA',     52.00),
    ('Pizza Frango com Catupiry (Grande)', 'Frango desfiado e catupiry',                  'PIZZA',     56.00),
    ('Pizza Portuguesa (Grande)',  'Presunto, ovos, cebola, ervilha e mussarela',         'PIZZA',     58.00),
    ('Pizza Quatro Queijos (Grande)', 'Mussarela, provolone, parmesão e gorgonzola',      'PIZZA',     60.00),
    ('Pizza Calabresa (Média)',    'Calabresa fatiada, cebola e mussarela',               'PIZZA',     42.00),
    ('Refrigerante 2L',            'Guaraná, cola ou laranja',                            'BEBIDA',    12.00),
    ('Suco de laranja 500 ml',     'Suco natural',                                        'BEBIDA',     9.00),
    ('Água mineral 500 ml',        'Sem gás',                                             'BEBIDA',     4.00),
    ('Pizza doce de chocolate (Média)', 'Chocolate ao leite e granulado',                 'SOBREMESA', 40.00),
    ('Brownie com sorvete',        'Brownie quente com bola de creme',                    'SOBREMESA', 18.00);
