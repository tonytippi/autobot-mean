# Mean‑RSI Signal Bot — Binance (REST polling) + Telegram + DB + Dashboard

Gửi tín hiệu **Mean‑RSI (BUY)** cho **nhiều cặp** & **nhiều khung thời gian** (4h, 1d) từ **Binance REST** và bắn cảnh báo lên **Telegram**.  
Lưu **lịch sử tín hiệu** vào **SQLite** (mặc định) hoặc **Postgres** (tuỳ chọn). Có sẵn **dashboard Streamlit** để theo dõi.

## 🔧 Tính năng
- REST polling `GET /api/v3/klines` (public, không cần API key).
- Bộ lọc Mean‑RSI: `Close < SMA20 - k*STD20` & `RSI(14) > rsi_min`.
- Gợi ý TP≈SMA20, SL≈ATR(14)×mult (giai đoạn đầu **chỉ gửi tín hiệu**).
- Nhiều cặp/timeframe, tránh trùng lặp bằng state.
- Lưu DB (SQLite / Postgres), có Dashboard.

---

## 🚀 Cách chạy nhanh (SQLite)
Yêu cầu: Docker + docker-compose

```bash
# 1) Chuẩn bị .env (Telegram)
cp .env.example .env
# mở và điền TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID

# 2) Chạy với SQLite (mặc định)
docker compose -f docker-compose.sqlite.yml up --build

# 3) Dashboard sẽ chạy ở: http://localhost:8501
```

## 🚀 Chạy với Postgres (tuỳ chọn)
```bash
# 1) Chuẩn bị .env (Telegram)
cp .env.example .env

# 2) Chạy với Postgres
docker compose -f docker-compose.postgres.yml up --build

# 3) Dashboard: http://localhost:8501
```
> Postgres sẽ dùng DATABASE_URL nội bộ: `postgresql+psycopg2://app:app@db:5432/meanrsi`

---

## ⚙️ Cấu hình
- `config.yaml`:
```yaml
symbols: ["APTUSDT", "BTCUSDT", "ETHUSDT"]
timeframes: ["4h", "1d"]
k: 1.0
rsi_min: 30
sl_atr_mult: 1.5
poll_seconds: 60
```
- `.env` (xem `.env.example`)
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
  - `DATABASE_URL` (tuỳ chọn). Mặc định SQLite: `sqlite:///data/signals.db`

---

## 📦 Cấu trúc
```
mean_rsi_binance_bot_docker/
├─ main.py
├─ binance_client.py
├─ indicators.py
├─ strategy_mean_rsi.py
├─ telegram_notifier.py
├─ database.py
├─ dashboard.py
├─ config.yaml
├─ .env.example
├─ requirements.txt
├─ docker-compose.sqlite.yml
├─ docker-compose.postgres.yml
├─ Dockerfile
└─ data/               # volume cho SQLite & state.json
```

---

## 🧪 Ghi chú vận hành
- Poll mỗi `poll_seconds`, kiểm tra **nến đã đóng** bằng `close_time` so với `now` (UTC).
- Lưu trữ:
  - SQLite: file `data/signals.db`
  - Postgres: service `db` trong docker-compose.
- Dashboard:
  - Trang tổng quan: filter theo symbol/timeframe, bảng tín hiệu mới nhất, và biểu đồ gần nhất.
- Khi chuyển sang auto‑trade, cần thêm API Key & quản trị lệnh (OCO/TP/SL), rate‑limit, kiểm thử kỹ.
