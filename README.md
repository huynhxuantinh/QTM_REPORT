# Network Health Check

Hệ thống kiểm tra sức khỏe router Cisco IOS trong GNS3 bằng Python, Netmiko,
FastAPI, PostgreSQL, React và Docker. Hệ thống thu thập CPU, RAM, uptime,
interface, packet loss và latency, sau đó đánh giá thành `Healthy`, `Warning`
hoặc `Critical`.

## Mô hình demo đã chuẩn bị

| Thiết bị | IP | Vai trò | Kết quả mong đợi |
|---|---|---|---|
| R1 | `192.168.141.11` | Router thật trong GNS3 | Kết nối SSH thành công |
| R2 | `192.168.141.12` | Router thật trong GNS3 | Kết nối SSH thành công |
| R3 | `192.168.141.13` | Router thật trong GNS3 | Kết nối SSH thành công |
| R4 - Mất kết nối (Demo) | `192.168.141.14` | Thiết bị giả, không có router thật | `Critical`, SSH thất bại |

- Project GNS3: `Network_Health_Check`
- Ubuntu VM chạy Docker: `192.168.141.128`
- Trang web: `http://192.168.141.128:3000`
- Tài khoản web demo: `admin / qtm`
- Tài khoản SSH router trong lab: `admin / qtm`

> Các tài khoản trên chỉ dùng cho môi trường lab, không dùng trong hệ thống thật.

## Cấu hình Settings khuyến nghị khi demo

Mở trang **Cấu hình** và đặt:

| Thông số | Cảnh báo | Nghiêm trọng |
|---|---:|---:|
| CPU | 70% | 90% |
| RAM | 75% | 90% |
| Packet loss | 10% | 30% |
| Latency | 50 ms | 150 ms |

- Chu kỳ tự động: `15 phút`.
- Số thiết bị kiểm tra đồng thời: `3`.
- Khi thuyết trình nên đặt `SCHEDULER_ENABLED=false` trong `.env` để chủ động
  bấm **Quét tất cả**. Nếu muốn trình diễn quét tự động thì đặt thành `true`.

## Checklist trước buổi demo

1. Bật Ubuntu VM và chờ Ubuntu khởi động hoàn tất.
2. Mở GNS3 trên Windows.
3. Mở project `Network_Health_Check`.
4. Bấm **Start All Nodes** và chờ khoảng 30 giây.
5. Kiểm tra Docker trên Ubuntu:

   ```bash
   cd ~/QTM
   docker compose ps
   ```

6. Nếu container chưa chạy:

   ```bash
   cd ~/QTM
   docker compose up -d
   ```

7. Mở `http://192.168.141.128:3000` và đăng nhập `admin / qtm`.
8. Bấm **Quét tất cả**.

Kết quả đúng là R1–R3 kết nối thành công và R4 Demo báo mất kết nối. Nhờ đó
Dashboard luôn có cả trường hợp tốt và nghiêm trọng để trình bày.

## Kịch bản thuyết trình đề xuất

1. Mở **Tổng quan**, giới thiệu số lượng thiết bị theo trạng thái.
2. Bấm **Quét tất cả** để chạy kiểm tra trực tiếp.
3. Mở R1 để trình bày CPU, RAM, uptime, interface, packet loss và latency.
4. Mở R4 Demo để trình bày khả năng phát hiện thiết bị mất kết nối.
5. Mở **Báo cáo**, lọc theo thời gian/trạng thái rồi xuất Excel (.xlsx) hoặc PDF.
6. Mở **Cấu hình** để giải thích cách thay đổi các ngưỡng đánh giá.

## Khôi phục SSH khi router báo mất kết nối

Nếu R1, R2 hoặc R3 ping được nhưng SSH thất bại, mở console của router đó và
chạy:

```cisco
enable
configure terminal
ip domain-name qtm.local
username admin privilege 15 secret qtm
enable secret qtm
crypto key generate rsa modulus 1024
ip ssh version 2
line vty 0 4
login local
transport input ssh
end
write memory
```

Sau đó quay lại web và bấm **Thử SSH**. Nếu trình duyệt vẫn hiển thị giao diện
cũ, nhấn `Ctrl + F5`.

## Lệnh kiểm tra nhanh

Trên Ubuntu VM:

```bash
ping -c 2 192.168.141.11
ping -c 2 192.168.141.12
ping -c 2 192.168.141.13
docker compose -f ~/QTM/docker-compose.yml ps
```

## Lưu ý để demo ổn định

- Không tạo router thật sử dụng IP `192.168.141.14` vì đây là IP lỗi demo.
- Không xóa thiết bị R4 Demo khỏi trang Thiết bị.
- Luôn dùng đúng project GNS3 `Network_Health_Check`.
- Sau khi sửa cấu hình router phải chạy `write memory`.
- Không xóa Docker volume `qtm_postgres_data`, vì volume chứa dữ liệu và lịch sử.
- Nên chạy thử toàn bộ checklist ít nhất một lần trước buổi báo cáo.

## Tài liệu

- [Kế hoạch triển khai 15 tuần](plans/network-health-check-blueprint.md)
- [Cấu hình GNS3 lab](docs/gns3-lab.md)
- [Hướng dẫn backend](backend/README.md)
- [Hướng dẫn frontend](frontend/README.md)
