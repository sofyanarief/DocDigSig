import os
import pdfquery
import xml.etree.ElementTree as ET
import fitz
from pyhanko import stamp
from pyhanko.stamp import QRPosition
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
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

        # Buka file PDF untuk modifikasi
        file_handle = fitz.open(pdf_in)
        first_page = file_handle[0]

        # Dapatkan tinggi dan lebar halaman untuk perhitungan Y yang benar
        page_height = first_page.mediabox.height
        page_width = first_page.mediabox.width
        print(str(x0))
        print(str(x1))
        print(str(page_width))
        print(str(y0))
        print(str(y1))
        print(str(page_height))

        image_rectangle = fitz.Rect(x0, page_height-y1, x1, page_height-y0)
        first_page.draw_rect(image_rectangle, color=(1, 1, 1), fill=(1, 1, 1), width=0)  # RGB (1,1,1) is white, width=0 removes border
        
        # Menambahkan teks di atas QR code
        first_page.insert_text((x0, page_height-y0), 
                               key_position,
                               fontsize=12,
                               fontname="Times-Roman",  # Menggunakan font standar Helvetica
                               color=(0, 0, 0))  # Warna hitam
        
        # Menambahkan teks di bawah QR code
        first_page.insert_text((x0, page_height-y0+160), 
                               key_name+"\n"+key_other_info, 
                               fontsize=12, 
                               fontname="Times-Roman",  # Menggunakan font standar Helvetica
                               color=(0, 0, 0))  # Warna hitam

        file_handle.save(pdf_in.replace('.pdf','-1.pdf'))
        file_handle.close()

        signer = signers.SimpleSigner.load(
            temp_key_file, temp_cert_file,
            key_passphrase=None
        )
        
        with open(pdf_in.replace('.pdf','-1.pdf'), 'rb') as inf:
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
                    stamp_text="",
                    border_width=0,
                    qr_position=QRPosition.ABOVE_TEXT
                )
            )
            
            with open(pdf_out, 'wb') as outf: 
                pdf_signer.sign_pdf(
                    w, output=outf,
                    appearance_text_params={'url': uri}
                )

        #cleanup temp file
        os.remove(pdf_in)
        os.remove(pdf_in.replace('.pdf','-1.pdf'))
        os.remove(temp_key_file)
        os.remove(temp_cert_file)
        os.rename(pdf_out,pdf_out.replace('-out',''))