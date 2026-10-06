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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS

from app.tasks.scan_task import scan_repository as scan_repository_task

from app.services.scan_history_service import get_all_scans
from app.services.finding_history_service import get_findings_by_scan
from app.services.scan_compare_service import compare_scan
from app.services.risk_queries import (
    get_all_risks,
    get_risk_by_id,
    get_findings_by_risk
)
from app.services.ai_analysis_service import (
    analyze_risk_with_ai,
    get_analysis_by_risk
)
from app.tasks.task_status import (
    get_task_status
)
from app.security.url_validator import (
    validate_repository_url,
    InvalidRepositoryURL
)
from app.services.scheduled_scan_service import (
    create_scheduled_scan,
    get_scheduled_scans,
    get_scheduled_scan,
    update_scheduled_scan,
    delete_scheduled_scan,
)


from app.websocket.routes import router as websocket_router


from sqlalchemy import func, or_
from app.database.session import SessionLocal
from app.models.scan import Scan
from app.models.finding import Finding
from app.models.asset import Asset
from app.models.risk import Risk


app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)

app.include_router(
    websocket_router
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception
):
    print(
        "ERRO INTERNO:",
        repr(exc)
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor."
        }
    )


@app.post("/")
def start_scan(repo_url: str):

    try:
        repo_url= validate_repository_url(repo_url)

    except InvalidRepositoryURL as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    task = scan_repository_task.delay(
        repo_url
    )

    return {
        "message": "Scan iniciado.",
        "task_id": task.id
    }


@app.get("/scans")
def list_scan():

    return get_all_scans()


@app.get("/scans/{scan_id}/findings")
def list_findings(scan_id: int):

    return get_findings_by_scan(scan_id)


@app.get("/findings")
def list_all_findings():

    db = SessionLocal()

    try:

        findings = (
            db.query(Finding)
            .order_by(Finding.id.desc())
            .all()
        )

        return [
            {
                "id": finding.id,
                "scan_id": finding.scan_id,
                "source": finding.source,
                "severity": finding.severity,
                "type": finding.type,
                "title": finding.title,
                "description": finding.description,
                "file": finding.file,
                "line": finding.line,
                "package_name": finding.package_name,
                "installed_version": finding.installed_version,
                "fixed_version": finding.fixed_version,
                "risk_score": finding.risk_score,
                "status": finding.status,
                "cve": getattr(finding, "cve", None),
                "cvss": getattr(finding, "cvss", None),
                "cwe": getattr(finding, "cwe", None),
                "owasp": getattr(finding, "owasp", None),
                "category": getattr(finding, "category", None),
                "rule_id": getattr(finding, "rule_id", None),
            }
            for finding in findings
        ]

    finally:

        db.close()


@app.get("/scans/{scan_id}/compare")
def compare_scan_endpoint(scan_id: int):

    return compare_scan(scan_id)


@app.get("/tasks/{task_id}")
def task_status(task_id: str):

    return get_task_status(
        task_id
    )


@app.get("/risks")
def list_risks():

    return get_all_risks()


@app.get("/risks/{risk_id}")
def risk_details(risk_id:  int):

    return get_risk_by_id(
        risk_id
    )


@app.get("/risks/{risk_id}/findings")
def risk_findings(risk_id: int):

    return get_findings_by_risk(
        risk_id
    )


@app.post("/risk/{risk_id}/analyze")
def analyze_risk_endpoint(
    risk_id: int
):
    
    return analyze_risk_with_ai(
        risk_id
    )


@app.get("/risk/{risk_id}/analysis")
def get_risk_analysis_endpoint(
    risk_id: int
):
    analysis = get_analysis_by_risk(risk_id)

    if not analysis:
        return {
            "analysis": None
        }

    return {
        "id": analysis.id,
        "risk_id": analysis.risk_id,
        "summary": analysis.summary,
        "impact": analysis.impact,
        "remediation": analysis.remediation,
        "created_at": analysis.created_at
    }


