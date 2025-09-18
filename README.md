# Flask + DynamoDB CRUD
Project ini digunakan untuk pembelajaran TKJ SMKN 1 Nglegok

## DynamoDB Table
- Buat dynamodb table dengan primary key: `id` dengan type `string`

## Jalankan Aplikasi
- Install dependensi: `pip install -r requirements.txt`
- Buat file .env di root project, isi contoh:
```
DDB_TABLE=MyTable
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_SESSION_TOKEN=OPTIONAL_SESSION_TOKEN
AWS_REGION=us-east-1
PORT=5000
```
- Jalankan aplikasi: `python app.py`

## Jalankan aplikasi dengan systemd
- buat systemd file di `/etc/systemd/system/flaskapp.service`
```
[Unit]
Description=Flask DynamoDB CRUD App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/flaskapp
ExecStart=/usr/bin/python3 /home/ubuntu/flaskapp/app.py
Restart=always

# ini penting supaya .env kebaca
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/ubuntu/flaskapp/.env

[Install]
WantedBy=multi-user.target
```
- Jalankan systemd
  - `sudo systemctl daemon-reload`
  - `sudo systemctl enable flaskapp`
  - `sudo systemctl start flaskapp`
  - `sudo systemctl status flaskapp`