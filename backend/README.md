# Network Health Collector

Chạy từ thư mục `backend`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
export ROUTER_PASSWORD='your-password'
python -m app.scripts.check_device
```

Báo cáo JSON mặc định được tạo tại `reports/r1-health.json`.

## Chạy API và PostgreSQL bằng Docker

Từ thư mục gốc dự án:

```powershell
Copy-Item .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Điền khóa vừa tạo vào `CREDENTIAL_KEY` trong `.env`, đổi
`POSTGRES_PASSWORD`, sau đó chạy:

```powershell
docker compose up -d --build
Invoke-RestMethod http://127.0.0.1:8001/api/v1/health
```

Swagger UI: `http://127.0.0.1:8001/docs`. PostgreSQL Docker được ánh xạ ra
`127.0.0.1:5434` để không xung đột PostgreSQL đang có trên máy.
