"""buithienkhiem-11/2/2025"""
# Nhập thành tiền từ bàn phím
thanh_tien = float(input("Thành tiền: "))

# Tính thuế VAT
thue_vat = (thanh_tien) * 0.1

# Tính tổng số tiền cần thanh toán
tong_tien = thanh_tien + thue_vat

# In ra kết quả
print(f"Thuế VAT (10%): {thue_vat: .3f}")
print(f"Thanh toán:     {tong_tien: .3f}")
