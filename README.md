# Vyper ASPM

**Application Security Posture Management**

A Vyper ASPM é uma plataforma para centralizar informações de segurança de aplicações, correlacionar vulnerabilidades e riscos e apresentar uma visão consolidada da postura de segurança.

A plataforma integra análise de código, dependências, segredos, containers e aplicações web em um único ambiente, permitindo acompanhar Findings, Risks, Assets, Security Score, histórico de scans, comparação entre análises e recomendações de segurança assistidas por IA.

---

# ⚡ Início rápido

A forma recomendada de executar a Vyper é utilizando Docker.

## Requisitos

- Docker Desktop no Windows ou Docker Engine + Docker Compose no Linux
- Git, caso o projeto seja obtido através de um repositório Git
- Conexão com a internet durante a instalação inicial
- Recursos suficientes de CPU e memória para executar os containers e scanners

Não é necessário instalar manualmente:

- Python
- Node.js
- PostgreSQL
- Redis
- Celery
- Semgrep
- Trivy
- Gitleaks
- OWASP ZAP

Esses componentes são executados no ambiente Docker.

---

# 💻 Instalação — Windows

## 1. Instalar o Docker Desktop

Instale o Docker Desktop para Windows e confirme que ele está funcionando.

Depois, abra o PowerShell e verifique:

```powershell
docker --version
docker compose version
```

Os dois comandos devem retornar as respectivas versões instaladas.

## 2. Obter o projeto

Clone o repositório:

```powershell
git clone https://github.com/ArmadilloClown/Vyper-ASPM.git
```

Entre na pasta:

```powershell
cd Vyper-ASPM
```

Caso tenha recebido o projeto como `.zip`, extraia o arquivo e entre na pasta principal do projeto.

## 3. Criar o `.env`

No PowerShell:

```powershell
Copy-Item .env.example .env
```

Edite o arquivo `.env` conforme necessário.

**Importante:** nunca publique o `.env` contendo credenciais, tokens ou outras informações sensíveis.

## 4. Configurar a IA

A Vyper utiliza Ollama como serviço de inteligência artificial.

Instale o Ollama no Windows e instale o modelo configurado:

```powershell
ollama pull llama3.2:latest
```

Verifique:

```powershell
ollama list
```

O modelo deve aparecer na lista.

A configuração utilizada pela Vyper é:

```env
OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=llama3.2:latest
AI_TIMEOUT=120
AI_TEMPERATURE=0.2
```

O Ollama deve estar em execução antes de utilizar as funcionalidades de IA.

## 5. Construir e iniciar a Vyper

Execute:

```powershell
docker compose build
```

Depois:

```powershell
docker compose up -d
```

Para verificar os containers:

```powershell
docker compose ps
```

Todos os principais serviços devem aparecer como `Up`.

---

# 🐧 Instalação — Linux

A Vyper pode ser executada em distribuições Linux utilizando Docker.

Os exemplos abaixo consideram Ubuntu/Debian.

## 1. Instalar Docker

Atualize os pacotes:

```bash
sudo apt update
```

Instale Docker:

```bash
sudo apt install docker.io
```

Instale Docker Compose:

```bash
sudo apt install docker-compose-v2
```

Verifique:

```bash
docker --version
docker compose version
```

## 2. Obter o projeto

Clone o repositório:

```bash
git clone https://github.com/ArmadilloClown/Vyper-ASPM.git
```

Entre na pasta:

```bash
cd Vyper-ASPM
```

Caso tenha recebido o projeto como `.zip`:

```bash
unzip Vyper-ASPM.zip
cd Vyper-ASPM
```

## 3. Criar o `.env`

Execute:

```bash
cp .env.example .env
```

Edite:

```bash
nano .env
```

ou:

```bash
vim .env
```

## 4. Configurar o Ollama

Instale o Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Instale o modelo:

```bash
ollama pull llama3.2:latest
```

Verifique:

```bash
ollama list
```

A configuração da Vyper utiliza:

```env
OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=llama3.2:latest
AI_TIMEOUT=120
AI_TEMPERATURE=0.2
```

### Importante no Linux

Como o Docker precisa acessar o Ollama executado no host, o serviço deve aceitar conexões além de `localhost`.

