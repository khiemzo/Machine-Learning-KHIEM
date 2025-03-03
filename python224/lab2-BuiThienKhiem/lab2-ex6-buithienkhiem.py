"""buithienkhiem-11/2/2025"""
def gio_ngay():
    try:
        total_seconds = int(input("nhập tổng số giây: "))
    except ValueError:
        print("Vui lòng nhập một số nguyên!")
        return

    days = total_seconds // (24 * 3600)
    remaining = total_seconds % (24 * 3600)
    hours = remaining // 3600
    remaining %= 3600
    minutes = remaining // 60
    seconds = remaining % 60

    result_parts = []
    if days > 0:
        result_parts.append(f"{days} ngày")
    if hours > 0:
        result_parts.append(f"{hours} giờ")
    if minutes > 0:
        result_parts.append(f"{minutes} phút")
    if seconds > 0:
        result_parts.append(f"{seconds} giây")

    # Nếu tất cả đều bằng 0, hiển thị 0 giây
    if not result_parts:
        result_parts.append("0 giây")

    print(" ".join(result_parts))

# Chạy chương trình
gio_ngay()
