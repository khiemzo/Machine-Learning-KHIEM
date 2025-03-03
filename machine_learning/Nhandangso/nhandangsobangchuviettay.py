import os
import tkinter as tk
from tkinter import *
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import tensorflow as tf
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Flatten
from tensorflow.keras.utils import to_categorical

# Đường dẫn lưu file mô hình đã huấn luyện
MODEL_FILENAME = "mnist_cnn.keras"


def create_model():
    """
    Tạo một mô hình CNN đơn giản cho nhận dạng chữ số trên ảnh 28x28 (dữ liệu MNIST).
    """
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(28, 28, 1)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(10, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def train_model():
    """
    Huấn luyện mô hình trên tập dữ liệu MNIST và lưu lại mô hình đã huấn luyện.
    """
    from tensorflow.keras.datasets import mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # Chuẩn hóa và chuyển đổi kích thước
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1).astype('float32') / 255
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1).astype('float32') / 255
    y_train = to_categorical(y_train, 10)
    y_test = to_categorical(y_test, 10)
    model = create_model()
    # Huấn luyện mô hình (sử dụng số epoch nhỏ để tiết kiệm thời gian)
    model.fit(x_train, y_train, batch_size=128, epochs=3, verbose=1, validation_data=(x_test, y_test))
    model.save(MODEL_FILENAME)
    return model


# Nếu đã có mô hình được huấn luyện, load mô hình; ngược lại, tiến hành huấn luyện.
if os.path.exists(MODEL_FILENAME):
    model = load_model(MODEL_FILENAME)
else:
    model = train_model()


# Tạo giao diện người dùng với Tkinter
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nhận dạng chữ số viết tay")
        self.resizable(0, 0)

        # Kích thước bảng vẽ
        self.canvas_width = 200
        self.canvas_height = 200

        # Bảng vẽ (panel bên trái)
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='white', cursor="cross")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        self.canvas.bind("<B1-Motion>", self.draw_lines)

        # Panel bên phải để hiển thị kết quả nhận dạng
        self.result_frame = tk.Frame(self)
        self.result_frame.grid(row=0, column=1, padx=10, pady=10)
        self.result_label = tk.Label(self.result_frame, text="Số được nhận dạng:", font=("Helvetica", 18))
        self.result_label.pack(pady=10)

        self.prediction_text = tk.StringVar()
        self.prediction_text.set("")
        self.prediction_display = tk.Label(self.result_frame, textvariable=self.prediction_text, font=("Helvetica", 48))
        self.prediction_display.pack(pady=10)

        # Các nút chức năng: "Predict" và "Clear"
        self.btn_predict = tk.Button(self, text="Nhận dạng", command=self.predict_digit)
        self.btn_predict.grid(row=1, column=0, pady=10)

        self.btn_clear = tk.Button(self, text="Xóa", command=self.clear_canvas)
        self.btn_clear.grid(row=1, column=1, pady=10)

        # Khởi tạo một hình ảnh để lưu nội dung bảng vẽ (giúp xử lý khi nhận dạng)
        self.image1 = Image.new("L", (self.canvas_width, self.canvas_height), 'white')
        self.draw = ImageDraw.Draw(self.image1)

    def draw_lines(self, event):
        """
        Vẽ các nét trên bảng khi kéo chuột.
        """
        x, y = event.x, event.y
        r = 8  # Bán kính brush
        # Vẽ trên canvas
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill='black')
        # Vẽ vào đối tượng ảnh để xử lý
        self.draw.ellipse([x - r, y - r, x + r, y + r], fill='black')

    def clear_canvas(self):
        """
        Xóa bảng vẽ và reset kết quả nhận dạng.
        """
        self.canvas.delete("all")
        self.draw.rectangle([0, 0, self.canvas_width, self.canvas_height], fill="white")
        self.prediction_text.set("")

    def predict_digit(self):
        """
        Xử lý hình ảnh từ bảng vẽ, chuyển đổi kích thước và chuẩn hóa, sau đó dùng mô hình để dự đoán chữ số.
        """
        # Resize ảnh về kích thước 28x28 (như dữ liệu MNIST)
        img = self.image1.resize((28, 28))
        # Đảo ngược màu sắc: cần có nền đen và chữ trắng
        img = ImageOps.invert(img)
        # Chuyển đổi ảnh về mảng numpy và chuẩn hóa
        img_array = np.array(img).astype('float32') / 255
        img_array = img_array.reshape(1, 28, 28, 1)
        # Dự đoán bằng mô hình
        prediction = model.predict(img_array)
        digit = np.argmax(prediction)
        self.prediction_text.set(str(digit))


if __name__ == "__main__":
    app = App()
    app.mainloop()