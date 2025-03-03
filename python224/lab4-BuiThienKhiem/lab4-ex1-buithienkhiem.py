"""buithienkhiem-25/2/2025"""
"""danh sách split"""
def extract_path_list(filepath):
    parts = filepath.split("\\")  # Tách đường dẫn theo dấu '\'
    filename = parts[-1]  # Lấy phần tử cuối cùng là tên file
    folder = "\\".join(parts[:-1])  # Nối lại phần còn lại làm đường dẫn thư mục
    return filename, folder

filepath = input("file path: ")
filename, folder = extract_path_list(filepath)
print(filename)
print(folder)

""" chuỗi rfind"""
"""def extract_path_string(filepath):
    index = filepath.rfind("\\")  # Tìm vị trí dấu '\' cuối cùng
    filename = filepath[index + 1:]  # Cắt phần sau cùng là tên file
    folder = filepath[:index]  # Lấy phần còn lại là đường dẫn thư mục
    return filename, folder

filepath = input("file path: ")
filename, folder = extract_path_string(filepath)
print(filename)
print(folder)
"""