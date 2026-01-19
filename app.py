import cv2
import numpy as np
import easyocr
import os
from flask import Flask, render_template, request

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_IMAGE = "static/output.png"

reader = easyocr.Reader(["en"], gpu=False)

@app.route("/", methods=["GET", "POST"])
def index():

    accuracies = []
    indexes = []
    texts = []
    full_text = ""

    if request.method == "POST":

        file = request.files["image"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = cv2.imread(path)

        result = reader.readtext(path, detail=1, paragraph=False)
        collect_text = []

        for i, one in enumerate(result):

            top_left = tuple(map(int, one[0][0]))
            bottom_right = tuple(map(int, one[0][2]))
            text = one[1]
            acc = one[2]

            if acc < 0.5:
                continue

            accuracies.append(acc)
            indexes.append(i)
            texts.append((text, round(acc,2)))

            collect_text.append(text)

            img = cv2.rectangle(img, top_left, bottom_right, (255,255,0), 2)
            img = cv2.putText(img, text, top_left,
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        full_text = " ".join(collect_text)

        cv2.imwrite(OUTPUT_IMAGE, img)

    return render_template("index.html",
                           texts=texts,
                           full_text=full_text,
                           img_path=OUTPUT_IMAGE)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)