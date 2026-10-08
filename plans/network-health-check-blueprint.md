# Blueprint: Network Health Check

## 1. Mục tiêu

Xây dựng hệ thống web tự động kiểm tra sức khỏe router Cisco IOS trong GNS3 bằng Netmiko. Hệ thống thu thập trạng thái thiết bị, CPU, RAM, interface, khả năng SSH, packet loss và latency; đánh giá `Healthy`, `Warning`, `Critical`; lưu lịch sử vào PostgreSQL; hiển thị bằng React và xuất báo cáo web/PDF/CSV. Toàn bộ ứng dụng chạy bằng Docker Compose.

## 2. Phạm vi đồ án và mốc MVP

MVP là mốc chứng minh luồng cốt lõi của đề tài hoạt động vào cuối tuần 10, không phải bản cắt giảm của sản phẩm cuối tuần 15.

### 2.1. Mốc MVP — cuối tuần 10

- Dựng được 3 router Cisco IOS 3660 và 2 đích ping trong GNS3.
- FastAPI, React và PostgreSQL chạy được bằng Docker Compose.
- Quản lý được danh sách thiết bị và thông tin kết nối.
- Netmiko thu thập được uptime, CPU, RAM và interface.
- Đo được management connectivity, path packet loss và latency.
- Đánh giá được `Healthy`, `Warning`, `Critical` và lưu findings.
- Kiểm tra được một thiết bị, `Run all` và tự động chạy theo lịch.
- Lưu được lịch sử và có dashboard cơ bản hiển thị trạng thái mới nhất.

**MVP đạt khi:** từ giao diện người dùng có thể chọn một router, chạy kiểm tra, xem trạng thái cùng nguyên nhân và tìm lại kết quả đó sau khi restart container.

### 2.2. Sản phẩm hoàn chỉnh — cuối tuần 15

- Backend: FastAPI, Netmiko, SQLAlchemy, Alembic và APScheduler 3.x.
- Frontend: React + Vite + TypeScript, Bootstrap, Chart.js và TanStack Query.
- Database: PostgreSQL; deployment gồm `frontend`, `backend`, `db` trong Docker Compose.
- Có đăng nhập admin tối thiểu và mã hóa credential thiết bị.
- Dashboard đầy đủ, trang chi tiết, lịch sử và biểu đồ.
- Có giao diện cấu hình ngưỡng CPU, RAM, packet loss, latency và chu kỳ kiểm tra.
- Báo cáo web, PDF và CSV theo khoảng thời gian.
- Có test, tài liệu dựng GNS3, README, sơ đồ kiến trúc và kịch bản bảo vệ.

### 2.3. Ngoài phạm vi 15 tuần

- Đa hãng, SNMP, RBAC nhiều vai trò, HA và Celery/Redis.
- Telegram/email và retention nâng cao chỉ làm khi toàn bộ tiêu chí chính đã đạt.

## 3. Tiêu chí hoàn thành

1. Thêm, sửa, xóa và bật/tắt thiết bị trên web.
2. Backend SSH được vào Cisco 3660 và thu thập đủ chỉ số.
3. Có thể kiểm tra một thiết bị hoặc toàn bộ thiết bị.
4. Kết quả được lưu theo từng lần kiểm tra trong PostgreSQL.
5. Trạng thái tổng hợp đúng theo ngưỡng cấu hình.
6. Dashboard hiển thị tổng quan, chi tiết và biểu đồ lịch sử.
7. Có kiểm tra tự động theo lịch.
8. Xuất được báo cáo PDF và CSV theo khoảng thời gian.
9. `docker compose up --build` khởi động được toàn hệ thống.
10. Có kịch bản demo cho cả ba mức Healthy/Warning/Critical.
11. API quản trị yêu cầu đăng nhập; credential thiết bị không xuất hiện trong API, log hoặc báo cáo.

## 4. Kiến trúc

```text
Browser
  |
  v
React/Nginx ----REST----> FastAPI
                           |  |
                           |  +----> PostgreSQL
                           |
                           +----SSH/ICMP----> GNS3 Cisco 3660
```

