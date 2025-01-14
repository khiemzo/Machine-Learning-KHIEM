import cv2
import face_recognition
#face_detection_cli:tập trung vào việc phát hiện khuôn mặt, thích hợp cho các tác vụ cơ bản như phân loại hoặc phân vùng khuôn mặt.
#face_recognition: hướng tới nhận diện khuôn mặt cụ thể và so sánh danh tính, phù hợp cho các ứng dụng yêu cầu nhận diện người dùng cụ thể.
#cv2 (OpenCV): OpenCV (Open Source Computer Vision Library) là một thư viện mã nguồn mở chuyên dụng cho xử lý và nhận diện hình ảnh, video. Nó bao gồm nhiều chức năng liên quan đến xử lý ảnh như cắt, chuyển đổi màu sắc, vẽ hình, nhận diện cạnh, phát hiện khuôn mặt, và nhiều hơn nữa.
# Thư viện: face_recognition có hàm:
'''face_encodings(): được sử dụng để mã hóa (encoding) các đặc trưng của khuôn mặt. Khi được áp dụng lên một hình ảnh khuôn mặt, hàm này sẽ tạo ra một vectơ số học đại diện cho khuôn mặt đó. Vectơ này chứa các thông tin quan trọng về hình dạng, vị trí và các đặc điểm độc nhất của khuôn mặt.
face_distance(): Hàm này được sử dụng để tính toán khoảng cách (độ tương tự) giữa các vectơ mã hóa của khuôn mặt. Khoảng cách này càng nhỏ thì hai khuôn mặt càng tương tự.
compare_faces(): Hàm này so sánh hai hoặc nhiều vectơ mã hóa của khuôn mặt để xác định xem chúng có tương tự hay không.
API: API của face_recognition cung cấp các chức năng chính cho việc nhận diện và xử lý khuôn mặt.
batch_face_locations(): Hàm này giúp tìm vị trí của nhiều khuôn mặt trong một danh sách ảnh.
face_landmarks(): Hàm này trích xuất các điểm đặc trưng của khuôn mặt, bao gồm mắt, mũi, miệng, v.v.
Hàm face_locations():sử dụng để xác định vị trí của các khuôn mặt trong một hình ảnh. Khi được áp dụng lên một hình ảnh, hàm này sẽ trả về một danh sách các hộp giới hạn (bounding boxes) chứa khuôn mặt. Mỗi hộp giới hạn được biểu diễn dưới dạng bốn tọa độ: (top, right, bottom, left), tương ứng với vị trí của hộp bao quanh khuôn mặt trong hình ảnh.
'''
# step 1 :
imganh1 = face_recognition.load_image_file("pic/hinhhoang/z4694981970053_60b82639be2acda236a5afaf6397b3ff.jpg")
imganh1 =cv2.cvtColor(imganh1,cv2.COLOR_BGR2RGB)
faceanh1 = face_recognition.face_locations(imganh1)[0]
print(faceanh1)
encodeElon = face_recognition.face_encodings(imganh1)[0] # mã hóa ảnh
cv2.rectangle(imganh1,(faceanh1[3],faceanh1[0]),(faceanh1[1],faceanh1[2]),(0,255,0),2)# (0,255,0) màu Lime, #00FF00


#step 2 :
imganh2 = face_recognition.load_image_file("pic/hinhkhiem/z4700043387622_da39bf2c4f39c337a5bb0061d643a6f4.jpg")
imganh2 =cv2.cvtColor(imganh2,cv2.COLOR_BGR2RGB)
faceanh2 = face_recognition.face_locations(imganh2)[0]
print(faceanh2)
encodeCheck = face_recognition.face_encodings(imganh2)[0]
cv2.rectangle(imganh2,(faceanh2[3],faceanh2[0]),(faceanh2[1],faceanh2[2]),(0,255,0),2)

