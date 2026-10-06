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

from app.celery_app import celery_app
from celery import current_task
from datetime import datetime, timedelta
from app.database.session import SessionLocal
from app.models.scheduled_scan import ScheduledScan


import shutil
import json
import os

from app.github.clone import clone_repository

from app.scanners.url_scanner import scan_urls
from app.scanners.docker_scanners import scan_docker
from app.scanners.pipeline_scanners import scan_pipelines
from app.scanners.secret_scanners import scan_secrets

from app.services.scan_service import (
    create_scan,
    update_scan_status
)

from app.services.finding_service import save_findings_db
from app.services.asset_service import save_assets_db

from app.services.finding_status_service import (
    get_previous_scan,
    get_findings_from_scan,
    compare_findings
)

from app.services.fixed_finding_service import (
    create_fixed_findings
)

from app.services.risk_service import (
    correlate_findings
)

from app.websocket.events import send_progress

# Semgrep
from app.integrations.semgrep.runner import run_semgrep
from app.normalizers.semgrep_normalizer import normalize_semgrep
from app.findings.findings_manager import save_findings

# Trivy
from app.integrations.trivy.runner import run_trivy
from app.normalizers.trivy_normalizer import normalize_trivy

# ZAP
from app.integrations.zap.runner import run_zap
from app.normalizers.zap_normalizer import normalize_zap
from app.config import ZAP_TARGET_URL


def update_progress(progress, message):
    current_task.update_state(
        state="PROGRESS",
        meta={
            "progress": progress,
            "message": message
        }
    )

    send_progress(
        current_task.request.id,
        progress,
        message
    )


