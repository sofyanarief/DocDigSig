import subprocess
import os
from pyhanko_certvalidator.context import ValidationContext
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign.signers import PdfSigner
from pyhanko.sign import PdfSigner, signers
from pyhanko.sign.general import load_private_key_from_pemder
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter


class SignAndEmbed:
    def __init__(self):
        pass

    def save_private_key_to_file(self, private_key_str, temp_key_file):
        """Simpan private key string ke file sementara"""
        with open(temp_key_file, 'w') as f:
            f.write(private_key_str)
        print(f"Private key disimpan ke {temp_key_file}")

    def generate_self_signed_certificate(self, private_key_file, cert_file, days=365):
        # Membaca private key dari file
        with open(private_key_file, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None, backend=default_backend())

        name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"ID"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Jawa Timur"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Malang"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Politeknik Negeri Malang"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"polinema.ac.id"),
        ])

        # Membuat sertifikat X.509
        certificate = (
            x509.CertificateBuilder()
            .subject_name(name)  # Nama subjek
            .issuer_name(name)  # Nama issuer (karena self-signed, sama dengan subjek)
            .public_key(private_key.public_key())  # Public key dari private key
            .serial_number(x509.random_serial_number())  # Serial number random
            .not_valid_before(datetime.utcnow())  # Tanggal mulai berlaku
            .not_valid_after(datetime.utcnow() + timedelta(days))  # Sertifikat valid 1 tahun
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(u"yourdomain.com")]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())  # Menandatangani sertifikat dengan private key
        )

        # Menyimpan sertifikat ke file
        with open(cert_file, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

    def sign_pdf(self, input_pdf, private_key_str):
        """Generate sertifikat self-signed dan tandatangani PDF menggunakan Sejda-console"""
        output_pdf = input_pdf.replace('out','sign')
        try:
            # Simpan private key ke file sementara
            temp_key_file = input_pdf.replace('out.pdf','priv.pem')
            temp_cert_file = input_pdf.replace('out.pdf','ca.pem')
            self.save_private_key_to_file(private_key_str, temp_key_file)

            # Generate sertifikat self-signed dari kunci privat
            self.generate_self_signed_certificate(temp_key_file, temp_cert_file)

            # with open(input_pdf, 'rb') as pdf_file:
            #     pdf_data = pdf_file.read()

            with open(temp_cert_file, 'rb') as cert_file, open(temp_key_file, 'rb') as key_file:
                cert = cert_file.read()
                key = key_file.read()

            print(temp_key_file)
            print(temp_cert_file)

            cms_signer = signers.SimpleSigner.load(
                temp_key_file, temp_cert_file,
                key_passphrase=None
            )

            with open(input_pdf, 'rb') as doc:
                w = IncrementalPdfFileWriter(doc)
                out = signers.sign_pdf(
                    w, signers.PdfSignatureMetadata(field_name='Signature1'),
                    signer=cms_signer,
                )
            # Hapus file sementara
            os.remove(temp_key_file)
            os.remove(temp_cert_file)

        except subprocess.CalledProcessError as e:
            print(f"Error signing PDF: {e}")