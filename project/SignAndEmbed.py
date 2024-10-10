from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from pikepdf import Pdf

class SignAndEmbed:
    def __init__(self):
        pass

    def sign_pdf(pdf_path, private_key):
        # Buka PDF dan baca isinya sebagai bytes
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        # Hash konten PDF menggunakan SHA-256
        hash_obj = SHA256.new(pdf_content)

        # Tandatangani hash menggunakan kunci privat (PKCS#1 v1.5)
        signature = pkcs1_15.new(private_key).sign(hash_obj)

        # # Simpan tanda tangan dalam file terpisah atau tambahkan ke PDF
        # signature_path = pdf_path.replace('.pdf', '_signed.sig')
        # with open(signature_path, 'wb') as f:
        #     f.write(signature)

        with Pdf.open(pdf_path) as pdf:
            # Tambahkan tanda tangan ke dalam metadata PDF
            pdf.docinfo["/Signature"] = signature.hex()
            # Simpan PDF baru dengan tanda tangan
            pdf.save(pdf_path)

        print(f'Tanda tangan telah dibuat dan disimpan didalam file pdf {pdf_path}')