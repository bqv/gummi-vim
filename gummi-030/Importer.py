
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------


class Importer:

	def __init__(self):
		self.bcenter = "\n\\begin{center}\n"
		self.ecenter = "\\end{center}\n"


	def generate_table(self, rows, columns):
		allign = ""
		table = ""
		rows = int(rows) + 1
		columns = int(columns) + 1
		for l in range(1,columns): allign = allign + "l"
		begin_tabular = 	"\\begin{tabular}{" + allign + "}\n"
		end_tabular = "\\end{tabular}\n"
		for k in range(1, rows):		
			for i in range(1,columns):
				if i == (columns-1): new = str(k) + str(i) + "\\\\ \n"
				elif i == 1: new = "\t" + str(k) + str(i) + " & " 
				else: new = str(k) + str(i) + " & " 
				table = table + new
		return begin_tabular + table + end_tabular

	def generate_image(self, imagefile,  scale, caption, label):
		include = "\t\\includegraphics"
		scale = "[scale=" + str(scale) + "]"
		file = "{" + imagefile + "}\n"
		caption = "\t\\captionof{" + caption + "}\n"
		label = "\t\\label{" + label + "}\n"
		end = "\\end{center}\n"
		return self.bcenter + include + scale + file + caption + label + end













