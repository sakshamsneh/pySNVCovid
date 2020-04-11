import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
import time
import os

# import covid as prog
from func import covid
prog = covid()

window = tk.Tk()  # Main window
gexffile = ""


def grid_config(frame):
    col_count, row_count = frame.grid_size()
    for col in range(col_count):
        frame.grid_columnconfigure(col, minsize=20)
    for row in range(row_count):
        frame.grid_rowconfigure(row, minsize=20)


def frame1(nb):
    f1 = Frame(nb, width=480, height=360)
    f1.grid_propagate(0)    # Resets grid shrink and growth auto

    Label(f1, text="INPUT LINK").grid(column=2, row=2, sticky='w')
    linkTxt = tk.StringVar()
    link = Entry(f1, width=50,  textvariable=linkTxt)
    linkTxt.set("")
    link.grid(column=4, row=2)

    btn = Button(f1, text="DOWNLOAD")

    # Nested click function for button
    def click():
        # add error msg checks for linktxt
        window.config(cursor="wait")
        # download db, on complete: continue
        l = prog.getdownload(linkTxt.get())
        if l is not None:
            files = [('Comma Separated Values', '*.csv')]
            save_file = asksaveasfile(filetypes=files, defaultextension=files)
            if save_file is not None:
                prog.save_df(save_file, 0)
                # btn["text"] = "NEXT"
            window.config(cursor="arrow")

    btn.configure(command=click)
    btn.grid(column=4, row=5, sticky='se')

    grid_config(f1)
    return f1


def frame2(nb):
    f2 = Frame(nb, width=480, height=360)
    f2.grid_propagate(0)    # Resets grid shrink and growth auto

    Label(f2, text="SELECT GRAPH TYPE:").grid(column=2, row=2, sticky='w')
    OPTIONS = [
        "SELECT",
        "P2P",
        "STATE",
        "DISTRICT",
        "CITY"
    ]
    graph_type = tk.StringVar(f2)
    graph_type.set(OPTIONS[0])
    option = OptionMenu(f2, graph_type, *OPTIONS)
    option.config(width=40)
    option.grid(column=3, row=2)

    btn = Button(f2, text="GENERATE")

    # Nested click function for button
    def click():
        global gexffile
        window.config(cursor="wait")
        # generate graph, on complete: continue
        prog.gen_graph(graph_type.get())
        files = [('Graph Exchange XML Format', '*.gexf')]
        save_file = asksaveasfile(filetypes=files, defaultextension=files)
        if save_file is not None:
            gexffile = save_file.name
            prog.save_df(gexffile, 1)
            # btn["text"] = "NEXT"
        window.config(cursor="arrow")

    btn.configure(command=click)
    btn.grid(column=3, row=5, sticky='se')

    grid_config(f2)
    return f2


def frame3(nb):
    global gexffile
    f3 = Frame(nb, width=480, height=360)
    f3.grid_propagate(0)    # Resets grid shrink and growth auto

    Label(f3, text="GRAPH DETAILS").grid(column=1, row=1, sticky='w')
    info = tk.Text(f3, height=5, width=40)
    info.insert(tk.END, prog.get_info())
    info.configure(state=tk.DISABLED)
    info.grid(column=1, row=2, sticky='nw')

    btn = Button(f3, text="LAUNCH GEPHI")

    # Nested click function for button
    def click():
        window.config(cursor="wait")
        # run GEPHI
        cmd = 'cmd /c ' + gexffile + ' --console suppress'
        print(cmd)
        os.system(cmd)
        window.config(cursor="arrow")

    btn.configure(command=click)
    btn.grid(column=2, row=6, sticky='se')

    ref = Button(f3, text="REFRESH")

    # Nested refresh function for ref button
    def refresh():
        info.configure(state=tk.NORMAL)
        info.delete('1.0', tk.END)
        info.insert(tk.END, prog.get_info())
        info.configure(state=tk.DISABLED)

    ref.configure(command=refresh)
    ref.grid(column=1, row=6, sticky='ws')

    grid_config(f3)
    return f3


def main():
    window.geometry('480x360')
    window.resizable(0, 0)
    window.title("pySNV")

    nb = Notebook(window)  # Notebook
    nb.grid()
    f1 = frame1(nb)
    f2 = frame2(nb)
    f3 = frame3(nb)

    # Adding three frames
    nb.add(f1, text="DOWNLOAD")
    nb.add(f2, text="SELECT")
    nb.add(f3, text="DISPLAY")

    nb.select(f1)
    nb.enable_traversal()

    window.mainloop()


if __name__ == "__main__":
    main()
