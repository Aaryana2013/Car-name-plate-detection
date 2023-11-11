import cv2
import imutils
import pytesseract
from tkinter import Tk, filedialog, Canvas, Button, Label, Toplevel
from PIL import ImageTk, Image

# Set the path to the Tesseract OCR engine executable
pytesseract.pytesseract.tesseract_cmd =   '/usr/local/bin/tesseract'

root = Tk()
root.geometry("500x400")
root.configure(bg="#20B2AA")

image_path = ""
analyzed_image = None
plate_text = ""

# Create a heading label in the middle of the window
heading_label = Label(root, text="License Plate Recognition", font=("Helvetica", 20))
heading_label.pack(pady=20)


def process_image():
    global image_path, analyzed_image, plate_text

    if not image_path:
        return

    # Read the image
    image = cv2.imread(image_path)
    image = imutils.resize(image, width=400)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply bilateral filtering for noise reduction
    gray_image = cv2.bilateralFilter(gray_image, 11, 17, 17)

    # Perform edge detection using the Canny algorithm
    edged = cv2.Canny(gray_image, 30, 200)

    # Find contours in the edged image
    cnts, new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and select the top 30
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]

    screenCnt = None

    # Iterate over the contours
    for c in cnts:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)
        if len(approx) == 4:
            screenCnt = approx
            x, y, w, h = cv2.boundingRect(c)
            new_img = image[y:y + h, x:x + w]
            cv2.imwrite('./7.png', new_img)
            break

    # Draw the detected license plate contour on the image
    if screenCnt is not None:
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 3)
        plate_image = cv2.imread('./7.png')
        plate_image = cv2.resize(plate_image, (image.shape[1], image.shape[0]))  # Resize plate_image to match image dimensions
        analyzed_image = cv2.hconcat([image, plate_image])
    else:
        print("No license plate contour found.")

    # Perform OCR on the cropped license plate image
    Cropped_loc = './7.png'
    plate_text = pytesseract.image_to_string(Cropped_loc, lang='eng')
    print("Number plate is:", plate_text)

    show_analyzed_image()

def show_analyzed_image():
    global analyzed_image, plate_text

    if analyzed_image is None:
        return

    top = Toplevel()
    top.geometry("500x400")
    top.configure(bg="#20B2AA")

    # Convert the analyzed image to PIL format
    img = Image.fromarray(analyzed_image)
    img = img.resize((400, 300))

    # Create a PhotoImage from the PIL image
    img_tk = ImageTk.PhotoImage(img)

    # Display the analyzed image on the top-level window
    label_img = Label(top, image=img_tk)
    label_img.pack()

    # Display the plate text below the analyzed image
    label_plate = Label(top, text="Number Plate: " + plate_text, bg="#20B2AA")
    label_plate.pack()

    top.mainloop()
def upload_image():
    global image_path, analyzed_image, plate_text
    image_path = filedialog.askopenfilename()
    analyzed_image = None
    plate_text = ""

    # Show the selected image on the root window
    img = Image.open(image_path)
    img = img.resize((400, 300))
    img_tk = ImageTk.PhotoImage(img)

    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk


canvas = Canvas(root, width=500, height=400)
canvas.pack()



upload_button = Button(root, text="Upload Image", command=upload_image, bg="#20B2AA")
canvas.create_window(170, 280, window=upload_button)

# Create the Analyze button
analyze_button = Button(root, text="Analyze", command=process_image, bg="#20B2AA")
canvas.create_window(340,280, window=analyze_button)

root.mainloop()
