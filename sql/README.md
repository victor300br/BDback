# Scripts SQL — BiblioCampusUECE

Scripts do **TP3** (PostgreSQL) necessários para rodar a API. Execute **nesta ordem** no pgAdmin 4 ou `psql`, conectado ao banco `biblioteca_universitaria`.

## 1. Criar o banco (uma vez)

No pgAdmin, conecte ao servidor → clique direito em **Databases** → **Create** → **Database**:

- Nome: `biblioteca_universitaria`

## 2. Executar os scripts

Abra **Query Tool** no banco `biblioteca_universitaria` e execute:

| Ordem | Arquivo | Conteúdo |
|-------|---------|----------|
| 1 | `01_create.sql` | Tabelas, PK, FK, CHECK, gatilhos |
| 2 | `02_insert.sql` | Dados iniciais |
| 3 | `03_objects.sql` | VIEW, índices, gatilho extra |

O arquivo `04_tests.sql` é opcional (testes do TP3; não é obrigatório para a aplicação).

## 3. Conferir

```sql
SELECT * FROM vw_emprestimos_detalhados LIMIT 5;
SELECT COUNT(*) FROM livro;
```

Se retornar dados, o banco está pronto para o `BDback`.
