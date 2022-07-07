import cv2 as cv

cap = cv.VideoCapture("data/results_2022-04-08T16-12-42.mp4")
while cap.isOpened():
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    binarized = cv.adaptiveThreshold(
        gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2
    )
    contours, hierarchy = cv.findContours(
        binarized, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE
    )
    frame_with_contours = cv.drawContours(
        image=frame.copy(),  # because cv.drawContours modifies in-place AND returns
        contours=contours,
        contourIdx=-1,
        color=(0, 255, 0),
        thickness=3,
    )
    cv.imshow("contours", frame_with_contours)
    if cv.waitKey(100) == ord("q"):
        break
cap.release()
cv.destroyAllWindows()
