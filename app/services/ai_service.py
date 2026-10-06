# Vyper ASPM
#
# Copyright (C) 2026 Pedro
#
# This file is part of Vyper ASPM.
#
# Vyper ASPM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Vyper ASPM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Vyper ASPM. If not, see <https://www.gnu.org/licenses/>.

import os
import re
import requests

from app.config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    AI_TIMEOUT,
    AI_TEMPERATURE,
)


# ============================================================
# FUNÇÕES DE EXECUÇÃO DINÂMICA / SHELL
# ============================================================

DANGEROUS_EXECUTION_FUNCTIONS = (
    "eval",
    "exec",
    "shell_exec",
    "system",
    "passthru",
    "proc_open",
    "popen",
    "pcntl_exec",
)


# ============================================================
# PADRÕES DE REMEDIAÇÃO AMBÍGUA PARA EXECUÇÃO DE COMANDOS
# ============================================================

AMBIGUOUS_COMMAND_REMEDIATION_PATTERNS = [
    # Recomendações genéricas relacionadas a funções shell
    r"forma segura de passar.*dados.*fun[cç][oõ]es.*comandos",
    r"forma segura de passar.*dados.*funcoes.*comandos",

    r"passar.*dados.*fun[cç][oõ]es.*shell",
    r"passar.*dados.*funcoes.*shell",

    r"fun[cç][oõ]es.*executam comandos shell",
    r"funcoes.*executam comandos shell",

    r"fun[cç][oõ]es.*execu[cç][aã]o.*comandos",
    r"funcoes.*execucao.*comandos",

    # Recomendações genéricas para continuar usando execução
    r"limitar.*uso.*avalia[cç][oõ]es.*comandos",
    r"limitar.*uso.*avaliacoes.*comandos",

    r"usar.*avalia[cç][oõ]es.*comandos",
    r"usar.*avaliacoes.*comandos",

    r"utilizar.*avalia[cç][oõ]es.*comandos",
    r"utilizar.*avaliacoes.*comandos",

    r"executar.*comandos.*com.*extremo cuidado",
    r"executar.*comandos.*cuidado",

    r"execu[cç][aã]o.*comandos.*extremo cuidado",
    r"execucao.*comandos.*extremo cuidado",

    # Manter execução de comandos sem definir mecanismo seguro
    r"apenas.*use.*comandos.*necess[aá]rio",
    r"apenas.*use.*comandos.*necessario",

    r"somente.*use.*comandos.*necess[aá]rio",
    r"somente.*use.*comandos.*necessario",
]




# ============================================================
# EXPRESSÕES QUE INDICAM QUE A IA ESTÁ RECOMENDANDO
# UMA FUNÇÃO COMO SOLUÇÃO
# ============================================================

RECOMMENDATION_WORDS = (
    "use",
    "usar",
    "utilize",
    "utilizar",
    "recomendo",
    "recomenda",
    "recomenda-se",
    "recomendado",
    "substitua",
    "substituir",
    "troque",
    "trocar",
    "prefira",
    "preferir",
    "adote",
    "adotar",
    "implemente",
    "implementar",
    "aplique",
    "aplicar",
    "considere",
    "considere utilizar",
    "uma solução é",
    "a solução é",
    "a correção é",
    "corrija usando",
    "corrigir usando",
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _normalize_text(text):
    """
    Normaliza o texto para facilitar as validações.
    """

    if not text:
        return ""

    text = text.lower()

    # Remove acentuação básica através de substituições.
    replacements = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "õ": "o",
        "ô": "o",
        "ú": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normaliza espaços.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def _function_pattern(function_name):
    """
    Cria regex para detectar uma função PHP.
    """

    return rf"\b{re.escape(function_name)}\s*\("


def _contains_function(text, function_name):
    """
    Verifica se determinada função aparece no texto.
    """

    return bool(
        re.search(
            _function_pattern(function_name),
            text,
            re.IGNORECASE
        )
    )


def _contains_any_dangerous_execution_function(text):
    """
    Verifica se o texto menciona funções de execução dinâmica.
    """

    for function_name in DANGEROUS_EXECUTION_FUNCTIONS:

        if _contains_function(
            text,
            function_name
        ):
            return True

    return False


def _looks_like_recommendation(text, function_name):
    """
    Determina se uma função perigosa está sendo mencionada
    como recomendação.

    A função não bloqueia simplesmente qualquer menção a
    shell_exec(), exec(), etc.

    Exemplo permitido:

        "O finding identifica o uso de shell_exec()."

    Exemplo bloqueado:

        "Use shell_exec() como solução."

    """

    normalized = _normalize_text(text)

    function_regex = _function_pattern(
        function_name
    )

    for recommendation_word in RECOMMENDATION_WORDS:

        pattern = (
            rf"{re.escape(recommendation_word)}"
            rf".{{0,100}}"
            rf"{function_regex}"
        )

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE
        ):
            return True

    return False


