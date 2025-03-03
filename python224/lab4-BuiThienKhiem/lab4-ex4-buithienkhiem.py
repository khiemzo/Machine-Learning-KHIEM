"""buithienkhiem-25/2/2025"""
def student_rating():
    scores = list(map(float, input("enter your quarter scores: ").split()))
    avg = sum(scores) / len(scores)

    if avg < 7:
        rating = "very poor"
    elif avg < 10:
        rating = "poor"
    elif avg < 13:
        rating = "fair"
    elif avg < 16:
        rating = "good"
    elif avg < 19:
        rating = "very good"
    else:
        rating = "outstanding"

    print(f"your final score is {avg:.2f}")
    print(f"rating: {rating}")


student_rating()
