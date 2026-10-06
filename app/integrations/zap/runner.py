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

import requests
import time
from app.security.url_validator import (
    validate_zap_target_url,
    InvalidRepositoryURL,
)
from app.config import (
    ZAP_URL,
    ZAP_API_KEY,
    ZAP_TIMEOUT,
    ZAP_SCAN_TIMEOUT,
    ZAP_VERIFY_SSL,
)

ZAP_BASE_URL = ZAP_URL.rstrip("/")



def zap_get(endpoint: str, params: dict | None = None):
    """
    Executa uma requisição GET na API do OWASP ZAP.
    """

    url = f"{ZAP_BASE_URL}/{endpoint.lstrip('/')}"

    params = params or {}

    if ZAP_API_KEY:
        params["apikey"] = ZAP_API_KEY

    try:
        response = requests.get(
            url,
            params=params,
            timeout=ZAP_TIMEOUT,
            verify=ZAP_VERIFY_SSL,
        )

        response.raise_for_status()

        return response.json()

    except requests.Timeout as exc:
        raise RuntimeError(
            f"OWASP ZAP excedeu o timeout de {ZAP_TIMEOUT} segundos."
        ) from exc

    except requests.ConnectionError as exc:
        raise RuntimeError(
            f"Não foi possível conectar ao OWASP ZAP em {ZAP_URL}. "
            "Verifique se o ZAP está em execução."
        ) from exc

    except requests.HTTPError as exc:
        raise RuntimeError(
            f"OWASP ZAP retornou HTTP {response.status_code}: "
            f"{response.text[:500]}"
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "OWASP ZAP retornou uma resposta que não é JSON válido."
        ) from exc


def run_zap(target_url: str):
    """
    Executa Spider + Active Scan no alvo informado.

    Possui:
    - validação do alvo;
    - timeout por requisição;
    - timeout global do scan;
    - tratamento dos IDs retornados pelo ZAP.
    """

    try:
        target_url = validate_zap_target_url(
            target_url
        )

    except InvalidRepositoryURL as error:
        raise ValueError(
            str(error)
        ) from error

    scan_started_at = time.monotonic()

    def check_global_timeout():
        elapsed = time.monotonic() - scan_started_at

        if elapsed > ZAP_SCAN_TIMEOUT:
            raise RuntimeError(
                "OWASP ZAP excedeu o tempo máximo "
                f"de execução "
                f"({ZAP_SCAN_TIMEOUT // 60} minutos)."
            )

    # --------------------------------------------------
    # TESTE DE CONEXÃO
    # --------------------------------------------------

    zap_get(
        "JSON/core/view/version/"
    )

    check_global_timeout()

    # --------------------------------------------------
    # SPIDER
    # --------------------------------------------------

    spider = zap_get(
        "JSON/spider/action/scan/",
        params={
            "url": target_url,
            "recurse": "true",
        },
    )

    spider_scan_id = spider.get(
        "scan"
    )

    if spider_scan_id is None:
        raise RuntimeError(
            "OWASP ZAP não retornou um ID válido "
            "para o Spider."
        )

    # --------------------------------------------------
    # AGUARDA SPIDER
    # --------------------------------------------------

    while True:

        check_global_timeout()

        spider_status = zap_get(
            "JSON/spider/view/status/",
            params={
                "scanId": spider_scan_id,
            },
        )

        try:
            status = int(
                spider_status.get(
                    "status",
                    0
                )
            )

        except (TypeError, ValueError) as error:
            raise RuntimeError(
                "OWASP ZAP retornou um status "
                "inválido para o Spider."
            ) from error

        print(
            f"ZAP Spider: {status}%"
        )

        if status >= 100:
            break

        time.sleep(2)

    # --------------------------------------------------
    # ACTIVE SCAN
    # --------------------------------------------------

    check_global_timeout()

    active_scan = zap_get(
        "JSON/ascan/action/scan/",
        params={
            "url": target_url,
            "recurse": "false",
        },
    )

    active_scan_id = active_scan.get(
        "scan"
    )

    if active_scan_id is None:
        raise RuntimeError(
            "OWASP ZAP não retornou um ID válido "
            "para o Active Scan."
        )

    # --------------------------------------------------
    # AGUARDA ACTIVE SCAN
    # --------------------------------------------------

    while True:

        check_global_timeout()

        active_status = zap_get(
            "JSON/ascan/view/status/",
            params={
                "scanId": active_scan_id,
            },
        )

        try:
            status = int(
                active_status.get(
                    "status",
                    0
                )
            )

        except (TypeError, ValueError) as error:
            raise RuntimeError(
                "OWASP ZAP retornou um status "
                "inválido para o Active Scan."
            ) from error

        print(
            f"ZAP Active Scan: {status}%"
        )

        if status >= 100:
            break

        time.sleep(2)

    # --------------------------------------------------
    # ALERTAS
    # --------------------------------------------------

    check_global_timeout()

    alerts = zap_get(
        "JSON/core/view/alerts/",
        params={
            "baseurl": target_url,
        },
    )

    return {
        "target": target_url,
        "spider_scan_id": spider_scan_id,
        "active_scan_id": active_scan_id,
        "alerts": alerts.get(
            "alerts",
            []
        ),
    }