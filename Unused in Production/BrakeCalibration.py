from tkinter import *


class CalibrationGUI:
    def __init__(self, master):
        self.master = master
        self.naive = IntVar()
        master.title("BBI Brake Calibration")

        self.label = Label(master,
                           text="what do I want here")

        self.naiveCheck = Checkbutton(
            master, text="Naive Check", variable=self.naive)

        self.CaliButton = Button(
            master, text="Calibrate", command=self.calibrate)

        self.menubar = Menu(master)

        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load", command=self.calibrate)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.kMenu = Menu(self.menubar, tearoff=0)
        self.kMenu.add_command(label="Produce Motor Variance Graph",
                               command=self.calibrate)
        self.kMenu.add_command(label="Set No Load Torque",
                               command=self.calibrate)
        self.menubar.add_cascade(label="Constants", menu=self.kMenu)

        self.master.config(menu=self.menubar)

        self.e = Entry(self.master)

        self.e.focus_set()

        self.brakeName = self.makeentry(self.master, "Brake Label:", 0)
        self.dateMade = self.makeentry(self.master, "Date Purchased:", 1)
        self.CaliButton.grid(row=2, column=0)
        self.naiveCheck.grid(row=2, column=1)
        # self.label.pack()

    def calibrate(self):
        if (self.naive).get():
            print("Works Well Enough")
        else:
            pass

    def makeentry(self, parent, caption, r, **options):
        Label(parent, text=caption).grid(row=r, column=0)
        entry = Entry(parent, **options)
        entry.grid(row=r, column=1)
        return entry


root = Tk()
gui = CalibrationGUI(root)
root.mainloop()
