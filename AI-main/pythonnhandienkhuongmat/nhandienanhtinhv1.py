
#sử dụng YOLO (You Only Look Once): hợp lý hơn so với ssd và R-cnns vì SSD (Single Shot Multibox Detector): Cũng nhanh và chính xác, nhưng tốn tài nguyên tính toán hơn YOLO. R-CNNs (Region-based Convolutional Neural Networks): Tính toán tốn kém và tốn thời gian.
'''
download pretrain model yolov8 - nhanh
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
results = model.predict(show=True, source="0")
print(results)
'''
"""
 # predict detect bằng CLI
 !yolo task=detect mode=predict model=yolov8.pt source="#chứa địa chỉ ảnh"
"""
'''
# prelict dêtct bằng python API
 from ultralytics import YOLO
 model = YOLO("yolov8.pt")
 results = model.predict(show=True, source="0") # source="#địa chỉ hình ảnh"
#print(results)
 '''
"""
#thử predict segmentation
!yolo task=segment mode=predict model=yolo8n-seg.pt source="# địa chỉ hình ảnh"
"""
from PIL import Image
from ultralytics import YOLO

# Load a pretrained YOLOv8n model
model = YOLO('yolov8n.pt')

# Run inference on 'bus.jpg'
results = model('D:/gitcode/pythonnhandienkhuongmat/pic/nguoivsdongvat/con-voi-an-gi-1.jpg')  # results list

# Show the results
for r in results:
    im_array = r.plot()  # plot a BGR numpy array of predictions
    im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
    im.show()  # show image
    im.save('results.jpg')  # save image

