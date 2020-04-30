import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile, askopenfilename
from pandastable import Table, TableModel
from ttkthemes import ThemedStyle
from tkcalendar import DateEntry
import pandas as pd
from subprocess import Popen
import queue
import webbrowser
import pyperclip
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from thread import ThreadedTask
import ListBox as lb


class GUI():
    """
    GUI class creates GUI for a passed tkinter object and a data program.
    This class uses ThreadedTask class for parallel processing of results.

    Args: prog: data program instance window: tkinter root instance
    """

    def __init__(self, prog, window):
        self.gexffile = ""
        self.frame_w = 480
        self.frame_h = 315
        self.prog = prog
        self.window = window
        self.statusTxt = tk.StringVar()
        self.statusTxt.set("STATUS")

    def msg(self, val):
        # Displays error message box with argument val
        messagebox.showerror("EMPTY", "INPUT VALUE "+val)

    def grid_config(self, frame):
        # Configures grid layout
        col_count, row_count = frame.grid_size()
        for col in range(col_count):
            frame.grid_columnconfigure(col, minsize=20)
        for row in range(row_count):
            frame.grid_rowconfigure(row, minsize=20)

    def frame1(self, nb):
        # Generates DOWNLOAD frame and returns
        f1 = Frame(nb, width=self.frame_w, height=self.frame_h/2)
        f1.grid_propagate(0)    # Resets auto grid shrink and growth

        # Table frame inside f1
        ft = Frame(f1, width=self.frame_w, height=self.frame_h/2)
        ft.pack(side=tk.BOTTOM)
        df = pd.DataFrame()     # Blank dataframe
        pt = Table(ft, dataframe=df, rows=5, height=100, width=400)

        Label(f1, text="INPUT LINK").grid(column=2, row=2, sticky='w')
        linkTxt = tk.StringVar()
        link = Entry(f1, width=50, textvariable=linkTxt)
        link.focus()
        linkTxt.set("")
        link.grid(column=4, row=2)

        # DOWNLOAD button start
        btn_down = Button(f1, text="DOWNLOAD")

        # Nested function for downloading dataframe using queue
        def process_queue_dldf():
            try:
                df = self.queue.get(0)
                if df is not None:
                    pt.updateModel(TableModel(df))
                    pt.show()
                    pt.redraw()
                    self.set_status("DOWNLOADED!")
                    self.window.config(cursor="arrow")
            except queue.Empty:
                self.window.after(100, process_queue_dldf)

        # Nested click function for DOWNLOAD button
        def click_down():
            if not linkTxt.get():
                self.msg("LINK")
                return
            self.window.config(cursor="wait")
            # download db using ThreadedTask class, on complete: continue
            self.set_status("DOWNLOADING!")
            self.queue = queue.Queue()
            ThreadedTask(self.queue, self.prog, "dldf", linkTxt.get()).start()
            df = self.window.after(100, process_queue_dldf)

        btn_down.configure(command=click_down)
        btn_down.grid(column=2, row=5, sticky='sw')
        # DOWNLOAD button end

        # SAVE button start
        btn_save = Button(f1, text="SAVE")

        # Nested function for saving dataframe as csv using queue
        def process_queue_scsv():
            try:
                msg = self.queue.get(0)
                if msg is not None:
                    self.set_status("FILE SAVED AT "+msg.name)
                    self.window.config(cursor="arrow")
            except queue.Empty:
                self.window.after(100, process_queue_scsv)

        # Nested click function for SAVE button
        def click_save():
            if df is not None:
                files = [('Comma Separated Values', '*.csv')]
                save_file = asksaveasfile(
                    filetypes=files, defaultextension=files)
                if not save_file:
                    return

                # save dataframe using ThreadedTask class, on complete: continue
                self.queue = queue.Queue()
                ThreadedTask(self.queue, self.prog, "scsv", save_file).start()
                self.window.after(100, process_queue_scsv)

        btn_save.configure(command=click_save)
        btn_save.grid(column=4, row=5, sticky='se')
        # SAVE button end

        self.grid_config(f1)
        return f1

    def frame2(self, nb):
        # Generates SELECT frame and returns
        f2 = Frame(nb, width=self.frame_w, height=self.frame_h)
        f2.grid_propagate(0)    # Resets grid shrink and growth auto

        Label(f2, text="SELECT GRAPH TYPE:").grid(column=2, row=2, sticky='w')
        graph_field = self.prog.get_graph_field()
        graph_type = tk.StringVar(f2)
        graph_type.set(graph_field[0])
        option = OptionMenu(f2, graph_type, *graph_field)
        option.config(width=40)
        option.grid(column=3, row=2)

        Label(f2, text="SELECT COLOR FIELD:").grid(column=2, row=3, sticky='w')
        color_field = self.prog.get_color_field()
        color_type = tk.StringVar(f2)
        color_type.set(color_field[0])
        optionc = OptionMenu(f2, color_type, *color_field)
        optionc.config(width=40)
        optionc.grid(column=3, row=3)

        # OPEN button start
        btn_open = Button(f2, text="OPEN")

        # Nested open function for open button
        def click_open():
            files = [('Comma Separated Values', '*.csv')]
            open_filename = askopenfilename(filetypes=files)
            if open_filename:
                self.prog.open_file(open_filename, 0)
                click_ref()
                self.set_status("FILE OPENED "+open_filename)

        btn_open.configure(command=click_open)
        btn_open.grid(column=2, row=1, sticky='wn')
        # OPEN button end

        Label(f2, text="SELECT DATE RANGE:").grid(column=2, row=4, sticky='w')
        # get start and end date in row 5
        calstart = DateEntry(f2, date_pattern="y-mm-dd", state=tk.DISABLED)
        calstart.grid(column=2, row=5, sticky='w')
        calend = DateEntry(f2, date_pattern="y-mm-dd", state=tk.DISABLED)
        calend.grid(column=3, row=5, sticky='e')

        # GENERATE button start
        btn_gen = Button(f2, text="GENERATE")

        # Nested function for saving nx graph as gexf using queue
        def process_queue_sgexf():
            try:
                save_file = self.queue.get(0)
                if save_file is not None:
                    self.set_status("FILE SAVED AT "+save_file)
                    self.window.config(cursor="arrow")
            except queue.Empty:
                self.window.after(100, process_queue_sgexf)

        # Nested function for generating nx graph using queue
        def process_queue_gengf():
            try:
                colord = self.queue.get(0)
                if type(colord) is dict:
                    color = ""
                    for k in colord.keys():
                        color += str(k)+":"+str(colord.get(k))+"\n"

                    Label(f2, text="COLOR DETAILS").grid(
                        column=2, row=9, sticky='w')
                    info = tk.Text(f2, height=5, width=30)
                    info.configure(state=tk.NORMAL)
                    info.insert(tk.END, color)
                    info.configure(state=tk.DISABLED)
                    info.grid(column=3, row=10, sticky='nw')

                    self.set_status("GRAPH GENERATED!")
                    self.window.config(cursor="arrow")

                    files = [('Graph Exchange XML Format', '*.gexf')]
                    save_file = asksaveasfile(
                        filetypes=files, defaultextension=files)
                    if not save_file:
                        return
                    self.window.config(cursor="wait")
                    self.gexffile = save_file.name

                    # save nx graph using ThreadedTask class, on complete: continue
                    self.queue = queue.Queue()
                    ThreadedTask(self.queue, self.prog,
                                 "sgexf", self.gexffile).start()
                    self.window.after(100, process_queue_sgexf)

            except queue.Empty:
                self.window.after(100, process_queue_gengf)

        # Nested click function for GENERATE button
        def click_gen():
            if graph_type.get() == "SELECT":
                self.msg("GRAPH TYPE")
                return
            elif color_type.get() == "SELECT":
                self.msg("COLOR TYPE")
                return
            self.window.config(cursor="wait")
            # generate nx graph using ThreadedTask class, on complete: continue
            self.queue = queue.Queue()
            ThreadedTask(self.queue, self.prog, "gengf",
                         graph_type.get(), color_type.get(), calstart.get_date(), calend.get_date()).start()
            self.window.after(100, process_queue_gengf)

        btn_gen.configure(command=click_gen)
        btn_gen.grid(column=3, row=7, sticky='se')
        # GENERATE button end

        # REFRESH button start
        btn_ref = Button(f2, text="REFRESH")

        # Nested refresh function for ref button
        def click_ref():
            graph_field = self.prog.get_graph_field()

            start, end = self.prog.get_daterange()
            calstart.config(state=tk.NORMAL, mindate=start, maxdate=end)
            calend.config(state=tk.NORMAL, mindate=start, maxdate=end)

            option['menu'].delete(0, 'end')
            graph_type.set(graph_field[0])
            for choice in graph_field:
                option['menu'].add_command(
                    label=choice, command=tk._setit(graph_type, choice))

            color_field = self.prog.get_color_field()
            optionc['menu'].delete(0, 'end')
            color_type.set(color_field[0])
            for choice in color_field:
                optionc['menu'].add_command(
                    label=choice, command=tk._setit(color_type, choice))
            self.set_status("REFRESHED!")

        btn_ref.configure(command=click_ref)
        btn_ref.grid(column=2, row=7, sticky='ws')
        # REFRESH button end

        self.grid_config(f2)
        return f2

    def frame3(self, nb):
        # Generates DISPLAY frame and returns
        f3 = Frame(nb, width=self.frame_w, height=self.frame_h)
        f3.grid_propagate(0)    # Resets grid shrink and growth auto

        Label(f3, text="GRAPH DETAILS").grid(column=2, row=2, sticky='w')
        info = tk.Text(f3, height=5, width=40)
        info.insert(tk.END, self.prog.get_info())
        info.configure(state=tk.DISABLED)
        info.grid(column=2, row=3, sticky='nw')

        # GEPHI button start
        btn_gephi = Button(f3, text="LAUNCH GEPHI")

        # Nested click function for gephi launch
        def click_gephi():
            self.window.config(cursor="wait")
            # run GEPHI
            cmd = 'cmd /c ' + self.gexffile
            Popen(cmd, shell=False)
            self.window.config(cursor="arrow")

        btn_gephi.configure(command=click_gephi)
        btn_gephi.grid(column=2, row=6, sticky='se')
        # GEPHI button end

        # REFRESH button start
        btn_ref = Button(f3, text="REFRESH")

        # Nested refresh function for ref button
        def click_ref():
            info.configure(state=tk.NORMAL)
            info.delete('1.0', tk.END)
            info.insert(tk.END, self.prog.get_info())
            info.configure(state=tk.DISABLED)
            self.set_status("REFRESHED!")

        btn_ref.configure(command=click_ref)
        btn_ref.grid(column=2, row=6, sticky='ws')
        # REFRESH button end

        # OPEN button start
        btn_open = Button(f3, text="OPEN")

        # Nested refresh function for open button
        def click_open():
            files = [('Graph Exchange XML Format', '*.gexf')]
            open_filename = askopenfilename(filetypes=files)
            if open_filename:
                infotxt = self.prog.open_file(open_filename, 1)
                self.gexffile = open_filename
                info.configure(state=tk.NORMAL)
                info.delete('1.0', tk.END)
                info.insert(tk.END, infotxt)
                info.configure(state=tk.DISABLED)
                self.set_status("FILE OPENED "+open_filename)

        btn_open.configure(command=click_open)
        btn_open.grid(column=2, row=1, sticky='wn')
        # OPEN button end

        self.grid_config(f3)
        return f3

    def showmatgraph(self, df, graph_type, legend, subplots, stacked):
        # Generates matplotlib graph in separate dialog
        plotsc = tk.Toplevel(self.window)
        plotsc.geometry('600x600')
        plotsc.transient()
        plotsc.focus_set()
        plotsc.title('STATIC GRAPH')

        figure = plt.Figure(figsize=(6, 6), dpi=100)
        ax = figure.add_subplot(111)
        chart_type = FigureCanvasTkAgg(figure, plotsc)
        chart_type.get_tk_widget().pack()
        ax.set_title(graph_type)
        graph_col = list(df.columns.values)

        if graph_type == 'bar':
            df.groupby(graph_col).size().unstack(fill_value=0).plot(
                kind='bar', rot=45, legend=legend, stacked=stacked, ax=ax, subplots=subplots)
        elif graph_type == 'barh':
            df.groupby(graph_col).size().unstack(
                fill_value=0).plot(kind='barh', rot=45, legend=legend, stacked=stacked, ax=ax, subplots=subplots)
        elif graph_type == 'pie':
            df.groupby(graph_col)[graph_col].count().plot(
                kind='pie', rot=45, legend=legend, stacked=stacked, ax=ax, subplots=subplots)
        elif graph_type == 'line':
            df.groupby([graph_col[0], graph_col[1]]).size().unstack(fill_value=0).plot(
                kind='line', rot=45, legend=legend, stacked=stacked, ax=ax, subplots=subplots)
        self.window.config(cursor="arrow")

    def frame4(self, nb):
        # Generates STATIC GRAPH frame and returns
        f4 = Frame(nb, width=self.frame_w, height=self.frame_h)
        f4.grid_propagate(0)    # Resets grid shrink and growth auto

        # OPEN button start
        btn_open = Button(f4, text="OPEN")

        # Nested refresh function for open button
        def click_open():
            files = [('Comma Separated Values', '*.csv')]
            open_filename = askopenfilename(filetypes=files)
            if open_filename:
                collist = self.prog.open_file(open_filename, 0)
                col_list.delete(0, tk.END)
                col_list.insert(tk.END, *collist)
                self.set_status("FILE OPENED "+open_filename)

        btn_open.configure(command=click_open)
        btn_open.grid(column=2, row=1, sticky='wn')
        # OPEN button end

        Label(f4, text="SELECT GRAPH TYPE:").grid(column=2, row=2, sticky='w')
        graph_field = ['SELECT', 'line', 'pie', 'bar', 'barh']
        graph_type = tk.StringVar(f4)
        graph_type.set(graph_field[0])
        option = OptionMenu(f4, graph_type, *graph_field)
        option.config(width=35)
        option.grid(column=2, row=3, sticky='s')
        graph_field_select_mode = tk.EXTENDED

        Label(f4, text="SELECT GRAPH COLUMNS:").grid(
            column=2, row=4, sticky='w')
        col_list = lb.Listbox2(f4, height=5, width=40,
                               selectmode=graph_field_select_mode)
        col_list.insert(tk.END, self.prog.get_graph_field())
        col_list.grid(column=2, row=5, sticky='nw')

        # trace method for graph_type
        def graphchange(var, indx, mode):
            gtype = graph_type.get()
            if gtype == 'pie':
                graph_field_select_mode = tk.SINGLE
            else:
                graph_field_select_mode = tk.EXTENDED
            col_list.config(selectmode=graph_field_select_mode)

        graph_type.trace_add('write', graphchange)

        Label(f4, text="OPTIONS:").grid(column=4, row=2, sticky='w')
        legend = tk.BooleanVar()
        legend.set(False)
        Checkbutton(f4, text="LEGEND", variable=legend).grid(
            column=4, row=3, sticky='nwe')
        subplots = tk.BooleanVar()
        subplots.set(False)
        Checkbutton(f4, text="SUBPLOTS", variable=subplots).grid(
            column=4, row=4, sticky='nwe')
        stacked = tk.BooleanVar()
        stacked.set(False)
        Checkbutton(f4, text="STACKED", variable=stacked).grid(
            column=4, row=5, sticky='nwe')

        # trace method for subplots
        def optionsubplot(var, indx, mode):
            if subplots.get() == True and stacked.get() == True:
                stacked.set(False)

        # trace method for stacked
        def optionstacked(var, indx, mode):
            if subplots.get() == True and stacked.get() == True:
                subplots.set(False)
        subplots.trace_add('write', optionsubplot)
        stacked.trace_add('write', optionstacked)

        # GRAPH button start
        btn_graph = Button(f4, text="GENERATE GRAPH")

        # Nested click function for gephi launch
        def click_graph():
            self.window.config(cursor="wait")
            # get dataframe and generate graph
            slist = []
            for i in col_list.curselection():
                slist.append(col_list.get(i))
            if not slist:
                self.msg("COLUMNS")
                return
            elif graph_type.get() == "SELECT":
                self.msg("GRAPH TYPE")
                return
            df = self.prog.get_df(slist)
            self.showmatgraph(df, graph_type.get(), legend.get(),
                              subplots.get(), stacked.get())

        btn_graph.configure(command=click_graph)
        btn_graph.grid(column=4, row=7, sticky='s')
        # GRAPH button end

        # REFRESH button start
        btn_ref = Button(f4, text="REFRESH")

        # Nested refresh function for ref button
        def click_ref():
            collist = self.prog.get_graph_field()
            col_list.delete(0, tk.END)
            col_list.insert(tk.END, *collist)
            self.set_status("REFRESHED!")

        btn_ref.configure(command=click_ref)
        btn_ref.grid(column=2, row=7, sticky='ws')
        # REFRESH button end

        self.grid_config(f4)
        return f4

    def statusbar(self):
        # Defines a single row statusbar using Label
        status = Label(self.window, textvariable=self.statusTxt,
                       relief=tk.SUNKEN, width=self.frame_w, cursor='hand2')
        return status

    def set_status(self, txt):
        # Sets status by changing statusbar Label textvariable
        self.statusTxt.set(txt)

    def getlink(self, *arg):
        # Copy link to clipboard
        pyperclip.copy('https://api.covid19india.org/raw_data.json')
        self.set_status("LINK COPIED TO CLIPBOARD!")

    def helpscreen(self, *arg):
        # Creates help window
        helpsc = tk.Toplevel(self.window)
        helpsc.geometry('300x300')
        helpsc.transient()
        helpsc.focus_set()
        helpsc.title('HELP')
        help_txt = """\nTabs:\n1.DOWNLOAD: Download, view first 100 rows and save dataframe as CSV\n2.SELECT: Select graph type, node color field, and view the color assigned, save the generated graph file as GEXF\n3.DISPLAY: Check the graph attributes, open the file in gephi(installation required for viewing graph).\n4.STATIC GRAPH: Select graph type, graph fields(& reorder them), options and generate static graph.\n\n Open CSV, GEXF file directly for viewing results."""
        Label(helpsc, text=help_txt, justify=tk.LEFT, wraplength=250).pack()

        # LINK button
        Button(helpsc, text="COPY LINK", command=self.getlink).pack()

        # GEPHI_DOWNLOAD button start
        btn_link = Button(helpsc, text="DOWNLOAD GEPHI")

        # Nested function for link button to open website
        def click_link():
            webbrowser.open('https://gephi.org/users/download/')

        btn_link.configure(command=click_link)
        btn_link.pack()
        # GEPHI_DOWNLOAD button end

    def aboutscreen(self, *arg):
        # Creates about window
        aboutsc = tk.Toplevel(self.window)
        aboutsc.geometry('300x300')
        aboutsc.transient()
        aboutsc.focus_set()
        aboutsc.title('ABOUT')
        about_txt = """\nPYSNV\n\nVersion:1.3\n\nThis software creates dynamic network graph from csv.\n\nPackages:Networkx, matplotlib, pandas, tkinter.\n\n"""
        Label(aboutsc, text=about_txt, justify=tk.CENTER, wraplength=250).pack()

        # LINK button start
        btn_link = Button(aboutsc, text="CHECK WEBSITE")

        # Nested function for link button to open website
        def click_link():
            webbrowser.open('https://github.com/sakshamsneh/pySNVCovid')

        btn_link.configure(command=click_link)
        btn_link.pack()
        # LINK button end

    def quitscreen(self, *arg):
        # Creates quit option from menu
        quitsc = tk.Toplevel(self.window)
        quitsc.geometry('220x50')
        quitsc.transient()
        quitsc.focus_set()
        quitsc.title('QUIT?')

        Button(quitsc, text="YES", command=self.window.quit).pack()
        Button(quitsc, text="NO", command=quitsc.destroy).pack()

    def menubar(self):
        menubar = tk.Menu(self.window)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Sample Link",
                             command=self.getlink, accelerator="Ctrl+l")
        helpmenu.add_command(
            label="Help", command=self.helpscreen, accelerator="Ctrl+h")
        helpmenu.add_command(
            label="About", command=self.aboutscreen, accelerator="Ctrl+Shift+a")
        helpmenu.add_command(
            label="Quit", command=self.quitscreen, accelerator="Ctrl+q")
        menubar.add_cascade(label="App", menu=helpmenu)

        return menubar

    def main(self):
        self.window.geometry('480x360')
        self.window.resizable(0, 0)
        self.window.title("pySNV")

        ThemedStyle(self.window).set_theme("arc")

        menubar = self.menubar()
        self.window.config(menu=menubar)

        nb = Notebook(self.window)  # Notebook
        nb.grid(row=1, sticky='nw')
        f1 = self.frame1(nb)
        f2 = self.frame2(nb)
        f3 = self.frame3(nb)
        f4 = self.frame4(nb)

        # Adding three frames
        nb.add(f1, text="DOWNLOAD")
        nb.add(f2, text="SELECT")
        nb.add(f3, text="DISPLAY")
        nb.add(f4, text="STATIC GRAPH")

        self.window.bind('<Control-l>', self.getlink)
        self.window.bind('<Control-h>', self.helpscreen)
        self.window.bind('<Control-A>', self.aboutscreen)
        self.window.bind('<Control-q>', self.quitscreen)

        self.window.protocol("WM_DELETE_WINDOW", self.quitscreen)

        nb.select(f1)
        nb.enable_traversal()

        st = self.statusbar()   # Creates status bar
        st.grid(row=2, sticky='ws')

        self.window.mainloop()
