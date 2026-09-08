"""Baixa todas as mídias de uma publicação pública do Instagram.

Exemplos:
    python download_post.py
    python download_post.py https://www.instagram.com/p/CODIGO/
    python download_post.py URL --assunto "viagem em família"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import threading
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import instaloader
from dotenv import load_dotenv


# O Instagram usa tanto /reel/ quanto /reels/ em links compartilhados.
POST_PATH_PATTERN = re.compile(r"/(?:p|reel|reels|tv)/([^/?#]+)/?", re.IGNORECASE)
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def shortcode_from_url(url: str) -> str:
    """Valida uma URL de post/reel e devolve seu shortcode."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc.lower().endswith("instagram.com"):
        raise ValueError("Informe uma URL válida de publicação do Instagram.")
    match = POST_PATH_PATTERN.search(parsed.path)
    if not match:
        raise ValueError("A URL deve apontar para uma publicação do Instagram (/p/, /reel/, /reels/ ou /tv/).")
    return match.group(1)


def safe_name(value: str, fallback: str = "sem-assunto", maximum: int = 80) -> str:
    """Converte um texto em nome de pasta compatível com Windows."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    normalized = INVALID_FILENAME_CHARS.sub("", normalized)
    normalized = re.sub(r"\s+", "-", normalized.strip())
    normalized = re.sub(r"-+", "-", normalized).strip(".- ")
    return (normalized[:maximum].rstrip(".- ") or fallback)


def subject_from_caption(caption: str | None, supplied_subject: str | None) -> str:
    if supplied_subject:
        return safe_name(supplied_subject)
    if caption:
        first_line = next((line.strip() for line in caption.splitlines() if line.strip()), "")
        if first_line:
            return safe_name(first_line)
    return "post"


def configure_loader() -> instaloader.Instaloader:
    # Apenas mídias são gravadas; metadados e thumbnails extras não são necessários.
    return instaloader.Instaloader(
        download_pictures=True,
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        save_metadata=False,
        compress_json=False,
        post_metadata_txt_pattern="",
        dirname_pattern="{target}",
        filename_pattern="{date_utc:%Y-%m-%d_%H-%M-%S}_{shortcode}",
        # A saída fica sob controle do indicador de progresso abaixo.
        quiet=True,
    )


class DownloadSpinner:
    """Exibe um indicador simples enquanto a chamada bloqueante baixa a mídia."""

    def __init__(self, message: str = "Baixando") -> None:
        self.message = message
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._render, daemon=True)

    def __enter__(self) -> "DownloadSpinner":
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join()
        # Limpa a linha usada pela animação antes da mensagem final.
        print("\r" + " " * 80 + "\r", end="", flush=True)

    def _render(self) -> None:
        frames = "|/-\\"
        index = 0
        while not self._stop.is_set():
            print(f"\r{self.message}... {frames[index % len(frames)]}", end="", flush=True)
            index += 1
            self._stop.wait(0.12)


def login_if_configured(loader: instaloader.Instaloader, session_file: Path) -> None:
    username = os.getenv("INSTAGRAM_USERNAME", "").strip()
    password = os.getenv("INSTAGRAM_PASSWORD", "")
    if not username:
        return

    if session_file.exists():
        try:
            loader.load_session_from_file(username, str(session_file))
            print(f"Sessão reutilizada para @{username}.")
            return
        except Exception as error:  # sessão vencida ou incompatível
            print(f"Não foi possível reutilizar a sessão ({error}). Tentando login...")

    if not password:
        raise RuntimeError(
            "INSTAGRAM_USERNAME foi definido, mas INSTAGRAM_PASSWORD está vazio e não há sessão válida."
        )
    try:
        loader.login(username, password)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        # O Instagram envia o código pelo método 2FA configurado na conta.
        verification_code = input("Digite o código de verificação em duas etapas do Instagram: ").strip()
        if not verification_code:
            raise RuntimeError("Nenhum código 2FA foi informado.")
        try:
            loader.two_factor_login(verification_code)
        except instaloader.exceptions.BadCredentialsException as error:
            raise RuntimeError("O código 2FA foi recusado. Execute novamente e informe um código válido.") from error
    loader.save_session_to_file(str(session_file))
    print(f"Login concluído; sessão salva em {session_file}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Baixa todas as mídias de um post público do Instagram.")
    parser.add_argument("url", nargs="?", help="URL da publicação, reel ou IGTV; se omitida, será solicitada")
    parser.add_argument("--assunto", help="Texto usado no nome da subpasta; por padrão, usa a legenda")
    args = parser.parse_args()

    load_dotenv()
    try:
        url = args.url or input("Cole o link da publicação do Instagram: ").strip()
        shortcode = shortcode_from_url(url)
        # A raiz é resolvida pelo Python, mas nunca é passada como ``target``
        # ao Instaloader: ele trata barras no target como caracteres de nome
        # de pasta no Windows. O padrão abaixo conserva as barras estruturais.
        output_root = Path(os.getenv("DOWNLOAD_DIR", "downloads")).expanduser().resolve()
        session_file = Path(os.getenv("SESSION_FILE", ".instagram-session")).expanduser()
        loader = configure_loader()
        login_if_configured(loader, session_file)

        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        date = post.date_utc.strftime("%Y-%m-%d")
        folder_name = f"{date}-{subject_from_caption(post.caption, args.assunto)}"
        profile_name = safe_name(post.owner_username, fallback="perfil")
        destination = output_root / profile_name / folder_name
        destination.mkdir(parents=True, exist_ok=True)

        # ``target`` contém somente o último segmento. ``dirname_pattern``
        # mantém a estrutura real de diretórios e evita criar uma pasta cujo
        # nome seja o caminho absoluto convertido em caracteres Unicode.
        loader.dirname_pattern = str(output_root / "{profile}" / "{target}")
        with DownloadSpinner():
            downloaded = loader.download_post(post, target=folder_name)
        status = "Download concluído" if downloaded else "Download já estava concluído"
        print(f"{status}: {destination}")
        return 0
    except (ValueError, RuntimeError, instaloader.exceptions.InstaloaderException) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
