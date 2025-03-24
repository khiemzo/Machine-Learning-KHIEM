import sys
import datetime

# ------------------------------
# Dữ liệu mẫu: 40 mặt hàng công nghệ
# ------------------------------
sample_products = [
    {'id': 'T001', 'name': 'Laptop Dell Inspiron', 'unit': 'chiếc', 'price': 15000000},
    {'id': 'T002', 'name': 'Laptop HP Pavilion', 'unit': 'chiếc', 'price': 14000000},
    {'id': 'T003', 'name': 'Laptop Lenovo ThinkPad', 'unit': 'chiếc', 'price': 20000000},
    {'id': 'T004', 'name': 'Smartphone Samsung Galaxy', 'unit': 'chiếc', 'price': 8000000},
    {'id': 'T005', 'name': 'Smartphone iPhone', 'unit': 'chiếc', 'price': 25000000},
    {'id': 'T006', 'name': 'Tablet iPad', 'unit': 'chiếc', 'price': 18000000},
    {'id': 'T007', 'name': 'Smartwatch Apple Watch', 'unit': 'chiếc', 'price': 9000000},
    {'id': 'T008', 'name': 'Monitor Samsung 24"', 'unit': 'cái', 'price': 4000000},
    {'id': 'T009', 'name': 'Monitor LG 27"', 'unit': 'cái', 'price': 5000000},
    {'id': 'T010', 'name': 'Motherboard ASUS', 'unit': 'cái', 'price': 3000000},
    {'id': 'T011', 'name': 'Graphics Card NVIDIA RTX 3060', 'unit': 'chiếc', 'price': 15000000},
    {'id': 'T012', 'name': 'Graphics Card AMD RX 6700', 'unit': 'chiếc', 'price': 14000000},
    {'id': 'T013', 'name': 'CPU Intel i7', 'unit': 'cái', 'price': 12000000},
    {'id': 'T014', 'name': 'CPU AMD Ryzen 7', 'unit': 'cái', 'price': 11000000},
    {'id': 'T015', 'name': 'RAM Corsair 16GB', 'unit': 'cái', 'price': 3000000},
    {'id': 'T016', 'name': 'SSD Samsung 1TB', 'unit': 'cái', 'price': 4000000},
    {'id': 'T017', 'name': 'HDD Seagate 2TB', 'unit': 'cái', 'price': 3000000},
    {'id': 'T018', 'name': 'Power Supply 650W', 'unit': 'cái', 'price': 1500000},
    {'id': 'T019', 'name': 'Gaming Chair', 'unit': 'cái', 'price': 5000000},
    {'id': 'T020', 'name': 'Mechanical Keyboard', 'unit': 'cái', 'price': 2000000},
    {'id': 'T021', 'name': 'Gaming Mouse', 'unit': 'cái', 'price': 1000000},
    {'id': 'T022', 'name': 'Headset Logitech', 'unit': 'cái', 'price': 1500000},
    {'id': 'T023', 'name': 'Printer HP', 'unit': 'cái', 'price': 4000000},
    {'id': 'T024', 'name': 'Router TP-Link', 'unit': 'cái', 'price': 800000},
    {'id': 'T025', 'name': 'External HDD 2TB', 'unit': 'cái', 'price': 2500000},
    {'id': 'T026', 'name': 'USB Flash Drive 64GB', 'unit': 'cái', 'price': 500000},
    {'id': 'T027', 'name': 'Webcam Logitech', 'unit': 'cái', 'price': 1000000},
    {'id': 'T028', 'name': 'Microphone Blue Yeti', 'unit': 'cái', 'price': 3500000},
    {'id': 'T029', 'name': 'Drone DJI', 'unit': 'chiếc', 'price': 30000000},
    {'id': 'T030', 'name': 'VR Headset Oculus', 'unit': 'chiếc', 'price': 12000000},
    {'id': 'T031', 'name': 'Projector Epson', 'unit': 'cái', 'price': 18000000},
    {'id': 'T032', 'name': 'Smart TV LG 55"', 'unit': 'cái', 'price': 22000000},
    {'id': 'T033', 'name': 'Soundbar Bose', 'unit': 'cái', 'price': 8000000},
    {'id': 'T034', 'name': 'Wireless Charger', 'unit': 'cái', 'price': 700000},
    {'id': 'T035', 'name': 'Bluetooth Speaker', 'unit': 'cái', 'price': 2000000},
    {'id': 'T036', 'name': 'Digital Camera Canon', 'unit': 'cái', 'price': 15000000},
    {'id': 'T037', 'name': 'Action Camera GoPro', 'unit': 'cái', 'price': 12000000},
    {'id': 'T038', 'name': 'Smart Home Hub', 'unit': 'cái', 'price': 3000000},
    {'id': 'T039', 'name': 'Fitness Tracker Xiaomi', 'unit': 'cái', 'price': 800000},
    {'id': 'T040', 'name': 'E-Reader Kindle', 'unit': 'cái', 'price': 3500000},
]

