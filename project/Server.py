from DatabaseConnector import DatabaseConnector
from User import User
from Key import Key
from Document import Document
from EmbedSign import EmbedSign
import os
from Crypto.PublicKey import RSA
import uuid
from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer

HOSTNAME = "localhost"
HOSTPORT = 8080
HOST_URL = 'http://'+HOSTNAME+':'+str(HOSTPORT)+'/'
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf'}
DBHOST = '192.168.73.198'
DBUSER = 'docdigsig'
DBPASS = 'docdigsig@2024'
DBNAME = 'docdigsig'

# Flask App
app = Flask(__name__)
app.config['ENV'] = 'production'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # Diperlukan untuk flash messages

# Koneksi database diinisialisasi
def get_db_connection():
    db = DatabaseConnector(DBHOST,DBUSER,DBPASS,DBNAME)
    db.connect()
    return db

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route untuk upload file
@app.route('/documents', methods=['POST'])
def add_document():
    # Cek apakah file ada di dalam request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    data = request.form
    origname_document = file.filename
    # upname_document = secure_filename(file.filename)
    upname_document = str(uuid.uuid4())+'.pdf'
    t_user_id_user = data.get('t_user_id_user')
    t_key_id_key = data.get('t_key_id_key')
    
    # Jika tidak ada file yang dipilih
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Jika file diizinkan (PDF)
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], upname_document))  # Simpan file
        db = get_db_connection()
        document = Document(db)
        document.insert_document(origname_document, upname_document, t_user_id_user, t_key_id_key)
        key = Key(db)
        key = key.get_key(t_key_id_key)
        db.close()
        file_url = HOST_URL+UPLOAD_FOLDER
        input_pdf = UPLOAD_FOLDER+upname_document
        output_pdf = UPLOAD_FOLDER+upname_document.rsplit(".", 1)[0]+'-out.pdf'
        embed_sign = EmbedSign()
        embed_sign.embed_and_sign(file_url,input_pdf,output_pdf,key[0]['key_position'],key[0]['key_name'],key[0]['key_other_info'],key[0]['key_priv_value'],key[0]['key_pub_value'])
        return jsonify({'message': 'File '+ upname_document.replace('-out','') +' has been signed successfully'}), 201
    
    return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

# Route untuk mendapatkan daftar file yang di-upload
@app.route('/files', methods=['GET'])
def get_uploaded_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files), 200

# Route untuk mendaftarkan user baru
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    userpass = data.get('userpass')
    user_nickname = data.get('user_nickname')

    db = get_db_connection()
    user = User(db)
    user.insert_user(username, userpass, user_nickname)
    db.close()

    return jsonify({'message': 'User added successfully'}), 201

# Route untuk mendaftarkan key baru
@app.route('/keys', methods=['POST'])
def add_key():
    data = request.json
    key_name = data.get('key_name')
    key_position = data.get('key_position')
    key_other_info = data.get('key_other_info')
    t_user_id_user = data.get('t_user_id_user')
    # Generate pasangan kunci RSA
    key = RSA.generate(2048)
    key_priv_value = key.export_key()
    key_pub_value = key.publickey().export_key()
    db = get_db_connection()
    key = Key(db)
    key.insert_key(key_priv_value, key_pub_value, key_name, key_position, key_other_info, t_user_id_user)
    db.close()

    return jsonify({'message': 'Key added successfully'}), 201

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Membuat folder jika belum ada
    # app.run(debug=True,host='0.0.0.0', port=HOSTPORT)
    http_server = WSGIServer(('', HOSTPORT), app)
    print("Server running")
    http_server.serve_forever()