-- =============================================================================
-- TP3 — Script 02: população de dados
-- =============================================================================

-- USUARIO
INSERT INTO usuario (id_usuario, nome, cpf, email, telefone) VALUES
    (1, 'Ana Paula Souza',       '11122233344', 'ana@uni.br',    '51999990001'),
    (2, 'Bruno Lima Costa',      '22233344455', 'bruno@uni.br',  '51999990002'),
    (3, 'Carla Mendes Rocha',    '33344455566', 'carla@uni.br',  '51999990003'),
    (4, 'Diego Ferreira Alves',  '44455566677', 'diego@uni.br',  '51999990004'),
    (5, 'Elena Martins Dias',    '55566677788', 'elena@uni.br',  '51999990005'),
    (6, 'Prof. Ricardo Nunes',   '66677788899', 'ricardo@uni.br','51999990006'),
    (7, 'Maria Bibliotecaria',   '77788899900', 'maria@bib.br',  '51999990007');

SELECT setval(pg_get_serial_sequence('usuario', 'id_usuario'), 7);

-- Subtipos (especialização t,d)
INSERT INTO estudante (id_usuario, matricula, curso, periodo, limite_emprestimo) VALUES
    (1, '2024001001', 'Ciência da Computação', 4, 3),
    (2, '2024001002', 'Engenharia Civil',      2, 3),
    (3, '2023002050', 'Administração',         6, 2);

INSERT INTO professor (id_usuario, departamento, titulacao, sala) VALUES
    (6, 'Departamento de Informática', 'Doutor', 'B201');

INSERT INTO funcionario (id_usuario, cod_funcional, setor, cargo, turno) VALUES
    (7, 'FUNC001', 'Biblioteca Central', 'Bibliotecária', 'Manhã');

-- CATEGORIA
INSERT INTO categoria (id_categoria, nome, descricao, icone, palavras_chave) VALUES
    (1, 'Literatura Brasileira', 'Obras clássicas e contemporâneas', 'book', 'romance, poesia'),
    (2, 'Tecnologia',            'Livros técnicos e computação',     'cpu',  'programação, banco de dados'),
    (3, 'História',              'História geral e regional',        'globe','brasil, mundo');

SELECT setval(pg_get_serial_sequence('categoria', 'id_categoria'), 3);

-- LIVRO (sem isbn)
INSERT INTO livro (id_livro, titulo, resumo, ano_publicacao, id_categoria) VALUES
    (1, 'Dom Casmurro',                    'Romance de Machado de Assis', 1899, 1),
    (2, 'Projeto de Banco de Dados',       'Livro-texto de modelagem',    2020, 2),
    (3, 'História do Brasil',              'Panorama histórico',          2015, 3),
    (4, 'Memórias Póstumas de Brás Cubas', 'Romance machadiano',          1881, 1);

SELECT setval(pg_get_serial_sequence('livro', 'id_livro'), 4);

-- AUTOR
INSERT INTO autor (id_autor, nome, nacionalidade, biografia, data_nascimento, id_usuario) VALUES
    (1, 'Machado de Assis',     'Brasileira', 'Escritor do Realismo', '1839-06-21', NULL),
    (2, 'Carlos Alberto Heuser', 'Brasileira', 'Professor e autor de BD', NULL, 6),
    (3, 'Boris Fausto',         'Brasileira', 'Historiador', '1930-01-01', NULL);

SELECT setval(pg_get_serial_sequence('autor', 'id_autor'), 3);

-- EDITORA
INSERT INTO editora (id_editora, razao_social, cnpj, website, telefone) VALUES
    (1, 'Companhia das Letras Ltda',  '12345678000190', 'https://companhiadasletras.com.br', '1130001000'),
    (2, 'Editora Bookman Ltda',       '23456789000181', 'https://bookman.com.br',            '5130002000'),
    (3, 'Editora da Universidade',  '34567890000172', NULL,                                '5130003000');

SELECT setval(pg_get_serial_sequence('editora', 'id_editora'), 3);

-- EMPRESTIMO (PK composta: id_usuario, id_livro, data_emprestimo)
INSERT INTO emprestimo (id_usuario, id_livro, data_emprestimo, data_prev_devolucao, status, data_devolucao, observacao) VALUES
    (1, 1, '2026-05-10', '2026-05-24', 'DEVOLVIDO',    '2026-05-20', 'Devolvido antes do prazo'),
    (2, 2, '2026-05-15', '2026-05-29', 'EM_ANDAMENTO', NULL,         NULL),
    (3, 3, '2026-04-01', '2026-04-15', 'ATRASADO',     NULL,         'Usuário não devolveu'),
    (1, 4, '2026-05-20', '2026-06-03', 'EM_ANDAMENTO', NULL,         'Renovação pendente'),
    (2, 1, '2026-03-01', '2026-03-15', 'DEVOLVIDO',    '2026-03-14', NULL);

-- PUBLICA (ternário)
INSERT INTO publica (id_livro, id_autor, id_editora, tipo_vinculo, ano_edicao, ordem_autoria, percentual_royalties) VALUES
    (1, 1, 1, 'AUTOR_PRINCIPAL', 2008, 1, 10.00),
    (2, 2, 2, 'AUTOR_PRINCIPAL', 2020, 1, 12.50),
    (3, 3, 3, 'AUTOR_PRINCIPAL', 2015, 1,  8.00),
    (4, 1, 1, 'AUTOR_PRINCIPAL', 2010, 1, 10.00);
