"""buithienkhiem-11/2/2025"""
def phan_tich_so():
    ds_so = []
    while True:
        try:
            so = int(input("nhập số nguyên hoặc 0 để thoát: "))
        except ValueError:
            continue  # Nếu nhập không hợp lệ, bỏ qua
        if so == 0:
            break
        ds_so.append(so)

    if not ds_so:
        print("Không có số nào được nhập.")
        return

    so_luong = len(ds_so)
    so_nho = min(ds_so)
    so_lon = max(ds_so)
    tong = sum(ds_so)
    trung_binh = tong / so_luong

    # Sắp xếp danh sách các số và tính trung vị
    ds_da_sap_xep = sorted(ds_so)
    if so_luong % 2 == 1:
        trung_vi = ds_da_sap_xep[so_luong // 2]
    else:
        trung_vi = (ds_da_sap_xep[so_luong // 2 - 1] + ds_da_sap_xep[so_luong // 2]) / 2

    print(f"bạn đã nhập {so_luong} giá trị,")
    print(f"giá trị min và max bạn nhập là {so_nho} và {so_lon},")
    print(f"tổng là {tong},")
    print(f"giá trị trung bình là {trung_binh:.2f}")
    print(f"danh sách các số đã nhập (theo thứ tự tăng dần): {ds_da_sap_xep}")
    print(f"trung vị của các số là {trung_vi}")


# Chạy chương trình
phan_tich_so()
