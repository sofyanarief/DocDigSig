import pdfquery
import xml.etree.ElementTree as ET
import fitz
from pyhanko import stamp
from pyhanko.stamp import QRPosition
from pyhanko.pdf_utils import text
from pyhanko.pdf_utils.font import opentype
from pyhanko.pdf_utils.content import PdfContent
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
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

class EmbedSign:
    def __init__(self):
        pass

    def extract_data_from_pdf(self,file_path):
        pdf = pdfquery.PDFQuery(file_path)
        pdf.load()
        label = pdf.pq('LTTextLineHorizontal:contains("[[PERSON<1>SIGN]]")')
        return label

    def convert_xml_to_arr(self,xml_text):
        root = ET.fromstring(xml_text)
        return root

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

    def embed_and_sign(self,uri,pdf_in,pdf_out,key_position,key_name,key_other_info, str_key_priv, str_key_pub):
        
        temp_key_file = pdf_in.replace('.pdf','priv.pem')
        temp_cert_file = pdf_in.replace('.pdf','ca.pem')
        self.save_private_key_to_file(str_key_priv, temp_key_file)

        # Generate sertifikat self-signed dari kunci privat
        self.generate_self_signed_certificate(temp_key_file, temp_cert_file)

        # with open(pdf_in, 'rb') as pdf_file:
        #     pdf_data = pdf_file.read()

        with open(temp_cert_file, 'rb') as cert_file, open(temp_key_file, 'rb') as key_file:
            cert = cert_file.read()
            key = key_file.read()

        print(temp_key_file)
        print(temp_cert_file)

        # Ekstrak posisi [[PERSON SIGN]] dari PDF
        data = self.extract_data_from_pdf(pdf_in)
        data_arr = self.convert_xml_to_arr(str(data))

        # Mendapatkan posisi (bbox) placeholder
        image_to_add_pos = data_arr.attrib['bbox']
        image_to_add_pos = image_to_add_pos.replace("[", "").replace("]", "")
        image_to_add_pos2 = image_to_add_pos.split(", ")

        # Koordinat awal
        x0 = float(image_to_add_pos2[0])
        y0 = float(image_to_add_pos2[1])
        x1 = float(image_to_add_pos2[2])
        y1 = float(image_to_add_pos2[3])

        signer = signers.SimpleSigner.load(
            temp_key_file, temp_cert_file,
            key_passphrase=None
        )
        
        with open(pdf_in, 'rb') as inf:
            w = IncrementalPdfFileWriter(inf,strict=False)
            fields.append_signature_field(
                w, sig_field_spec=fields.SigFieldSpec(
                    'Signature', box=(x0, y1-200, x0+200, y1)
                )
            )

            meta = signers.PdfSignatureMetadata(field_name='Signature')
            pdf_signer = signers.PdfSigner(
                meta,
                signer=signer,
                stamp_style=stamp.QRStampStyle(
                    # Let's include the URL in the stamp text as well
                    stamp_text=key_position+'\n'+key_name+'\n'+key_other_info,
                    # text_box_style=text.TextBoxStyle(
                    #     font=opentype.GlyphAccumulatorFactory('./TNR-Bold.ttf')
                    # ),
                    border_width=0,
                    qr_position=QRPosition.ABOVE_TEXT
                )
            )
            
            with open(pdf_out, 'wb') as outf: 
                # with QR stamps, the 'url' text parameter is special-cased and mandatory, even if it
                # doesn't occur in the stamp text: this is because the value of the 'url' parameter is
                # also used to render the QR code.
                pdf_signer.sign_pdf(
                    w, output=outf,
                    appearance_text_params={'url': uri}
                )