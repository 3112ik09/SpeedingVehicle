from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
import copy
import csv
import cars
# import camrcnn
# from object_detection.protos.optimizer_pb2 import LearningRate
# import cam
import cars2
from tkinter import filedialog
import carCam

master = Tk()


class NewWindow(Toplevel):

    def __init__(self, master=None):

        # super().__init__(master=master)
        root = Tk()
        root.title("Python - Import CSV File To Tkinter Table")
        width = 700
        height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        root.geometry("%dx%d+%d+%d" % (width, height, x, y))
        root.resizable(0, 0)
        TableMargin = Frame(root, width=500)
        TableMargin.pack(side=TOP)
        scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
        scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
        tree = ttk.Treeview(TableMargin, columns=("Vehicle_Id", "Speed", "Vehicle_Type"), height=400,
                            selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        tree.heading("#0", text="Images")
        tree.heading("Vehicle_Id", text="Vehicle Id", anchor=W)
        tree.heading('Speed', text="Speed", anchor=W)
        tree.heading('Vehicle_Type', text="Vehicle_Type", anchor=W)
        tree.column('#0', stretch=NO, minwidth=0, width=0)
        tree.column('#1', stretch=NO, minwidth=0, width=200)
        tree.column('#2', stretch=NO, minwidth=0, width=200)
        tree.column('#3', stretch=NO, minwidth=0, width=300)
        tree.pack()
        with open('Result.csv') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                Vehicle_Id = row['0']
                Speed = row['1']
                Vehicle_Type = row['2']
                # print(Speed)
                with Image.open(str(Vehicle_Id) + '.jpg') as nImg:
                    NewImg = ImageTk.PhotoImage(nImg)
                    # print(self._img)
                    tree.insert("", 0, values=(Vehicle_Id, Speed, Vehicle_Type))


class VideoPlayer(ttk.Frame):
    def __init__(self, parent: ttk.Frame = None, **prop: dict):
        setup = self.set_setup(prop)
        # FRAME TK ::
        ttk.Frame.__init__(self, parent)

        # Memberss
        self.__cap = object
        self.__size = (1500, 640)
        self.__image_ratio = 640 / 1500
        self.__frames_numbers = 0
        self.__play = False
        self.__algo = False
        self.__frame = np.array
        self.__initialdir = "/"
        self.__initialdir_movie = "/"
        self.file_name = 'cars1.mp4'

        self._command = []

        self.frame = np.array

        self._build_widget(parent, setup)

    def set_setup(self, prop: dict) -> dict:

        default = {'play': True, 'camera': False, 'pause': True,
                   'stop': True, 'image': False, 'algo': False}
        setup = default.copy()
        setup.update(prop)
        self.algo = setup['algo']
        return setup

    def resize(self, event):
        w, h = event.width, event.height
        width = h / self.__image_ratio
        height = h
        if width > w:
            width = w
            height = w * self.__image_ratio
        self.__size = (int(width), int(height))
        if Image.isImageType(self.frame):
            image = copy.deepcopy(self.frame)
            self.show_image(image)

    def _build_widget(self, parent: ttk.Frame = None, setup: dict = dict):
        if parent is None:
            self.master.geometry('1000x1000')
            self.main_panel = Frame(self.master)
            self.main_panel.place(relx=0.1, rely=0.1,
                                  relwidth=0.8, relheight=0.8)
        else:
            self.main_panel = parent
        self.main_panel.config(bg='grey')

        icon_width = 45
        icon_height = 50
        canvas_progressbar_height = 2
        self.canvas_image = Canvas(self.main_panel, bg='grey')
        self.canvas_image.pack(fill=BOTH, expand=True, side=TOP)
        self.canvas_image.bind('<Configure>', self.resize)

        self.board = Label(self.canvas_image, bg='white', width=44, height=14)
        self.board.pack(fill=BOTH, expand=True)

        canvas_progressbar = Canvas(self.main_panel, relief=FLAT, height=canvas_progressbar_height,
                                    bg="black", highlightthickness=0)
        canvas_progressbar.pack(fill=X, padx=10, pady=10)

        # s = ttk.Style()
        # s.theme_use('clam')
        # s.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=3)
        # self.progressbar = ttk.Progressbar(canvas_progressbar, style="red.Horizontal.TProgressbar", orient='horizontal',
        #                                    length=200, mode="determinate")
        # self.progressbar.pack(side= BOTTOM, fill=X , padx=20)

        # Control Buttons
        algo_frame = Frame(self.main_panel, bg='grey', relief=SUNKEN)
        algo_frame.pack(side=BOTTOM, fill=X, pady=20)

        control_frame = Frame(self.main_panel, bg='grey', relief=SUNKEN)
        control_frame.pack(side=BOTTOM, fill=X, padx=20)

        icon_path = '/home/ishu/Desktop/KG_main/Icons'

        # 1 : camera
        self.icon_camera = PhotoImage(
            file=os.path.join(icon_path, 'camera.png'))
        button_camera = Button(control_frame, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'),
                               text="camera", bg='white', image=self.icon_camera, height=icon_height,
                               width=icon_width, command=lambda: self.camera_capture())
        button_camera.pack(side='left', padx=10)
        # 2 : pause
        self.icon_pause = PhotoImage(
            file=os.path.join(icon_path, 'pause2.png'))

        self.button_pause_video = Button(control_frame, padx=10, pady=10, bd=8, fg="black",
                                         font=('arial', 12, 'bold'),
                                         text="Pause", bg='white', image=self.icon_pause,
                                         height=icon_height, width=icon_width,
                                         command=lambda: self.pause_movie())
        self.button_pause_video.pack(side='left', padx=10)

        # 3: For camara video detection
        self.icon_image = PhotoImage(file=os.path.join(icon_path, 'image.png'))
        button_load_image = Button(control_frame, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'),
                                   text="Load Image", bg="white", image=self.icon_image,
                                   height=icon_height, width=icon_width,
                                   command=lambda: self.load_image())
        button_load_image.pack(side='left', padx=10)

        # select video
        self.button_select_video = Button(control_frame, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'),
                                          text="Choose video ", bg="white", height=2, width=30,
                                          command=self.browseFiles)
        self.button_select_video.pack(side='left', padx=10)
        # run video
        self.icon_play = PhotoImage(file=os.path.join(icon_path, 'pp.png'))
        button_play = Button(control_frame, padx=10, pady=10, bd=8, fg='black', font=('arial', 12, 'bold'),
                             text="->load video", bg='white', image=self.icon_play, height=icon_height,
                             width=icon_width, command=lambda: self.play_movie(self.file_name))
        button_play.pack(side="left", padx=10)
        # to stop video
        self.icon_stop = PhotoImage(file=os.path.join(icon_path, 'stop.png'))
        button_stop_video = Button(control_frame, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'),
                                   text="stop", bg='white', height=icon_height, width=icon_width,
                                   image=self.icon_stop,
                                   command=lambda: self.pause_video())

        button_stop_video.pack(side='left', padx=10)

        # for Algo :::
        self.label_file_explorer = Label(algo_frame,
                                         text=self.file_name,
                                         width=20, height=4,
                                         fg="blue")
        self.button_Yolo = Button(algo_frame,
                                  text="YOLO",
                                  command=self.extract1, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'), bg="white", height=2, width=15,)

        self.button_explore = Button(algo_frame,
                                     text="Apply algo",
                                     command=self.extract, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'), bg="white", height=2, width=25,)

        self.button_image = Button(algo_frame,
                                   text="Result",
                                   command=self.image, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'),
                                   bg="white", height=2, width=8,)

        self.button_exit = Button(algo_frame,
                                  text="exit",
                                  command=exit, padx=10, pady=10, bd=8, fg="black", font=('arial', 12, 'bold'),
                                  bg="white", height=2, width=8,)

        # Grid method is chosen for placing
        # the widgets at respective positions
        # in a table like structure by
        # specifying rows and columns
        self.label_file_explorer.pack(side='left', padx=10, pady=10)
        self.button_Yolo.pack(side='left', padx=10, pady=10)
        self.button_explore.pack(side='left', padx=10, pady=10)

        self.button_image.pack(side='left', pady=10, padx=10)

        self.button_exit.pack(side='left', pady=10, padx=10)

    def image(self):
        NewWindow(master)
        pass

    def load_movie(self):
        print('ok')

    def camera_capture(self):
        self.__cap = cv2.VideoCapture(0)
        self.__frames_numbers = 1
        self.__play = not self.__play
        self.show_frame()
        # self.__cap = cam.camera()

    def show_frame(self):
        _, frame = self.__cap.read()
        # frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        cv2image = cv2.resize(cv2image, (800, 600))
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.board.imgtk = imgtk
        self.board.configure(image=imgtk)
        self.board.after(10, self.show_frame)

    def pause_movie(self):
        if self.__cap.isOpened():
            self.__cap.release()
        else:
            self.camera_capture()
        if self.__play:
            self.button_pause_video.config(image=self.icon_pause)
        elif not self.__play:

            self.button_pause_video.config(image=self.icon_play)

    def pause_video(self):
        if self.__cap.isOpened():
            self.__cap.release()
        else:
            self.play_movie(self.file_name)
        if self.__play:
            self.button_pause_video.config(image=self.icon_pause)
        elif not self.__play:

            self.button_pause_video.config(image=self.icon_play)

    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir="/home/ishu/obj_api/models/research/object_detection/gun2.mp4",
                                              title="Select a File",
                                              filetypes=(("video",
                                                          "*.avi*"),
                                                         ("mp4",
                                                         "*.mp4*")))

        # Change label contents
        self.file_name = filename.split("/")[-1]
        self.label_file_explorer.configure(text=self.file_name)
        # camrcnn.video_test(filename)

    def play_movie(self, movie_filename: str):
        print(movie_filename)
        self.__cap = cv2.VideoCapture(movie_filename)
        self.__frames_numbers = 1
        self.__play = not self.__play
        self.show_frame()

    def load_image(self):
        carCam.trackMultipleObjects()

    def extract(self):
        cars2.trackMultipleObjects(self.file_name)

    def extract1(self):
        cars.applyAlgo(self.file_name)


if __name__ == "__main__":
    vid = VideoPlayer(image=True, play=True, camera=True, algo=True)
    vid.mainloop()
