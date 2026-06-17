-- =============================================================================
-- TP3 — Script 03: objetos físicos complementares
-- VIEW, índice e gatilho (PL/pgSQL)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- VIEW: empréstimos com dados do usuário, livro e categoria
-- Justificativa: consulta frequente no sistema para painel da biblioteca
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_emprestimos_detalhados AS
SELECT
    e.id_usuario,
    u.nome              AS nome_usuario,
    e.id_livro,
    l.titulo            AS titulo_livro,
    c.nome              AS categoria,
    e.data_emprestimo,
    e.data_prev_devolucao,
    e.data_devolucao,
    e.status,
    e.observacao
FROM emprestimo e
JOIN usuario u   ON u.id_usuario   = e.id_usuario
JOIN livro l     ON l.id_livro     = e.id_livro
JOIN categoria c ON c.id_categoria = l.id_categoria;

COMMENT ON VIEW vw_emprestimos_detalhados IS
    'Painel de empréstimos: une usuario, livro e categoria em uma consulta.';

-- -----------------------------------------------------------------------------
-- ÍNDICE: busca de empréstimos por status (filtro comum na aplicação)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_emprestimo_status
    ON emprestimo (status);

CREATE INDEX idx_livro_categoria
    ON livro (id_categoria);

COMMENT ON INDEX idx_emprestimo_status IS
    'Acelera filtros por status (EM_ANDAMENTO, ATRASADO, DEVOLVIDO).';

-- -----------------------------------------------------------------------------
-- Gatilho adicional: impedir empréstimo duplicado ativo do mesmo livro/usuário
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_impedir_emprestimo_duplicado_ativo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM emprestimo e
        WHERE e.id_usuario = NEW.id_usuario
          AND e.id_livro   = NEW.id_livro
          AND e.status IN ('EM_ANDAMENTO', 'ATRASADO')
          AND (e.id_usuario, e.id_livro, e.data_emprestimo)
              <> (NEW.id_usuario, NEW.id_livro, NEW.data_emprestimo)
    ) THEN
        RAISE EXCEPTION
            'Usuário % já possui empréstimo ativo do livro %.',
            NEW.id_usuario, NEW.id_livro;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_emprestimo_duplicado_ativo
    BEFORE INSERT ON emprestimo
    FOR EACH ROW EXECUTE FUNCTION fn_impedir_emprestimo_duplicado_ativo();

COMMENT ON FUNCTION fn_impedir_emprestimo_duplicado_ativo() IS
    'Impede dois empréstimos ativos simultâneos do mesmo livro para o mesmo usuário.';