def _contains_function_as_remediation(text):
    """
    Detecta funções perigosas apresentadas como remediação.
    """

    for function_name in DANGEROUS_EXECUTION_FUNCTIONS:

        if _looks_like_recommendation(
            text,
            function_name
        ):
            return True

    return False


# ============================================================
# DETECÇÃO DE SUBSTITUIÇÕES PERIGOSAS
# ============================================================

def _contains_dangerous_substitution(text):
    """
    Detecta construções como:

        substitua exec() por shell_exec()
        use shell_exec() em vez de exec()
        troque exec() por system()
        substituir eval() por ...
    """

    normalized = _normalize_text(text)

    dangerous_functions = [
        re.escape(function)
        for function in DANGEROUS_EXECUTION_FUNCTIONS
    ]

    functions_pattern = (
        r"(?:"
        + "|".join(dangerous_functions)
        + r")\s*\("
    )

    substitution_patterns = [

        # substitua X por Y
        rf"(?:substitua|substituir|troque|trocar)"
        rf".{{0,120}}"
        rf"{functions_pattern}"
        rf".{{0,120}}"
        rf"(?:por|para)"
        rf".{{0,120}}"
        rf"{functions_pattern}",

        # use X em vez de Y
        rf"(?:use|usar|utilize|utilizar)"
        rf".{{0,120}}"
        rf"{functions_pattern}"
        rf".{{0,120}}"
        rf"(?:em vez de|no lugar de)"
        rf".{{0,120}}"
        rf"{functions_pattern}",

        # X é uma alternativa segura
        rf"{functions_pattern}"
        rf".{{0,100}}"
        rf"(?:seguro|segura|mais seguro|mais segura|alternativa)",

        # X pode ser utilizado como solução
        rf"{functions_pattern}"
        rf".{{0,100}}"
        rf"(?:solucao|correcao|remediacao)",
    ]

    for pattern in substitution_patterns:

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# DETECÇÃO DE BYPASS
# ============================================================

def _contains_security_bypass(text):
    """
    Detecta recomendações explícitas para desabilitar ou
    contornar mecanismos de segurança.
    """

    normalized = _normalize_text(text)

    bypass_patterns = [

        r"desabilite.{0,80}(validacao|autenticacao|autorizacao|seguranca)",

        r"desative.{0,80}(validacao|autenticacao|autorizacao|seguranca)",

        r"ignore.{0,80}(validacao|autenticacao|autorizacao|seguranca)",

        r"remova.{0,80}(validacao|autenticacao|autorizacao)",

        r"bypass.{0,100}(seguranca|autenticacao|autorizacao)",

        r"contorne.{0,100}(seguranca|autenticacao|autorizacao)",

        r"ignore.{0,100}controle de acesso",

        r"desabilitar.{0,100}controle de acesso",
    ]

    for pattern in bypass_patterns:

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# DETECÇÃO DE RECOMENDAÇÕES DE EXECUÇÃO DE INPUT
# ============================================================