Netmiko là thư viện đồng bộ nên mỗi đợt quét chạy trong thread pool, không chạy trực tiếp trên event loop của FastAPI. Collector thread chỉ trả DTO; không chia sẻ SQLAlchemy Session giữa các thread. Trong phạm vi đồ án, backend chỉ chạy một Uvicorn worker và không dùng `--reload` trong Compose để tránh APScheduler tạo lịch trùng.

## 5. Cấu trúc mã nguồn dự kiến

```text
QTM/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   │   ├── collectors/
│   │   │   ├── parsers/
│   │   │   ├── health/
│   │   │   ├── scheduler/
│   │   │   └── reports/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   │   └── fixtures/cisco_ios/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── types/
│   ├── Dockerfile
│   └── package.json
├── plans/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 6. Mô hình dữ liệu

### `devices`

- `id`, `name`, `host`, `port`, `device_type`, `username`.
- `password_encrypted`, `secret_encrypted`.
- `site`, `is_active`, `check_interval_minutes`.
- `created_at`, `updated_at`.

API không bao giờ trả mật khẩu. Mật khẩu được mã hóa bằng Fernet với khóa lấy từ biến môi trường.

### `health_checks`

- `id`, `device_id`, `started_at`, `finished_at`.
- `overall_status`, `management_ping_reachable`, `ssh_reachable`.
- `cpu_percent`, `memory_percent`, `uptime_seconds`.
- `error_message`.

`execution_status` dùng duy nhất `queued/running/succeeded/failed`. Không SSH được là lần thu thập đã `succeeded` nhưng sức khỏe là `Critical`; `failed` chỉ dành cho lỗi nội bộ khiến hệ thống không thể tạo kết quả hợp lệ.

### `scan_runs`

- Đại diện một lần `Run all`, dùng để polling và tạo báo cáo cùng đợt.
- `id`, `execution_status`, `started_at`, `finished_at`, tổng số check thành công/thất bại.
- `health_checks.scan_run_id` là khóa ngoại nullable để check đơn lẻ vẫn hoạt động.

### `device_ping_targets`

- `device_id`, `target`, `name`, `is_required`, `is_active`.

### `monitored_interfaces`

- `device_id`, `interface_name`, `is_required`, `is_active`.

### `interface_results`

- `id`, `health_check_id`, `name`.
- `admin_status`, `oper_status`.
- `input_errors`, `output_errors`, `crc_errors`, `drops`.

Các counter interface là số tích lũy. Hệ thống lưu giá trị hiện tại nhưng chỉ đánh giá phần tăng so với lần check thành công trước; lần đầu chỉ tạo baseline. Chỉ interface được đánh dấu theo dõi mới ảnh hưởng trạng thái tổng. Cổng không sử dụng và đã shutdown không được tính là lỗi.

### `ping_results`

- `id`, `health_check_id`, `target`.
- `source_type`: `backend` cho management ping hoặc `device` cho path ping chạy từ router.
- `packets_sent`, `packets_received`, `packet_loss_percent`.
- `latency_min_ms`, `latency_avg_ms`, `latency_max_ms`.

### `findings`

- `id`, `health_check_id`, `metric`, `severity`.
- `actual_value`, `threshold_value`, `message`.

### `settings`

- Ngưỡng CPU, RAM, packet loss, latency.
- Chu kỳ kiểm tra và số luồng tối đa.

### `users`

- Một tài khoản admin trong phạm vi đồ án.
- Lưu password hash; không lưu hoặc ghi log mật khẩu rõ.

Các timestamp lưu bằng UTC, frontend hiển thị theo `Asia/Ho_Chi_Minh`. Tạo index tối thiểu cho `(device_id, started_at)`, `overall_status` và `scan_run_id`. Xóa thiết bị theo kiểu soft-delete để giữ lịch sử.

Không lưu file báo cáo trong database; PDF/CSV được tạo từ dữ liệu lịch sử khi người dùng yêu cầu.

## 7. Quy tắc đánh giá mặc định

| Chỉ số | Healthy | Warning | Critical |
|---|---:|---:|---:|
| CPU | `< 70%` | `70–89%` | `>= 90%` |
| RAM | `< 75%` | `75–89%` | `>= 90%` |
| Packet loss với 10 gói | `0%` | `10–20%` | `>= 30%` |
| Latency trung bình | `< 50 ms` | `50–150 ms` | `> 150 ms` |
| SSH | Thành công | — | Thất bại |
| Interface được theo dõi | Up, counter không tăng | Counter CRC/drop tăng | Down |

Quy tắc tổng hợp:

- Có bất kỳ chỉ số `Critical` thì thiết bị là `Critical`.
- Không có `Critical` nhưng có `Warning` thì là `Warning`.
- Tất cả chỉ số đạt ngưỡng thì là `Healthy`.
- SSH thành công nhưng ICMP thất bại không tự động kết luận thiết bị down vì ICMP có thể bị chặn; tạo finding cảnh báo kết nối.
- Thiếu dữ liệu do parser không nhận dạng phải ghi rõ `Unknown` ở cấp chỉ số và tạo finding `Warning`, không âm thầm coi là Healthy.
- CPU dùng giá trị trung bình 5 phút từ `show processes cpu`.
- RAM dùng Processor pool: `used / (used + free) * 100`.
- Management ping đo từ backend tới management IP. Path ping chạy từ router tới từng ping target bằng IOS CLI.
- Nếu có nhiều target bắt buộc, trạng thái path lấy target xấu nhất. Target tùy chọn chỉ tạo finding, không kéo trạng thái tổng xuống.

## 8. API chính

```text
POST   /api/v1/auth/login
GET    /api/v1/devices
POST   /api/v1/devices
GET    /api/v1/devices/{id}
PUT    /api/v1/devices/{id}
DELETE /api/v1/devices/{id}
POST   /api/v1/devices/{id}/test-connection
POST   /api/v1/devices/{id}/checks
POST   /api/v1/checks/run-all
GET    /api/v1/checks/{id}
GET    /api/v1/scan-runs/{id}
GET    /api/v1/devices/{id}/history
GET    /api/v1/dashboard/summary
GET    /api/v1/reports/csv
GET    /api/v1/reports/pdf
GET    /api/v1/settings
PUT    /api/v1/settings
```

Endpoint tạo check trả `202 Accepted`; nếu cùng thiết bị đang chạy thì trả `409 Conflict`. React polling API cho đến khi hoàn tất; WebSocket nằm ngoài phạm vi 15 tuần.

## 9. Kế hoạch triển khai

### Bước 1 — Chốt yêu cầu, dựng lab GNS3 và kiểm tra đường mạng

**Phụ thuộc:** Không.

**Bối cảnh:** Ứng dụng chỉ hoạt động khi host và container backend có đường IP tới management IP của router. Cisco 3660 cần image có crypto để dùng SSH.

**Công việc:**

1. Dựng `R1 -- R2 -- R3`, thêm một mạng management kết nối tới host.
2. Đặt IP, hostname, route và tài khoản privilege 15 cho từng router.
3. Cấu hình domain, RSA key, SSH v2 và `line vty` dùng `login local`.
4. Đặt Idle-PC cho từng router để tránh CPU máy host bị chiếm cao.
5. Lưu startup-config và file project GNS3.
6. Từ Windows, ping và SSH tới cả ba management IP.
7. Ghi IP/topology vào `docs/gns3-lab.md`, không ghi mật khẩu thật.

**Kiểm tra:**

```powershell
ping <management-ip>
ssh admin@<management-ip>
```

**Hoàn thành khi:** Windows truy cập được cả ba router và chạy được `show version` qua SSH. Kiểm tra từ container được hoàn tất ở Bước 2 sau khi backend image tồn tại.

**Rollback:** Khôi phục snapshot/project GNS3 trước cấu hình; không thay đổi ứng dụng.

### Bước 2 — Khởi tạo repository và Docker skeleton

**Phụ thuộc:** Bước 1 chỉ cần hoàn tất trước lúc kiểm thử Netmiko; có thể làm song song phần khởi tạo.

**Bối cảnh:** Workspace hiện trống và chưa phải Git repository.

**Công việc:**

1. Khởi tạo Git, `.gitignore`, `.editorconfig`, `.env.example`.
2. Tạo FastAPI tối thiểu với `/api/v1/health`.
3. Tạo React Vite TypeScript tối thiểu.
4. Tạo PostgreSQL service, volume và healthcheck.
5. Viết Dockerfile development/production cho backend và frontend.
6. Chọn runtime nền ổn định và khóa dependency trong lock file; dùng URL `postgresql+psycopg://...`; cấu hình Vitest ngay từ đầu.
7. Khởi tạo Alembic và base migration. Backend entrypoint chạy `alembic upgrade head` trước Uvicorn để database rỗng tự khởi tạo.
8. Cấu hình CORS chỉ cho URL frontend và bind port host vào `127.0.0.1`.
9. Thêm endpoint healthcheck và dependency order trong Compose.
10. Cài công cụ ICMP cần thiết trong backend image và từ chính image chạy smoke test ping + Netmiko tới router; không chỉ dựa vào SSH native của Windows.
11. Viết README cách chạy cơ bản.

