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
