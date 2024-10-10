import pdfquery
import xml.etree.ElementTree as ET
import fitz
from PIL import Image

class EmbedQR:
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

    def embed(self,pdf_in,pdf_out,qr,key_position,key_name,key_other_info):
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

        # Penyesuaian sumbu Y (menjaga posisi QR code tepat di atas placeholder)
        y0_new = page_height - y0  # Menggunakan y1 sebagai posisi atas

        # Mengisi area placeholder dengan kotak putih untuk "menghapus" teks placeholder
        placeholder_rect = fitz.Rect(x0, page_height - y1, x1, page_height - y0)  # Membalikkan sumbu Y
        first_page.draw_rect(placeholder_rect, color=(1, 1, 1), fill=(1, 1, 1))  # Isi area dengan warna putih

        # Atur proporsi gambar QR agar tidak berubah
        qr_image_path = qr
        img = Image.open(qr_image_path)
        aspect_ratio = img.height / img.width

        new_width = x1 - x0 + 50  # Tambahkan lebar sesuai keinginan
        new_height = new_width * aspect_ratio  # Menjaga proporsi tinggi berdasarkan lebar

        # Koordinat penempatan gambar QR (di atas placeholder, tidak lebih rendah)
        image_rectangle = fitz.Rect(x0, y0_new, x0 + new_width, y0_new + new_height)

        # Insert QR code ke halaman PDF
        with open(qr_image_path, "rb") as img_file:
            img_data = img_file.read()
            first_page.insert_image(image_rectangle, stream=img_data)

        # Menambahkan teks di atas QR code
        first_page.insert_text((x0, y0_new), 
                               key_position, 
                               fontsize=12, 
                               fontname="Times-Roman",  # Menggunakan font standar Helvetica
                               color=(0, 0, 0))  # Warna hitam

        # Menambahkan teks di bawah QR code
        first_page.insert_text((x0, y0_new + 20 + new_height), 
                               key_name+"\n"+key_other_info, 
                               fontsize=12, 
                               fontname="Times-Roman",  # Menggunakan font standar Helvetica
                               color=(0, 0, 0))  # Warna hitam

        # Simpan PDF yang telah dimodifikasi
        file_handle.save(pdf_out)
        file_handle.close()

        print("QR Code dan teks telah berhasil ditambahkan.")