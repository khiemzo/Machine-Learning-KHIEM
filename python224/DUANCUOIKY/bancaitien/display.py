import tkinter as tk
from tkinter import ttk, messagebox
from forecast import forecast_advanced

def display_climate_data_with_forecast(data, cities, data_types, months, result_table, forecast_horizon=1,
                                       forecast_method='linear', poly_degree=2):
    """
    Hiển thị dữ liệu khí hậu và dự báo giá trị tháng tiếp theo trên Treeview.
    Nếu dữ liệu đã có các khóa dự báo (ví dụ: temp_forecast) thì sử dụng luôn thay vì tính lại.
    """
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    # Xóa dữ liệu cũ trong bảng
    for row in result_table.get_children():
        result_table.delete(row)

    columns = ["City", "Data Type"] + [month_names[i][:3] for i in months] + ["Min", "Max", "Avg", "Forecast", "MAE", "CI"]
    result_table["columns"] = columns
    result_table.heading("#0", text="", anchor=tk.W)
    for col in columns:
        result_table.heading(col, text=col, anchor=tk.CENTER)
        result_table.column(col, anchor=tk.CENTER, width=80)

    for city in cities:
        for dtype in data_types:
            values = data.get(city, {}).get(dtype, [])
            if not values:
                continue
            selected_values = [values[i] for i in months]
            try:
                min_val = min(selected_values)
                max_val = max(selected_values)
                avg_val = sum(selected_values) / len(selected_values)
            except Exception as e:
                messagebox.showerror("Lỗi dữ liệu", f"Không thể tính toán giá trị cho {city} - {dtype.upper()}: {e}")
                continue

            min_month = month_names[months[selected_values.index(min_val)]]
            max_month = month_names[months[selected_values.index(max_val)]]

            # Kiểm tra nếu dự báo đã được tính trước trong dữ liệu
            forecast_key = f"{dtype}_forecast"
            mae_key = f"{dtype}_mae"
            ci_key = f"{dtype}_ci"
            city_data = data.get(city, {})
            if forecast_key in city_data:
                forecast_val = city_data.get(forecast_key)
                mae_val = city_data.get(mae_key)
                ci_val = city_data.get(ci_key)
            else:
                try:
                    forecast, mae, conf_int = forecast_advanced(values, forecast_horizon, forecast_method, poly_degree)
                    forecast_val = forecast[0] if forecast is not None and len(forecast) > 0 else None
                    mae_val = mae
                    ci_val = conf_int
                except Exception as e:
                    messagebox.showerror("Lỗi dự báo", str(e))
                    continue

            forecast_str = f"{forecast_val:.1f}" if forecast_val is not None else "N/A"
            mae_str = f"{mae_val:.1f}" if mae_val is not None else "N/A"
            ci_str = ""
            if ci_val:
                ci_str = ", ".join([f"[{lo:.1f}, {up:.1f}]" for lo, up in ci_val])
            row_data = [city.title(), dtype.upper()] + \
                       [f"{v:.1f}" for v in selected_values] + \
                       [f"{min_val:.1f} ({min_month})", f"{max_val:.1f} ({max_month})", f"{avg_val:.1f}",
                        forecast_str, mae_str, ci_str]
            result_table.insert("", tk.END, values=row_data)
