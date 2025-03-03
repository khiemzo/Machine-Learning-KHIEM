import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import speech_recognition as sr

def main():
    print("Kiểm tra Speech Recognition")
    r = sr.Recognizer()
    
    # Liệt kê microphone
    microphones = sr.Microphone.list_microphone_names()
    print(f"Danh sách microphone ({len(microphones)}):")
    for i, microphone in enumerate(microphones):
        print(f"  {i}: {microphone}")
    
    print("\nKiểm tra thiết bị thu âm mặc định:")
    try:
        with sr.Microphone() as source:
            print("Đã khởi tạo Microphone thành công")
            print("Điều chỉnh cho tiếng ồn môi trường...")
            r.adjust_for_ambient_noise(source, duration=1)
            print(f"Ngưỡng năng lượng: {r.energy_threshold}")
            
            print("\nVui lòng nói một câu (5 giây)...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Ghi âm xong, đang chuyển đổi thành văn bản...")
            
            try:
                text = r.recognize_google(audio, language="vi-VN")
                print(f"Nhận dạng Google: {text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition không nhận dạng được giọng nói")
            except sr.RequestError as e:
                print(f"Không thể yêu cầu kết quả từ Google Speech Recognition; {e}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