Configure o Ollama para escutar na interface necessária ao Docker.

Em instalações utilizando `systemd`, pode ser necessário configurar:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Depois:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Verifique:

```bash
sudo systemctl status ollama
```

## 5. Construir e iniciar

Na pasta do projeto:

```bash
sudo docker compose build
```

Depois:

```bash
sudo docker compose up -d
```

Verifique:

```bash
sudo docker compose ps
```

---

## ⚙️ Configuração

A Vyper utiliza variáveis de ambiente para configurar banco de dados, Redis, OWASP ZAP, IA, ferramentas de segurança e CORS.

Para criar o arquivo local de configuração:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### Execução com Docker

Quando a Vyper é executada através do `docker compose`, os containers se comunicam através dos **nomes dos serviços Docker**, e não através de `localhost`.

Os serviços utilizados internamente são:

```text
PostgreSQL → postgres:5432
Redis      → redis:6379
OWASP ZAP  → zap:8080
```

Portanto, as variáveis utilizadas pelos containers devem seguir este padrão:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/vyper
REDIS_URL=redis://redis:6379/0

ZAP_URL=http://zap:8080
ZAP_API_KEY=
ZAP_VERIFY_SSL=true
ZAP_TIMEOUT=30
ZAP_SCAN_TIMEOUT=1800

OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=llama3.2:latest
AI_TIMEOUT=120
AI_TEMPERATURE=0.2

SEMGREP_BIN=
TRIVY_BIN=
GITLEAKS_BIN=

CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

A comunicação interna fica organizada desta forma:

```text
Frontend
   │
   ▼
Backend
   │
   ├── PostgreSQL → postgres:5432
   ├── Redis      → redis:6379
   ├── ZAP        → zap:8080
   └── Ollama     → host.docker.internal:11434
```

### Por que não utilizar `localhost`?

Dentro de um container Docker, `localhost` aponta para o **próprio container**.

Por exemplo:

```text
Backend container
      │
      └── localhost:5432
              │
              └── procura PostgreSQL dentro do próprio container
```

Isso não corresponde à arquitetura da Vyper.

O PostgreSQL está em outro container, chamado `postgres`. Portanto:

```text
Backend
   │
   └── postgres:5432
          │
          └── PostgreSQL
```

O mesmo princípio é utilizado para Redis e OWASP ZAP:

```text
redis:6379
zap:8080
```

### Ollama

O Ollama possui um comportamento diferente porque, na configuração atual, ele é executado no **host**, enquanto o Backend/Worker executa dentro do Docker.

Por isso, o container utiliza:

```env
OLLAMA_URL=http://host.docker.internal:11434/api/generate
```

O `host.docker.internal` permite que o container acesse o serviço Ollama executado na máquina hospedeira.

### Variáveis do `.env`

As principais variáveis utilizadas pela aplicação são:

| Variável | Valor no Docker | Finalidade |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@postgres:5432/vyper` | Conexão com PostgreSQL |
| `REDIS_URL` | `redis://redis:6379/0` | Conexão com Redis |
| `ZAP_URL` | `http://zap:8080` | Comunicação com OWASP ZAP |
| `OLLAMA_URL` | `http://host.docker.internal:11434/api/generate` | Comunicação com Ollama |
| `OLLAMA_MODEL` | `llama3.2:latest` | Modelo utilizado pela IA |
| `AI_TIMEOUT` | `120` | Timeout das requisições de IA |
| `AI_TEMPERATURE` | `0.2` | Temperatura das respostas da IA |

> **Importante:** os valores `postgres`, `redis` e `zap` correspondem aos nomes dos serviços definidos no `docker-compose.yml`. Eles são resolvidos automaticamente pela rede interna do Docker Compose.

> **Importante:** a porta `8080` do ZAP pode ser publicada no host como `127.0.0.1:8080:8080`, mas o Backend deve utilizar `http://zap:8080` para comunicação interna entre containers.

> **Importante:** não é necessário alterar `OLLAMA_URL` para `localhost` quando o Ollama está sendo executado no host. Dentro do container, `localhost` apontaria para o próprio container.

