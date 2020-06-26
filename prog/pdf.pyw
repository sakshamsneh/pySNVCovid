from datetime import datetime
from io import BytesIO

import reportlab.lib.colors as colors
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg


class ReportGen():
    """
    ReportGen class creates pdf report from image and text
    """

    def __init__(self, graph_type, legend, subplot, stacked, slist, selecteddict):
        self.graph_type = graph_type.upper()
        self.legend = legend
        self.stacked = stacked
        self.subplot = subplot
        self.slist = slist
        self.selecteddict = selecteddict
        self.image_list=list()

    def create_template(self, c, now):
        head = "PySNV"
        c.setFontSize(20)
        c.setFillColor(colors.blue)
        c.drawString(1.0*inch, 11.0*inch, head)

        c.setFontSize(10)
        c.setFillColor(colors.black)
        # adds rect around graph area
        c.rect(1*inch, 1.5*inch, 6.4*inch, 6.5*inch)

        c.line(0*inch, 0.9*inch, 10.5*inch, 0.9*inch)
        c.drawString(5.5*inch, 0.7*inch, "SAKSHAM SNEH MANDAL")
        c.drawString(5.5*inch, 0.5*inch, now)

    def transform_img(self, img):
        imgdata = BytesIO()
        img.savefig(imgdata, format='svg')
        imgdata.seek(0)  # rewind the data
        drawing = svg2rlg(imgdata)

        scaling_x = scaling_y = 0.8
        drawing.width = drawing.minWidth() * scaling_x
        drawing.height = drawing.height * scaling_y
        drawing.scale(scaling_x, scaling_y)
        return drawing

    def set_image(self, img):
        self.img = self.transform_img(img)

    def add_extra_img(self, img):
        self.image_list.append(self.transform_img(img))
        # self.image_list = list(self.transform_img(img) for img in image_list)

    # def add_subplots(self, c, now):
    #     for img in self.image_list:
    #         self.create_template(c, now)
    #         renderPDF.draw(img, c, 1.3*inch, 1.8*inch)
    #         c.showPage()

    # Create report and add data it
    def gen_report(self, filename):
        self.filename = filename
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = canvas.Canvas(self.filename, pagesize=A4, bottomup=1)
        c.setTitle(self.graph_type+" GRAPH")

        # Show options
        c.drawString(1.0*inch, 10.4*inch, "GRAPH TYPE:"+self.graph_type)
        c.drawString(1.0*inch, 10.0*inch, "COLUMNS SELECTED:"+str(self.slist))
        c.drawString(1.0*inch, 9.6*inch, "GRAPH OPTIONS:")
        if(self.legend):
            c.setFillColor(colors.green)
        else:
            c.setFillColor(colors.red)
        c.drawString(1.5*inch, 9.4*inch, "LEGEND:"+str(self.legend))
        if(self.subplot):
            c.setFillColor(colors.green)
        else:
            c.setFillColor(colors.red)
        c.drawString(1.5*inch, 9.2*inch, "SUBPLOT:"+str(self.subplot))
        if(self.stacked):
            c.setFillColor(colors.green)
        else:
            c.setFillColor(colors.red)
        c.drawString(1.5*inch, 9.0*inch, "STACKED:"+str(self.stacked))

        c.setFillColor(colors.black)
        c.drawString(1.0*inch, 8.5*inch, self.graph_type+" GRAPH")

        self.create_template(c, now)
        renderPDF.draw(self.img, c, 1.3*inch, 1.8*inch)     # show graph
        # if not self.subplot or self.graph_type=='PIE':
        #     renderPDF.draw(self.img, c, 1.3*inch, 1.8*inch)     # show graph
        # else:
        #     c.showPage()
        #     self.add_subplots(c, now)

        c.save()


# if __name__ == "__main__":
#     import matplotlib.pyplot as plt
#     r = ReportGen("line", True, False, False, "na", "na")
#     fig = plt.figure(figsize=(4, 3))
#     plt.plot([1, 2, 3, 4])
#     plt.ylabel('some numbers')
#     r.set_image(fig)
#     r.gen_report("test1.pdf")
