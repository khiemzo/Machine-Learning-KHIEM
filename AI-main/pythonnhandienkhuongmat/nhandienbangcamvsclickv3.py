from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch
model = YOLO("yolov8x.pt")  # load a pretrained model (recommended for training)

# Use the model
#model.train(data=".pre-commit-config.yaml", epochs=3)  # train the model
results = model(source=0, show=True, conf=0.8,save=True)