def _contains_unsafe_input_execution(text):
    """
    Detecta recomendações para executar entrada controlada
    pelo usuário.
    """

    normalized = _normalize_text(text)

    execution_terms = (
        "exec",
        "shell_exec",
        "system",
        "passthru",
        "proc_open",
        "popen",
        "eval",
    )

    input_terms = (
        "entrada do usuario",
        "input do usuario",
        "dados do usuario",
        "entrada fornecida pelo usuario",
        "dados fornecidos pelo usuario",
        "input fornecido pelo usuario",
        "parametro do usuario",
        "parametros do usuario",
        "dados nao confiaveis",
        "entrada nao confiavel",
    )

    for execution in execution_terms:

        for user_input in input_terms:

            pattern = (
                rf"{re.escape(execution)}"
                rf".{{0,150}}"
                rf"{re.escape(user_input)}"
                rf"|"
                rf"{re.escape(user_input)}"
                rf".{{0,150}}"
                rf"{re.escape(execution)}"
            )

            if re.search(
                pattern,
                normalized,
                re.IGNORECASE
            ):
                return True

    return False


# ============================================================
# VALIDAÇÃO DA RESPOSTA
# ============================================================

def validate_ai_response(response):
    """
    Valida a resposta da IA antes que ela seja armazenada.

    Retorna:

        (True, "")

    quando a resposta é aceitável.

    Retorna:

        (False, motivo)

    quando a resposta viola alguma regra.
    """

    if not response:
        return (
            False,
            "A IA retornou uma resposta vazia."
        )

    response = response.strip()

    if len(response) < 30:
        return (
            False,
            "A resposta da IA é muito curta."
        )

    normalized = _normalize_text(
        response
    )

    # --------------------------------------------------------
    # SEÇÕES OBRIGATÓRIAS
    # --------------------------------------------------------

    required_sections = (
        "resumo",
        "impacto",
        "remediacao",
    )

    missing_sections = []

    for section in required_sections:

        if section not in normalized:
            missing_sections.append(
                section
            )

    if missing_sections:

        return (
            False,
            "Seções obrigatórias ausentes: "
            + ", ".join(missing_sections)
        )

    # --------------------------------------------------------
    # SEÇÃO DE REMEDIAÇÃO
    # --------------------------------------------------------

    remediation_match = re.search(
        r"remediacao\s*:?(.*)",
        normalized,
        re.IGNORECASE
    )

    remediation_text = ""

    if remediation_match:
        remediation_text = remediation_match.group(1)


    # --------------------------------------------------------
    # REMEDIAÇÕES AMBÍGUAS ENVOLVENDO COMANDOS
    # --------------------------------------------------------

    for pattern in AMBIGUOUS_COMMAND_REMEDIATION_PATTERNS:

        if re.search(
            pattern,
            remediation_text,
            re.IGNORECASE
        ):

            return (
                False,
                "A remediação contém uma recomendação "
                "ambígua relacionada à execução de comandos."
            )



    # --------------------------------------------------------
    # SUBSTITUIÇÕES PERIGOSAS
    # --------------------------------------------------------

    if _contains_dangerous_substitution(
        remediation_text
    ):

        return (
            False,
            "A remediação recomenda substituir "
            "uma função de execução por outra."
        )

    # --------------------------------------------------------
    # FUNÇÕES DE EXECUÇÃO COMO RECOMENDAÇÃO
    # --------------------------------------------------------

    if _contains_function_as_remediation(
        remediation_text
    ):

        return (
            False,
            "A remediação recomenda uma função "
            "de execução dinâmica ou shell."
        )

    # --------------------------------------------------------
    # BYPASS DE SEGURANÇA
    # --------------------------------------------------------

    if _contains_security_bypass(
        remediation_text
    ):

        return (
            False,
            "A remediação recomenda desabilitar "
            "ou contornar controles de segurança."
        )

    # --------------------------------------------------------
    # EXECUÇÃO DE INPUT NÃO CONFIÁVEL
    # --------------------------------------------------------

    if _contains_unsafe_input_execution(
        remediation_text
    ):

        return (
            False,
            "A remediação associa execução de "
            "comandos a entrada potencialmente não confiável."
        )

    return True, ""


# ============================================================
# FALLBACK SEGURO
# ============================================================