**Kiểm tra:**

```powershell
docker compose config
docker compose up --build -d
docker compose ps
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-WebRequest http://localhost:3000
```

**Hoàn thành khi:** Ba service `frontend`, `backend`, `db` đều healthy, backend kết nối được PostgreSQL và Netmiko trong container chạy được `show version` trên cả ba router.

**Rollback:** `docker compose down`; giữ volume database trừ khi chắc chắn muốn xóa dữ liệu.

### Bước 3 — Thiết kế database và CRUD thiết bị

**Phụ thuộc:** Bước 2.

**Bối cảnh:** Cần cấu trúc dữ liệu ổn định trước khi lưu kết quả collector.

**Công việc:**

1. Tạo SQLAlchemy models và Alembic migration cho các bảng ở mục 6, gồm `scan_runs`, ping targets và monitored interfaces.
2. Tạo Pydantic schemas, repository và service layer.
3. Mã hóa credential bằng khóa môi trường; che credential trong response/log.
4. Viết CRUD thiết bị và cấu hình ping targets/interface theo dõi; xóa logic là soft-delete.
5. Tạo đăng nhập admin tối thiểu và bảo vệ API quản trị.
6. Validate host, port và `device_type`; chỉ cho phép địa chỉ thuộc CIDR lab; không cho người dùng truyền lệnh CLI tùy ý.
7. Thêm pagination, filter theo site/status và unique constraint phù hợp.
8. Viết unit/integration tests cho migration, auth và API CRUD.

