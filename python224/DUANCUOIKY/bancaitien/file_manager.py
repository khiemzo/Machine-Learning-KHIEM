import csv
import pandas as pd
from tkinter import filedialog, messagebox

def save_to_file(forecasts, format_choice):
    """Lưu kết quả vào file theo định dạng .csv hoặc .xlsx."""
    filepath = filedialog.asksaveasfilename(
        defaultextension=f".{format_choice}",
        filetypes=[(f"{format_choice.upper()} Files", f"*.{format_choice}")],
        title="Chọn đường dẫn và tên file để lưu"
    )
    if not filepath:
        return

    try:
        if format_choice == "csv":
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["City", "Data Type", "Forecast"])
                for (city, dtype), (forecast, mae, conf_int) in forecasts.items():
                    forecast_str = ", ".join([f"{f:.1f}" for f in forecast])
                    writer.writerow([city.title(), dtype.upper(), forecast_str])
        elif format_choice == "xlsx":
            df = pd.DataFrame({
                "City": [city.title() for (city, _) in forecasts.keys()],
                "Data Type": [dtype.upper() for (_, dtype) in forecasts.keys()],
                "Forecast": [", ".join([f"{f:.1f}" for f in forecasts[(city, dtype)][0]]) for (city, dtype) in forecasts.keys()]
            })
            df.to_excel(filepath, index=False)
        messagebox.showinfo("Thành công", f"Dữ liệu đã được lưu vào {filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}\nVui lòng kiểm tra quyền truy cập hoặc định dạng file.")
