# Frontend Network Health Check

Frontend React + TypeScript + Vite cho hệ thống giám sát router Cisco IOS.

## Chạy kiểm tra cục bộ

```bash
npm ci
npm run lint
npm test -- --run
npm run build
```

## Chạy bằng Docker

Docker Compose của toàn hệ thống nằm ở thư mục gốc:

```bash
cd ~/QTM
docker compose up -d --build frontend
```

Truy cập: `http://192.168.141.128:3000`.

Quy trình chuẩn bị GNS3, cấu hình Settings và kịch bản thuyết trình được ghi tại
[README chính](../README.md#checklist-trước-buổi-demo).
