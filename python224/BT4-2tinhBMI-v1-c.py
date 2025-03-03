import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json


class HealthAdvisor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tư Vấn Sức Khỏe Thông Minh")
        self.window.geometry("1000x800")
        self.window.configure(bg='#f0f0f0')

        # Khởi tạo dữ liệu
        self.init_data()

        # Tạo giao diện
        self.create_gui()

        # Cập nhật thời gian
        self.update_clock()

        self.window.mainloop()

    def init_data(self):
        """Khởi tạo dữ liệu cho ứng dụng"""
        self.activities = {
            "nam": {
                "teen": {
                    "cardio": ["Bóng đá", "Bơi lội", "Chạy bộ"],
                    "strength": ["Tập tạ nhẹ", "Kéo xà", "Gập bụng"],
                    "nutrition": ["Sữa tăng chiều cao", "Thịt nạc", "Trứng", "Cá"]
                },
                "adult": {
                    "cardio": ["Chạy bộ", "Đạp xe", "Boxing"],
                    "strength": ["Tập tạ", "Plank", "Hít đất"],
                    "nutrition": ["Protein whey", "Thịt đỏ", "Cá hồi", "Ngũ cốc"]
                },
                "elder": {
                    "cardio": ["Đi bộ", "Bơi chậm", "Đạp xe tại chỗ"],
                    "strength": ["Yoga", "Thái cực quyền", "Kéo dãn"],
                    "nutrition": ["Canxi", "Omega-3", "Rau xanh", "Trái cây"]
                }
            },
            "nu": {
                "teen": {
                    "cardio": ["Nhảy dây", "Aerobic", "Bơi lội"],
                    "strength": ["Yoga", "Pilates nhẹ", "Squat"],
                    "nutrition": ["Sắt", "Canxi", "Sữa", "Trái cây"]
                },
                "adult": {
                    "cardio": ["Zumba", "Đạp xe", "Aerobic"],
                    "strength": ["Pilates", "Yoga", "Resistance bands"],
                    "nutrition": ["Protein nạc", "Omega-3", "Rau củ", "Đậu"]
                },
                "elder": {
                    "cardio": ["Đi bộ", "Dưỡng sinh", "Yoga nhẹ"],
                    "strength": ["Thái cực quyền", "Kéo dãn", "Tập với bóng"],
                    "nutrition": ["Canxi", "Vitamin D", "Protein dễ tiêu", "Trà xanh"]
                }
            }
        }

    def create_gui(self):
        """Tạo giao diện người dùng"""
        # Frame thời gian
        self.clock_frame = ttk.Frame(self.window)
        self.clock_frame.pack(fill='x', pady=5)
        self.clock_label = ttk.Label(self.clock_frame, font=('Arial', 14))
        self.clock_label.pack()

        # Frame nhập liệu
        input_frame = ttk.LabelFrame(self.window, text="Thông tin cá nhân", padding=10)
        input_frame.pack(padx=20, pady=10, fill='x')

        # Giới tính
        ttk.Label(input_frame, text="Giới tính:").grid(row=0, column=0, pady=5)
        self.gender_var = tk.StringVar(value="nam")
        ttk.Radiobutton(input_frame, text="Nam", variable=self.gender_var,
                        value="nam").grid(row=0, column=1)
        ttk.Radiobutton(input_frame, text="Nữ", variable=self.gender_var,
                        value="nu").grid(row=0, column=2)

        # Tuổi
        ttk.Label(input_frame, text="Tuổi:").grid(row=1, column=0, pady=5)
        self.age_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.age_var).grid(row=1, column=1, columnspan=2)

        # Chiều cao, cân nặng
        ttk.Label(input_frame, text="Chiều cao (cm):").grid(row=2, column=0, pady=5)
        self.height_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.height_var).grid(row=2, column=1, columnspan=2)

        ttk.Label(input_frame, text="Cân nặng (kg):").grid(row=3, column=0, pady=5)
        self.weight_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.weight_var).grid(row=3, column=1, columnspan=2)

        # Mức độ vận động
        ttk.Label(input_frame, text="Mức độ vận động:").grid(row=4, column=0, pady=5)
        self.activity_var = tk.StringVar(value="medium")
        ttk.Radiobutton(input_frame, text="Ít", variable=self.activity_var,
                        value="low").grid(row=4, column=1)
        ttk.Radiobutton(input_frame, text="Vừa", variable=self.activity_var,
                        value="medium").grid(row=4, column=2)
        ttk.Radiobutton(input_frame, text="Nhiều", variable=self.activity_var,
                        value="high").grid(row=4, column=3)

        # Nút phân tích
        ttk.Button(input_frame, text="Phân tích & Tư vấn",
                   command=self.analyze).grid(row=5, column=0, columnspan=4, pady=10)

        # Frame kết quả
        self.result_frame = ttk.LabelFrame(self.window, text="Kết quả phân tích", padding=10)
        self.result_frame.pack(padx=20, pady=10, fill='both', expand=True)

    def update_clock(self):
        """Cập nhật đồng hồ"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.clock_label.config(text=current_time)
        self.window.after(1000, self.update_clock)

    def calculate_bmi(self, weight, height):
        """Tính BMI"""
        try:
            height_m = height / 100
            bmi = weight / (height_m * height_m)
            return round(bmi, 1)
        except ZeroDivisionError:
            raise ValueError("Chiều cao không thể bằng 0")

    def get_age_group(self, age):
        """Xác định nhóm tuổi"""
        if age < 18:
            return "teen"
        elif age < 50:
            return "adult"
        else:
            return "elder"

    def get_bmi_category(self, bmi):
        """Phân loại BMI"""
        if bmi < 18.5:
            return "Thiếu cân"
        elif 18.5 <= bmi < 23:
            return "Bình thường"
        elif 23 <= bmi < 25:
            return "Thừa cân"
        elif 25 <= bmi < 30:
            return "Béo phì độ I"
        else:
            return "Béo phì độ II"

    def generate_advice(self, gender, age_group, bmi_category, activity_level):
        """Tạo lời khuyên dựa trên thông tin người dùng"""
        activities = self.activities[gender][age_group]
        advice = f"Lời khuyên cho sức khỏe của bạn:\n\n"

        # Lời khuyên về tập luyện
        advice += "1. Bài tập cardio phù hợp:\n"
        for exercise in activities["cardio"]:
            advice += f"   - {exercise}\n"

        advice += "\n2. Bài tập sức mạnh đề xuất:\n"
        for exercise in activities["strength"]:
            advice += f"   - {exercise}\n"

        advice += "\n3. Dinh dưỡng cần thiết:\n"
        for food in activities["nutrition"]:
            advice += f"   - {food}\n"

        # Lời khuyên theo BMI
        advice += f"\n4. Khuyến nghị dựa trên BMI ({bmi_category}):\n"
        if bmi_category == "Thiếu cân":
            advice += "   - Tăng khẩu phần ăn\n   - Tập các bài tăng cơ\n   - Ăn nhiều protein\n"
        elif bmi_category == "Bình thường":
            advice += "   - Duy trì chế độ ăn hiện tại\n   - Tập đều đặn\n   - Cân bằng dinh dưỡng\n"
        else:
            advice += "   - Giảm khẩu phần\n   - Tăng cường cardio\n   - Hạn chế tinh bột\n"

        # Lời khuyên theo mức độ vận động
        advice += f"\n5. Điều chỉnh theo mức vận động ({activity_level}):\n"
        if activity_level == "low":
            advice += "   - Tăng dần thời gian vận động\n   - Bắt đầu với bài tập nhẹ\n"
        elif activity_level == "medium":
            advice += "   - Duy trì đều đặn\n   - Đa dạng bài tập\n"
        else:
            advice += "   - Chú ý nghỉ ngơi\n   - Tăng cường dinh dưỡng\n"

        return advice

    def analyze(self):
        """Xử lý phân tích khi nhấn nút"""
        try:
            # Lấy và kiểm tra dữ liệu
            height = float(self.height_var.get())
            weight = float(self.weight_var.get())
            age = int(self.age_var.get())
            gender = self.gender_var.get()
            activity = self.activity_var.get()

            if height <= 0 or weight <= 0 or age <= 0:
                raise ValueError("Các giá trị phải lớn hơn 0")

            # Tính toán
            bmi = self.calculate_bmi(weight, height)
            bmi_category = self.get_bmi_category(bmi)
            age_group = self.get_age_group(age)

            # Xóa kết quả cũ
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            # Hiển thị kết quả mới
            ttk.Label(self.result_frame,
                      text=f"BMI: {bmi} - Phân loại: {bmi_category}",
                      font=('Arial', 12, 'bold')).pack(pady=5)

            advice = self.generate_advice(gender, age_group, bmi_category, activity)
            text_widget = tk.Text(self.result_frame, wrap=tk.WORD, height=20)
            text_widget.pack(fill='both', expand=True, pady=5)
            text_widget.insert('1.0', advice)
            text_widget.config(state='disabled')

        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", "Đã xảy ra lỗi không mong muốn!")


if __name__ == "__main__":
    app = HealthAdvisor()