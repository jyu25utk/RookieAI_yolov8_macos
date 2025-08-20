
import cv2
import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

avg_fps = []
video_writer = None

def draw_text_with_bg(img, text, pos, font_scale=0.6, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 2
    padding= 15 # Equal padding on all sides
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    rect_width = text_width + 2 * padding
    rect_height = text_height + baseline + 2 * padding
    x, y = pos # Calculate rectangle position
    rect_x1 = x
    rect_y1 = y - text_height
    rect_x2 = rect_x1 + rect_width
    rect_y2 = rect_y1 + rect_height
    cv2.rectangle(img, (rect_x1, rect_y1), (rect_x2, rect_y2), bg_color, -1) # Draw background rectangle 
    text_x = rect_x1 + padding # Center text in rectangle with equal padding
    text_y = rect_y1 + padding + text_height # Properly centered vertically
    cv2.putText(img, text, (text_x, text_y), font, font_scale, text_color, thickness)


def yolo_coreml (source=0, model="yolo11n.pt", size=(960, 1080)):
    yolo_model = YOLO (model) # Initialize YOLO
    names = yolo_model.names
    cap = cv2.VideoCapture(source)

    _, _, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    video_writer = cv2.VideoWriter("yolo-output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, size)
        start_time = time.time()
        results = yolo_model.predict(frame, verbose=False)[0] # Process frame
        process_time = time.time() - start_time
        annotator = Annotator(frame)
        boxes = results.boxes.xyxy.tolist() 
        clss = results.boxes.cls.tolist()
        for box, cls in zip (boxes, clss):
            annotator.box_label(box, label=names [cls], color=colors (cls, True))
        fps = 1.0 / process_time if process_time > 0 else 0 # Calculate FPS 
        avg_fps.append(fps)
        fps = sum(avg_fps) / len(avg_fps)


        # Add text with background
        draw_text_with_bg(frame, f'FPS: {int(fps)}', (50, 60), bg_color=(255, 42, 4), font_scale=1.2)
        draw_text_with_bg (frame, f'Time: {process_time * 1000:.1f}ms', (50, 120), bg_color=(255, 42, 4), font_scale=1.2)
        cv2.imshow('Ultralytics YOLO', frame)
        video_writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    video_writer.release() 
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Usage examples:
    # yolo_coreml(0, model="yolo11n.pt")
    #yolo export model=yolo11n.pt format=coreml
    yolo_coreml (0, model="yolo11n.mlpackage")
    #yololln.pt
    # yolo_coreml(1, model="yolo11n.pt")
    # export official model
    #yololln.mlpackage