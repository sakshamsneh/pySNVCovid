import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile, askopenfilename
from pandastable import Table, TableModel
import pandas as pd
from subprocess import Popen
import queue
import threading

# import covid as prog
from func import covid
from thread import ThreadedTask


class GUI():
    gexffile = ""
    frame_w = 480
    frame_h = 315

    def __init__(self, prog, window):
        super().__init__()
        self.prog = prog
        self.window = window
        self.statusTxt = tk.StringVar()
        self.statusTxt.set("STATUS")

    def msg(self, val):
        messagebox.showerror("EMPTY", "INPUT VALUE "+val)

    def grid_config(self, frame):
        col_count, row_count = frame.grid_size()
        for col in range(col_count):
            frame.grid_columnconfigure(col, minsize=20)
        for row in range(row_count):
            frame.grid_rowconfigure(row, minsize=20)

    def frame1(self, nb):
        f1 = Frame(nb, width=self.frame_w, height=self.frame_h/2)
        f1.grid_propagate(0)    # Resets grid shrink and growth auto

        ft = Frame(f1, width=self.frame_w, height=self.frame_h/2)
        ft.pack(side=tk.BOTTOM)
        # Label(f1, text="DATA").grid(column=2, row=7, sticky='w')
        df = pd.DataFrame()
        pt = Table(ft, dataframe=df, rows=5, height=100, width=400)
        # pt.show()

        Label(f1, text="INPUT LINK").grid(column=2, row=2, sticky='w')
        linkTxt = tk.StringVar()
        link = Entry(f1, width=50,  textvariable=linkTxt)
        link.focus()
        linkTxt.set("")
        link.grid(column=4, row=2)

        btn_down = Button(f1, text="DOWNLOAD")

        def process_queue_dldf():
            try:
                df = self.queue.get(0)
                if df is not None:
                    pt.updateModel(TableModel(df))
                    pt.show()
                    pt.redraw()
                    self.set_status("DOWNLOADED!")
                    window.config(cursor="arrow")
            except queue.Empty:
                self.window.after(100, process_queue_dldf)

        # Nested click function for button
        def click_down():
            if not linkTxt.get():
                self.msg("LINK")
                return
            window.config(cursor="wait")
            # download db, on complete: continue
            self.set_status("DOWNLOADING!")
            self.queue = queue.Queue()
            ThreadedTask(self.queue, self.prog, "dldf", linkTxt.get()).start()
            df = self.window.after(100, process_queue_dldf)

        btn_down.configure(command=click_down)
        btn_down.grid(column=2, row=5, sticky='sw')

        btn_save = Button(f1, text="SAVE")

        def process_queue_scsv():
            try:
                msg = self.queue.get(0)
                if msg is not None:
                    self.set_status("FILE SAVED AT "+msg.name)
                    window.config(cursor="arrow")
            except queue.Empty:
                self.window.after(100, process_queue_scsv)

        def click_save():
            if df is not None:
                files = [('Comma Separated Values', '*.csv')]
                save_file = asksaveasfile(
                    filetypes=files, defaultextension=files)
                if not save_file:
                    return

                self.queue = queue.Queue()
                ThreadedTask(self.queue, self.prog, "scsv", save_file).start()
                self.window.after(100, process_queue_scsv)

        btn_save.configure(command=click_save)
        btn_save.grid(column=4, row=5, sticky='se')

        self.grid_config(f1)
        return f1

    def frame2(self, nb):
        f2 = Frame(nb, width=self.frame_w, height=self.frame_h)
        f2.grid_propagate(0)    # Resets grid shrink and growth auto

        Label(f2, text="SELECT GRAPH TYPE:").grid(column=2, row=2, sticky='w')
        graph_field = prog.get_graph_field()
        graph_type = tk.StringVar(f2)
        graph_type.set(graph_field[0])
        option = OptionMenu(f2, graph_type, *graph_field)
        option.config(width=40)
        option.grid(column=3, row=2)

        Label(f2, text="SELECT COLOR FIELD:").grid(column=2, row=3, sticky='w')
        color_field = prog.get_color_field()
        color_type = tk.StringVar(f2)
        color_type.set(color_field[0])
        optionc = OptionMenu(f2, color_type, *color_field)
        optionc.config(width=40)
        optionc.grid(column=3, row=3)

        btn = Button(f2, text="GENERATE")

        def process_queue_sgexf():
            try:
                save_file = self.queue.get(0)
                if save_file is not None:
                    self.set_status("FILE SAVED AT "+save_file)
                    window.config(cursor="arrow")
            except queue.Empty:
                self.window.after(100, process_queue_sgexf)

        def process_queue_gengf():
            try:
                colord = self.queue.get(0)
                if type(colord) is dict:
                    color = ""
                    for k in colord.keys():
                        color += str(k)+":"+str(colord.get(k))+"\n"

                    Label(f2, text="COLOR DETAILS").grid(
                        column=2, row=8, sticky='w')
                    info = tk.Text(f2, height=5, width=30)
                    info.configure(state=tk.NORMAL)
                    info.insert(tk.END, color)
                    info.configure(state=tk.DISABLED)
                    info.grid(column=3, row=9, sticky='nw')

                    self.set_status("GRAPH GENERATED!")
                    window.config(cursor="arrow")

                    files = [('Graph Exchange XML Format', '*.gexf')]
                    save_file = asksaveasfile(
                        filetypes=files, defaultextension=files)
                    if not save_file:
                        return
                    window.config(cursor="wait")
                    self.gexffile = save_file.name

                    self.queue = queue.Queue()
                    ThreadedTask(self.queue, self.prog,
                                 "sgexf", self.gexffile).start()
                    self.window.after(100, process_queue_gengf)

            except queue.Empty:
                self.window.after(100, process_queue_gengf)

        # Nested click function for button
        def click():
            if graph_type.get() == "SELECT":
                self.msg("GRAPH TYPE")
                return
            elif color_type.get() == "SELECT":
                self.msg("COLOR TYPE")
                return
            window.config(cursor="wait")
            # generate graph, on complete: continue
            self.queue = queue.Queue()
            ThreadedTask(self.queue, self.prog, "gengf",
                         graph_type.get(), color_type.get()).start()
            self.window.after(100, process_queue_gengf)

        btn.configure(command=click)
        btn.grid(column=3, row=5, sticky='se')

        ref = Button(f2, text="REFRESH")

        # Nested refresh function for ref button
        def refresh():
            graph_field = prog.get_graph_field()
            option['menu'].delete(0, 'end')
            graph_type.set(graph_field[0])
            for choice in graph_field:
                option['menu'].add_command(
                    label=choice, command=tk._setit(graph_type, choice))

            color_field = prog.get_color_field()
            optionc['menu'].delete(0, 'end')
            color_type.set(color_field[0])
            for choice in color_field:
                optionc['menu'].add_command(
                    label=choice, command=tk._setit(color_type, choice))
            self.set_status("REFRESHED!")

        ref.configure(command=refresh)
        ref.grid(column=2, row=5, sticky='ws')

        ref = Button(f2, text="OPEN")

        # Nested refresh function for open button
        def open():
            files = [('Comma Separated Values', '*.csv')]
            open_filename = askopenfilename(filetypes=files)
            if open_filename:
                prog.open_file(open_filename, 0)
                refresh()
                self.set_status("FILE OPENED "+open_filename)

        ref.configure(command=open)
        ref.grid(column=2, row=1, sticky='wn')

        self.grid_config(f2)
        return f2

    def frame3(self, nb):
        f3 = Frame(nb, width=self.frame_w, height=self.frame_h)
        f3.grid_propagate(0)    # Resets grid shrink and growth auto

        Label(f3, text="GRAPH DETAILS").grid(column=2, row=2, sticky='w')
        info = tk.Text(f3, height=5, width=40)
        info.insert(tk.END, prog.get_info())
        info.configure(state=tk.DISABLED)
        info.grid(column=2, row=3, sticky='nw')

        btn = Button(f3, text="LAUNCH GEPHI")

        # Nested click function for button
        def click():
            window.config(cursor="wait")
            # run GEPHI
            cmd = 'cmd /c ' + self.gexffile
            Popen(cmd, shell=False)
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
            self.set_status("REFRESHED!")

        ref.configure(command=refresh)
        ref.grid(column=2, row=6, sticky='ws')

        ref = Button(f3, text="OPEN")

        # Nested refresh function for open button
        def open():
            files = [('Graph Exchange XML Format', '*.gexf')]
            open_filename = askopenfilename(filetypes=files)
            if open_filename:
                infotxt = prog.open_file(open_filename, 1)
                self.gexffile = open_filename
                info.configure(state=tk.NORMAL)
                info.delete('1.0', tk.END)
                info.insert(tk.END, infotxt)
                info.configure(state=tk.DISABLED)
                self.set_status("FILE OPENED "+open_filename)

        ref.configure(command=open)
        ref.grid(column=2, row=1, sticky='wn')

        self.grid_config(f3)
        return f3

    def statusbar(self):
        status = Label(window, textvariable=self.statusTxt,
                       relief=tk.SUNKEN, width=self.frame_w, cursor='hand2')
        return status

    def set_status(self, txt):
        self.statusTxt.set(txt)

    def main(self):
        window.geometry('480x360')
        window.resizable(0, 0)
        window.title("pySNV")

        nb = Notebook(window)  # Notebook
        nb.grid(row=1, sticky='nw')
        f1 = self.frame1(nb)
        f2 = self.frame2(nb)
        f3 = self.frame3(nb)

        # Adding three frames
        nb.add(f1, text="DOWNLOAD")
        nb.add(f2, text="SELECT")
        nb.add(f3, text="DISPLAY")

        nb.select(f1)
        nb.enable_traversal()

        st = self.statusbar()   # Status bar
        st.grid(row=2, sticky='ws')

        window.mainloop()


if __name__ == "__main__":
    prog = covid()          # Program
    window = tk.Tk()        # Blank window
    gui = GUI(prog, window)  # Main Program with both prog and window
    gui.main()
