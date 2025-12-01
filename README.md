# Sistema de Gerenciamento de Monografias - Sistemas de Informação

Este projeto é uma aplicação web desenvolvida como parte da disciplina de **Sistemas Distribuídos**, sob a orientação do Prof. Alessandro Vivas Andrade. O objetivo é criar um sistema robusto para gerenciar todo o ciclo de vida das monografias do curso de Sistemas de Informação, desde o cadastro inicial até a avaliação final.

Esta entrega contempla a **Parte 1** dos requisitos, focada em autenticação, controle de acesso e operações CRUD (Create, Read, Update, Delete) para as entidades principais do sistema.

## Equipe

  * Daniel Gonçalves
  * Enzo Veloso
  * Kaique Xavier
  * Lucas Martins

## Funcionalidades Implementadas (Parte 1)

O sistema atualmente implementa as seguintes funcionalidades:

### 1\. Autenticação e Controle de Acesso

  * **Sistema de Autenticação Completo:** Utiliza o `django-allauth` para gerenciar o registro, login (por e-mail), logout e recuperação de senha.
  * **Perfis de Usuário:** O sistema distingue três tipos de usuários:
      * **Alunos:** Podem criar e gerenciar sua própria monografia.
      * **Professores:** Podem ser orientadores, coorientadores e membros de bancas.
      * **Administradores (Staff):** Têm acesso total ao sistema através da interface de administração do Django para gerenciar alunos, professores e todos os dados.
  * **Registro de Auditoria:** As ações de login, logout e tentativas de login falhas são registradas no sistema para fins de auditoria, conforme implementado em `core/signals.py`.

### 2\. Dashboard do Usuário

  * Após o login, cada usuário é direcionado para um **Dashboard** personalizado.
  * **Alunos:** Visualizam o status da sua monografia ou um link para criá-la.
  * **Professores:** Visualizam uma lista das monografias que orientam.

### 3\. Gerenciamento de Monografias (CRUD Completo)

  * **Criação:** Alunos podem cadastrar suas monografias, preenchendo campos como título, resumo, orientador, e fazer o **upload do arquivo PDF** do trabalho.
  * **Leitura:**
      * Uma lista paginada de todas as monografias está disponível.
      * Um campo de **busca** permite filtrar monografias por título, autor, orientador ou palavras-chave.
      * A página de detalhes exibe todas as informações da monografia, incluindo um link para download do PDF (disponível apenas para o autor e orientadores).
  * **Atualização:** O aluno autor, o orientador e administradores podem editar as informações da monografia.
  * **Exclusão:** Apenas usuários com permissão (`core.can_delete_monografia`) podem excluir uma monografia, com uma tela de confirmação.

### 4\. Gerenciamento de Bancas (CRUD Completo)

  * **Agendamento:** Orientadores e administradores podem agendar a banca de uma monografia, definindo a data, local e os professores avaliadores.
  * **Leitura:** Visualização dos detalhes da banca, incluindo os membros e a nota final (se atribuída).
  * **Atualização:** As informações da banca podem ser editadas pelos responsáveis.
  * **Exclusão:** Bancas podem ser removidas do sistema.

### 5\. Histórico de Alterações

  * Utilizando o `django-simple-history`, o sistema rastreia e exibe o histórico de todas as alterações feitas em uma monografia, incluindo quem alterou e quando.

## Tecnologias Utilizadas

  * **Backend:** Python 3.12, Django 5.2
  * **Banco de Dados:** PostgreSQL 16
  * **Gerenciador de Dependências:** Poetry
  * **Autenticação:** `django-allauth`
  * **Histórico de Modelos:** `django-simple-history`
  * **Variáveis de Ambiente:** `python-decouple`
  * **Containerização:** Docker e Docker Compose

## Pré-requisitos

  * Docker
  * Docker Compose

## Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar o ambiente de desenvolvimento.

**1. Clone o repositório:**

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

**2. Crie o arquivo de variáveis de ambiente:**
Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.

```bash
cp .env.example .env
```

> **Nota:** O arquivo `.env` já vem com valores padrão para o ambiente Docker e não precisa de alterações para a execução local. A `SECRET_KEY` deve ser alterada para um ambiente de produção.

**3. Suba os containers Docker:**
Este comando irá construir as imagens Docker (se ainda não existirem), iniciar os serviços do banco de dados e da aplicação web, e aplicar as migrações do banco de dados.

```bash
docker-compose up --build
```

**4. Acesse a aplicação:**
Após a conclusão do build, a aplicação estará disponível no seu navegador no seguinte endereço:
[http://localhost:8000](https://www.google.com/search?q=http://localhost:8000)

**5. Documentação da API (Swagger/Redoc):**

- Swagger UI: `http://localhost:8000/api/docs/swagger/`
- Redoc: `http://localhost:8000/api/docs/redoc/`
- Esquema OpenAPI: `http://localhost:8000/api/schema/`

**6. Acessando o Admin:**
Para criar um superusuário e acessar a área administrativa do Django, execute o seguinte comando em um novo terminal:

```bash
docker-compose exec web poetry run python manage.py createsuperuser
```

Siga as instruções para criar seu usuário administrador. Depois, acesse [http://localhost:8000/admin](https://www.google.com/search?q=http://localhost:8000/admin).

**7. Popular o banco com dados de exemplo (seed)**

Para iniciar o projeto já com usuários, monografias, bancas e histórico, execute:

```bash
poetry run python manage.py seed               # cria dados padrão
poetry run python manage.py seed --count 20    # personaliza a quantidade de monografias/alunos
poetry run python manage.py seed --clear       # limpa os dados antes de gerar novamente
poetry run python manage.py seed --fake        # simula sem gravar no banco
```

No Docker Compose:

```bash
docker-compose exec backend poetry run python manage.py seed
docker-compose exec backend poetry run python manage.py seed --clear
```

## Estrutura do Projeto

  * `config/`: Contém as configurações globais do projeto Django (`settings.py`, `urls.py`).
  * `core/`: É a aplicação principal do projeto, onde estão definidos os modelos, views, forms e URLs relacionados ao gerenciamento de monografias.
  * `templates/`: Contém todos os templates HTML do projeto, organizados por aplicação.
  * `media/`: Diretório onde os arquivos de upload (PDFs das monografias) são armazenados.
  * `Dockerfile`: Define a imagem Docker para a aplicação Django.
  * `docker-compose.yml`: Orquestra os serviços da aplicação (web e banco de dados).

## Modelos (Schema do Banco de Dados)

O sistema é estruturado em torno dos seguintes modelos principais:

  * **`Professor`**: Perfil associado a um `User`, com campos para titulação e área de pesquisa.
  * **`Aluno`**: Perfil associado a um `User`, com um campo para a matrícula.
  * **`Monografia`**: O modelo central, contendo título, resumo, palavras-chave, status, `arquivo_documento` (FileField) e as chaves estrangeiras para `Aluno` (autor), `Professor` (orientador) e `Professor` (coorientador).
  * **`Banca`**: Associada a uma `Monografia`, contém os professores avaliadores (relação Many-to-Many), data, local da defesa e a nota final.

## Próximos Passos (Parte 2)

A próxima etapa do desenvolvimento incluirá:

  * Implementação de uma **API REST** com Django REST Framework.
  * Criação de **endpoints públicos** (somente leitura) para listar monografias e professores.
  * Criação de **endpoints restritos** (com autenticação) para o CRUD de monografias e agendamento de bancas.
  * Desenvolvimento de funcionalidades extras, como a geração de atas e dashboards com gráficos.
