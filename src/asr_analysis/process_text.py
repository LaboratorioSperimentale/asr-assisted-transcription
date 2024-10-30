import re

def remove_spaces(transcription):
	tot_subs = 0

	new_string, subs_made = re.subn(r"\t", "", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# removing newlines
	new_string, subs_made = re.subn(r"\n", "", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# removing double spaces
	new_string, subs_made = re.subn(r"\s\s+", " ", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()


# def check_parentheses(self):

# 		for annotation in self.transcription_units:
# 			annotation.check_normal_parentheses("(", ")")
# 			annotation.check_normal_parentheses("[", "]")
# 			annotation.check_angular_parentheses()

# 	def check_normal_parentheses(self, open_char, close_char):
# 		is_open = False

# 		for char in self.annotation:
# 			if char == open_char:
# 				if is_open:
# 					self.errors["UNBALANCED_PARENTHESES"] += 1
# 					return
# 				else:
# 					is_open = True

# 			if char == close_char:
# 				if not is_open:
# 					self.errors["UNBALANCED_PARENTHESES"] += 1
# 					return
# 				else:
# 					is_open = False

# 		if is_open:
# 			self.errors["UNBALANCED_PARENTHESES"] += 1

# 	def check_angular_parentheses(self):
# 		openlist = {"left": False,
# 			 	"right": False}

# 		for char in self.annotation:
# 			if char == ">":
# 				if openlist["left"]:
# 					openlist["left"] = False
# 				elif not openlist["right"]:
# 					openlist["right"] = True

# 			if char == "<":
# 				if openlist["right"]:
# 					openlist["right"] = False
# 				elif not openlist["left"]:
# 					openlist["left"] = True

# 		if openlist["left"] or openlist["right"]:
# 			self.errors["UNBALANCED_PARENTHESES"] += 1


def replace_spaces(match):
	return '{' + match.group(1).replace(' ', '_') + '}'

def meta_tag(transcription):
	subs_map = {"((": "{",
				"))": "}",
				"(.)": "{PAUSE}"}

	for old_string, new_string in subs_map.items():
		sub_annotation, subs_made = re.subn(re.escape(old_string), new_string, transcription)
		transcription = sub_annotation

		# replace spaces with _ in comments
		transcription = re.sub(r"\{([\w ]+)\}", replace_spaces, transcription)

	return transcription
