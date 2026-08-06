from pathlib import Path
from datetime import datetime, timedelta, timezone
import ctypes
from ctypes import wintypes
import ipaddress
import os
import sys

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


LOCALAPPDATA = (
    Path(os.environ["LOCALAPPDATA"])
    / "Sundial"
    / "Sundial"
    / "tls"
)

CERT_FILE = LOCALAPPDATA / "localhost.crt"
KEY_FILE = LOCALAPPDATA / "localhost.key"


# ----------------------------------------------------------------------
# Windows DPAPI
# ----------------------------------------------------------------------

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


crypt32 = ctypes.WinDLL("crypt32.dll")
kernel32 = ctypes.WinDLL("kernel32.dll")


crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(DATA_BLOB),
    wintypes.LPCWSTR,
    ctypes.POINTER(DATA_BLOB),
    wintypes.LPVOID,  # Fixed
    wintypes.LPVOID,  # Fixed
    wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB),
]

crypt32.CryptProtectData.restype = wintypes.BOOL


crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(DATA_BLOB),
    ctypes.POINTER(wintypes.LPWSTR),
    ctypes.POINTER(DATA_BLOB),
    wintypes.LPVOID,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB),
]

crypt32.CryptUnprotectData.restype = wintypes.BOOL


kernel32.LocalFree.argtypes = [
    wintypes.HLOCAL
]

kernel32.LocalFree.restype = wintypes.HLOCAL


def _make_blob(data: bytes):
    buffer = ctypes.create_string_buffer(data)

    blob = DATA_BLOB(
        len(data),
        ctypes.cast(
            buffer,
            ctypes.POINTER(ctypes.c_byte)
        ),
    )

    return blob, buffer


def dpapi_protect(data: bytes) -> bytes:
    """
    Encrypt data using Windows DPAPI.

    The encrypted data can normally only be decrypted by
    the same Windows user on the same Windows installation.
    """

    input_blob, input_buffer = _make_blob(data)
    output_blob = DATA_BLOB()

    # Optional description stored with the DPAPI blob.
    description = "App localhost TLS private key"

    success = crypt32.CryptProtectData(
        ctypes.byref(input_blob),
        description,
        None,
        None,
        None,
        0,
        ctypes.byref(output_blob),
    )

    if not success:
        raise ctypes.WinError()

    try:
        return ctypes.string_at(
            output_blob.pbData,
            output_blob.cbData,
        )
    finally:
        kernel32.LocalFree(output_blob.pbData)


def dpapi_unprotect(data: bytes) -> bytes:
    """
    Decrypt data using Windows DPAPI.
    """

    input_blob, input_buffer = _make_blob(data)
    output_blob = DATA_BLOB()
    description = wintypes.LPWSTR()

    success = crypt32.CryptUnprotectData(
        ctypes.byref(input_blob),
        ctypes.byref(description),
        None,
        None,
        None,
        0,
        ctypes.byref(output_blob),
    )

    if not success:
        raise ctypes.WinError()

    try:
        return ctypes.string_at(
            output_blob.pbData,
            output_blob.cbData,
        )
    finally:
        if description:
            kernel32.LocalFree(description)

        kernel32.LocalFree(output_blob.pbData)


# ----------------------------------------------------------------------
# Certificate generation
# ----------------------------------------------------------------------

def generate():

    if os.name != "nt":
        raise RuntimeError(
            "Windows DPAPI is only available on Windows."
        )

    LOCALAPPDATA.mkdir(
        parents=True,
        exist_ok=True,
    )

    if CERT_FILE.exists() and KEY_FILE.exists():
        load_private_key()
        return

    # Generate RSA private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(
            NameOID.COMMON_NAME,
            "localhost",
        ),
    ])

    now = datetime.now(timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(
            x509.random_serial_number()
        )
        .not_valid_before(
            now - timedelta(minutes=1)
        )
        .not_valid_after(
            now + timedelta(days=3650)
        )
        .add_extension(
            x509.BasicConstraints(
                ca=False,
                path_length=None,
            ),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(
                    ipaddress.IPv4Address("127.0.0.1")
                ),
                x509.IPAddress(
                    ipaddress.IPv6Address("::1")
                ),
            ]),
            critical=False,
        )
        .sign(
            key,
            hashes.SHA256(),
        )
    )

    # Serialize private key into PKCS8 PEM
    private_key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Protect the PEM using Windows DPAPI
    protected_key = dpapi_protect(
        private_key_pem
    )

    # Write certificate
    with open(CERT_FILE, "wb") as f:
        f.write(
            cert.public_bytes(
                serialization.Encoding.PEM
            )
        )

    # Write DPAPI-protected private key
    with open(KEY_FILE, "wb") as f:
        f.write(protected_key)


# ----------------------------------------------------------------------
# Loading the private key
# ----------------------------------------------------------------------

def load_private_key():
    """
    Read the DPAPI-protected localhost.key and return
    a cryptography private-key object.
    """

    protected_key = KEY_FILE.read_bytes()

    private_key_pem = dpapi_unprotect(
        protected_key
    )

    return serialization.load_pem_private_key(
        private_key_pem,
        password=None,
    )


if __name__ == "__main__":
    try:
        generate()
        sys.exit(0)
    except Exception as e:
        print(f"TLS initialization failed: {e}")
        sys.exit(1)