**Kiểm tra:**

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend pytest tests/api tests/db -q
```

**Hoàn thành khi:** CRUD hoạt động, API quản trị từ chối request chưa đăng nhập, host ngoài CIDR bị từ chối, migration chạy từ database rỗng, mật khẩu không xuất hiện trong API hoặc log.

**Rollback:** Alembic downgrade đúng một revision; sao lưu DB trước khi rollback trên dữ liệu thật.

### Bước 4 — Xây collector Netmiko và parser Cisco IOS

**Phụ thuộc:** Bước 1 và Bước 3.

**Bối cảnh:** Cisco 3660 có output phụ thuộc phiên bản IOS. Parser phải dựa trên output thật của image đang dùng, không chỉ giả định output hiện đại.

**Công việc:**

1. Tạo command profile `cisco_ios` cho `show version`, CPU, memory, interface và ping.
2. Viết lớp kết nối Netmiko với timeout, retry có giới hạn và đóng session trong `finally`.
3. Dùng TextFSM/ntc-templates khi phù hợp; thêm parser riêng có test fixture cho output chưa được hỗ trợ.
4. Chuẩn hóa output thành DTO độc lập với vendor; CPU là 5-minute, RAM là Processor pool.
5. Thu thập output thật từ R1/R2/R3 và lưu bản đã xóa thông tin nhạy cảm vào fixtures.
6. Tách management ping `backend → router` và path ping `router → target`; path ping dùng 10 gói để khớp ngưỡng live.
7. Phân biệt lỗi ping, lỗi TCP/SSH, lỗi xác thực và lỗi parser.
8. Giới hạn số kết nối đồng thời bằng `ThreadPoolExecutor`; thread chỉ trả DTO và không giữ/chia sẻ DB Session.

**Các lệnh dự kiến:**

```text
show version
show processes cpu
show memory statistics
show ip interface brief
show interfaces
ping <target> repeat 10
```

**Kiểm tra:**

```powershell
docker compose exec backend pytest tests/services/collectors tests/services/parsers -q
docker compose exec backend python -m app.scripts.check_device --device-id <id>
```

**Hoàn thành khi:** Một lần chạy trả về dữ liệu chuẩn hóa cho CPU, RAM, uptime, interface và ping; mọi fixture đều có test parser.

**Rollback:** Tắt collector mới bằng feature flag hoặc quay lại command profile trước đó; không sửa dữ liệu lịch sử.

### Bước 5 — Bộ đánh giá sức khỏe và lưu kết quả

**Phụ thuộc:** Bước 3 và Bước 4.

**Bối cảnh:** Đánh giá phải thuần logic để kiểm thử được mà không cần GNS3.

**Công việc:**

1. Viết evaluator nhận DTO + thresholds và trả status/findings.
2. Xử lý chính xác các giá trị sát biên ngưỡng.
3. Chỉ đánh giá interface được cấu hình theo dõi.
4. Tính delta của CRC/drop so với check thành công trước; lần đầu chỉ lưu baseline.
5. Tạo check record trước khi chạy và cập nhật execution status khi hoàn tất/thất bại. Không SSH được vẫn tạo kết quả `Critical` với execution `succeeded`.
6. Lưu health check, interface results, ping results và findings trong transaction với Session riêng.
7. Thêm endpoint kiểm tra một thiết bị, toàn bộ thiết bị và xem lịch sử.
8. Chặn chạy trùng trên cùng thiết bị; đặt timeout tổng cho job.

**Kiểm tra:**

```powershell
docker compose exec backend pytest tests/services/health tests/api/test_checks.py -q
```

**Kịch bản bắt buộc:** 69/70/89/90% CPU bằng fixture; interface down; counter delta 0 và >0; SSH sai mật khẩu; 0/10/20/30% loss; timeout.

**Hoàn thành khi:** Trạng thái và findings đúng với bảng ngưỡng, lịch sử được lưu đầy đủ kể cả lần chạy thất bại.

**Rollback:** Tạm ngưng endpoint check và giữ dữ liệu; evaluator cũ có thể được chọn theo version cấu hình.

### Bước 6 — Scheduler và kiểm tra nhiều thiết bị

**Phụ thuộc:** Bước 5.

**Bối cảnh:** Netmiko blocking và mỗi router có thể timeout lâu. Scheduler không được làm treo API hoặc tạo job trùng.

**Công việc:**

1. Tích hợp APScheduler theo API 3.x trong FastAPI lifespan; Uvicorn chạy một worker, không reload.
2. Đọc chu kỳ kiểm tra từ settings/device.
3. Chạy nhiều thiết bị qua thread pool với giới hạn cấu hình được.
4. Đặt `coalesce=true`, `max_instances=1` và khóa theo device để tránh đợt quét trùng.
5. Ghi log có `check_id`, `device_id`, thời lượng và loại lỗi.
6. Dọn lịch sử theo retention policy tùy chọn.
7. Hiển thị trạng thái job `queued/running/succeeded/failed` cho frontend polling.

**Kiểm tra:**

```powershell
docker compose exec backend pytest tests/services/scheduler -q
docker compose logs backend --since 10m
```

**Hoàn thành khi:** Lịch tự chạy tối thiểu hai chu kỳ; không có hai check `running` cùng device; POST check phản hồi dưới 1 giây; router timeout kết thúc trong tối đa 30 giây; API health vẫn phản hồi trong lúc đó.

**Rollback:** Tắt `SCHEDULER_ENABLED`; kiểm tra thủ công vẫn hoạt động.

### Bước 7 — React Dashboard và quản lý thiết bị

**Phụ thuộc:** Bước 3 cho bản mock; bản tích hợp thật phụ thuộc Bước 5. Có thể bắt đầu UI bằng mock API trong khi Bước 4–5 đang làm.

**Bối cảnh:** Frontend chỉ hiển thị dữ liệu backend, không chứa credential và không tự suy luận trạng thái.

**Công việc:**

1. Cấu hình React Router, Axios client và TanStack Query.
2. Tạo trang đăng nhập admin, lưu token an toàn phù hợp phạm vi local demo và xử lý hết hạn đăng nhập.
3. Tạo layout Bootstrap responsive và bảng màu nhất quán.
4. Trang Dashboard: tổng thiết bị, Healthy/Warning/Critical, lần quét gần nhất.
5. Trang Devices: danh sách, thêm/sửa, test connection, kích hoạt/tạm dừng.
6. Trang Device Detail: tổng quan, CPU/RAM, interfaces, ping, findings và lịch sử.
7. Dùng Chart.js cho CPU/RAM, latency/loss theo thời gian.
8. Nút Check now/Run all có loading, polling, lỗi rõ ràng và chống bấm lặp.
9. Thêm empty/loading/error states và xác nhận khi xóa.

**Kiểm tra:**

```powershell
docker compose exec frontend npm run lint
docker compose exec frontend npm run test
docker compose exec frontend npm run build
```

**Hoàn thành khi:** Toàn bộ luồng thêm router → test SSH → chạy check → xem kết quả/lịch sử thực hiện được trên web.

**Rollback:** Frontend có thể quay lại API mock; backend không phụ thuộc frontend.

### Bước 8 — Báo cáo web, PDF và CSV

**Phụ thuộc:** Bước 5; tích hợp UI sau Bước 7.

**Bối cảnh:** Báo cáo là ảnh chụp dữ liệu trong khoảng thời gian, không phải một hệ thống đánh giá riêng.

**Công việc:**

1. Cho chọn khoảng thời gian, site, thiết bị và trạng thái.
2. Quy định số liệu kỳ báo cáo: trạng thái mới nhất; max/avg CPU, RAM, loss, latency; tổng findings theo severity.
3. Xuất CSV UTF-8 BOM để mở đúng trong Excel và chống CSV formula injection với giá trị bắt đầu bằng `=`, `+`, `-`, `@`.
4. Xuất PDF bằng ReportLab, nhúng font Noto Sans để hiển thị đúng tiếng Việt; gồm tổng quan, bảng thiết bị và findings chính.
5. Stream file từ backend, đặt tên có timestamp.
6. Thêm nút tải trên React và test dữ liệu rỗng/dữ liệu lớn.
7. Không ghi credential hoặc raw command output vào báo cáo.

**Kiểm tra:**

```powershell
docker compose exec backend pytest tests/services/reports tests/api/test_reports.py -q
```

**Hoàn thành khi:** CSV mở đúng cột/tiếng Việt; PDF mở đúng và không lỗi font; số dòng và số liệu tổng hợp của cả hai định dạng khớp truy vấn SQL chuẩn.

**Rollback:** Tắt route download; dữ liệu gốc không bị ảnh hưởng.

### Bước 9 — Kiểm thử hệ thống, bảo mật và ổn định

**Phụ thuộc:** Bước 6–8.

**Bối cảnh:** Cần chứng minh ứng dụng chịu được thiết bị mất kết nối, output lạ và restart container.

**Công việc:**

1. Chạy unit tests cho evaluator/parser và integration tests cho API/PostgreSQL.
2. Thực hiện các tình huống demo: bình thường, CPU/RAM cảnh báo bằng fixture, interface shutdown, sai credential, router tắt, packet loss 100%.
3. Kiểm tra timeout, retry, race condition và job trùng.
4. Restart backend/db và xác nhận volume giữ dữ liệu.
5. Quét dependency, kiểm tra `.env`, log và response không lộ secret.
6. Kiểm tra responsive cơ bản và lỗi API trên UI.
7. Ghi `docs/test-results.md` với bằng chứng/screenshot.
8. Kiểm tra Fernet key tồn tại ổn định qua restart; thiếu/sai key phải fail-fast với lỗi rõ ràng.

**Kiểm tra:**

```powershell
docker compose exec backend pytest --cov=app --cov-report=term-missing
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
docker compose restart backend db
docker compose ps
```

**Hoàn thành khi:** Parser có fixture cho 100% command bắt buộc; mọi biên threshold và counter delta có test; restart không mất dữ liệu; không có secret trong Git/log/report; các lỗi mạng không làm backend crash.

**Rollback:** Tắt scheduler và dùng kiểm tra thủ công để cô lập lỗi; khôi phục backup DB nếu migration gây lỗi.

### Bước 10 — Tài liệu, đóng gói và kịch bản bảo vệ

**Phụ thuộc:** Bước 9.

**Bối cảnh:** Đồ án cần tái lập được trên máy khác và có demo ngắn, có chủ đích.

**Công việc:**

1. Hoàn thiện README: yêu cầu, kiến trúc, cấu hình môi trường, cách chạy và troubleshooting.
2. Tạo sơ đồ kiến trúc, ERD, sequence diagram quá trình health check.
3. Ghi hướng dẫn dựng GNS3 và kết nối Docker.
4. Tạo dữ liệu mẫu và lệnh reset chỉ dành cho môi trường demo.
5. Viết kịch bản demo 7–10 phút: thêm thiết bị, quét, tạo lỗi, xem đổi trạng thái, tải báo cáo.
6. Viết phần giới hạn: CPU giả lập không phản ánh thiết bị thật, IOS cũ, chỉ hỗ trợ Cisco IOS.
7. Chuẩn bị hướng mở rộng: SNMP, đa vendor, Celery/Redis, alert, RBAC.

**Kiểm tra:**

```powershell
docker compose down
docker compose up --build -d
docker compose ps
```

**Hoàn thành khi:** Một máy sạch có thể chạy hệ thống theo README và hoàn tất kịch bản demo mà không sửa mã nguồn.

**Rollback:** Giữ bản release/tag demo ổn định; không đưa ý tưởng mở rộng vào phạm vi chính ở phút cuối.

## 10. Quan hệ phụ thuộc và phần có thể làm song song

```text
B1 Lab -----------+----> B4 Collector ----+
                  |                       |