# ------------------------------
# Dữ liệu mã giảm giá (ví dụ)
# ------------------------------
sample_discount_codes = [
    {'code': 'DISC10', 'type': 'percent', 'value': 10, 'min_order': 100000, 'description': 'Giảm 10% cho đơn hàng trên 100,000 VNĐ'},
    {'code': 'DISC5000', 'type': 'fixed', 'value': 5000, 'min_order': 50000, 'description': 'Giảm 5,000 VNĐ cho đơn hàng trên 50,000 VNĐ'},
]

# ------------------------------
# Dữ liệu nhân viên (giả lập)
# ------------------------------
employee_data = {
    'EMP001': {"name": "Nguyen Van A"},
    'EMP002': {"name": "Tran Thi B"},
}

# ------------------------------
# Một số hàm hỗ trợ chung
# ------------------------------
def generate_invoice_number():
    now = datetime.datetime.now()
    return f"HD{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

def search_product(query):
    query = query.lower()
    return [prod for prod in sample_products if query in prod['id'].lower() or query in prod['name'].lower()]

def add_product(invoice_items, product, qty, custom_price=None):
    """Thêm sản phẩm vào hóa đơn (nếu custom_price được cung cấp thì dùng nó thay cho giá mặc định)"""
    price = custom_price if custom_price is not None else product['price']
    for item in invoice_items:
        if item['id'] == product['id']:
            item['quantity'] += qty
            item['price'] = price  # cập nhật giá nếu có thay đổi
            item['total'] = price * item['quantity']
            return
    invoice_items.append({
        'id': product['id'],
        'name': product['name'],
        'unit': product['unit'],
        'price': price,
        'quantity': qty,
        'total': price * qty
    })

def calculate_totals(invoice):
    subtotal = sum(item['total'] for item in invoice['invoice_items'])
    total_discount = 0
    valid_discounts = []
    for disc in invoice['applied_discounts']:
        if subtotal >= disc['min_order']:
            if disc['type'] == 'percent':
                disc_amount = subtotal * disc['value'] / 100
            else:
                disc_amount = disc['value']
            total_discount += disc_amount
            valid_discounts.append(disc)
        else:
            print(f"--> Mã giảm giá '{disc['code']}' bị hủy vì đơn hàng chưa đạt {disc['min_order']:,} VNĐ")
    invoice['applied_discounts'] = valid_discounts
    total = subtotal - total_discount
    if total < 0:
        total = 0
    return subtotal, total_discount, total

def process_payment(total):
    while True:
        try:
            amount = float(input("Nhập số tiền khách trả (VNĐ): "))
            if amount < total:
                print("Số tiền khách trả không đủ. Vui lòng nhập lại.")
            else:
                return amount, amount - total
        except Exception:
            print("Giá trị không hợp lệ. Vui lòng nhập số tiền hợp lệ.")

