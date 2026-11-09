# Rabbitech Anti-Tamper — Pybricks MicroPython 3.6.1
# SHA-256 integrity check. This is not cryptographic DRM.
import hashlib
PROJECT_ID = "RABBITECH-PYBRICKS"
SECURITY_VERSION = "1.0.0"
EXPECTED = {
    "base.py": "GENERATE_MANIFEST", "memoria.py": "GENERATE_MANIFEST",
    "saida_1.py": "GENERATE_MANIFEST", "saida_2.py": "GENERATE_MANIFEST",
    "saida_3.py": "GENERATE_MANIFEST", "saida_4.py": "GENERATE_MANIFEST",
    "saida_5.py": "GENERATE_MANIFEST", "saida_6.py": "GENERATE_MANIFEST",
    "saida_7.py": "GENERATE_MANIFEST", "saida_8.py": "GENERATE_MANIFEST",
}
def verify_sources(source_map):
    for name, expected in EXPECTED.items():
        if expected == "GENERATE_MANIFEST":
            print("INTEGRIDADE: manifesto nao configurado:", name)
            return False
        if hashlib.sha256(source_map.get(name, b"")).hexdigest() != expected:
            print("INTEGRIDADE: arquivo alterado:", name)
            return False
    return True
