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

from app.database.session import SessionLocal

from app.models.risk import Risk
from app.models.finding import Finding
from app.models.ai_analysis import AIAnalysis

from app.services.ai_service import (
    analyze_risk,
    validate_ai_response,
)


# ============================================================
# BUSCAR RISCO
# ============================================================

def get_risk(db, risk_id):

    return (
        db.query(Risk)
        .filter(
            Risk.id == risk_id
        )
        .first()
    )


# ============================================================
# BUSCAR FINDINGS DO RISCO
# ============================================================

def get_risk_findings(db, risk_id):

    return (
        db.query(Finding)
        .filter(
            Finding.risk_id == risk_id
        )
        .all()
    )


# ============================================================
# SALVAR ANÁLISE
# ============================================================

def save_analysis(
    db,
    risk_id,
    summary,
    impact,
    remediation
):

    analysis = AIAnalysis(
        risk_id=risk_id,
        summary=summary,
        impact=impact,
        remediation=remediation
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


# ============================================================
# VALIDAR ANÁLISE EXISTENTE
# ============================================================

def existing_analysis_is_valid(
    analysis
):
    """
    Verifica se uma análise antiga continua válida.

    A análise é convertida para o mesmo formato esperado
    pelo validador da IA.
    """

    if not analysis:
        return False

    summary = analysis.summary or ""
    impact = analysis.impact or ""
    remediation = analysis.remediation or ""

    combined_response = f"""
Resumo:

{summary}

Impacto:

{impact}

Remediação:

{remediation}
"""

    is_valid, reason = validate_ai_response(
        combined_response
    )

    if not is_valid:

        print(
            "Análise existente considerada inválida:"
        )

        print(
            reason
        )

        return False

    return True


# ============================================================
# PARSER DA RESPOSTA DA IA
# ============================================================

def parse_ai_response(response):

    summary = ""
    impact = ""
    remediation = ""

    current = None

    for line in response.splitlines():

        line = line.strip()

        if not line:
            continue

        clean = (
            line
            .replace("*", "")
            .replace("#", "")
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        if clean.startswith("resumo"):

            current = "summary"

            content = line.split(
                ":",
                1
            )

            if len(content) == 2:
                summary += (
                    content[1].strip()
                    + "\n"
                )

            continue

        # ----------------------------------------------------
        # IMPACTO
        # ----------------------------------------------------

        if clean.startswith("impacto"):

            current = "impact"

            content = line.split(
                ":",
                1
            )

            if len(content) == 2:
                impact += (
                    content[1].strip()
                    + "\n"
                )

            continue

        # ----------------------------------------------------
        # REMEDIAÇÃO
        # ----------------------------------------------------

        if (
            clean.startswith("remediacao")
            or clean.startswith("remediação")
        ):

            current = "remediation"

            content = line.split(
                ":",
                1
            )

            if len(content) == 2:
                remediation += (
                    content[1].strip()
                    + "\n"
                )

            continue

        # ----------------------------------------------------
        # CONTEÚDO
        # ----------------------------------------------------

        if current == "summary":

            summary += (
                line
                + "\n"
            )

        elif current == "impact":

            impact += (
                line
                + "\n"
            )

        elif current == "remediation":

            remediation += (
                line
                + "\n"
            )

    return {
        "summary": summary.strip(),
        "impact": impact.strip(),
        "remediation": remediation.strip(),
    }


# ============================================================
# ANALISAR RISCO COM IA
# ============================================================

def analyze_risk_with_ai(
    risk_id
):

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # BUSCAR RISCO
        # ----------------------------------------------------

        risk = get_risk(
            db,
            risk_id
        )

        if not risk:

            raise Exception(
                "Risk não encontrado."
            )

        # ----------------------------------------------------
        # BUSCAR FINDINGS
        # ----------------------------------------------------

        findings = get_risk_findings(
            db,
            risk_id
        )

        # ----------------------------------------------------
        # VERIFICAR ANÁLISE EXISTENTE
        # ----------------------------------------------------

        existing_analysis = (
            db.query(AIAnalysis)
            .filter(
                AIAnalysis.risk_id == risk_id
            )
            .first()
        )

        if existing_analysis:

            print(
                "Análise existente encontrada."
            )

            # ----------------------------------------------
            # VALIDAR ANÁLISE EXISTENTE
            # ----------------------------------------------

            if existing_analysis_is_valid(
                existing_analysis
            ):

                print(
                    "Análise existente aprovada "
                    "pela validação."
                )

                return existing_analysis

            # ----------------------------------------------
            # ANÁLISE ANTIGA INVÁLIDA
            # ----------------------------------------------

            print(
                "Análise existente inválida."
            )

            print(
                "Gerando nova análise de IA..."
            )

            # Removemos a análise antiga.
            db.delete(
                existing_analysis
            )

            db.commit()

        # ----------------------------------------------------
        # GERAR NOVA ANÁLISE
        # ----------------------------------------------------

        print(
            f"Gerando análise de IA para o risco "
            f"{risk_id}..."
        )

        ai_response = analyze_risk(
            risk,
            findings
        )

        # ----------------------------------------------------
        # LOG DA RESPOSTA
        # ----------------------------------------------------

        print(
            "===== RESPOSTA DA IA ====="
        )

        print(
            ai_response
        )

        print(
            "=========================="
        )

        # ----------------------------------------------------
        # VALIDAÇÃO FINAL
        # ----------------------------------------------------

        is_valid, reason = validate_ai_response(
            ai_response
        )

        if not is_valid:

            print(
                "ERRO: resposta da IA não passou "
                "na validação:"
            )

            print(
                reason
            )

            raise RuntimeError(
                "A resposta da IA não passou "
                "na validação de segurança."
            )

        # ----------------------------------------------------
        # PARSE
        # ----------------------------------------------------

        analysis = parse_ai_response(
            ai_response
        )

        print(
            "===== ANÁLISE PARSED ====="
        )

        print(
            "SUMMARY:",
            analysis["summary"]
        )

        print(
            "IMPACT:",
            analysis["impact"]
        )

        print(
            "REMEDIATION:",
            analysis["remediation"]
        )

        print(
            "=========================="
        )

        # ----------------------------------------------------
        # VERIFICAR CAMPOS PARSED
        # ----------------------------------------------------

        if not analysis["summary"]:

            raise RuntimeError(
                "A IA não retornou um resumo válido."
            )

        if not analysis["impact"]:

            raise RuntimeError(
                "A IA não retornou um impacto válido."
            )

        if not analysis["remediation"]:

            raise RuntimeError(
                "A IA não retornou uma remediação válida."
            )

        # ----------------------------------------------------
        # SALVAR
        # ----------------------------------------------------

        saved_analysis = save_analysis(
            db=db,
            risk_id=risk.id,
            summary=analysis["summary"],
            impact=analysis["impact"],
            remediation=analysis["remediation"],
        )

        return saved_analysis

    finally:

        db.close()


# ============================================================
# BUSCAR ANÁLISE EXISTENTE
# ============================================================

def get_analysis_by_risk(
    risk_id
):

    db = SessionLocal()

    try:

        analysis = (
            db.query(AIAnalysis)
            .filter(
                AIAnalysis.risk_id == risk_id
            )
            .first()
        )

        if not analysis:
            return None

        if not existing_analysis_is_valid(
            analysis
        ):
            print(
                f"Análise {analysis.id}"
                f"considerada inválida."
            )

            return None
        
        return analysis

    finally:

        db.close()