# Proxy API for Mininet SDN

API proxy untuk mengeksekusi command SSH ke Mininet Virtual Machine. Dibangun menggunakan FastAPI dan Paramiko untuk memudahkan interaksi dengan Mininet VM dari sistem host.

## Deskripsi

Aplikasi ini menyediakan REST API endpoint yang memungkinkan eksekusi command pada Mininet VM melalui koneksi SSH. Berguna dalam automasi menggunakan LLM untuk testing, monitoring, dan kontrol Mininet dari aplikasi eksternal tanpa perlu login manual ke VM.

## Fitur

- REST API endpoint untuk eksekusi command SSH
- Validasi input menggunakan Pydantic
- Error handling yang komprehensif
- Timeout configuration untuk koneksi dan eksekusi
- Response lengkap dengan stdout, stderr, dan exit status
- Resource management yang proper (auto-close connection)

## Requirements

- Python 3.7+
- FastAPI
- Paramiko
- Pydantic
- Uvicorn (untuk menjalankan server)
- Mininet VM running
  ![image](https://hackmd.io/_uploads/ByE-n0Ab-l.png)



## Instalasi

1. Install dependencies:
```bash
pip install fastapi paramiko uvicorn pydantic
```

Atau menggunakan file requirements (jika tersedia):
```bash
pip install -r requirements.txt
```

## Konfigurasi

Edit konfigurasi koneksi SSH di `main.py`:

```python
HOST = "192.168.56.101"   # IP Mininet VM
USER = "mininet"          # Username SSH
PASSWORD = "mininet"      # Password SSH
SSH_TIMEOUT = 10          # Timeout koneksi (detik)
CMD_TIMEOUT = 30          # Timeout eksekusi command (detik)
```

## Menjalankan Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Atau dengan auto-reload untuk development:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server akan berjalan di `http://localhost:8000`

## Penggunaan API

### Endpoint: POST /run

Mengeksekusi command pada Mininet VM via SSH.

**Request Body:**
```json
{
  "cmd": "ip addr show"
}
```

**Response:**
```json
{
  "stdout": "output dari command",
  "stderr": "error output (jika ada)",
  "exit_status": 0,
  "success": true
}
```

### Contoh Penggunaan

#### Mengecek IP Interface
```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "ip addr show"}'
```

#### Menjalankan Ryu Controller
```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "nohup ryu-manager ryu.app.simple_switch_13 > /tmp/ryu.log 2>&1 &"}'
```

#### Menjalankan Mininet dengan Test Ping
```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "sudo mn --topo single,2 --controller remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13 --test pingall"}'
```

#### Mengecek Proses yang Berjalan
```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "ps aux | grep ryu"}'
```

## API Documentation

Setelah server berjalan, dokumentasi interaktif tersedia di:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

API mengembalikan HTTP status code yang sesuai untuk berbagai kondisi error:

- `400 Bad Request`: Invalid input/validation error
- `401 Unauthorized`: Authentication failed
- `408 Request Timeout`: Connection timeout
- `500 Internal Server Error`: SSH error atau unexpected error

## Struktur Response

Setiap request akan mengembalikan object dengan field:

| Field | Type | Deskripsi |
|-------|------|-----------|
| stdout | string | Output standar dari command |
| stderr | string | Error output dari command |
| exit_status | integer | Exit code dari command (0 = sukses) |
| success | boolean | true jika exit_status = 0 |

## Testing Dengan LLM

<img width="744" height="589" alt="image" src="https://github.com/user-attachments/assets/d8c93b8c-06af-4561-951f-d04e6a75ace4" />
<img width="732" height="600" alt="image" src="https://github.com/user-attachments/assets/3172538a-f8de-4b51-b18c-5450db82e60e" />