> **Nunca publique o arquivo `.env` contendo credenciais, chaves ou outras informações sensíveis. O arquivo `.env.example` deve conter somente valores de exemplo ou placeholders.**

---

# ▶️ Executando a Vyper

Depois de configurar o ambiente:

```bash
docker compose up -d --build
```

No Linux:

```bash
sudo docker compose up -d --build
```

Verifique os containers:

```bash
docker compose ps
```

Para acompanhar todos os logs:

```bash
docker compose logs -f
```

Somente o backend:

```bash
docker compose logs -f backend
```

Somente o worker:

```bash
docker compose logs -f worker
```

Para parar a aplicação:

```bash
docker compose down
```

No Linux:

```bash
sudo docker compose down
```

**Não utilize `docker compose down -v` se quiser preservar os dados persistidos do PostgreSQL.**

---

# 🌐 Acesso

Depois que os containers estiverem funcionando:

### Dashboard

```text
http://localhost:3000
```

### FastAPI

```text
http://localhost:8000
```

### Swagger

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

---

# 🔍 Executando uma análise

A partir do Dashboard, o usuário pode iniciar uma análise informando o repositório da aplicação.

Fluxo simplificado:

```text
Repositório
    │
    ▼
Validação da URL
    │
    ▼
Clone temporário
    │
    ▼
Scanners
    │
    ├── Semgrep
    ├── Trivy
    ├── Gitleaks
    └── OWASP ZAP
    │
    ▼
Normalização
    │
    ▼
Findings
    │
    ▼
Correlação
    │
    ▼
Risks
    │
    ▼
Dashboard
```

Os repositórios utilizados durante os scans são armazenados temporariamente.

Após a análise, o diretório temporário é removido.

---

# ⚠️ Aviso de segurança

**ATENÇÃO:** os scans da Vyper executam ferramentas de segurança sobre o repositório e/ou aplicação informados.

Execute scans somente em aplicações, repositórios e ambientes que você possui ou para os quais possui autorização explícita para realizar testes de segurança.

Para análises DAST utilizando OWASP ZAP, recomenda-se utilizar ambientes de teste, homologação ou outros ambientes especificamente autorizados. Evite executar scans ativos diretamente contra ambientes de produção sem autorização e avaliação prévia dos possíveis impactos.

Os repositórios atualmente suportados devem utilizar HTTPS e pertencer aos hosts permitidos pela aplicação:

- GitHub
- GitLab
- Bitbucket

A URL é validada antes da execução do scan para impedir destinos não autorizados, credenciais embutidas e outros formatos considerados inseguros.

---

# 📊 Funcionalidades

## Dashboard

O Dashboard apresenta uma visão geral da postura de segurança:

- Security Score
- Findings
- Risks
- Assets
- distribuição de severidades
- principais riscos
- principais pacotes vulneráveis
- histórico de análises
- superfície de ataque

## Findings

A área de Findings apresenta as vulnerabilidades encontradas pelos scanners.

Um finding pode conter:

- fonte
- severidade
- tipo
- título
- descrição
- arquivo
- linha
- pacote afetado
- versão instalada
- versão corrigida
- CVE
- CVSS
- CWE
- OWASP
- categoria
- identificador da regra
- risk score
- status

### Estados dos findings

| Estado | Descrição |
|---|---|
| `new` | Vulnerabilidade identificada na análise atual |
| `active` | Vulnerabilidade encontrada também em análise anterior |
| `fixed` | Vulnerabilidade encontrada anteriormente que não apareceu na análise atual |

## Risks

A Vyper correlaciona findings para produzir uma visão orientada a riscos.

A área de Risks apresenta:

- prioridade
- severidade
- quantidade de evidências
- findings relacionados
- informações de risco
- análise assistida por IA
- recomendações de remediação

## Security Score

O Security Score é calculado com base nas vulnerabilidades ativas.

Findings corrigidos não participam do cálculo atual.

| Severidade | Peso |
|---|---:|
| Critical | 5 |
| High | 3 |
| Medium | 1.5 |
| Low | 0.3 |
| Warning | 0.05 |

O resultado é limitado ao intervalo de `0` a `100`.

## Assets / Attack Surface