'''
imganh1 = face_recognition.load_image_file("pic/hinhhoang/z4694981970053_60b82639be2acda236a5afaf6397b3ff.jpg")
    #imganh1: Đây là biến lưu trữ hình ảnh đã được tải.
    #face_recognition.load_image_file: Đây là hàm của thư viện face_recognition dùng để tải một hình ảnh từ đường dẫn file.
    #"pic/hinhhoang/z4694981970053_60b82639be2acda236a5afaf6397b3ff.jpg": Đây là đường dẫn đến tập tin hình ảnh. Trong trường hợp này, nó được tải từ thư mục "pic/hinhhoang" và có tên là "z4694981970053_60b82639be2acda236a5afaf6397b3ff.jpg".
imganh1 =cv2.cvtColor(imganh1,cv2.COLOR_BGR2RGB)
    #hình ảnh sẽ được chuyển từ không gian màu BGR (Blue-Green-Red) sang không gian màu RGB (Red-Green-Blue). Các kênh màu được hoán đổi vị trí.
    #Lý do phổ biến để chuyển đổi từ không gian màu BGR sang RGB là nhiều thư viện hỗ trợ RGB và nó là không gian màu phổ biến trong hầu hết các trường hợp. Tuy nhiên, OpenCV thường sử dụng BGR.
faceanh1 = face_recognition.face_locations(imganh1)[0]
    #Xác đinh vị trí khuôn mặt cần nhận dạng
    #face_recognition.face_locations(imganh1): Đây là một hàm của thư viện face_recognition được sử dụng để xác định vị trí của khuôn mặt trong hình ảnh.
    #imganh1: Đây là hình ảnh mà chúng ta muốn xác định vị trí của khuôn mặt.
    #[0]: Sau khi sử dụng hàm face_locations, chúng ta nhận được một danh sách các vị trí khuôn mặt. Trong trường hợp này, vì ta xác định khuôn mặt đầu tiên, nên chúng ta sử dụng [0] để lấy vị trí của khuôn mặt đầu tiên.
    #faceanh1 là một tuple chứa tọa độ của khuôn mặt đầu tiên trong ảnh imganh1, có dạng (y1, x2, y2, x1).
    #(x1, y1): Góc trên bên trái của khuôn mặt.
    #(x2, y2): Góc dưới bên phải của khuôn mặt.
print(faceanh1) #(y1,x2,y2,x1)
encodeElon = face_recognition.face_encodings(imganh1)[0]
    # mã hóa ảnh
    #face_recognition.face_encodings(imganh1): Đây là một hàm của thư viện face_recognition được sử dụng để mã hóa khuôn mặt trong hình ảnh thành một vector số học.
    #imganh1: Đây là hình ảnh mà chúng ta muốn mã hóa khuôn mặt.
    #encodeElon là một array chứa vector số học mã hóa khuôn mặt đầu tiên trong ảnh imganh1.
cv2.rectangle(imganh1,(faceanh1[1],faceanh1[0]),(faceanh1[3],faceanh1[2]),(255,0,255),2)
    #cv2.rectangle: Đây là hàm của thư viện OpenCV được sử dụng để vẽ một hình chữ nhật trên hình ảnh.
    #imganh1: Đây là hình ảnh mà chúng ta muốn vẽ hình chữ nhật lên.
    #(faceanh1[1], faceanh1[0]): Đây là tọa độ (x, y) của góc trên bên phải của hình chữ nhật.
    #faceanh1[1]: Là tọa độ x (hoành độ) của góc trên bên phải.
    #faceanh1[0]: Là tọa độ y (tung độ) của góc trên bên phải.
    #(faceanh1[3], faceanh1[2]): Đây là tọa độ (x, y) của góc dưới bên trái của hình chữ nhật.
    #faceanh1[3]: Là tọa độ x (hoành độ) của góc dưới bên trái.
    #faceanh1[2]: Là tọa độ y (tung độ) của góc dưới bên trái.
    #(255, 0, 255): Đây là màu của hình chữ nhật. Trong trường hợp này, màu được biểu diễn theo chuẩn RGB. Ở đây, màu được đặt là màu magenta.
    #2: Đây là độ dày của viền của hình chữ nhật.
    => Dòng mã này vẽ một hình chữ nhật xung quanh khuôn mặt được xác định bởi faceanh1 trên hình ảnh imganh1
'''
'''
face_distance1 = face_recognition.face_distance([encodeElon], encodeCheck)
print("Điểm khác nhau:", face_distance1[0])
# Kiểm tra điều kiện khớp (ví dụ: nếu điểm khác nhau nhỏ hơn 0.6 thì coi là khớp)
if face_distance1[0] < 0.5:
    face_distance=("[Khop]")
    print(face_distance)
else:
    face_distance=("[Khong khop]")
    print(face_distance)
cv2.putText(imgCheck,f"{face_distance}{(round(face_distance1[0],2))}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
'''
# nó sẽ so sánh hình ảnh mã hóa với các điểm trên khuôn mặt xem có khớp o
results = face_recognition.compare_faces([encodeElon],encodeCheck)
print(results) # Kết quả True
# tuy nhiên khi có nhiều hình ảnh thì chúng ta cần phải biết
# khoảng cách (sai số ) giữa các bức ảnh là bao nhiêu?
faceDis = face_recognition.face_distance([encodeElon],encodeCheck)
print(results,faceDis)
cv2.putText(imganh2,f"{results}{(round(faceDis[0],2))}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)

'''
cv2.putText(): Hàm này được sử dụng để vẽ văn bản lên hình ảnh.

imganh2: Hình ảnh trên đó văn bản sẽ được vẽ.

f"{results}{round(faceDis[0],2)}": Đây là chuỗi văn bản sẽ được hiển thị lên hình ảnh. Nó gồm hai phần:

results: Giá trị của biến results - danh sách các giá trị True/False.
round(faceDis[0],2): Khoảng cách giữa hai khuôn mặt, được làm tròn đến 2 chữ số sau dấu thập phân. faceDis là một danh sách chứa khoảng cách giữa các khuôn mặt, và [0] truy cập vào phần tử đầu tiên.
(50,50): Đây là tọa độ (x, y) của điểm gốc nơi văn bản sẽ được vẽ trên hình ảnh.
cv2.FONT_HERSHEY_COMPLEX: Đây là font chữ được sử dụng. Trong trường hợp này, cv2.FONT_HERSHEY_COMPLEX là một trong các loại font có sẵn.
1: Kíchthước của font chữ.
(0,0,255): Đây là màu của văn bản. Trong trường hợp này, màu này được biểu diễn bởi bộ màu BGR, với (0, 0, 255) tương ứng với màu đỏ.
2: Độ dày của đường vẽ văn bản.
Dòng code này sẽ vẽ văn bản lên hình ảnh imgCheck, hiển thị kết quả results và khoảng cách giữa khuôn mặt được làm tròn đến 2 chữ số sau dấu thập phân. Văn bản sẽ được vẽ tại tọa độ (50,50) với font chữ và màu sắc cụ thể, cùng với độ dày của văn bản.
'''
cv2.imshow("Elon",imganh1)  # view thử ảnh để kiểm tra
cv2.imshow("ElonCheck",imganh2) # view thử ảnh
cv2.waitKey()
cv2.destroyAllWindows()  # thoát tất cả các cửa sổ
'''
Đoạn code trên sử dụng thư viện OpenCV (cv2) để hiển thị hai hình ảnh trên các cửa sổ riêng biệt và cho phép người dùng kiểm tra kết quả.

cv2.imshow("Elon",imganh1): Dòng này hiển thị hình ảnh imganh1 trên một cửa sổ có tiêu đề là "Elon".

cv2.imshow("ElonCheck",imganh2): Dòng này hiển thị hình ảnh imganh2 trên một cửa sổ có tiêu đề là "ElonCheck".

cv2.waitKey(): Dòng này chờ người dùng nhấn một phím bất kỳ trên bàn phím. Khi người dùng nhấn phím, nó sẽ tiếp tục chạy.

cv2.destroyAllWindows(): Dòng này đóng tất cả các cửa sổ hiển thị hình ảnh. Sau khi người dùng nhấn phím bất kỳ và cv2.waitKey() trả về, cửa sổ sẽ bị đóng.
'''

    
    
