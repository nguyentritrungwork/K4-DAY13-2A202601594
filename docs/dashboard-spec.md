# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

Dashboard chính cần đủ 6 nhóm thông tin:

1. Latency P50/P95/P99.
2. Traffic: request count hoặc QPS.
3. Error rate và breakdown theo loại lỗi.
4. Cost theo thời gian.
5. Tổng token input/output.
6. Quality proxy.

Tiêu chuẩn trình bày:

- Khoảng thời gian mặc định: 1 giờ.
- Tự refresh mỗi 15–30 giây nếu công cụ hỗ trợ.
- Có threshold hoặc SLO line.
- Ghi rõ đơn vị.
- Chỉ giữ 6–8 panel quan trọng ở lớp chính.
- Screenshot phải nhìn được tên panel và khoảng thời gian.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```

## Đặc tả chi tiết (Dashboard Specification)

Công cụ sử dụng: **Langfuse Dashboard / Custom Script (validate_dashboard.py)**
Khoảng thời gian mặc định: **1 giờ (60 phút)**
Tự động làm mới: **Mỗi 30 giây**

| Nhóm chỉ số | Tên Panel (Title) | Đơn vị (Unit) | Threshold / SLO Line |
| --- | --- | --- | --- |
| **1. Latency** | Latency percentiles | ms | P95 <= 3000 ms |
| **2. Traffic** | Request traffic | requests per minute | Rate >= 1 req/min |
| **3. Error** | Error rate and breakdown | % (percent) | Error Rate <= 2% |
| **4. Cost** | Cost over time | USD | Total <= 2.5 USD |
| **5. Tokens** | Input and output tokens | tokens | Sum <= 50,000 tokens |
| **6. Quality** | Quality proxy | Score (0 to 1) | Mean >= 0.75 |
