import PyPDF2
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def create_qrcode(data, qr_code_path):
    """Fungsi untuk membuat QR code"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    img.save(qr_code_path)

def calculate_qr_size(text, page_width, page_height, qr_max_ratio=0.6):
    """Fungsi untuk menghitung ukuran QR Code berdasarkan posisi placeholder dan margin"""
    # Temukan posisi placeholder [[PERSON<1>SIGN]] dalam teks
    placeholder_position = text.find('[[PERSON<1>SIGN]]')
    
    # Jika placeholder ditemukan, hitung jarak ke tepi kanan dan bawah halaman
    if placeholder_position != -1:
        # Anggap posisi placeholder di area bawah kanan, sesuaikan sesuai logika teks di halaman
        # Misalkan kita asumsikan bahwa [[PERSON<1>SIGN]] berada di posisi (x_placeholder, y_placeholder)
        # Halaman PDF biasanya memiliki lebar dan tinggi tertentu (misal: A4 atau letter)
        
        x_placeholder = 400  # Posisi placeholder di sumbu X (dari kiri)
        y_placeholder = 100  # Posisi placeholder di sumbu Y (dari bawah)

        # Hitung jarak dari placeholder ke tepi kanan dan bawah halaman
        distance_to_right_margin = page_width - x_placeholder
        distance_to_bottom_margin = y_placeholder
        
        # Tentukan ukuran QR code maksimal (60% dari jarak ke tepi halaman)
        max_qr_width = distance_to_right_margin * qr_max_ratio
        max_qr_height = distance_to_bottom_margin * qr_max_ratio
        
        # Ukuran QR code yang proporsional
        qr_size = min(max_qr_width, max_qr_height)
        
        return qr_size, x_placeholder, y_placeholder
    else:
        return None, None, None

def add_qrcode_to_pdf(input_pdf_path, output_pdf_path, qr_code_path):
    # Baca file PDF asli
    with open(input_pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        pdf_writer = PyPDF2.PdfWriter()

        # Loop melalui halaman di PDF
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            
            # Ambil teks dari halaman
            text = page.extract_text()
            
            # Ukuran halaman PDF
            page_width = float(page.mediabox.upper_right[0])  # Lebar halaman
            page_height = float(page.mediabox.upper_right[1])  # Tinggi halaman

            # Cek apakah placeholder [[PERSON<1>SIGN]] ada di halaman ini
            if '[[PERSON<1>SIGN]]' in text:
                # Hapus placeholder dari teks halaman
                text = text.replace('[[PERSON<1>SIGN]]', '')

                # Hitung ukuran QR Code dan posisi berdasarkan margin dan posisi placeholder
                qr_size, x_placeholder, y_placeholder = calculate_qr_size(text, page_width, page_height)

                if qr_size is not None:
                    # Buat QR code dan tambahkan ke halaman yang ditandai
                    packet = BytesIO()
                    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    
                    # Tentukan ukuran dan posisi QR Code (proporsi 60% dari jarak ke margin)
                    can.drawImage(qr_code_path, x_placeholder, y_placeholder, width=qr_size, height=qr_size)
                    can.save()

                    # Pindah ke halaman
                    packet.seek(0)

                    # Baca halaman QR Code
                    new_pdf = PyPDF2.PdfReader(packet)
                    qr_page = new_pdf.pages[0]

                    # Gabungkan halaman QR dengan halaman PDF asli
                    page.merge_page(qr_page)
            
            # Tambahkan halaman ke penulis PDF
            pdf_writer.add_page(page)

        # Simpan PDF yang telah dimodifikasi
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

if __name__ == "__main__":
    # Data untuk QR Code
    qr_data = "This is the QR Code signature"
    qr_code_path = "qrcode.png"
    
    # Buat QR code dari data yang diberikan
    create_qrcode(qr_data, qr_code_path)
    
    # Path file PDF input dan output
    input_pdf = "Sample.pdf"
    output_pdf = "Sample_out.pdf"
    
    # Tambahkan QR code ke PDF
    add_qrcode_to_pdf(input_pdf, output_pdf, qr_code_path)

    print("QR code berhasil ditambahkan pada halaman yang ditandai.")
