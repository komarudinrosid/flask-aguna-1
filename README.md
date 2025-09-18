# Flask + DynamoDB CRUD
Project ini digunakan untuk pembelajaran TKJ SMKN 1 Nglegok

### DynamoDB Table
- Buat dynamodb table dengan primary key: `id` dengan type `string`

### Jalankan Aplikasi
- Install dependensi: `pip install -r requirements.txt`
- Buat file .env di root project, isi contoh:
```
DDB_TABLE=MyTable
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_SESSION_TOKEN=OPTIONAL_SESSION_TOKEN
AWS_REGION=us-east-1
```
- Jalankan aplikasi: `python app.py`
