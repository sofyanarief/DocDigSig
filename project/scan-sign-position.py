import pdfquery
import xml.etree.ElementTree as ET
import fitz

def extract_data_from_pdf(file_path):
    pdf = pdfquery.PDFQuery(file_path)
    pdf.load()
    label = pdf.pq('LTTextLineHorizontal:contains("[[PERSON<1>SIGN]]")')
    return label

def convert_xml_to_arr(xml_text):
    root = ET.fromstring(xml_text)
    return root
data = extract_data_from_pdf('Sample.pdf')
# print(data)
data_arr = convert_xml_to_arr(str(data))
# print(data_arr.tag)
# print(data_arr.attrib['bbox'])
image_to_add_pos = data_arr.attrib['bbox']
image_to_add_pos = image_to_add_pos.replace("[","")
image_to_add_pos = image_to_add_pos.replace("]","")
image_to_add_pos2 = image_to_add_pos.split(", ")
print(image_to_add_pos2)
x0 = float(image_to_add_pos2[0])
print(x0)
y0 = float(image_to_add_pos2[1])
print(y0)
x1 = float(image_to_add_pos2[2])+50
print(x1)
y1 = float(image_to_add_pos2[3])+50
print(y1)
file_handle = fitz.open('Sample.pdf')
first_page = file_handle[0]
print(first_page.mediabox.height)
# x0 = first_page.mediabox.width - x0
# print(x0)
# y0 = first_page.mediabox.height - y0
# print(y0)
# x1 = first_page.mediabox.width - x1
# print(x1)
# y1 = first_page.mediabox.height - y1
# print(y1)
image_rectangle = fitz.Rect(x0,y0,x1,y1)
img = open("MyQRCode2.png", "rb").read()  # an image file
img_xref = 0
first_page.insert_image(image_rectangle,stream=img,xref=img_xref)
file_handle.save('Sample-out.pdf')