def _safe_fallback_response():
    """
    Resposta conservadora utilizada quando a IA não produz
    uma recomendação que passe pela validação.
    """

    return """
Resumo:

Foram identificados problemas de segurança nos findings associados
a este risco. A análise automática não conseguiu produzir uma
recomendação de remediação suficientemente segura e específica.

Impacto:

O impacto depende da vulnerabilidade identificada, do componente
afetado, da exposição do recurso e das condições necessárias para
exploração.

Remediação:

Revise os findings individualmente e aplique a correção específica
indicada pela documentação oficial da tecnologia afetada. Evite
executar código ou comandos a partir de entradas não confiáveis,
utilize validação e allowlists quando aplicáveis e aplique o
princípio do menor privilégio. Quando os dados disponíveis não forem
suficientes para determinar a correção exata, realize uma revisão
manual antes de aplicar qualquer alteração.
""".strip()


# ============================================================
# CONSTRUÇÃO DO PROMPT
# ============================================================

def _build_prompt(
    risk,
    findings,
    strict=False
):
    """
    Constrói o prompt enviado ao Ollama.
    """

    findings_text = ""

    for index, finding in enumerate(
        findings,
        start=1
    ):

        findings_text += f"""
Finding {index}:

Fonte:
{getattr(finding, "source", None)}

Tipo:
{getattr(finding, "type", None)}

Título:
{getattr(finding, "title", None)}

Descrição:
{getattr(finding, "description", None)}

Arquivo:
{getattr(finding, "file", None)}

Linha:
{getattr(finding, "line", None)}

CVE:
{getattr(finding, "cve", None)}

CVSS:
{getattr(finding, "cvss", None)}

Pacote:
{getattr(finding, "package_name", None)}

Versão instalada:
{getattr(finding, "installed_version", None)}

Versão corrigida:
{getattr(finding, "fixed_version", None)}
"""

    strict_instruction = ""

    if strict:

        strict_instruction = """
A resposta anterior foi rejeitada pela camada de segurança.

Produza uma nova resposta ainda mais conservadora.

REGRAS ABSOLUTAS:

- NÃO recomende eval().
- NÃO recomende exec().
- NÃO recomende shell_exec().
- NÃO recomende system().
- NÃO recomende passthru().
- NÃO recomende proc_open().
- NÃO recomende popen().
- NÃO recomende pcntl_exec().
- NÃO recomende trocar uma função de execução por outra.
- NÃO apresente nenhuma dessas funções como alternativa "segura".
- NÃO recomende executar entrada controlada pelo usuário.
- NÃO recomende desabilitar autenticação.
- NÃO recomende desabilitar autorização.
- NÃO recomende desabilitar validações.
- NÃO recomende ignorar controles de segurança.
- NÃO invente bibliotecas.
- NÃO invente versões.
- NÃO invente CVEs.
- NÃO invente APIs.
- NÃO invente arquivos ou linhas.
- NÃO invente correções específicas que não possam ser sustentadas
  pelos findings.

Quando uma vulnerabilidade envolver execução de comandos:

- prefira evitar shell quando possível;
- prefira APIs específicas da aplicação quando existirem;
- valide e restrinja entradas;
- utilize allowlists quando aplicável;
- mantenha argumentos separados do comando quando a tecnologia
  permitir;
- aplique o princípio do menor privilégio;
- remova a necessidade de executar entrada controlada pelo usuário;
- consulte a documentação oficial quando a correção depender da
  tecnologia específica.

Se não houver informação suficiente para recomendar uma correção
específica, diga explicitamente que é necessária revisão manual.
"""

    prompt = f"""
Você é um especialista em Application Security e Application
Security Posture Management (ASPM).

Analise o risco utilizando EXCLUSIVAMENTE os findings fornecidos.

Não invente informações.

Não faça suposições não sustentadas pelos findings.

Não invente CVEs, versões, bibliotecas, APIs, arquivos, linhas ou
detalhes da aplicação.

O objetivo é produzir uma análise técnica conservadora.

IMPORTANTE:

Mencionar uma função vulnerável na descrição do problema é diferente
de recomendar essa função como solução.

Uma função de execução de comandos não deve ser considerada segura
simplesmente porque outra função de execução foi utilizada.

Por exemplo, estas recomendações são INACEITÁVEIS:

- substituir exec() por shell_exec();
- substituir exec() por system();
- substituir exec() por passthru();
- substituir eval() por outra função de execução;
- utilizar shell_exec() como alternativa segura;
- utilizar system() como alternativa segura;
- executar entrada fornecida pelo usuário;
- desabilitar mecanismos de segurança.

Não forneça código de correção quando os findings não forem
suficientes para determinar uma implementação segura.

DADOS DO RISCO:

Título:
{getattr(risk, "title", None)}

Severidade:
{getattr(risk, "severity", None)}

Score:
{getattr(risk, "score", None)}

Prioridade:
{getattr(risk, "priority", None)}

Quantidade de evidências:
{len(findings)}

FINDINGS:

{findings_text}

{strict_instruction}

RESPONDA EM PORTUGUÊS.

Utilize exatamente estas três seções:

Resumo:

Impacto:

Remediação:

Não crie outras seções.

A seção Remediação deve conter apenas recomendações tecnicamente
seguras e sustentadas pelos findings.
"""

    return prompt.strip()