A Vyper identifica ativos relacionados às aplicações analisadas.

Entre eles:

- URLs
- containers
- pipelines

Essas informações permitem visualizar a superfície de ataque identificada durante os scans.

---

# 🛡️ Ferramentas de segurança

## Semgrep

Análise estática de código (**SAST**).

## Trivy

Identificação de vulnerabilidades relacionadas a dependências, sistemas de arquivos e containers.

## Gitleaks

Identificação de possíveis segredos expostos no código.

## OWASP ZAP

Análise dinâmica de aplicações web (**DAST**).

---

# 🤖 Inteligência Artificial

A Vyper utiliza Ollama para auxiliar na análise de riscos.

A IA pode produzir:

- resumo do risco
- impacto
- recomendações de remediação

As respostas passam por validações de segurança antes de serem utilizadas pela aplicação.

A configuração pode ser controlada através de:

```env
OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=llama3.2:latest
AI_TIMEOUT=120
AI_TEMPERATURE=0.2
```

O modelo pode ser alterado através da variável:

```env
OLLAMA_MODEL
```

---

# 🔄 Comparação entre scans

A Vyper mantém o histórico das análises realizadas.

Quando uma aplicação é analisada novamente, os findings podem ser comparados com uma análise anterior.

A comparação identifica:

- novos findings
- findings corrigidos
- findings que permaneceram ativos

Exemplo:

```text
Scan anterior
    │
    ├── Finding A
    ├── Finding B
    └── Finding C
            │
            ▼
Scan atual
    │
    ├── Finding A → active
    ├── Finding B → active
    ├── Finding D → new
    └── Finding C → fixed
```

---

# ⚡ Execução assíncrona

Os scans são executados utilizando Celery.

Isso permite que análises demoradas continuem sendo executadas no backend sem depender da permanência do navegador aberto.

Arquitetura simplificada:

```text
Frontend
   │
   ▼
FastAPI
   │
   ▼
Redis
   │
   ▼
Celery Worker
   │
   ├── Semgrep
   ├── Trivy
   ├── Gitleaks
   └── OWASP ZAP
```

---

# 📡 WebSocket

A Vyper utiliza WebSocket para informar o progresso dos scans em tempo real.

Exemplo:

```text
5%    Preparando análise
10%   Clonando repositório
25%   Analisando aplicação
45%   Executando scanners
70%   Processando findings
85%   Correlacionando riscos
95%   Finalizando
100%  Scan concluído
```

O progresso é armazenado temporariamente no Redis e transmitido ao frontend através de WebSocket.

---

# ⏰ Scans automatizados

A Vyper permite configurar análises automáticas.

É possível definir:

- repositório
- intervalo
- ativação/desativação da programação

O intervalo mínimo configurado atualmente é de **10 minutos**.

O agendamento é controlado pelo Celery Beat, portanto o navegador não precisa permanecer aberto.

O próximo scan é calculado a partir da conclusão da análise anterior.

---

# 🐳 Docker

A infraestrutura Docker possui containers para:

- Frontend
- Backend
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat
- OWASP ZAP
- inicialização do banco

O Backend/Worker possui as ferramentas necessárias para análise:

- Semgrep
- Trivy
- Gitleaks

O OWASP ZAP é executado em seu próprio container.

Isso permite executar a Vyper sem instalar manualmente Python, Node.js, PostgreSQL, Redis, Celery ou os scanners na máquina hospedeira.

---

# 🏗️ Arquitetura

```text
                         ┌─────────────────┐
                         │     Usuário     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Next.js     │
                         │    Dashboard    │
                         └────────┬────────┘
                                  │
                              HTTP / WS
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     FastAPI     │
                         │     Backend     │
                         └───────┬─┬───────┘
                                 │ │
                    ┌────────────┘ └────────────┐
                    ▼                           ▼
             ┌─────────────┐             ┌─────────────┐
             │ PostgreSQL  │             │    Redis    │
             └─────────────┘             └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │   Celery    │
                                         │    Worker   │
                                         └──────┬──────┘
                                                │
                       ┌────────────┬───────────┼───────────┐
                       ▼            ▼           ▼           ▼
                    Semgrep       Trivy      Gitleaks      ZAP
```

