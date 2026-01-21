import cv2


def analyze_video_faces(video_path):
    """
    Analyze recorded video and detect faces using OpenCV Haar Cascade
    """

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return None

    total_frames = 0
    frames_with_face = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60)
        )

        if len(faces) > 0:
            frames_with_face += 1

    cap.release()

    if total_frames == 0:
        face_percentage = 0
    else:
        face_percentage = round((frames_with_face / total_frames) * 100, 2)

    return {
        "total_frames": total_frames,
        "frames_with_face": frames_with_face,
        "face_percentage": face_percentage
    }

