"""
Phase 4.0 — Dev mTLS certificate bootstrap for the edge agent bridge.

Generates a self-signed AfriGround CA, a server certificate (for the API /
reverse proxy), and one client certificate per station agent. The client
certificate's common name MUST equal the agent_id registered in
station_agent_identities (services/agent_auth.py resolves CN -> identity).

Files are written under <out_dir> (default .docker-data/certs):

  ca/ca.crt, ca/ca.key
  server/server.crt, server/server.key
  agents/<agent_id>.crt, agents/<agent_id>.key

Run from apps/api:
    & .venv\Scripts\python.exe scripts\gen_agent_certs.py
    & .venv\Scripts\python.exe scripts\gen_agent_certs.py --agent station-01 sim-edge-01
"""
import argparse
import datetime
import ipaddress
import os
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

DEFAULT_OUT = os.path.join("..", "..", ".docker-data", "certs")


def _key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _write_key(path: Path, key) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def _write_cert(path: Path, cert) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def build_ca(out_dir: Path) -> None:
    ca_dir = out_dir / "ca"
    if (ca_dir / "ca.crt").exists():
        print(f"CA already exists: {ca_dir / 'ca.crt'}")
        return

    key = _key()
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "AfriGround Dev CA")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, key_encipherment=True, key_cert_sign=True,
            crl_sign=True, content_commitment=False, data_encipherment=False,
            key_agreement=False, encipher_only=False, decipher_only=False,
        ), critical=True)
        .sign(key, hashes.SHA256())
    )
    _write_key(ca_dir / "ca.key", key)
    _write_cert(ca_dir / "ca.crt", cert)
    print(f"CA written: {ca_dir / 'ca.crt'}")


def build_server(out_dir: Path, ca_cert: x509.Certificate, ca_key) -> None:
    server_dir = out_dir / "server"
    if (server_dir / "server.crt").exists():
        print(f"Server cert already exists: {server_dir / 'server.crt'}")
        return

    key = _key()
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    _write_key(server_dir / "server.key", key)
    _write_cert(server_dir / "server.crt", cert)
    print(f"Server cert written: {server_dir / 'server.crt'}")


def build_agent(out_dir: Path, agent_id: str, ca_cert: x509.Certificate, ca_key) -> None:
    agent_dir = out_dir / "agents"
    cert_path = agent_dir / f"{agent_id}.crt"
    if cert_path.exists():
        print(f"Agent cert already exists: {cert_path}")
        return

    key = _key()
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, agent_id)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    _write_key(agent_dir / f"{agent_id}.key", key)
    _write_cert(agent_dir / f"{agent_id}.crt", cert)
    print(f"Agent cert written: {cert_path} (CN={agent_id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap AfriGround dev mTLS certificates")
    parser.add_argument("--out", default=DEFAULT_OUT, help="certificate output directory")
    parser.add_argument("--agent", action="append", default=[], help="agent_id to issue a client cert for")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    build_ca(out_dir)

    ca_path = out_dir / "ca" / "ca.crt"
    ca_key_path = out_dir / "ca" / "ca.key"
    ca_cert = x509.load_pem_x509_certificate(ca_path.read_bytes())
    ca_key = serialization.load_pem_private_key(ca_key_path.read_bytes(), password=None)

    build_server(out_dir, ca_cert, ca_key)
    for agent_id in args.agent or ["sim-edge-01"]:
        build_agent(out_dir, agent_id, ca_cert, ca_key)

    print("\nTrust the CA at: %s" % (out_dir / "ca" / "ca.crt"))
    print("Server cert:    %s (key: %s)" % (out_dir / "server" / "server.crt", out_dir / "server" / "server.key"))
    print("Serve with mTLS (uvicorn):")
    print("  --ssl-certfile server.crt --ssl-keyfile server.key --ssl-ca-certs ca/ca.crt --ssl-cert-reqs 2")


if __name__ == "__main__":
    main()