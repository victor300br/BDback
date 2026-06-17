# BiblioCampusUECE — Back-end (API)

API REST em **Python + FastAPI** para o Projeto Final da disciplina de Banco de Dados (UECE).

Repositório do front-end: [github.com/victor300br/BDfront](https://github.com/victor300br/BDfront)

---

## Pré-requisitos

1. **Python 3.11+**
2. **PostgreSQL** (15 ou superior recomendado)
3. Banco `biblioteca_universitaria` criado com os scripts em [`sql/`](sql/)

---

## Passo a passo completo

### 1. Criar o banco de dados

Siga as instruções em [`sql/README.md`](sql/README.md):

1. Crie o banco `biblioteca_universitaria` no pgAdmin.
2. Execute, nesta ordem: `01_create.sql` → `02_insert.sql` → `03_objects.sql`.

### 2. Configurar a API

Na pasta `BDback`:

```bat
copy .env.example .env
```

Edite `.env` com sua senha do PostgreSQL:

```
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/biblioteca_universitaria
```

### 3. Instalar dependências e iniciar a API

**Opção rápida (Windows):**

```bat
run.bat
```

Na primeira execução o script cria o ambiente virtual, instala pacotes e sobe o servidor.

**Manualmente:**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Iniciar o front-end

Em outro terminal, clone e rode o [BDfront](https://github.com/victor300br/BDfront):

```bat
run.bat
```

Abra http://127.0.0.1:8080

---

## URLs úteis

| Serviço | URL |
|---------|-----|
| API | http://127.0.0.1:8000/api |
| Documentação Swagger | http://127.0.0.1:8000/docs |
| Health check | http://127.0.0.1:8000/api/health |
| Front-end | http://127.0.0.1:8080 |

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Framework | FastAPI |
| Servidor ASGI | Uvicorn |
| Driver PostgreSQL | psycopg v3 |
| Validação | Pydantic |
| IDE | Cursor / VS Code |

---

## Estrutura do repositório

```
BDback/
├── app/
│   ├── main.py           # FastAPI, CORS
│   ├── database.py       # Conexão PostgreSQL
│   ├── schemas.py        # Validação Pydantic
│   ├── errors.py         # Erros de integridade
│   └── routers/          # Rotas REST
├── sql/                  # Scripts PostgreSQL (TP3)
│   ├── 01_create.sql
│   ├── 02_insert.sql
│   ├── 03_objects.sql
│   └── README.md
├── requirements.txt
├── run.bat
├── .env.example
└── README.md
```

---

## Requisitos do Projeto Final (PF)

| Exigência | Implementação |
|-----------|----------------|
| Inserir / atualizar / remover / listar / consultar | `livros`, `usuarios`, `categorias` |
| Busca por substring | `GET /api/livros?busca=termo` |
| Operação composta | `POST /api/emprestimos` |
| JOIN | `GET /api/relatorios/emprestimos-detalhados` (VIEW) |
| GROUP BY | `GET /api/relatorios/por-status` |
| HAVING | `GET /api/relatorios/categorias-populares` |
| Gatilho PostgreSQL | `PATCH /api/emprestimos/devolver` |
| Erro de integridade | HTTP 409 (CPF duplicado, FK, empréstimo ativo) |

---

## Ajustes em relação ao TP3

- Nenhuma alteração no DDL do banco.
- API adaptada à PK composta de `emprestimo`.
- Cadastro de leitor com generalização (estudante, professor, funcionário).

---

## Integrante

**Victor Araújo Silva** — UECE
