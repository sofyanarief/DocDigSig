# Importing library
import qrcode

# Data to encode
data = "https://www.geeksforgeeks.org/generate-qr-code-using-qrcode-in-python/"

# Creating an instance of QRCode class
qr = qrcode.QRCode()

# Adding data to the instance 'qr'
qr.add_data(data)

qr.make(fit = True)
img = qr.make_image()

img.save('MyQRCode2.png')
