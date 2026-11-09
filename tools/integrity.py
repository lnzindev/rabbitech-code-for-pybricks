#!/usr/bin/env python3
"""Verify the checked-in Rabbitech source against its approved Git blob IDs.

Usage:
    python tools/integrity.py verify
    python tools/integrity.py update

This is a repository/build-time check. It is not imported by Pybricks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrity_manifest.json"
WATCHED = [
    "main.py",
    "base.py",
    "memoria.py",
    "saida_1.py",
    "saida_2.py",
    "saida_3.py",
    "saida_4.py",
    "saida_5.py",
    "saida_6.py",
    "saida_7.py",
    "saida_8.py",
]


def git_blob_id(data: bytes) -> str:
    """Return the same SHA-1 object ID Git uses for a blob."""
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def current_manifest() -> dict:
    result = {}
    for relative in WATCHED:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("Arquivo esperado nao encontrado: " + relative)
        result[relative] = git_blob_id(path.read_bytes())
    return {
        "project": "RABBITECH-PYBRICKS",
        "manifest_version": 1,
        "algorithm": "git-blob-sha1",
        "files": result,
    }


def update() -> int:
    manifest = current_manifest()
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Manifesto atualizado:", MANIFEST.relative_to(ROOT))
    print("Revise o diff e publique o manifesto junto com as mudancas aprovadas.")
    return 0


def verify() -> int:
    if not MANIFEST.is_file():
        print("ERRO: integrity_manifest.json nao existe. Execute 'update'.")
        return 1

    try:
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
        actual = current_manifest()
    except (OSError, ValueError, KeyError) as error:
        print("ERRO ao ler manifesto:", error)
        return 1

    if expected.get("project") != actual["project"]:
        print("ERRO: identificador do projeto nao confere.")
        return 1
    if expected.get("algorithm") != actual["algorithm"]:
        print("ERRO: algoritmo do manifesto nao suportado.")
        return 1

    expected_files = expected.get("files", {})
    failed = False
    for name, actual_id in actual["files"].items():
        expected_id = expected_files.get(name)
        if expected_id != actual_id:
            print("ALTERADO:", name)
            failed = True
        else:
            print("OK:", name)

    for name in expected_files:
        if name not in actual["files"]:
            print("NAO MONITORADO:", name)
            failed = True

    if failed:
        print("FALHA: a fonte difere da versao aprovada no manifesto.")
        return 1

    print("INTEGRIDADE OK: os arquivos correspondem ao manifesto.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "update"), nargs="?", default="verify")
    args = parser.parse_args()
    return update() if args.command == "update" else verify()


if __name__ == "__main__":
    sys.exit(main())
