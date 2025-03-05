# Hệ thống An ninh Thông minh cho Raspberry Pi 4B

Hệ thống này được phát triển để chạy trên Raspberry Pi 4B, thực hiện hai chức năng chính:
1. Nhận dạng té ngã
2. Nhận dạng ăn trộm

## Tính năng chính

### Nhận dạng té ngã
- Sử dụng mô hình học sâu để phát hiện té ngã
- Gửi tín hiệu thông báo qua chân GPIO của Raspberry Pi
- Tối ưu hóa xử lý cho Raspberry Pi 4B

### Nhận dạng ăn trộm
- Nhận dạng khuôn mặt để phân biệt người nhà và người lạ
- Phân tích hành vi đáng ngờ:
  - Đột nhập vào nhà
  - Xuất hiện vào thời gian bất thường
  - Dáng đi lén lút
  - Che kín mặt
- Gửi tín hiệu cảnh báo qua chân GPIO khi phát hiện ăn trộm

## Yêu cầu cài đặt

```bash
# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

## Cấu hình hệ thống

1. Kết nối camera với Raspberry Pi
2. Cấu hình GPIO pins trong file `config.py`
3. Thêm hình ảnh người trong gia đình vào thư mục `faces/family`
4. Điều chỉnh các tham số trong file `config.py`

## Chạy chương trình

```bash
python main.py
```

## Cấu trúc mã nguồn

```
├── config.py               # Cấu hình hệ thống
├── main.py                 # Chương trình chính
├── fall_detection/         # Module nhận dạng té ngã
│   ├── __init__.py
│   ├── model.py            # Mô hình học sâu nhận dạng té ngã
│   └── detector.py         # Xử lý phát hiện té ngã
├── intruder_detection/     # Module nhận dạng ăn trộm
│   ├── __init__.py
│   ├── face_recognition.py # Nhận dạng khuôn mặt
│   └── behavior_analysis.py # Phân tích hành vi
├── gpio_handler.py         # Xử lý tín hiệu GPIO
└── utils/                  # Các tiện ích khác
    ├── __init__.py
    ├── camera.py           # Xử lý camera
    └── logger.py           # Ghi log
``` 