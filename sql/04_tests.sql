-- =============================================================================
-- TP3 — Script 04: testes no console SQL
-- Execute após 01, 02 e 03
-- =============================================================================

\echo '=== 1. JOIN: empréstimos com usuário e livro ==='
SELECT
    u.nome,
    l.titulo,
    e.data_emprestimo,
    e.status
FROM emprestimo e
JOIN usuario u ON u.id_usuario = e.id_usuario
JOIN livro l   ON l.id_livro   = e.id_livro
ORDER BY e.data_emprestimo;

\echo ''
\echo '=== 2. GROUP BY + agregação: empréstimos por status ==='
SELECT
    status,
    COUNT(*)            AS total,
    AVG(id_livro)       AS media_id_livro
FROM emprestimo
GROUP BY status
ORDER BY total DESC;

\echo ''
\echo '=== 3. HAVING: categorias com mais de 1 livro ==='
SELECT
    c.nome,
    COUNT(l.id_livro) AS qtd_livros
FROM categoria c
JOIN livro l ON l.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nome
HAVING COUNT(l.id_livro) > 1;

\echo ''
\echo '=== 4. Subconsulta: usuários com empréstimo atrasado ==='
SELECT nome, cpf
FROM usuario
WHERE id_usuario IN (
    SELECT id_usuario
    FROM emprestimo
    WHERE status = 'ATRASADO'
);

\echo ''
\echo '=== 5. VIEW vw_emprestimos_detalhados ==='
SELECT * FROM vw_emprestimos_detalhados
WHERE status = 'EM_ANDAMENTO'
ORDER BY data_prev_devolucao;

\echo ''
\echo '=== 6. Consulta que usa o índice idx_emprestimo_status ==='
EXPLAIN ANALYZE
SELECT id_usuario, id_livro, data_emprestimo
FROM emprestimo
WHERE status = 'ATRASADO';

\echo ''
\echo '=== 7. Restrição UNIQUE (cpf duplicado — deve falhar) ==='
DO $$
BEGIN
    INSERT INTO usuario (nome, cpf) VALUES ('Teste Duplicado', '11122233344');
    RAISE EXCEPTION 'FALHA: UNIQUE de cpf não bloqueou';
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'OK: restrição UNIQUE em cpf funcionou.';
END;
$$;

\echo ''
\echo '=== 8. Restrição CHECK (status inválido — deve falhar) ==='
DO $$
BEGIN
    INSERT INTO emprestimo (id_usuario, id_livro, data_emprestimo, data_prev_devolucao, status)
    VALUES (1, 2, '2026-06-01', '2026-06-15', 'INVALIDO');
    RAISE EXCEPTION 'FALHA: CHECK de status não bloqueou';
EXCEPTION
    WHEN check_violation THEN
        RAISE NOTICE 'OK: restrição CHECK de status funcionou.';
END;
$$;

\echo ''
\echo '=== 9. Gatilho fn_emprestimo_status (devolução → DEVOLVIDO) ==='
UPDATE emprestimo
SET data_devolucao = CURRENT_DATE
WHERE id_usuario = 2 AND id_livro = 2 AND data_emprestimo = '2026-05-15';

SELECT id_usuario, id_livro, status, data_devolucao
FROM emprestimo
WHERE id_usuario = 2 AND id_livro = 2 AND data_emprestimo = '2026-05-15';

\echo ''
\echo '=== 10. Gatilho especialização disjunta (deve falhar) ==='
DO $$
BEGIN
    INSERT INTO professor (id_usuario, departamento)
    VALUES (1, 'Informática');
    RAISE EXCEPTION 'FALHA: subtipo duplicado não bloqueou';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'OK: especialização disjunta bloqueou: %', SQLERRM;
END;
$$;

\echo ''
\echo '=== 11. Transação com ROLLBACK ==='
BEGIN;
    UPDATE livro SET titulo = 'Título Temporário' WHERE id_livro = 1;
    SELECT titulo FROM livro WHERE id_livro = 1;
ROLLBACK;
SELECT titulo FROM livro WHERE id_livro = 1;

\echo ''
\echo '=== 12. Transação com COMMIT ==='
BEGIN;
    UPDATE categoria SET descricao = 'Obras clássicas atualizadas' WHERE id_categoria = 1;
COMMIT;
SELECT descricao FROM categoria WHERE id_categoria = 1;

\echo ''
\echo '=== Testes concluídos ==='
