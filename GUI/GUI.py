import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox

window = tk.Tk()

tagTxt = tk.StringVar()
countVal = tk.IntVar()
date_sinceTxt = tk.StringVar()
chk_state = tk.BooleanVar()
dbsave_state = tk.BooleanVar()

OPTIONS = [
    "SELECT",
    "P2P",
    "STATE",
    "DISTRICT",
    "CITY"
]
graph_type = tk.StringVar(window)

tag = Entry(window, width=25,  textvariable=tagTxt)
count = Entry(window, width=25,  textvariable=countVal)
date_since = Entry(window, width=25, textvariable=date_sinceTxt)


def click():
    window.config(cursor="wait")
    if (not dbsave_state.get()):
        messagebox.showerror("EMPTY", "DOWNLOAD DATABASE!")
    elif(graph_type.get() == "SELECT"):
        messagebox.showerror("EMPTY", "INPUT GRAPH TYPE!")
    else:
        msg = "DETAILS:\nDOWNLOAD:\t"+str(dbsave_state.get())+"\nGRAPH TYPE:\t" + \
            str(graph_type.get())+"\nSAVE:\t\t"+str(chk_state.get())
        messagebox.showinfo("SUBMITTED", msg)
    window.config(cursor="arrow")


def clear():
    tagTxt.set("")
    countVal.set("")
    date_sinceTxt.set("")
    dbsave_state.set(False)
    chk_state.set(False)
    graph_type.set(OPTIONS[0])
    window.config(cursor="")


def main():
    window.geometry('260x300')
    window.resizable(0, 0)
    window.title("pySNV")

    Label(window, text="").grid(row=0)

    Label(window, text="DOWNLOAD DATA?").grid(row=1, sticky=tk.W)
    chk = Checkbutton(window, text='YES', var=dbsave_state)
    chk.grid(column=3, row=1)

    Label(window, text="SELECT GRAPH TYPE:").grid(row=2, sticky=tk.W)
    # chk = Checkbutton(window, text='P2P', var=chk_state)
    # chk.grid(column=3, row=2)
    # chk = Checkbutton(window, text='STATE', var=chk_state)
    # chk.grid(column=3, row=3)
    # chk = Checkbutton(window, text='DISTRICT', var=chk_state)
    # chk.grid(column=3, row=4)
    # chk = Checkbutton(window, text='CITY', var=chk_state)
    # chk.grid(column=3, row=5)
    option = OptionMenu(window, graph_type, *OPTIONS)
    # option = OptionMenu(window, graph_type, "SELECT",
    #                     "P2P", "STATE", "DISTRICT", "CITY")
    option.grid(column=3, row=2)

    Label(window, text="SAVE DATABASE?").grid(row=6, sticky=tk.W)
    chk = Checkbutton(window, text='YES', var=chk_state)
    chk.grid(column=3, row=6)

    Label(window, text="").grid(row=7)

    Button(window, text="SUBMIT", command=click).grid(row=8)
    Button(window, text="CLEAR", command=clear).grid(
        row=8, column=3, sticky=tk.E)

    window.mainloop()


if __name__ == "__main__":
    main()
