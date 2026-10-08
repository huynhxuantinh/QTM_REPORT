# Network Health Check

Hệ thống kiểm tra sức khỏe router Cisco IOS trong GNS3 bằng Python và
Netmiko. Dự án thu thập CPU, RAM, uptime, interface, packet loss và latency,
sau đó tổng hợp thành `Healthy`, `Warning` hoặc `Critical`.

## Trạng thái hiện tại

- GNS3 Cisco 3660 R1 hoạt động tại `192.168.141.11`.
- Ubuntu VMware làm máy collector tại `192.168.141.128`.
- Collector Netmiko đã chạy thành công và xuất báo cáo JSON.
- Parser và health evaluator có 17 unit test, coverage 80%.

## Tài liệu

- [Kế hoạch triển khai 15 tuần](plans/network-health-check-blueprint.md)
- [Cấu hình GNS3 lab](docs/gns3-lab.md)
- [Hướng dẫn collector](backend/README.md)
