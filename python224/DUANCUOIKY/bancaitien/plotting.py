import plotly.graph_objects as go
import plotly.offline as pyo
import tkinter as tk
from tkinter import messagebox
import os
import tempfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


def plot_trends(data, cities, data_types, months):
    """
    Vẽ biểu đồ xu hướng của từng thành phố và hiển thị trực tiếp
    trong một cửa sổ Tkinter.
    """
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Tạo figure và thêm các trace cho từng thành phố và loại dữ liệu
    fig = go.Figure()
    for city in cities:
        for dtype in data_types:
            values = data.get(city, {}).get(dtype, [])
            if not values:
                continue
            selected_values = [values[i] for i in months]
            x_vals = [month_names[i] for i in months]
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=selected_values,
                mode='lines+markers',
                name=f"{city.title()} - {dtype.upper()}",
                hovertemplate="Month: %{x}<br>Value: %{y:.1f}<extra></extra>"
            ))

    fig.update_layout(
        title="Xu hướng dữ liệu khí hậu",
        xaxis_title="Month",
        yaxis_title="Value",
        template="plotly_dark"
    )

    try:
        # Tạo cửa sổ Tkinter mới để hiển thị biểu đồ
        chart_window = tk.Toplevel()
        chart_window.title("Biểu đồ xu hướng dữ liệu khí hậu")
        chart_window.geometry("1000x700")
        
        # Tạo file HTML tạm thời
        temp_dir = tempfile.gettempdir()
        html_file = os.path.join(temp_dir, "temp_plot.html")
        
        # Lưu biểu đồ dưới dạng HTML
        html_content = pyo.plot(fig, include_plotlyjs='cdn', output_type='div')
        
        # Tạo frame để chứa biểu đồ
        frame = tk.Frame(chart_window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo một Text widget với hỗ trợ HTML
        from tkinter import scrolledtext
        import tkinter.font as tkfont
        
        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, "Đang tải biểu đồ...")
        
        # Tạo một button để mở biểu đồ trong trình duyệt nếu cần
        def open_in_browser():
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write('<html><head><title>Biểu đồ xu hướng</title></head><body>')
                f.write(html_content)
                f.write('</body></html>')
            import webbrowser
            webbrowser.open('file://' + os.path.realpath(html_file))
            
        browser_btn = tk.Button(chart_window, text="Mở trong trình duyệt", command=open_in_browser)
        browser_btn.pack(pady=10)

        # Phương pháp thay thế: Sử dụng matplotlib để hiển thị biểu đồ
        # Tạo figure sử dụng matplotlib
        plt_fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = plt_fig.add_subplot(111)
        
        # Vẽ dữ liệu
        for city in cities:
            for dtype in data_types:
                values = data.get(city, {}).get(dtype, [])
                if not values:
                    continue
                selected_values = [values[i] for i in months]
                x_vals = [month_names[i][:3] for i in months]  # Sử dụng 3 chữ cái đầu tiên của tháng
                ax.plot(x_vals, selected_values, marker='o', label=f"{city.title()} - {dtype.upper()}")
        
        # Thêm tiêu đề và nhãn
        ax.set_title("Xu hướng dữ liệu khí hậu")
        ax.set_xlabel("Tháng")
        ax.set_ylabel("Giá trị")
        ax.legend()
        ax.grid(True)
        
        # Tạo canvas Tkinter từ matplotlib figure
        canvas = FigureCanvasTkAgg(plt_fig, master=frame)
        canvas.draw()
        
        # Xóa text widget và thay thế bằng biểu đồ
        text_widget.pack_forget()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Tạo toolbar cho biểu đồ
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể hiển thị biểu đồ: {e}")
