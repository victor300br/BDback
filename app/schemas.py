from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

TipoLeitor = Literal["ESTUDANTE", "PROFESSOR", "FUNCIONARIO"]


class LivroCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    resumo: Optional[str] = None
    ano_publicacao: Optional[int] = None
    id_categoria: int


class LivroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    resumo: Optional[str] = None
    ano_publicacao: Optional[int] = None
    id_categoria: Optional[int] = None


class CategoriaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=60)
    descricao: str = Field(..., min_length=1, max_length=255)
    icone: Optional[str] = Field(None, max_length=60)
    palavras_chave: Optional[str] = Field(None, max_length=255)


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=60)
    descricao: Optional[str] = Field(None, min_length=1, max_length=255)
    icone: Optional[str] = Field(None, max_length=60)
    palavras_chave: Optional[str] = Field(None, max_length=255)


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    cpf: str = Field(..., min_length=11, max_length=11)
    email: Optional[str] = None
    telefone: Optional[str] = None
    tipo: TipoLeitor
    matricula: Optional[str] = Field(None, max_length=30)
    curso: Optional[str] = Field(None, max_length=80)
    periodo: Optional[int] = None
    limite_emprestimo: Optional[int] = None
    departamento: Optional[str] = Field(None, max_length=80)
    titulacao: Optional[str] = Field(None, max_length=60)
    sala: Optional[str] = Field(None, max_length=20)
    cod_funcional: Optional[str] = Field(None, max_length=30)
    setor: Optional[str] = Field(None, max_length=80)
    cargo: Optional[str] = Field(None, max_length=60)
    turno: Optional[str] = Field(None, max_length=20)

    @model_validator(mode="after")
    def validar_campos_por_tipo(self):
        if self.tipo == "ESTUDANTE":
            if not self.matricula or not self.curso:
                raise ValueError("Matricula e curso sao obrigatorios para estudante")
        elif self.tipo == "PROFESSOR":
            if not self.departamento:
                raise ValueError("Departamento e obrigatorio para professor")
        elif self.tipo == "FUNCIONARIO":
            if not self.cod_funcional or not self.setor:
                raise ValueError("Codigo funcional e setor sao obrigatorios para funcionario")
        return self


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=120)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[str] = None
    telefone: Optional[str] = None
    tipo: Optional[TipoLeitor] = None
    matricula: Optional[str] = Field(None, max_length=30)
    curso: Optional[str] = Field(None, max_length=80)
    periodo: Optional[int] = None
    limite_emprestimo: Optional[int] = None
    departamento: Optional[str] = Field(None, max_length=80)
    titulacao: Optional[str] = Field(None, max_length=60)
    sala: Optional[str] = Field(None, max_length=20)
    cod_funcional: Optional[str] = Field(None, max_length=30)
    setor: Optional[str] = Field(None, max_length=80)
    cargo: Optional[str] = Field(None, max_length=60)
    turno: Optional[str] = Field(None, max_length=20)

    @model_validator(mode="after")
    def validar_campos_por_tipo(self):
        if self.tipo == "ESTUDANTE" and (not self.matricula or not self.curso):
            raise ValueError("Matricula e curso sao obrigatorios para estudante")
        if self.tipo == "PROFESSOR" and not self.departamento:
            raise ValueError("Departamento e obrigatorio para professor")
        if self.tipo == "FUNCIONARIO" and (not self.cod_funcional or not self.setor):
            raise ValueError("Codigo funcional e setor sao obrigatorios para funcionario")
        return self


class EmprestimoCreate(BaseModel):
    id_usuario: int
    id_livro: int
    data_emprestimo: date
    data_prev_devolucao: date
    observacao: Optional[str] = None


class EmprestimoDevolver(BaseModel):
    id_usuario: int
    id_livro: int
    data_emprestimo: date
    data_devolucao: Optional[date] = None
