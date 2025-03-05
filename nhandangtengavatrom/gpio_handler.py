"""
Module xử lý GPIO để gửi tín hiệu ra chân của Raspberry Pi khi phát hiện té ngã hoặc ăn trộm
"""

import time
import threading
import logging
import RPi.GPIO as GPIO
from config import (
    GPIO_FALL_DETECTION_PIN,
    GPIO_INTRUDER_DETECTION_PIN,
    GPIO_OUTPUT_DURATION
)

logger = logging.getLogger(__name__)

class GPIOHandler:
    """Lớp xử lý các tín hiệu GPIO khi phát hiện té ngã hoặc ăn trộm"""
    
    def __init__(self):
        """Khởi tạo cấu hình GPIO"""
        # Sử dụng chế độ đánh số BCM
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Cấu hình các chân GPIO là output
        GPIO.setup(GPIO_FALL_DETECTION_PIN, GPIO.OUT)
        GPIO.setup(GPIO_INTRUDER_DETECTION_PIN, GPIO.OUT)
        
        # Khởi tạo các chân ở mức thấp (0V)
        GPIO.output(GPIO_FALL_DETECTION_PIN, GPIO.LOW)
        GPIO.output(GPIO_INTRUDER_DETECTION_PIN, GPIO.LOW)
        
        logger.info("GPIO đã được khởi tạo thành công")
    
    def trigger_fall_alarm(self):
        """Kích hoạt cảnh báo khi phát hiện té ngã"""
        self._trigger_pin_with_duration(GPIO_FALL_DETECTION_PIN, "té ngã")
    
    def trigger_intruder_alarm(self):
        """Kích hoạt cảnh báo khi phát hiện ăn trộm"""
        self._trigger_pin_with_duration(GPIO_INTRUDER_DETECTION_PIN, "ăn trộm")
    
    def _trigger_pin_with_duration(self, pin, detection_type):
        """
        Kích hoạt chân GPIO trong một khoảng thời gian xác định
        
        Args:
            pin: Số chân GPIO cần kích hoạt
            detection_type: Loại phát hiện (té ngã hoặc ăn trộm)
        """
        # Sử dụng thread để không chặn luồng chính
        def _set_pin():
            try:
                logger.info(f"Kích hoạt cảnh báo {detection_type} tại chân GPIO {pin}")
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(GPIO_OUTPUT_DURATION)
                GPIO.output(pin, GPIO.LOW)
                logger.info(f"Kết thúc cảnh báo {detection_type} tại chân GPIO {pin}")
            except Exception as e:
                logger.error(f"Lỗi khi kích hoạt chân GPIO {pin}: {e}")
        
        # Tạo và khởi động thread
        gpio_thread = threading.Thread(target=_set_pin)
        gpio_thread.daemon = True
        gpio_thread.start()
    
    def cleanup(self):
        """Giải phóng tài nguyên GPIO khi kết thúc chương trình"""
        GPIO.cleanup()
        logger.info("Đã giải phóng tài nguyên GPIO")


# Singleton instance
_gpio_handler = None

def get_gpio_handler():
    """Trả về đối tượng singleton GPIOHandler"""
    global _gpio_handler
    if _gpio_handler is None:
        _gpio_handler = GPIOHandler()
    return _gpio_handler 