@celery_app.task
def scan_repository(repo_url, scheduled_scan_id=None):

    print("ENTROU NA ROTA")

    scan_id = None
    repo_path = None

    try:
        # --------------------------------------------------
        # 1. CRIA SCAN
        # --------------------------------------------------

        scan_id = create_scan(repo_url)

        print("SCAN ID:", scan_id)

        update_progress(
            5,
            "Criando scan"
        )

        # --------------------------------------------------
        # 2. CLONA REPOSITÓRIO
        # --------------------------------------------------

        repo_path = clone_repository(repo_url)

        print("REPO PATH:", repo_path)
        print(
            "EXISTE?",
            os.path.exists(repo_path)
        )

        update_progress(
            10,
            "Clonando repositório"
        )

        # --------------------------------------------------
        # 3. DESCOBERTA DE ASSETS
        # --------------------------------------------------

        urls = scan_urls(repo_path)

        save_assets_db(
            scan_id,
            "url",
            urls
        )

        docker_asset = scan_docker(repo_path)

        save_assets_db(
            scan_id,
            "docker",
            docker_asset
        )

        pipelines = scan_pipelines(repo_path)

        save_assets_db(
            scan_id,
            "pipeline",
            pipelines
        )

        secrets = scan_secrets(repo_path)

        update_progress(
            25,
            "Descobrindo ativos"
        )

        # --------------------------------------------------
        # 4. SEMGREP
        # --------------------------------------------------

        raw_findings = run_semgrep(repo_path)

        if raw_findings.get("results"):

            print(
                "===== PRIMEIRO FINDING SEMGREP ====="
            )

            print(
                json.dumps(
                    raw_findings["results"][0],
                    indent=2
                )
            )

        normalized_findings = normalize_semgrep(
            raw_findings
        )

        update_progress(
            45,
            "Executando Semgrep"
        )

        # --------------------------------------------------
        # 5. TRIVY
        # --------------------------------------------------

        raw_trivy = run_trivy(repo_path)

        if raw_trivy.get("Results"):

            for result in raw_trivy["Results"]:

                vulns = result.get(
                    "Vulnerabilities",
                    []
                )

                if vulns:

                    print(
                        "===== PRIMEIRA VULNERABILIDADE TRIVY ====="
                    )

                    print(
                        json.dumps(
                            vulns[0],
                            indent=2
                        )
                    )

                break

        normalized_trivy = normalize_trivy(
            raw_trivy
        )

        update_progress(
            60,
            "Executando Trivy"
        )

        # --------------------------------------------------
        # 6. ZAP
        # --------------------------------------------------

        print(
            "===== EXECUTANDO ZAP ====="
        )

        zap_target_url = ZAP_TARGET_URL

        normalized_zap = []

        if zap_target_url:

            print(
                "ALVO ZAP",
                zap_target_url
            )

            raw_zap = run_zap(
                zap_target_url
            )

            normalized_zap = normalize_zap(
                raw_zap.get("alerts", [])
            )

            update_progress(
                70,
                "Executando ZAP"
            )

        else:

            print(
                "ZAP IGNORADO:"
                "ZAP_TARGET_URL não configurado."

            )
            
        # --------------------------------------------------
        # 7. JUNTA FINDINGS
        # --------------------------------------------------

        all_findings = (
            normalized_findings
            + normalized_trivy
            + normalized_zap
        )

        # --------------------------------------------------
        # 8. CORRELAÇÃO DE RISCOS
        # --------------------------------------------------

        all_findings = correlate_findings(
            all_findings
        )

        update_progress(
            75,
            "Correlacionando riscos"
        )

        # --------------------------------------------------
        # 9. COMPARAÇÃO COM SCAN ANTERIOR
        # --------------------------------------------------

        previous_scan = get_previous_scan(
            repo_url,
            scan_id
        )

        if previous_scan:

            previous_findings = get_findings_from_scan(
                previous_scan.id
            )

            fixed_keys = compare_findings(
                previous_findings,
                all_findings
            )

            print(
                "FINDINGS CORRIGIDOS:",
                len(fixed_keys)
            )

            fixed_findings = create_fixed_findings(
                fixed_keys
            )

            update_progress(
                85,
                "Comparando histórico"
            )

            all_findings.extend(
                fixed_findings
            )

        else:

            print(
                "Primeiro scan do repositório"
            )

        # --------------------------------------------------
        # 10. SALVA FINDINGS
        # --------------------------------------------------

        save_findings(
            all_findings,
            scan_id
        )

        print(
            "===== CVSS TESTE ====="
        )

        for finding in all_findings:

            if finding.get("source") == "trivy":

                print(
                    finding.get("title"),
                    finding.get("cvss")
                )

                break

        save_findings_db(
            scan_id,
            all_findings
        )

        update_progress(
            95,
            "Salvando resultados"
        )

        # --------------------------------------------------
        # 11. FINALIZA SCAN
        # --------------------------------------------------

        update_scan_status(
            scan_id,
            "completed"
        )

        update_progress(
            100,
            "Scan concluído"
        )

        print(
            "SCAN FINALIZADO COM SUCESSO:",
            scan_id
        )

        if scheduled_scan_id is not None:
            db = SessionLocal()

            try:
                scheduled_scan = (
                    db.query(ScheduledScan)
                    .filter(
                        ScheduledScan.id == scheduled_scan_id
                    )
                    .first()
                )   

                if scheduled_scan:
                    finished_at = datetime.utcnow()

                    scheduled_scan.last_finished_at = finished_at

                    scheduled_scan.next_run_at = (
                        finished_at
                        + timedelta(
                            minutes=scheduled_scan.interval_minutes
                        )
                    )

                    scheduled_scan.updated_at = finished_at

                    db.commit()

            finally:
                db.close()



        return {
            "repository": repo_url,
            "urls": urls,
            "docker_assets": docker_asset,
            "pipelines": pipelines,
            "secrets": secrets,
            "findings": all_findings
        }

    except Exception as e:

        print(
            "ERRO NO SCAN:",
            repr(e)
        )

        # Só tenta atualizar o banco
        # se o scan realmente foi criado.
        if scan_id is not None:

            try:

                update_scan_status(
                    scan_id,
                    "failed"
                )

            except Exception as status_error:

                print(
                    "ERRO AO ATUALIZAR STATUS DO SCAN:",
                    repr(status_error)
                )

        # Se este scan veio de um agendamento,
        # libera o agendamento mesmo em caso de falha.
        if scheduled_scan_id is not None:

            db = SessionLocal()

            try:

                scheduled_scan = (
                    db.query(ScheduledScan)
                    .filter(
                        ScheduledScan.id == scheduled_scan_id
                    )
                    .first()
                )

                if scheduled_scan:

                    finished_at = datetime.utcnow()

                    scheduled_scan.last_finished_at = finished_at

                    scheduled_scan.next_run_at = (
                        finished_at
                        + timedelta(
                            minutes=scheduled_scan.interval_minutes
                        )
                    )

                    scheduled_scan.updated_at = finished_at

                    db.commit()

            except Exception as scheduled_error:

                db.rollback()

                print(
                    "ERRO AO ATUALIZAR AGENDAMENTO APÓS FALHA:",
                    repr(scheduled_error)
                )

            finally:

                db.close()

        raise

    finally:

        # Cleanup seguro.
        # Só tenta remover se o clone
        # realmente tiver criado um caminho.

        if repo_path:

            try:

                shutil.rmtree(
                    repo_path,
                    ignore_errors=True
                )

                print(
                    "REPOSITÓRIO TEMPORÁRIO REMOVIDO:",
                    repo_path
                )

            except Exception as cleanup_error:

                print(
                    "ERRO NO CLEANUP:",
                    repr(cleanup_error)
                )