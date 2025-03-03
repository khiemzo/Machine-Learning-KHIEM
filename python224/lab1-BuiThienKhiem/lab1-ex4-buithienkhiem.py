"""buithienkhiem-11/2/2025"""
def tinh_tien_thoi():
    # Mệnh giá tiền
    menh_gia = [500000, 200000, 100000, 50000, 20000, 10000, 5000, 2000, 1000, 500]

    # Nhập số tiền khách hàng phải trả và số tiền nhận được từ khách hàng
    tien_phai_tra = float(input("tiền khách hàng phải trả cho cửa hàng: "))
    tien_nhan = float(input("số tiền nhận từ khách hàng đã đưa: "))

    # Tính tiền thối lại
    tien_thoi = tien_nhan - tien_phai_tra
    print("Tiền thối lại cho khách hàng: ", tien_thoi)

    # Tính số tờ tiền thối lại cho từng mệnh giá
    print("Bao gồm:")
    for i in range(len(menh_gia)):
        so_to = int(tien_thoi / menh_gia[i])
        tien_thoi -= so_to * menh_gia[i]
        print(f"{menh_gia[i]}: {so_to}")

# Gọi hàm
tinh_tien_thoi()
