import queue
import threading
from pandastable import TableModel


class ThreadedTask(threading.Thread):
    def __init__(self, queue, prog, task, *arg):
        threading.Thread.__init__(self)
        self.queue = queue
        self.arg = arg
        self.prog = prog
        self.task = task

    def run(self):
        if self.task == "dldf":         # download dataframe
            df = self.prog.getdownload(self.arg[0])
            # df = TableModel.getSampleData()
            self.queue.put(df)
        elif self.task == "scsv":       # save csv
            self.prog.save_df(self.arg[0], 0)
            self.queue.put(self.arg[0])
        elif self.task == "gengf":      # generate graph
            colord = self.prog.gen_graph(self.arg[0], self.arg[1])
            self.queue.put(colord)
        elif self.task == "sgexf":      # save gexf
            self.prog.save_df(self.arg[0], 1)
            self.queue.put(self.arg[0])