# ------------------------------
# Các hàm hiển thị và xử lý hóa đơn
# ------------------------------
def print_current_invoice(invoice):
    print("\n--- HÓA ĐƠN TẠM TÍNH ---")
    print(f"Số hóa đơn: {invoice['invoice_number']}")
    print(f"Ngày: {invoice['date']}")
    if 'employee' in invoice:
        print(f"Nhân viên: {invoice['employee']['id']} - {invoice['employee']['name']}")
    if 'customer' in invoice:
        print(f"Khách hàng: {invoice['customer']['name']} - SĐT: {invoice['customer']['phone']}")
    print("-" * 60)
    if not invoice['invoice_items']:
        print("Chưa có sản phẩm nào.")
    else:
        header = "{:<5} {:<10} {:<25} {:<10} {:<12} {:<10}".format("STT", "Mã SP", "Tên sản phẩm", "Đơn vị", "Đơn giá", "SL")
        print(header)
        for idx, item in enumerate(invoice['invoice_items'], 1):
            print("{:<5} {:<10} {:<25} {:<10} {:<12,} {:<10}".format(
                idx, item['id'], item['name'], item['unit'], item['price'], item['quantity']))
    subtotal, discount_total, total = calculate_totals(invoice)
    print("-" * 60)
    print(f"Tạm tính: {subtotal:,} VNĐ")
    print(f"Giảm giá: {discount_total:,} VNĐ")
    print(f"Tổng thanh toán: {total:,} VNĐ")
    print("-" * 60)

def print_invoice(invoice):
    # Tính toán tổng tiền
    subtotal, discount_total, total = calculate_totals(invoice)
    # In header công ty
    print("\n" + "=" * 70)
    print(" " * 15 + "CÔNG TY CÔNG NGHỆ ĐÀ NẴNG")
    print(" " * 8 + "Địa chỉ: 123 Đường Lê Lợi, Quận Hải Châu, Đà Nẵng, Việt Nam")
    print(" " * 20 + "QR CODE: [### SIMULATED ###]")
    print("=" * 70)
    # Thông tin hóa đơn, khách hàng, nhân viên
    print(f"Số hóa đơn: {invoice['invoice_number']}")
    print(f"Ngày: {invoice['date']}")
    print(f"Nhân viên: {invoice['employee']['id']} - {invoice['employee']['name']}")
    print(f"Khách hàng: {invoice['customer']['name']} - SĐT: {invoice['customer']['phone']}")
    print("-" * 70)
    header = "{:<5} {:<10} {:<25} {:<10} {:<12} {:<10} {:<15}".format(
        "STT", "Mã SP", "Tên sản phẩm", "Đơn vị", "Đơn giá", "SL", "Thành tiền")
    print(header)
    for idx, item in enumerate(invoice['invoice_items'], 1):
        line = "{:<5} {:<10} {:<25} {:<10} {:<12,} {:<10} {:<15,}".format(
            idx, item['id'], item['name'], item['unit'], item['price'], item['quantity'], item['total'])
        print(line)
    print("-" * 70)
    print(f"Tạm tính: {subtotal:,} VNĐ")
    if invoice['applied_discounts']:
        for disc in invoice['applied_discounts']:
            if disc['type'] == 'percent':
                disc_text = f"{disc['code']} (-{disc['value']}%)"
            else:
                disc_text = f"{disc['code']} (-{disc['value']:,} VNĐ)"
            print(disc_text)
        print(f"Giảm giá: {discount_total:,} VNĐ")
    print(f"Tổng thanh toán: {total:,} VNĐ")
    # Thanh toán: nhập tiền khách trả và tính tiền trả
    print("-" * 70)
    payment, change = process_payment(total)
    print(f"Tiền khách trả: {payment:,} VNĐ")
    print(f"Tiền trả lại: {change:,} VNĐ")
    print("=" * 70)
    print("Cảm ơn quý khách đã mua hàng!\n")

