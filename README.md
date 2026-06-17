# BiblioCampusUECE — Back-end (API)

API REST em **Python + FastAPI** para o Projeto Final da disciplina de Banco de Dados. Conecta-se ao PostgreSQL do **TP3** (`biblioteca_universitaria`).

## Pré-requisitos

- Python 3.11+
- PostgreSQL com o banco do TP3 criado (scripts `01_create.sql` … `03_objects.sql`)
- Front-end em execução em `http://127.0.0.1:8080` (repositório **BDfront**)

## Como rodar

```bat
run.bat
```

Ou manualmente:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000/api  
- Documentação interativa: http://127.0.0.1:8000/docs  
- Health check: http://127.0.0.1:8000/api/health  

Configure a conexão em `.env`:

```
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/biblioteca_universitaria
```

## Stack

| Item | Tecnologia |
|------|------------|
| Framework | FastAPI |
| Servidor | Uvicorn |
| Driver PostgreSQL | psycopg v3 |
| Validação | Pydantic |

## Endpoints e requisitos do PF

| Requisito | Rota / módulo |
|-----------|----------------|
| Inserir registro | `POST /api/livros`, `/api/usuarios`, `/api/categorias`, `/api/emprestimos` |
| Atualizar registro | `PUT /api/livros/{id}`, `/api/usuarios/{id}`, `/api/categorias/{id}` |
| Remover registro | `DELETE /api/livros/{id}`, `/api/usuarios/{id}`, `/api/categorias/{id}` |
| Listar registros | `GET` em cada recurso |
| Consulta específica | `GET /api/livros/{id}`, `/api/usuarios/{id}`, etc. |
| Busca por substring | `GET /api/livros?busca=termo` (`ILIKE` no título) |
| Operação composta | `POST /api/emprestimos` (usuário + livro + datas) |
| JOIN | `GET /api/relatorios/emprestimos-detalhados` (VIEW do TP3) |
| GROUP BY | `GET /api/relatorios/por-status` |
| HAVING | `GET /api/relatorios/categorias-populares` |
| Gatilho PostgreSQL | `PATCH /api/emprestimos/devolver` → atualiza `data_devolucao`; gatilho define `status` |
| Erro de integridade | CPF duplicado, empréstimo ativo duplicado, FK ao excluir categoria/livro → HTTP 409 |

## Estrutura

```
app/
├── main.py          # FastAPI, CORS, rotas
├── database.py      # Conexão psycopg
├── schemas.py       # Modelos Pydantic
├── errors.py        # Tratamento de erros do PostgreSQL
└── routers/         # livros, usuarios, categorias, emprestimos, relatorios, health
```

## Ajustes em relação ao TP3

- Nenhuma alteração no DDL do banco.
- API adaptada à **PK composta** de `emprestimo` (`id_usuario`, `id_livro`, `data_emprestimo`).
- Generalização de usuário: insert/update em `estudante`, `professor` ou `funcionario`.
- Relatórios consomem a VIEW `vw_emprestimos_detalhados` e consultas SQL do TP3.

## Integrante

Victor Araújo Silva — UECE
