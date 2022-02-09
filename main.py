
import os.path

prototxt_path = 'colorization_deploy_v2.prototxt'
model_path = 'colorization_release_v2.caffemodel'
kernel_path = 'pts_in_hull.npy'
image_path = r'C:\Users\DAVID\Downloads\pipe-a-WQTwsgq_mxg-unsplash.jpg'

# net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
# points = np.load(kernel_path)
#
# points = points.transpose().reshape(2, 313, 1, 1)
# net.getLayer(net.getLayerId("class8_ab")).blobs = [points.astype(np.float32)]
# net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [np.full([1, 313], 2.606, dtype="float32")]
#
# bw_image = cv2.imread(image_path)
# normalized = bw_image.astype("float32") / 255
# lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)
#
# resized = cv2.resize(lab, (224, 224))
# L = cv2.split(resized)[0]
# L -= 50
#
# net.setInput(cv2.dnn.blobFromImage(L))
# ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
# ab = cv2.resize(ab, (bw_image.shape[1], bw_image.shape[0]))
# L = cv2.split(lab)[0]
# colorized = np.concatenate((L[:,:,np.newaxis],ab),axis=2)
#
# colorized = cv2.cvtColor(colorized,cv2.COLOR_LAB2BGR)
# colorized = (255.0 * colorized).astype("uint8")
#
# cv2.imshow("BW Image",bw_image)
# cv2.imshow("Colorized",bw_image)
#
# cv2.waitKey(0)
# cv2.destroyAllWindow()

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import numpy as np
import cv2 as cv
import os.path

numpy_file = np.load(kernel_path)
Caffe_net = cv.dnn.readNetFromCaffe(prototxt_path,
                                   model_path)
numpy_file = numpy_file.transpose().reshape(2, 313, 1, 1)


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.master = master
        self.pos = []
        self.master.title("B&W Image Colorization")
        self.pack(fill=BOTH, expand=1)

        menu = Menu(self.master)
        self.master.config(menu=menu)

        file = Menu(menu)
        file.add_command(label="Upload Image", command=self.uploadImage)
        file.add_command(label="Color Image", command=self.color)
        menu.add_cascade(label="File", menu=file)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image = None
        self.image2 = None

        label1 = Label(self, image=img)
        label1.image = img
        label1.place(x=400, y=370)

    def uploadImage(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd())
        if not filename:
            return
        load = Image.open(filename)

        load = load.resize((480, 360), Image.ANTIALIAS)

        if self.image is None:
            w, h = load.size
            width, height = root.winfo_width(), root.winfo_height()
            self.render = ImageTk.PhotoImage(load)
            self.image = self.canvas.create_image((w / 2, h / 2), image=self.render)

        else:
            self.canvas.delete(self.image3)
            w, h = load.size
            width, height = root.winfo_screenmmwidth(), root.winfo_screenheight()

            self.render2 = ImageTk.PhotoImage(load)
            self.image2 = self.canvas.create_image((w / 2, h / 2), image=self.render2)

        frame = cv.imread(filename)

        Caffe_net.getLayer(Caffe_net.getLayerId('class8_ab')).blobs = [numpy_file.astype(np.float32)]
        Caffe_net.getLayer(Caffe_net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]

        input_width = 224
        input_height = 224

        rgb_img = (frame[:, :, [2, 1, 0]] * 1.0 / 255).astype(np.float32)
        lab_img = cv.cvtColor(rgb_img, cv.COLOR_RGB2Lab)
        l_channel = lab_img[:, :, 0]

        l_channel_resize = cv.resize(l_channel, (input_width, input_height))
        l_channel_resize -= 50

        Caffe_net.setInput(cv.dnn.blobFromImage(l_channel_resize))
        ab_channel = Caffe_net.forward()[0, :, :, :].transpose((1, 2, 0))

        (original_height, original_width) = rgb_img.shape[:2]
        ab_channel_us = cv.resize(ab_channel, (original_width, original_height))
        lab_output = np.concatenate((l_channel[:, :, np.newaxis], ab_channel_us), axis=2)
        bgr_output = np.clip(cv.cvtColor(lab_output, cv.COLOR_Lab2BGR), 0, 1)

        cv.imwrite("./result.png", (bgr_output * 255).astype(np.uint8))

    def color(self):

        load = Image.open("./result.png")
        load = load.resize((480, 360), Image.ANTIALIAS)

        if self.image is None:
            w, h = load.size
            self.render = ImageTk.PhotoImage(load)
            self.image = self.canvas.create_image((w / 2, h / 2), image=self.render)
            root.geometry("%dx%d" % (w, h))
        else:
            w, h = load.size
            width, height = root.winfo_screenmmwidth(), root.winfo_screenheight()

            self.render3 = ImageTk.PhotoImage(load)
            self.image3 = self.canvas.create_image((w / 2, h / 2), image=self.render3)
            self.canvas.move(self.image3, 500, 0)


root = tk.Tk()
root.geometry("%dx%d" % (980, 600))
root.title("B&W Image Colorization GUI")
img = ImageTk.PhotoImage(Image.open(image_path))

app = Window(root)
app.pack(fill=tk.BOTH, expand=1)
root.mainloop()