def remove_product(invoice_items):
    if not invoice_items:
        print("Hóa đơn trống, không có sản phẩm để xóa.")
        return
    print("Danh sách sản phẩm trong hóa đơn:")
    for idx, item in enumerate(invoice_items, 1):
        print(f"{idx}. {item['id']} - {item['name']} - SL: {item['quantity']}")
    try:
        sel = int(input("Chọn số thứ tự sản phẩm cần xóa: "))
        if sel < 1 or sel > len(invoice_items):
            print("Lựa chọn không hợp lệ.")
        else:
            removed = invoice_items.pop(sel - 1)
            print(f"Đã xóa sản phẩm '{removed['name']}' khỏi hóa đơn.")
    except Exception as e:
        print("Lỗi khi xóa sản phẩm, vui lòng thử lại.")

def apply_discount(invoice, discount_codes):
    if not invoice['invoice_items']:
        print("Chưa có sản phẩm nào trong hóa đơn!")
        return
    discount_code = input("Nhập mã giảm giá: ").strip().upper()
    if not discount_code:
        print("Mã giảm giá không được để trống.")
        return
    if any(d['code'] == discount_code for d in invoice['applied_discounts']):
        print(f"Mã giảm giá '{discount_code}' đã được áp dụng!")
        return
    found_discount = None
    for disc in discount_codes:
        if disc['code'] == discount_code:
            found_discount = disc
            break
    if not found_discount:
        print(f"Mã giảm giá '{discount_code}' không hợp lệ!")
        return
    subtotal = sum(item['total'] for item in invoice['invoice_items'])
    if subtotal < found_discount['min_order']:
        print(f"Không thể áp dụng mã giảm giá. Đơn hàng tối thiểu: {found_discount['min_order']:,} VNĐ")
        return
    invoice['applied_discounts'].append(found_discount)
    print(f"Đã áp dụng mã giảm giá '{discount_code}' thành công: {found_discount['description']}")

def auto_generate_invoice(invoice):
    """
    Tạo hóa đơn tự động từ danh sách 40 sản phẩm.
    Người dùng chọn chế độ:
      1. Dựa trên số lượng sản phẩm (nhập số lượng cho từng sản phẩm)
      2. Dựa trên đơn giá tùy chỉnh (nhập giá tùy chỉnh và số lượng (mặc định 1 nếu bỏ qua))
    """
    print("\nChọn chế độ tạo hóa đơn tự động:")
    print("1. Dựa trên số lượng sản phẩm")
    print("2. Dựa trên đơn giá tùy chỉnh")
    mode = input("Chọn chế độ (1 hoặc 2): ").strip()
    if mode not in ['1', '2']:
        print("Chế độ không hợp lệ.")
        return

    for prod in sample_products:
        print(f"\n[Sản phẩm] {prod['id']} - {prod['name']} - Giá: {prod['price']:,} VNĐ/{prod['unit']}")
        if mode == '1':
            qty_in = input("Nhập số lượng (để trống nếu không thêm): ").strip()
            if qty_in:
                try:
                    qty = int(qty_in)
                    if qty > 0:
                        add_product(invoice['invoice_items'], prod, qty)
                except:
                    print("Giá trị không hợp lệ, bỏ qua sản phẩm này.")
        else:
            custom_price_in = input("Nhập đơn giá tùy chỉnh (để trống dùng giá mặc định): ").strip()
            try:
                custom_price = float(custom_price_in) if custom_price_in else prod['price']
            except:
                print("Giá không hợp lệ, dùng giá mặc định.")
                custom_price = prod['price']
            qty_in = input("Nhập số lượng (mặc định 1 nếu để trống): ").strip()
            try:
                qty = int(qty_in) if qty_in else 1
                if qty > 0:
                    add_product(invoice['invoice_items'], prod, qty, custom_price)
            except:
                print("Giá trị số lượng không hợp lệ, bỏ qua sản phẩm này.")
    print("\nĐã tạo hóa đơn tự động từ danh sách sản phẩm.")