---

# 📁 Estrutura do projeto

```text
Vyper-ASPM/
│
├── app/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── tasks/
│   ├── websocket/
│   └── main.py
│
├── storage/
├── temp/
│
├── vyper-dashboard/
│   └── src/
│
├── create_tables.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .env.example
├── .gitignore
├── LICENSE.md
└── README.md
```

A estrutura interna de `app/` pode evoluir conforme novas funcionalidades sejam adicionadas.

---

# 🔐 Segurança

A Vyper possui mecanismos para reduzir riscos durante a execução dos scans.

Entre eles:

- validação de URLs
- restrição de hosts permitidos
- utilização de HTTPS para repositórios
- bloqueio de credenciais embutidas em URLs
- validação de portas
- validação dos alvos utilizados pelo OWASP ZAP
- bloqueio de destinos locais, privados ou reservados nos scans DAST
- restrição das portas permitidas para os alvos do ZAP
- execução de subprocessos sem `shell=True`
- utilização de caminhos explícitos para ferramentas
- timeouts para processos externos
- limpeza dos diretórios temporários
- configuração através de variáveis de ambiente
- CORS configurável
- validação das respostas geradas pela IA

---

# 🗄️ Banco de dados e isolamento

Cada implantação da Vyper possui seu próprio ambiente de dados.

```text
Máquina A
├── Vyper
├── PostgreSQL A
└── Redis A


Máquina B
├── Vyper
├── PostgreSQL B
└── Redis B
```

As instalações não compartilham automaticamente os dados.

Cada instalação possui seus próprios:

- scans
- findings
- risks
- assets
- análises de IA
- configurações de agendamento

O compartilhamento entre instalações somente ocorre caso uma infraestrutura externa seja configurada explicitamente para isso.

---

# 🧹 Dados temporários e retenção

Os repositórios utilizados durante os scans são armazenados temporariamente.

Após a análise, os diretórios temporários são removidos pelo mecanismo de limpeza da aplicação.

Os dados persistidos no PostgreSQL representam o histórico da aplicação e não são removidos automaticamente como parte da limpeza dos repositórios temporários.

Políticas adicionais de retenção, arquivamento e backup podem ser implementadas conforme as necessidades do ambiente.

---

# 🧪 Testes e validação

Durante o desenvolvimento foram realizados testes envolvendo:

- execução dos containers Docker
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat
- Semgrep
- Trivy
- Gitleaks
- OWASP ZAP
- integração com IA
- scans completos
- persistência de findings
- comparação entre scans
- Security Score
- scans automatizados
- WebSocket
- limpeza de repositórios temporários
- build do frontend
- endpoints da API

A aplicação foi validada através de scans reais e testes de integração entre seus principais componentes.

---

# ⚠️ Limitações atuais

A Vyper atualmente está estruturada como uma aplicação de implantação individual.

Possíveis evoluções futuras incluem:

- autenticação de usuários
- controle de permissões
- múltiplas organizações
- arquitetura multi-tenant
- sistema avançado de backups
- políticas configuráveis de retenção
- observabilidade avançada
- escalabilidade horizontal dos workers
- reverse proxy e HTTPS automatizado
- novas integrações de segurança

---

# 📌 Status

A Vyper possui uma implementação funcional de um MVP de Application Security Posture Management, incluindo:

- coleta de vulnerabilidades
- centralização de findings
- correlação de riscos
- dashboard
- histórico de scans
- comparação entre análises
- Security Score
- superfície de ataque
- análise assistida por IA
- scans automatizados
- execução assíncrona
- acompanhamento de progresso em tempo real

A plataforma está estruturada para execução através de Docker e preparada para futuras evoluções.

---

# 👨‍💻 Projeto

**Vyper ASPM**

Application Security Posture Management

Desenvolvido como projeto acadêmico e técnico para estudo e aplicação prática de conceitos de segurança de aplicações, integração de ferramentas DevSecOps, processamento assíncrono e análise de riscos.

---

## 📄 Licença

Este projeto é distribuído sob os termos da **GNU General Public License v3.0 (GPLv3)**.

Consulte o arquivo `LICENSE.md` para obter o texto completo da licença.
