import cv2 as cv


def main():
    img = cv.imread(cv.samples.findFile("starry_night.jpg"))
    cv.imshow("Display window", img)
    cv.waitKey()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
