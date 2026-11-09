#!/usr/bin/env python3
"""Confere os arquivos do Rabbitech contra o manifesto aprovado.

Execute no computador, na raiz do repositorio:
    python tools/integrity.py verify
    python tools/integrity.py update
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrity_manifest.json"
WATCHED = [
    "main.py", "base.py", "memoria.py",
    "saida_1.py", "saida_2.py", "saida_3.py", "saida_4.py",
    "saida_5.py", "saida_6.py", "saida_7.py", "saida_8.py",
]


def git_blob_id(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def current_manifest():
    files = {}
    for name in WATCHED:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError("Arquivo ausente: " + name)
        files[name] = git_blob_id(path.read_bytes())
    return {
        "project": "RABBITECH-PYBRICKS",
        "manifest_version": 1,
        "algorithm": "git-blob-sha1",
        "files": files,
    }


def verify():
    if not MANIFEST.is_file():
        print("FALHA: manifesto ausente.")
        return 1
    try:
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
        actual = current_manifest()
    except Exception as error:
        print("FALHA AO LER MANIFESTO:", error)
        return 1

    failed = False
    for name, digest in actual["files"].items():
        if expected.get("files", {}).get(name) != digest:
            print("ALTERADO:", name)
            failed = True
        else:
            print("OK:", name)

    if failed:
        print("INTEGRIDADE REPROVADA. Revise as alteracoes.")
        return 1

    print("INTEGRIDADE APROVADA.")
    return 0


def update():
    data = current_manifest()
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Manifesto atualizado. Revise-o antes de publicar.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "update"), nargs="?", default="verify")
    command = parser.parse_args().command
    return update() if command == "update" else verify()


if __name__ == "__main__":
    sys.exit(main())
