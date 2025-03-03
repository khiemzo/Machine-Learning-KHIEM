"""buithienkhiem-11/2/2025"""
import random

def generate_random_number():
    """Hàm sinh số ngẫu nhiên trong khoảng [100, 999]."""
    return random.randint(100, 999)

def display_addition_problem(num1, num2):
    """Hiển thị phép cộng theo định dạng xếp chồng."""
    width = max(len(str(num1)), len(str(num2))) + 2
    print(str(num1).rjust(width))
    print("+" + str(num2).rjust(width - 1))
    print("-" * width, "(nhập kết quả)")

def get_user_answer():
    """Lấy kết quả nhập từ người dùng."""
    try:
        return int(input())
    except ValueError:
        print("Vui lòng nhập một số nguyên!")
        return None

def check_answer(user_answer, correct_answer):
    """Kiểm tra kết quả và in ra thông báo tương ứng."""
    if user_answer == correct_answer:
        print("Câu trả lời đúng!")
    else:
        print(f"Đáp án sai, đáp án đúng là {correct_answer}")

def addition_game():
    """Chương trình chính để chơi trò chơi phép cộng."""
    num1 = generate_random_number()
    num2 = generate_random_number()
    correct_sum = num1 + num2

    display_addition_problem(num1, num2)
    user_answer = get_user_answer()

    if user_answer is not None:
        check_answer(user_answer, correct_sum)

# Chạy chương trình
addition_game()