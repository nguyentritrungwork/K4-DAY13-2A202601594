# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: C6-2
- Repository URL:https://github.com/nguyentritrungwork/K4-DAY13-2A202601594
- Commit SHA cuối:
- Thành viên và vai trò:Nguyễn Nhật Minh ,Nguyễn Trí Trung, Trần Đặng Vương Quốc Long

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 30/100
- Tổng số traces: 10
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:day13-chat
- Version/label baseline:  3.2.1
- Version/label candidate:	3.2.1
- Trace ID của mỗi version:
      baseline: run: 1ba44fecee2c20585b87fce05970de13
      candidate: run: b3085ca32edbc4ff6da353296c5fbbb2
- Bằng chứng đổi label hoặc rollback:
https://cloud.langfuse.com/project/cmsofrgxh00obad0cs7kwe4bb/prompts/day13-chat?version=1&tab=linked-generations

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`
- Triệu chứng từ metrics:
  - Latency trung bình trên server tăng đột biến từ mức bình thường (~150ms) lên tới **2.6 giây (2600ms)**, vi phạm nghiêm trọng ngưỡng SLO thiết lập (2000ms).
  - Từ góc nhìn của client khi chạy tải đồng thời (`concurrency 5`), latency tích lũy tăng dần từ **14939.0ms (gần 15 giây)** do các requests bị nghẽn queue.
  - Endpoint ảnh hưởng: `/chat` với feature `monitoring`.
- Trace ID liên quan:
  - Có thể tìm kiếm trực tiếp trên Langfuse bằng các tag hoặc metadata chứa Correlation ID: `req-3de71d9f`, `req-6b5d0bc1`, `req-6e15fd91`, `req-84fd2415`, `req-a5268ee8`.
- Log line/correlation ID liên quan:
  - Correlation IDs: `req-3de71d9f`, `req-6b5d0bc1`, `req-6e15fd91`, `req-84fd2415`, `req-a5268ee8`.
  - Dòng log mẫu từ `data/logs.jsonl` khi gửi request:
    `{"service": "api", "payload": {"message_preview": "Summarize the observability workflow for an AI API."}, "event": "request_received", "user_id_hash": "cbc3dffc63cf", "model": "claude-sonnet-4-5", "session_id": "k4-challenge-s03", "feature": "monitoring", "env": "dev", "correlation_id": "req-3de71d9f", "level": "info", "ts": "2026-08-11T10:22:36.202543Z"}`
    `{"service": "api", "latency_ms": 3666, "tokens_in": 43, "tokens_out": 94, "cost_usd": 0.001539, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer..."}, "event": "response_sent", "user_id_hash": "cbc3dffc63cf", "model": "claude-sonnet-4-5", "session_id": "k4-challenge-s03", "feature": "monitoring", "env": "dev", "correlation_id": "req-3de71d9f", "level": "info", "ts": "2026-08-11T10:22:40.503622Z"}`
- Root cause:
  - Sự cố bắt nguồn từ việc kích hoạt incident `rag_slow` (chuyển đổi cờ trạng thái trong `app/mock_rag.py`), dẫn đến việc hàm RAG `retrieve` kích hoạt lệnh sleep đồng bộ:
    ```python
    if STATE["rag_slow"]:
        time.sleep(2.5)
    ```
  - Lệnh sleep đồng bộ (`time.sleep`) trong một FastAPI endpoint đồng bộ chạy đơn luồng (single worker) của Uvicorn đã chặn hoàn toàn event loop. Khi client gửi nhiều request đồng thời, các request bị xếp hàng (queued) và thực thi tuần tự, làm tăng lũy kế latency ở phía client lên gấp nhiều lần.
- Fix action:
  - Khắc phục tức thời bằng cách gọi POST API để tắt incident: `/incidents/rag_slow/disable`.
  - Tối ưu hóa Vector DB và các câu truy vấn RAG để rút ngắn thời gian phản hồi thực tế của bước retrieval dưới 500ms.
- Preventive measure:
  - Thiết lập timeout cho dịch vụ RAG (ví dụ: tối đa 1.5s), nếu quá thời gian thì trả về kết quả fallback hoặc báo lỗi ngay thay vì treo luồng.
  - Sử dụng cơ chế chạy đa luồng/nhiều worker cho Uvicorn (ví dụ: `--workers 4`) để ngăn chặn việc một request bị nghẽn làm ảnh hưởng đến các request đồng thời khác.
  - Chuyển đổi các cuộc gọi RAG sang dạng bất đồng bộ (`async`/`await asyncio.sleep`) để tránh chặn event loop của ứng dụng.
  - Áp dụng caching đối với các câu hỏi hoặc tài liệu RAG phổ biến để giảm tải cho Vector DB.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