@app.get("/scheduled-scans")
def list_scheduled_scans():
    scheduled_scans = get_scheduled_scans()

    return [
        {
            "id": item.id,
            "repository_url": item.repository_url,
            "enabled": item.enabled,
            "interval_minutes": item.interval_minutes,
            "last_started_at": item.last_started_at,
            "last_finished_at": item.last_finished_at,
            "next_run_at": item.next_run_at,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        for item in scheduled_scans
    ]


@app.post("/scheduled-scans")
def create_scheduled_scan_route(
    repository_url: str,
    interval_minutes: int,
):
    try:
        scheduled_scan = create_scheduled_scan(
            repository_url=repository_url,
            interval_minutes=interval_minutes,
        )

        return {
            "message": "Agendamento criado com sucesso.",
            "scheduled_scan": {
                "id": scheduled_scan.id,
                "repository_url": scheduled_scan.repository_url,
                "enabled": scheduled_scan.enabled,
                "interval_minutes": scheduled_scan.interval_minutes,
                "next_run_at": scheduled_scan.next_run_at,
            },
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.patch("/scheduled-scans/{scheduled_scan_id}")
def update_scheduled_scan_route(
    scheduled_scan_id: int,
    interval_minutes: int | None = None,
    enabled: bool | None = None,
):
    try:
        scheduled_scan = update_scheduled_scan(
            scheduled_scan_id=scheduled_scan_id,
            interval_minutes=interval_minutes,
            enabled=enabled,
        )

        if not scheduled_scan:
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado.",
            )

        return {
            "message": "Agendamento atualizado com sucesso.",
            "scheduled_scan": {
                "id": scheduled_scan.id,
                "repository_url": scheduled_scan.repository_url,
                "enabled": scheduled_scan.enabled,
                "interval_minutes": scheduled_scan.interval_minutes,
                "next_run_at": scheduled_scan.next_run_at,
            },
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.delete("/scheduled-scans/{scheduled_scan_id}")
def delete_scheduled_scan_route(scheduled_scan_id: int):
    deleted = delete_scheduled_scan(scheduled_scan_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado.",
        )

    return {
        "message": "Agendamento removido com sucesso."
    }


@app.get("/dashboard")
def dashboard():

    db = SessionLocal()

    try:

        total_scans = db.query(Scan).count()

        total_findings = db.query(Finding).count()

        total_assets = db.query(Asset).count()

        total_risks = db.query(Risk).count()

        return {

            "total_scans": total_scans,

            "total_findings": total_findings,

            "total_assets": total_assets,

            "total_risks": total_risks

        }

    finally:

        db.close()


def _normalize_severity(value):
    """
    Padroniza a severidade para o mesmo critério usado nas telas:
    - ERROR (Semgrep) conta como CRITICAL
    - Informational (ZAP) conta como INFO
    - maiúsculas/minúsculas não importam
    """
    severity = (value or "").strip().upper()

    if severity == "ERROR":
        return "CRITICAL"

    if severity == "INFORMATIONAL":
        return "INFO"

    return severity or "UNKNOWN"


def _count_findings_by_severity(db, only_open=False):
    """
    Conta findings por severidade já padronizada.
    only_open=True ignora os corrigidos (status "fixed"), mas mantém
    os que estão com status vazio (NULL).
    """
    query = db.query(
        Finding.severity,
        func.count(Finding.id)
    )

    if only_open:
        query = query.filter(
            or_(
                Finding.status.is_(None),
                Finding.status != "fixed"
            )
        )

    counts = {}

    for severity, total in query.group_by(Finding.severity).all():
        key = _normalize_severity(severity)
        counts[key] = counts.get(key, 0) + total

    return counts


@app.get("/dashboard/severity")
def dashboard_severity():

    db = SessionLocal()

    try:
        counts = _count_findings_by_severity(db)

        severities = [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "WARNING",
            "LOW",
            "INFO"
        ]

        return [
            {
                "severity": severity,
                "count": counts.get(severity, 0)
            }
            for severity in severities
        ]

    finally:
        db.close()


@app.get("/dashboard/scans-history")
def dashboard_scans_history():

    db = SessionLocal()

    try:
        scans = (
            db.query(
                func.date(Scan.created_at).label("date"),
                func.count(Scan.id).label("total")
            )
            .group_by(func.date(Scan.created_at))
            .order_by(func.date(Scan.created_at))
            .all()
        )

        return [
            {
                "date": str(scan.date),
                "total": scan.total
            }
            for scan in scans
        ]

    finally:
        db.close()


@app.get("/dashboard/top-risks")
def dashboard_top_risks():

    db = SessionLocal()

    try:
        risks = (
            db.query(Risk)
            .order_by(Risk.score.desc())
            .limit(10)
            .all()
        )

        return risks

    finally:
        db.close()


@app.get("/dashboard/top-packages")
def dashboard_top_packages():

    db = SessionLocal()

    try:
        data = (
            db.query(
                Finding.package_name,
                func.count(Finding.id).label("total")
            )
            .filter(Finding.package_name != None)
            .group_by(Finding.package_name)
            .order_by(func.count(Finding.id).desc())
            .limit(10)
            .all()
        )

        return [
            {
                "package": item.package_name,
                "total": item.total
            }
            for item in data
        ]

    finally:
        db.close()


@app.get("/dashboard/assets")
def dashboard_assets():

    db = SessionLocal()

    try:
        assets = (
            db.query(
                Asset.asset_type,
                func.count(Asset.id)
            )
            .group_by(Asset.asset_type)
            .all()
        )

        return [
            {
                "type": a[0],
                "total": a[1]
            }
            for a in assets
        ]

    finally:
        db.close()


@app.get("/dashboard/security-score")
def dashboard_security_score():

    db = SessionLocal()

    try:
        counts = _count_findings_by_severity(
            db,
            only_open=True
        )

        critical = counts.get("CRITICAL", 0)
        high = counts.get("HIGH", 0)
        medium = counts.get("MEDIUM", 0)
        low = counts.get("LOW", 0)
        warning = counts.get("WARNING", 0)

        score = 100

        score -= critical * 5
        score -= high * 3
        score -= medium * 1.5
        score -= low * 0.3
        score -= warning * 0.05

        score = max(
            0,
            min(
                100,
                round(score)
            )
        )

        if score >= 90:
            status = "Excellent"
        elif score >= 70:
            status = "Good"
        elif score >= 50:
            status = "Medium"
        else:
            status = "Poor"

        return {
            "score": score,
            "status": status,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "warning": warning
        }

    finally:
        db.close()
