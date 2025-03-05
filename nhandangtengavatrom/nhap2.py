#!/usr/bin/python3
import os
import sys
import subprocess
import time

def print_step(step, description):
    """In thông tin về bước đang thực hiện"""
    print(f"\n{'='*80}")
    print(f"Bước {step}: {description}")
    print(f"{'='*80}\n")

def run_command(command, description=None):
    """Chạy lệnh và hiển thị kết quả"""
    if description:
        print(f"\n>> {description}")
    
    print(f"Đang chạy: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Lỗi (mã {result.returncode}):")
        print(result.stderr)
        return False
    else:
        print("Thành công!")
        if result.stdout.strip():
            print("Kết quả:")
            print(result.stdout)
        return True

def main():
    # Kiểm tra quyền root
    if os.geteuid() != 0:
        print("Vui lòng chạy script này với quyền sudo!")
        sys.exit(1)
    
    print_step(1, "Cập nhật hệ thống")
    run_command("apt-get update", "Cập nhật danh sách gói")
    run_command("apt-get upgrade -y", "Nâng cấp các gói hiện có")
    
    print_step(2, "Cài đặt các gói phụ thuộc cơ bản")
    dependencies = [
        "python3-pip",
        "python3-dev",
        "libatlas-base-dev",       # Cho numpy
        "libjasper-dev",           # Cho OpenCV
        "libqt4-test",             # Cho OpenCV
        "libwebp-dev",             # Cho OpenCV
        "libtiff5-dev",            # Cho OpenCV
        "libopenexr-dev",          # Cho OpenCV
        "libgstreamer1.0-dev",     # Cho OpenCV
        "libavcodec-dev",          # Cho OpenCV
        "libavformat-dev",         # Cho OpenCV
        "libswscale-dev",          # Cho OpenCV
        "libqtgui4",               # Cho OpenCV
        "libqt4-test",             # Cho OpenCV
        "cmake",                   # Cho dlib
        "build-essential",         # Cho nhiều gói
        "gfortran",                # Cho các thư viện khoa học
        "git",                     # Cho tải mã nguồn
        "pkg-config",              # Cho nhiều gói
    ]
    
    run_command(f"apt-get install -y {' '.join(dependencies)}", "Cài đặt các gói phụ thuộc")
    
    print_step(3, "Cài đặt và cấu hình virtualenv")
    run_command("pip3 install virtualenv", "Cài đặt virtualenv")
    
    if not os.path.exists("/home/pi/security_system"):
        run_command("mkdir -p /home/pi/security_system", "Tạo thư mục cho dự án")
        run_command("chown -R pi:pi /home/pi/security_system", "Đặt quyền cho thư mục")
    
    # Chuyển đến thư mục của người dùng pi để tạo môi trường ảo
    os.chdir("/home/pi/security_system")
    
    # Tạo và kích hoạt môi trường ảo
    if not os.path.exists("venv"):
        run_command("python3 -m virtualenv venv", "Tạo môi trường ảo")
    
    print_step(4, "Cài đặt các thư viện Python")
    # Cài đặt các thư viện trong môi trường ảo
    pip_packages = [
        "numpy",
        "scipy",
        "matplotlib",
        "pillow",
        "scikit-learn",
        "imutils",
        "dlib",
        "RPi.GPIO",
        "pickle-mixin",
        "face-recognition",
        "datetime",
        "logging",
        "tqdm",  # Để hiển thị tiến trình
    ]
    
    run_command(f"/home/pi/security_system/venv/bin/pip3 install {' '.join(pip_packages)}", 
               "Cài đặt các thư viện Python cơ bản")
    
    print_step(5, "Cài đặt OpenCV")
    # OpenCV có thể mất nhiều thời gian để cài đặt
    run_command("/home/pi/security_system/venv/bin/pip3 install opencv-contrib-python==4.5.3.56", 
               "Cài đặt OpenCV (có thể mất nhiều thời gian)")
    
    print_step(6, "Cài đặt TensorFlow Lite")
    run_command("/home/pi/security_system/venv/bin/pip3 install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp39-cp39-linux_armv7l.whl", 
               "Cài đặt TensorFlow Lite Runtime")
    
    print_step(7, "Tạo cấu trúc thư mục cho dự án")
    folders = ["models", "logs", "data"]
    for folder in folders:
        if not os.path.exists(f"/home/pi/security_system/{folder}"):
            run_command(f"mkdir -p /home/pi/security_system/{folder}", f"Tạo thư mục {folder}")
    
    # Đặt quyền cho toàn bộ dự án
    run_command("chown -R pi:pi /home/pi/security_system", "Đặt quyền cho thư mục dự án")
    
    print_step(8, "Tạo script khởi động")
    startup_script = """#!/bin/bash
cd /home/pi/security_system
source venv/bin/activate
python3 home_security.py
"""
    
    with open("/home/pi/security_system/start.sh", "w") as f:
        f.write(startup_script)
    
    run_command("chmod +x /home/pi/security_system/start.sh", "Đặt quyền thực thi cho script khởi động")
    
    # Tạo dịch vụ systemd để chạy khi khởi động
    service_content = """[Unit]
Description=Home Security System
After=network.target

[Service]
ExecStart=/home/pi/security_system/start.sh
WorkingDirectory=/home/pi/security_system
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
"""
    
    with open("/etc/systemd/system/home-security.service", "w") as f:
        f.write(service_content)
    
    run_command("systemctl daemon-reload", "Tải lại dịch vụ systemd")
    run_command("systemctl enable home-security.service", "Kích hoạt dịch vụ tự động khởi động")
    
    print_step(9, "Kiểm tra cài đặt")
    # Tạo script kiểm tra
    test_script = """
import cv2
import numpy as np
import RPi.GPIO as GPIO
import tflite_runtime.interpreter as tflite
import face_recognition

print("OpenCV version:", cv2.__version__)
print("NumPy version:", np.__version__)
print("TFLite available:", tflite.__name__)
print("face_recognition available:", face_recognition.__name__)
print("GPIO available:", GPIO.__name__)

print("\\nTất cả thư viện đã được cài đặt thành công!")
"""
    
    with open("/home/pi/security_system/test_install.py", "w") as f:
        f.write(test_script)
    
    run_command("/home/pi/security_system/venv/bin/python3 /home/pi/security_system/test_install.py", 
               "Kiểm tra cài đặt thư viện")
    
    print("\n" + "="*80)
    print("""
CÀI ĐẶT HOÀN TẤT!

Các thư mục của dự án:
- /home/pi/security_system/         (Thư mục chính)
- /home/pi/security_system/models/  (Lưu trữ mô hình)
- /home/pi/security_system/logs/    (File log)
- /home/pi/security_system/data/    (Dữ liệu bổ sung)

Để chạy hệ thống:
1. Tự động khi khởi động: Đã được thiết lập
2. Thủ công: sudo systemctl start home-security
3. Kiểm tra trạng thái: sudo systemctl status home-security
4. Xem log: sudo journalctl -u home-security -f

Copy chương trình chính vào /home/pi/security_system/home_security.py
""")
    print("="*80)

if __name__ == "__main__":
    main()