B2 Skeleton -> B3 Database/API ----------+--> B5 Evaluator/Persistence -> B6 Scheduler
                         |                                   |
                         +----> B7 React (mock trước) -------+
                                                             |
                                      B8 Reports <------------+
                                             |
                                      B9 System test -> B10 Docs/demo
```

- Sau B2, B1 và B3 có thể làm song song.
- Sau CRUD của B3, frontend B7 có thể làm bằng mock data trong khi B4/B5 đang phát triển.
- B8 có thể phát triển song song phần cuối B7 sau khi schema kết quả của B5 ổn định.
- Không nên làm scheduler trước khi một lần kiểm tra đơn lẻ và transaction lưu kết quả đã ổn định.

## 11. Lịch thực hiện trong 15 tuần

| Tuần | Nội dung | Đầu ra |
|---|---|---|
| 1 | Phân tích yêu cầu, use case, kiến trúc | Phạm vi, tiêu chí, sơ đồ tổng thể được chốt |
| 2 | B1: dựng GNS3 R1–R3, cấu hình IP/SSH | Windows ping/SSH được cả ba router |
| 3 | B2: repository, FastAPI, React, PostgreSQL, Docker | `docker compose up --build` chạy skeleton |
| 4 | B3: schema, Alembic, mã hóa credential, auth | Migration và đăng nhập admin hoạt động |
| 5 | B3 + B7: API và giao diện CRUD thiết bị | Thêm/sửa/tạm dừng/test connection trên web |
| 6 | B4: Netmiko connection và thu output thật | Container chạy lệnh trên Cisco 3660 |
| 7 | B4: parser uptime, CPU, RAM | DTO chuẩn hóa và fixture tests |
| 8 | B4: interface, management ping, path ping | Có interface, loss và latency chuẩn hóa |
| 9 | B5: evaluator, findings, transaction lưu kết quả | Healthy/Warning/Critical và lịch sử đúng |
| 10 | B6 + B7 cơ bản: Run all, scheduler, dashboard trạng thái | **Mốc MVP:** chạy trọn luồng từ web và giữ lịch sử sau restart |
| 11 | B7: hoàn thiện dashboard và polling | Cards, trạng thái, danh sách lần quét, xử lý lỗi UI |
| 12 | B7: chi tiết, biểu đồ, lịch sử, settings | Trang thiết bị và cấu hình ngưỡng hoàn chỉnh |
| 13 | B8: báo cáo web, PDF, CSV | Lọc theo kỳ và tải hai định dạng |
| 14 | B9: test lỗi mạng, bảo mật, restart, sửa lỗi | Biên bản test và bản release candidate |
| 15 | B10: README, sơ đồ, báo cáo đồ án, demo | Bản cuối, slide và kịch bản bảo vệ 7–10 phút |

## 12. Rủi ro chính và cách xử lý

Các cổng kiểm soát tiến độ:

1. **Tuần 3 — Infrastructure gate:** GNS3, Docker và PostgreSQL kết nối được.
2. **Tuần 5 — Management gate:** database, auth và CRUD thiết bị hoạt động.
3. **Tuần 10 — MVP gate:** hoàn tất luồng thu thập → đánh giá → lưu → dashboard → lịch tự động.
4. **Tuần 13 — Feature-complete gate:** biểu đồ, settings, PDF và CSV hoàn tất.
5. **Tuần 15 — Final gate:** test đạt, tài liệu đủ và demo tái lập được.

Retention UI và cảnh báo Telegram/email là tùy chọn; không được làm trước khi feature-complete gate đạt.

| Rủi ro | Xử lý |
|---|---|
| Container không route được tới GNS3 | Giải quyết ở B1 trước khi viết Netmiko; ghi rõ adapter/route |
| Image 3660 không hỗ trợ SSH v2 | Kiểm tra feature set `k9`; tạm SSH v1 chỉ trong lab nếu bắt buộc và ghi giới hạn |
| Output IOS cũ khác template | Lưu fixture thật và viết parser có test |
| Cổng shutdown không sử dụng gây Critical giả | Chỉ đánh giá interface được theo dõi |
| CRC/drop cũ gây Warning mãi | Đánh giá delta giữa hai lần check; lần đầu tạo baseline |
| Ping bị chặn nhưng SSH vẫn hoạt động | Không đồng nhất ping fail với device down |
| Netmiko làm treo API | Thread pool, timeout, retry giới hạn, job status |
| Scheduler chạy trùng | Một scheduler process và PostgreSQL advisory lock |
| Mật khẩu bị lộ | Mã hóa, mask response/log, `.env` không commit |
| CPU GNS3 không thực tế | Dùng để demo logic, không kết luận hiệu năng thiết bị thật |
| Mở rộng quá sớm | Giữ phạm vi một vendor; Celery/Redis, đa hãng, SNMP và RBAC đưa sang giai đoạn sau |

## 13. Bộ dữ liệu và kịch bản demo

1. `R1 Healthy`: SSH thành công, interface theo dõi up, loss thấp.
2. `R2 Warning`: trong demo live dùng ngưỡng demo được ghi chú hoặc làm counter/loss tăng; fixture chỉ dùng để chứng minh unit test CPU/RAM.
3. `R3 Critical`: shutdown interface được theo dõi hoặc tắt router/sai route để SSH thất bại.
4. Chạy `Run all`, quan sát ba màu trên dashboard.
5. Mở chi tiết R3 để xem finding và nguyên nhân.
6. Khôi phục R3, quét lại và chứng minh lịch sử vẫn giữ lần lỗi cũ.
7. Xuất PDF và CSV của đợt kiểm tra.

## 14. Quy tắc thay đổi kế hoạch

- Mỗi thay đổi phạm vi phải ghi: lý do, bước bị ảnh hưởng, migration/API có đổi hay không và cách rollback.
- Chỉ thêm tính năng mở rộng sau khi tiêu chí B9 đạt.
- Nếu một bước quá lớn hơn một tuần, tách thành backend/frontend/test nhưng giữ nguyên tiêu chí đầu ra.
- Không đổi schema hoặc status contract âm thầm sau khi frontend đã tích hợp; phải version migration và cập nhật API schema/tests.
- Nếu bỏ một bước, ghi rõ tiêu chí hoàn thành nào được loại bỏ hoặc chuyển sang giai đoạn sau.
