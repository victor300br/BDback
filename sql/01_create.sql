-- =============================================================================
-- TP3 — Biblioteca Universitária
-- Script 01: criação do banco (PostgreSQL)
-- Derivado do projeto lógico TP2 (atualizado)
-- =============================================================================

-- Opcional: criar banco dedicado (execute conectado ao postgres como superuser)
-- CREATE DATABASE biblioteca_universitaria
--     WITH ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8' TEMPLATE template0;
-- \c biblioteca_universitaria

-- -----------------------------------------------------------------------------
-- Remoção (ordem inversa das dependências)
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_emprestimos_detalhados CASCADE;
DROP TABLE IF EXISTS publica CASCADE;
DROP TABLE IF EXISTS emprestimo CASCADE;
DROP TABLE IF EXISTS autor CASCADE;
DROP TABLE IF EXISTS livro CASCADE;
DROP TABLE IF EXISTS editora CASCADE;
DROP TABLE IF EXISTS categoria CASCADE;
DROP TABLE IF EXISTS estudante CASCADE;
DROP TABLE IF EXISTS professor CASCADE;
DROP TABLE IF EXISTS funcionario CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

DROP FUNCTION IF EXISTS fn_validar_subtipo_usuario() CASCADE;
DROP FUNCTION IF EXISTS fn_emprestimo_status() CASCADE;
DROP FUNCTION IF EXISTS fn_usuario_exclusivo_subtipo() CASCADE;

-- -----------------------------------------------------------------------------
-- Tabelas
-- -----------------------------------------------------------------------------

CREATE TABLE usuario (
    id_usuario      SERIAL          PRIMARY KEY,
    nome            VARCHAR(120)    NOT NULL,
    cpf             CHAR(11)        NOT NULL UNIQUE,
    email           VARCHAR(120),
    telefone        VARCHAR(20),
    CONSTRAINT ck_usuario_cpf_digitos CHECK (cpf ~ '^[0-9]{11}$')
);

CREATE TABLE estudante (
    id_usuario          INTEGER         PRIMARY KEY
                                        REFERENCES usuario (id_usuario)
                                        ON DELETE CASCADE,
    matricula           VARCHAR(20)     NOT NULL UNIQUE,
    curso               VARCHAR(80)     NOT NULL,
    periodo             INTEGER,
    limite_emprestimo   INTEGER,
    CONSTRAINT ck_estudante_periodo CHECK (periodo IS NULL OR periodo BETWEEN 1 AND 20),
    CONSTRAINT ck_estudante_limite CHECK (limite_emprestimo IS NULL OR limite_emprestimo > 0)
);

CREATE TABLE professor (
    id_usuario      INTEGER         PRIMARY KEY
                                    REFERENCES usuario (id_usuario)
                                    ON DELETE CASCADE,
    departamento    VARCHAR(80)     NOT NULL,
    titulacao       VARCHAR(40),
    sala            VARCHAR(20)
);

CREATE TABLE funcionario (
    id_usuario      INTEGER         PRIMARY KEY
                                    REFERENCES usuario (id_usuario)
                                    ON DELETE CASCADE,
    cod_funcional   VARCHAR(20)     NOT NULL UNIQUE,
    setor           VARCHAR(60)     NOT NULL,
    cargo           VARCHAR(60),
    turno           VARCHAR(20)
);

CREATE TABLE categoria (
    id_categoria    SERIAL          PRIMARY KEY,
    nome            VARCHAR(60)     NOT NULL,
    descricao       VARCHAR(255)    NOT NULL,
    icone           VARCHAR(60),
    palavras_chave  VARCHAR(255)
);

CREATE TABLE livro (
    id_livro        SERIAL          PRIMARY KEY,
    titulo          VARCHAR(200)    NOT NULL,
    resumo          TEXT,
    ano_publicacao  INTEGER,
    id_categoria    INTEGER         NOT NULL
                                    REFERENCES categoria (id_categoria)
                                    ON DELETE RESTRICT,
    CONSTRAINT ck_livro_ano CHECK (ano_publicacao IS NULL OR ano_publicacao BETWEEN 1000 AND 2100)
);

CREATE TABLE autor (
    id_autor            SERIAL          PRIMARY KEY,
    nome                VARCHAR(120)    NOT NULL,
    nacionalidade       VARCHAR(60)     NOT NULL,
    biografia           TEXT,
    data_nascimento     DATE,
    id_usuario          INTEGER         UNIQUE
                                        REFERENCES usuario (id_usuario)
                                        ON DELETE SET NULL
);

CREATE TABLE editora (
    id_editora    SERIAL          PRIMARY KEY,
    razao_social    VARCHAR(120)    NOT NULL,
    cnpj            CHAR(14)        NOT NULL UNIQUE,
    website         VARCHAR(200),
    telefone        VARCHAR(20),
    CONSTRAINT ck_editora_cnpj CHECK (cnpj ~ '^[0-9]{14}$')
);

