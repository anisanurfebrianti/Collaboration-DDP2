from tkinter import *

class SapaApp:
    def __init__(self, root):
        self.root = root

        self.nama_label = Label(root, text="Nama:")
        self.nama_label.pack()

        self.nama_entry = Entry(root)
        self.nama_entry.pack()

        self.hasil_label = Label(root, text="Hasil")
        self.hasil_label.pack()

        self.tombol = Button(root, text="Sapa", command=self.sapa)
        self.tombol.pack()

    def sapa(self):
        nama = self.nama_entry.get()               # ambil input
        self.hasil_label["text"] = "Halo, " + nama # ubah teks label

root = Tk()
app = SapaApp(root)
root.mainloop()