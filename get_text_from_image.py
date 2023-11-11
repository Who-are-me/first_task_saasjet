# for this code i use this source
# https://medium.com/pythoneers/text-detection-and-extraction-from-image-with-python-5c0c75a8ff14
# packages opencv-python pytesseract opencv-python-headless opencv-contrib-python
# install opencv in PC in my cause -> sudo zypper in opencv

# from PIL import Image
# from pytesseract import pytesseract
#
# image = Image.open('/home/forever/Downloads/text.jpg')
# # image = image.resize((1662,786))
# image = image.resize((400,200))
# image.save('sample.png')

# https://stackoverflow.com/questions/37745519/use-pytesseract-ocr-to-recognize-text-from-an-image
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"/bin/tesseract"

image = cv2.imread('test_data/textv.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3,3), 0)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
invert = 255 - opening

data = pytesseract.image_to_string(invert, lang='eng', config='--psm 6')
print(data)

cv2.imshow('thresh', thresh)
cv2.imshow('opening', opening)
cv2.imshow('invert', invert)
cv2.waitKey()