-- Entidade associativa: PK composta (alternativa A do TP2)
CREATE TABLE emprestimo (
    id_usuario              INTEGER         NOT NULL
                                            REFERENCES usuario (id_usuario)
                                            ON DELETE RESTRICT,
    id_livro                INTEGER         NOT NULL
                                            REFERENCES livro (id_livro)
                                            ON DELETE RESTRICT,
    data_emprestimo         DATE            NOT NULL,
    data_prev_devolucao     DATE            NOT NULL,
    status                  VARCHAR(20)     NOT NULL DEFAULT 'EM_ANDAMENTO',
    data_devolucao          DATE,
    observacao              VARCHAR(255),
    PRIMARY KEY (id_usuario, id_livro, data_emprestimo),
    CONSTRAINT ck_emprestimo_status CHECK (
        status IN ('EM_ANDAMENTO', 'DEVOLVIDO', 'ATRASADO')
    ),
    CONSTRAINT ck_emprestimo_prazo CHECK (data_prev_devolucao >= data_emprestimo),
    CONSTRAINT ck_emprestimo_devolucao CHECK (
        data_devolucao IS NULL OR data_devolucao >= data_emprestimo
    )
);

CREATE TABLE publica (
    id_livro                INTEGER         NOT NULL
                                            REFERENCES livro (id_livro)
                                            ON DELETE RESTRICT,
    id_autor                INTEGER         NOT NULL
                                            REFERENCES autor (id_autor)
                                            ON DELETE RESTRICT,
    id_editora              INTEGER         NOT NULL
                                            REFERENCES editora (id_editora)
                                            ON DELETE RESTRICT,
    tipo_vinculo            VARCHAR(40)     NOT NULL,
    ano_edicao              INTEGER         NOT NULL,
    ordem_autoria           INTEGER,
    percentual_royalties    NUMERIC(5, 2),
    PRIMARY KEY (id_livro, id_autor, id_editora),
    CONSTRAINT ck_publica_tipo CHECK (
        tipo_vinculo IN ('AUTOR_PRINCIPAL', 'COAUTOR', 'ORGANIZADOR')
    ),
    CONSTRAINT ck_publica_ano CHECK (ano_edicao BETWEEN 1000 AND 2100),
    CONSTRAINT ck_publica_royalties CHECK (
        percentual_royalties IS NULL OR (percentual_royalties >= 0 AND percentual_royalties <= 100)
    )
);

-- -----------------------------------------------------------------------------
-- Funções e gatilhos (também referenciados em 03_objects.sql)
-- -----------------------------------------------------------------------------

-- Garante especialização total disjunta: usuário em no máximo um subtipo
CREATE OR REPLACE FUNCTION fn_usuario_exclusivo_subtipo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
    v_id    INTEGER;
BEGIN
    v_id := COALESCE(NEW.id_usuario, OLD.id_usuario);

    SELECT COUNT(*) INTO v_count
    FROM (
        SELECT id_usuario FROM estudante   WHERE id_usuario = v_id
        UNION ALL
        SELECT id_usuario FROM professor   WHERE id_usuario = v_id
        UNION ALL
        SELECT id_usuario FROM funcionario WHERE id_usuario = v_id
    ) sub;

    IF TG_OP = 'INSERT' AND v_count > 1 THEN
        RAISE EXCEPTION 'Usuário % pertence a mais de um subtipo (especialização disjunta).', v_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_estudante_subtipo_unico
    AFTER INSERT OR UPDATE ON estudante
    FOR EACH ROW EXECUTE FUNCTION fn_usuario_exclusivo_subtipo();

CREATE TRIGGER trg_professor_subtipo_unico
    AFTER INSERT OR UPDATE ON professor
    FOR EACH ROW EXECUTE FUNCTION fn_usuario_exclusivo_subtipo();

CREATE TRIGGER trg_funcionario_subtipo_unico
    AFTER INSERT OR UPDATE ON funcionario
    FOR EACH ROW EXECUTE FUNCTION fn_usuario_exclusivo_subtipo();

-- Regra de negócio: status ao registrar devolução
CREATE OR REPLACE FUNCTION fn_emprestimo_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.data_devolucao IS NOT NULL THEN
        NEW.status := 'DEVOLVIDO';
    ELSIF NEW.data_prev_devolucao < CURRENT_DATE AND NEW.data_devolucao IS NULL THEN
        NEW.status := 'ATRASADO';
    ELSIF NEW.status IS NULL THEN
        NEW.status := 'EM_ANDAMENTO';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_emprestimo_status
    BEFORE INSERT OR UPDATE ON emprestimo
    FOR EACH ROW EXECUTE FUNCTION fn_emprestimo_status();

COMMENT ON TABLE emprestimo IS 'Entidade associativa N:N entre usuario e livro (PK composta).';
COMMENT ON COLUMN emprestimo.status IS 'Valor inicial EM_ANDAMENTO (regra de negócio TP1).';
