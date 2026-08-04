from pathlib import Path
from datetime import datetime, timedelta, timezone
import ipaddress
import os
import sys

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


# PROGRAMDATA = Path(os.getenv("PROGRAMDATA")) / "ActivityWatch" / "tls"

# CERT_FILE = PROGRAMDATA / "localhost.crt"
# KEY_FILE = PROGRAMDATA / "localhost.key"

LOCALAPPDATA = Path(os.environ["LOCALAPPDATA"]) / "Sundial" / "Sundial" / "tls"

CERT_FILE = LOCALAPPDATA / "localhost.crt"
KEY_FILE = LOCALAPPDATA / "localhost.key"


def generate():
    # PROGRAMDATA.mkdir(parents=True, exist_ok=True)
    LOCALAPPDATA.mkdir(parents=True, exist_ok=True)

    if CERT_FILE.exists() and KEY_FILE.exists():
        print("TLS certificate already exists.")
        return

    print("Generating TLS certificate...")

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=3650)
        )
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())

    )

    with open(KEY_FILE, "wb") as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    with open(CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

if __name__ == "__main__":
    try:
        generate()
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)