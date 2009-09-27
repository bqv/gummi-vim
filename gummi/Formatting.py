
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

STYLES = ["tool_bold", "tool_italic", "tool_unline"]
ALLIGN = ["tool_left", "tool_center", "tool_right"]


class Formatting:

	def __init__(self, widget, editorbuffer):
		try:		
			self.buffer = editorbuffer
			self.buffer.begin_user_action()
			ins = self.buffer.get_selection_bounds()[0]
			begintag, endtag = self.get_style_commands(widget)
			#write function to check for conflicting tags				
			self.buffer.insert(ins, begintag)
			end = self.buffer.get_selection_bounds()[1]
			self.buffer.insert(end, endtag)
			self.buffer.end_user_action()
		except IndexError: 
			return # will silenty pass if no text selected

	def get_style_commands(self, widget):
		caller = widget.get_name()
		begintag = ""; endtag = ""
		if caller in STYLES:
			if caller == "tool_bold": begintag = "\\textbf{"
			elif caller == "tool_italic": begintag = "\\textit{"
			elif caller == "tool_unline": begintag = "\\underline{"
			endtag = "}"
		elif caller in ALLIGN:
			if caller == "tool_left": cmd = "flushleft"
			elif caller == "tool_center": cmd = "center"
			elif caller == "tool_right": cmd = "flushright"
			begintag = "\\begin{" + cmd + "}"
			endtag = "\\end{" + cmd + "}"
		return begintag, endtag