# ------------------------------
# Hàm main, menu chính
# ------------------------------
def main():
    print("=== PHẦN MỀM QUẢN LÝ HÓA ĐƠN (Terminal Version - Advanced) ===\n")
    invoice = {}
    invoice['invoice_number'] = generate_invoice_number()
    invoice['date'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    invoice['invoice_items'] = []
    invoice['applied_discounts'] = []

    # Xác minh nhân viên (giả lập)
    while True:
        emp_id = input("Nhập mã nhân viên để xác minh (hoặc gõ 'exit' để thoát): ").strip().upper()
        if emp_id.lower() == 'exit':
            sys.exit(0)
        if emp_id in employee_data:
            invoice['employee'] = {'id': emp_id, 'name': employee_data[emp_id]['name']}
            print(f"Xác minh thành công: {employee_data[emp_id]['name']} ({emp_id})")
            break
        else:
            print("Mã nhân viên không hợp lệ, vui lòng thử lại.")

    # Nhập thông tin khách hàng
    invoice['customer'] = {}
    invoice['customer']['name'] = input("Nhập tên khách hàng: ").strip() or "Khách lẻ"
    invoice['customer']['phone'] = input("Nhập số điện thoại khách hàng: ").strip() or "Không có"

    # Menu chính
    while True:
        print("\n--- Menu ---")
        print("1. Thêm sản phẩm (tìm kiếm theo mã/tên)")
        print("2. Xóa sản phẩm")
        print("3. Áp dụng mã giảm giá")
        print("4. Xem hóa đơn hiện tại")
        print("5. Reset hóa đơn")
        print("6. Tạo hóa đơn (In hóa đơn và thanh toán)")
        print("7. Tạo hóa đơn tự động từ 40 mặt hàng")
        print("8. Thoát")
        choice = input("Chọn chức năng: ").strip()

        if choice == '1':
            query = input("Nhập mã hoặc tên sản phẩm cần tìm: ").strip()
            matches = search_product(query)
            if not matches:
                print("Không tìm thấy sản phẩm nào!")
            else:
                print("Danh sách sản phẩm tìm thấy:")
                for idx, prod in enumerate(matches, 1):
                    print(f"{idx}. {prod['id']} - {prod['name']} - {prod['price']:,} VNĐ/{prod['unit']}")
                try:
                    sel = int(input("Chọn số thứ tự sản phẩm: "))
                    if sel < 1 or sel > len(matches):
                        print("Lựa chọn không hợp lệ.")
                    else:
                        selected = matches[sel - 1]
                        qty = int(input("Nhập số lượng: "))
                        if qty <= 0:
                            print("Số lượng phải lớn hơn 0.")
                        else:
                            add_product(invoice['invoice_items'], selected, qty)
                            print("Đã thêm sản phẩm vào hóa đơn.")
                except Exception as e:
                    print("Lỗi khi chọn sản phẩm, vui lòng thử lại.")
        elif choice == '2':
            remove_product(invoice['invoice_items'])
        elif choice == '3':
            apply_discount(invoice, sample_discount_codes)
        elif choice == '4':
            print_current_invoice(invoice)
        elif choice == '5':
            invoice['invoice_items'].clear()
            invoice['applied_discounts'].clear()
            invoice['invoice_number'] = generate_invoice_number()
            invoice['date'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print("Hóa đơn đã được reset.")
        elif choice == '6':
            if not invoice['invoice_items']:
                print("Hóa đơn trống, không thể tạo hóa đơn!")
            else:
                print_invoice(invoice)
        elif choice == '7':
            # Tạo hóa đơn tự động từ danh sách 40 mặt hàng
            auto_generate_invoice(invoice)
        elif choice == '8':
            print("Thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng thử lại.")

if __name__ == '__main__':
    main()
