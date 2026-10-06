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

from urllib.parse import urlparse


ALLOWED_HOSTS = {
    "github.com",
    "gitlab.com",
    "bitbucket.org",
}


class InvalidRepositoryURL(ValueError):
    """Erro gerado quando uma URL de repositório não é permitida."""


def validate_repository_url(repo_url: str) -> str:
    """
    Valida e normaliza uma URL de repositório Git.

    Regras:
    - somente HTTPS
    - somente GitHub, GitLab ou Bitbucket
    - sem usuário/senha embutidos
    - somente porta HTTPS padrão
    - precisa possuir caminho de repositório
    - não aceita query string ou fragmento
    """

    if not isinstance(repo_url, str):
        raise InvalidRepositoryURL(
            "A URL do repositório deve ser uma string."
        )

    repo_url = repo_url.strip()

    if not repo_url:
        raise InvalidRepositoryURL(
            "A URL do repositório não pode estar vazia."
        )

    if len(repo_url) > 2048:
        raise InvalidRepositoryURL(
            "A URL do repositório é muito longa."
        )

    try:
        parsed = urlparse(repo_url)
    except Exception as error:
        raise InvalidRepositoryURL(
            "Não foi possível interpretar a URL do repositório."
        ) from error

    # Somente HTTPS
    if parsed.scheme.lower() != "https":
        raise InvalidRepositoryURL(
            "A URL do repositório deve utilizar HTTPS."
        )

    # Host obrigatório
    if not parsed.hostname:
        raise InvalidRepositoryURL(
            "A URL do repositório precisa possuir um domínio."
        )

    hostname = parsed.hostname.lower().rstrip(".")

    # Somente provedores permitidos
    if hostname not in ALLOWED_HOSTS:
        raise InvalidRepositoryURL(
            "O domínio do repositório não é permitido. "
            "Utilize GitHub, GitLab ou Bitbucket."
        )

    # Não permitir usuário/senha na URL
    if parsed.username is not None or parsed.password is not None:
        raise InvalidRepositoryURL(
            "URLs com credenciais embutidas não são permitidas."
        )

    # Não permitir portas alternativas
    try:
        port = parsed.port
    except ValueError as error:
        raise InvalidRepositoryURL(
            "A porta informada na URL é inválida."
        ) from error

    if port is not None and port != 443:
        raise InvalidRepositoryURL(
            "Somente a porta HTTPS padrão é permitida."
        )

    # Precisa existir caminho
    path = parsed.path.strip()

    if not path or path == "/":
        raise InvalidRepositoryURL(
            "A URL precisa apontar para um repositório."
        )

    # Não permitir query string
    if parsed.query:
        raise InvalidRepositoryURL(
            "Query strings não são permitidas na URL do repositório."
        )

    # Não permitir fragmentos
    if parsed.fragment:
        raise InvalidRepositoryURL(
            "Fragmentos não são permitidos na URL do repositório."
        )

    # Evitar caminhos obviamente inválidos
    if "\x00" in path:
        raise InvalidRepositoryURL(
            "A URL contém caracteres inválidos."
        )

    # Normalização simples
    normalized_url = (
        f"https://{hostname}{path}"
    )

    return normalized_url

def validate_zap_target_url(target_url: str) -> str:
    """
    Valida uma URL que será utilizada como alvo pelo OWASP ZAP.

    Regras:
    - somente HTTP/HTTPS
    - sem credenciais
    - sem fragmentos
    - sem localhost
    - sem IPs privados/loopback
    - sem portas inesperadas
    """

    if not isinstance(target_url, str):
        raise InvalidRepositoryURL(
            "O alvo do ZAP deve ser uma string."
        )

    target_url = target_url.strip()

    if not target_url:
        raise InvalidRepositoryURL(
            "O alvo do ZAP não pode estar vazio."
        )

    if len(target_url) > 2048:
        raise InvalidRepositoryURL(
            "O alvo do ZAP é muito longo."
        )

    try:
        parsed = urlparse(target_url)
    except Exception as error:
        raise InvalidRepositoryURL(
            "Não foi possível interpretar o alvo do ZAP."
        ) from error

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        raise InvalidRepositoryURL(
            "O alvo do ZAP deve utilizar HTTP ou HTTPS."
        )

    hostname = parsed.hostname

    if not hostname:
        raise InvalidRepositoryURL(
            "O alvo do ZAP precisa possuir um domínio."
        )

    hostname = hostname.lower().rstrip(".")

    if parsed.username is not None or parsed.password is not None:
        raise InvalidRepositoryURL(
            "URLs com credenciais não são permitidas no ZAP."
        )

    if hostname in {
        "localhost",
        "localhost.localdomain",
    }:
        raise InvalidRepositoryURL(
            "Alvos localhost não são permitidos pelo ZAP."
        )

    # Rejeita IPs diretamente.
    import ipaddress

    try:
        ip = ipaddress.ip_address(hostname)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            raise InvalidRepositoryURL(
                "Endereços IP privados ou internos "
                "não são permitidos como alvo do ZAP."
            )

    except ValueError:
        # Não é um IP; é um hostname normal.
        pass

    try:
        port = parsed.port
    except ValueError as error:
        raise InvalidRepositoryURL(
            "A porta informada no alvo do ZAP é inválida."
        ) from error

    allowed_ports = {
        None,
        80,
        443,
    }

    if port not in allowed_ports:
        raise InvalidRepositoryURL(
            "Somente as portas HTTP/HTTPS padrão "
            "são permitidas no alvo do ZAP."
        )

    if parsed.fragment:
        raise InvalidRepositoryURL(
            "Fragmentos não são permitidos no alvo do ZAP."
        )

    if "\x00" in target_url:
        raise InvalidRepositoryURL(
            "O alvo do ZAP contém caracteres inválidos."
        )

    return target_url