# ============================================================
# CONSULTA AO OLLAMA
# ============================================================

def _request_ollama(prompt):
    """
    Executa a chamada ao Ollama.
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": AI_TEMPERATURE,
        },
        timeout=AI_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    ai_response = data.get(
        "response"
    )

    if not ai_response:

        raise RuntimeError(
            "O Ollama não retornou o campo 'response'."
        )

    return ai_response.strip()


# ============================================================
# ANÁLISE PRINCIPAL
# ============================================================

def analyze_risk(
    risk,
    findings
):
    """
    Gera uma análise de IA para um risco.

    Fluxo:

        primeira geração
              ↓
          validação
          ↙      ↘
        OK      rejeitada
        ↓          ↓
      retorna   segunda geração
                    ↓
                validação
                 ↙     ↘
               OK     rejeitada
               ↓          ↓
             retorna    fallback
    """

    risk_id = getattr(
        risk,
        "id",
        "desconhecido"
    )

    print(
        f"Gerando análise de IA para o risco {risk_id}..."
    )

    # --------------------------------------------------------
    # PRIMEIRA TENTATIVA
    # --------------------------------------------------------

    prompt = _build_prompt(
        risk,
        findings,
        strict=False
    )

    try:

        first_response = _request_ollama(
            prompt
        )

    except requests.RequestException as error:

        print(
            "ERRO AO CONSULTAR O OLLAMA:",
            repr(error)
        )

        raise RuntimeError(
            "Não foi possível consultar o serviço de IA."
        ) from error

    except Exception as error:

        print(
            "ERRO NA IA:",
            repr(error)
        )

        raise

    # --------------------------------------------------------
    # VALIDA PRIMEIRA RESPOSTA
    # --------------------------------------------------------

    is_valid, reason = validate_ai_response(
        first_response
    )

    if is_valid:

        print(
            "Resposta da IA aprovada pela validação."
        )

        return first_response

    print(
        "Resposta da IA rejeitada:",
        reason
    )

    # --------------------------------------------------------
    # SEGUNDA TENTATIVA
    # --------------------------------------------------------

    print(
        "Solicitando uma nova resposta "
        "com restrições adicionais..."
    )

    strict_prompt = _build_prompt(
        risk,
        findings,
        strict=True
    )

    try:

        second_response = _request_ollama(
            strict_prompt
        )

    except requests.RequestException as error:

        print(
            "ERRO NA SEGUNDA CONSULTA AO OLLAMA:",
            repr(error)
        )

        print(
            "Utilizando fallback seguro."
        )

        return _safe_fallback_response()

    except Exception as error:

        print(
            "ERRO NA SEGUNDA ANÁLISE:",
            repr(error)
        )

        print(
            "Utilizando fallback seguro."
        )

        return _safe_fallback_response()

    # --------------------------------------------------------
    # VALIDA SEGUNDA RESPOSTA
    # --------------------------------------------------------

    is_valid, second_reason = validate_ai_response(
        second_response
    )

    if is_valid:

        print(
            "Segunda resposta da IA aprovada."
        )

        return second_response

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    print(
        "Segunda resposta da IA também foi rejeitada:",
        second_reason
    )

    print(
        "Utilizando fallback seguro."
    )

    return _safe_fallback_response()