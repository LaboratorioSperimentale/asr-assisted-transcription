import regex as re

def remove_spaces(transcription):
	tot_subs = 0

	new_string, subs_made = re.subn(r"\t+", "", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# removing newlines
	new_string, subs_made = re.subn(r"\n+", "", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# removing double spaces
	new_string, subs_made = re.subn(r"\s\s+", " ", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

# transform "pò" into "po'" (keep count)
def replace_po(transcription):
	tot_subs = 0
	new_string, subs_made = re.subn(r"\bpò\b", "po'", transcription)

	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

# transform "chè" into "ché" (keep count)
def replace_che(transcription):
	tot_subs = 0
	regex = r"\b(perchè|benchè|finchè|poiché|anziché|dopodiché|granché|fuorché|affinché|pressoché)\b"
	# chè > ché
	new_string, subs_made = re.subn(regex, lambda m: m.group(0).replace("chè", "ché"), transcription)

	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

# remove initial and final pauses (keep count)
def remove_pauses(transcription):
	tot_subs = 0
	new_string, subs_made = re.subn(r"^([\[\]()<>°]?)\s*\{P\}\s*|\s*\{P\}\s*([\[\]()<>°]?)$",
									r"\1\2",
									transcription)

	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

# remove symbols that are not part of jefferson (keep count)
# TODO: numeri?
def clean_non_jefferson_symbols(transcription):
	tot_subs = 0
	new_string, subs_made = re.subn(r"[^,\?.:=°><\[\]\(\)\w\s'\-~$#]",
									"",
									transcription) # keeping also the apostrophe, # and $

	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

# correct unbalanced °° (must be even)
def check_even_dots(transcription):
	even_dots_count = transcription.count ("°")

	if even_dots_count % 2 == 0:
		return True
	else:
		return False

def check_normal_parentheses(annotation, open_char, close_char):
	isopen = False
	# count = 0
	for char in annotation:
		if char == open_char:
			if isopen:
				return False
			else:
				isopen = True
			# count += 1
		elif char == close_char:
			if isopen:
				isopen = False
			else:
				return False
			# count -= 1
			# if count < 0:
			# 	return True

	return isopen is False

def check_angular_parentheses(annotation):

	fastsequence = False   # >....<
	slowsequence = False    # <.....>
	for char in annotation:
		if char == "<":
			if fastsequence:
				fastsequence = False
			elif not slowsequence:
				slowsequence = True

		elif char == ">":
			if slowsequence:
				slowsequence = False
			elif not fastsequence:
				fastsequence = True

	if fastsequence or slowsequence:
		return False
	return True

def check_spaces(transcription):

	tot_subs = 0

	# "[ ([^ ])" -> [$1
	new_string, subs_made = re.subn(r"([\[\(]) ([^ ])", r"\1\2", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# "([^ ]) ]" -> $1]
	new_string, subs_made = re.subn(r"([^ ]) ([\)\]])", r"\1\2", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# "[^ ] [.,:?]" -> $1$2
	new_string, subs_made = re.subn(r"([^ ]) ([.,:?])", r"\1\2)", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# "[^ \[\(<>°](.)" -> $1 (.)
	new_string, subs_made = re.subn(r"([^ \[\(<>°])(\{[^}]+\})", r"\1 \2", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# "(.)[^ \]]" -> (.) $1
	new_string, subs_made = re.subn(r"(\{[^}]+\})([^ \]\)<>°])", r"\1 \2", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

def check_spaces_dots(transcription):
	matches = re.split(r"(°[^°]+°)", transcription)
	matches = [x for x in matches if len(x)>0]
	subs = 0
	if len(matches)>0:
		for match_no, match in enumerate(matches):
			if match[0] == "°":
				if match[1] == " ":
					match = match[0]+match[2:]
					subs += 1
				if match[-2] == " ":
					match = match[:-2]+match[-1]
					subs += 1
				matches[match_no] = match
		transcription = "".join(matches)

	return subs, transcription.strip()

def check_spaces_angular(transcription):

	matches = []

	fastsequence = False   # >....<
	slowsequence = False    # <.....>

	cur_split = []
	for char in transcription:
		if char == "<":
			if fastsequence:
				cur_split.append(char)
				matches.append(cur_split)
				cur_split = []
				fastsequence = False
			elif not slowsequence:
				matches.append(cur_split)
				cur_split = []
				cur_split.append(char)
				slowsequence = True

		elif char == ">":
			if slowsequence:
				cur_split.append(char)
				matches.append(cur_split)
				cur_split = []
				slowsequence = False
			elif not fastsequence:
				matches.append(cur_split)
				cur_split = []
				cur_split.append(char)
				fastsequence = True

		else:
			cur_split.append(char)

	matches = ["".join(x) for x in matches if len(x)>0]
	subs = 0
	if len(matches)>0:
		for match_no, match in enumerate(matches):
			if match[0] in [">", "<"]:
				if match[1] == " ":
					match = match[0]+match[2:]
					subs += 1
				if match[-2] == " ":
					match = match[:-2]+match[-1]
					subs += 1
				matches[match_no] = match
		transcription = "".join(matches)

	return subs, transcription.strip()
	# return matches

def check_numbers(transcription):

	if any(c.isdigit() for c in transcription):
		return True
	else:
		return False

def replace_spaces(match):
	return '{' + match.group(1).replace(' ', '_') + '}'

def meta_tag(transcription):
	subs_map = {"((": "{",
				"))": "}",
				"(.)": "{P}"}

	for old_string, new_string in subs_map.items():
		sub_annotation, subs_made = re.subn(re.escape(old_string), new_string, transcription)
		transcription = sub_annotation

		# replace spaces with _ in comments
		transcription = re.sub(r"\{([\w ]+)\}", replace_spaces, transcription)

	return transcription


def remove_prosodiclinks(transcription):
	tot_subs = 0
	new_string, subs_made = re.subn(r"^([\[\]()<>°]?)\s*=\s*|\s*=\s*([\[\]()<>°]?)$",
									"\1\2",
									transcription)

	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()


def push_parentheses(transcription):

	inverse_map = {"[": "]",
					"]": "[",
					"(": ")",
					")": "(",
					">": "<",
					"<": ">",
					"°": "°"}

	list_annotation = list(transcription)
	subs = 0

	opening = []
	closing = []

	fastsequence = False   # >....<
	slowsequence = False    # <.....>
	volumesequence = False
	for char_pos, char in enumerate(list_annotation):
		# print(char_pos, char)
		if char == "<":
			if fastsequence:
				closing.append(char_pos)
				fastsequence = False
			elif not slowsequence:
				opening.append(char_pos)
				slowsequence = True

		elif char == ">":
			if slowsequence:
				closing.append(char_pos)
				slowsequence = False
			elif not fastsequence:
				opening.append(char_pos)
				fastsequence = True

		elif char in ["[", "("]:
			opening.append(char_pos)

		elif char in ["]", ")"]:
			closing.append(char_pos)

		elif char == "°":
			if volumesequence:
				closing.append(char_pos)
				volumesequence = False
			else:
				opening.append(char_pos)
				volumesequence = True

	opening = sorted(opening)

	for char_pos in opening:
		if char_pos>0:
			i = char_pos
			j = char_pos-1

			while j > 0 and list_annotation[j] not in [" ", "="]:
				# print(list_annotation[i])
				if list_annotation[j] == inverse_map[list_annotation[i]]:
					print("ISSUE!!", list_annotation)
					break

				list_annotation[i], list_annotation[j] = list_annotation[j], list_annotation[i]

				subs += 1
				i-=1
				j-=1

			if j == 0:
				list_annotation[i], list_annotation[j] = list_annotation[j], list_annotation[i]
				subs += 1

	opening = []
	closing = []

	fastsequence = False   # >....<
	slowsequence = False    # <.....>
	volumesequence = False
	for char_pos, char in enumerate(list_annotation):
		# print(char_pos, char)
		if char == "<":
			if fastsequence:
				closing.append(char_pos)
				fastsequence = False
			elif not slowsequence:
				opening.append(char_pos)
				slowsequence = True

		elif char == ">":
			if slowsequence:
				closing.append(char_pos)
				slowsequence = False
			elif not fastsequence:
				opening.append(char_pos)
				fastsequence = True

		elif char in ["[", "("]:
			opening.append(char_pos)

		elif char in ["]", ")"]:
			closing.append(char_pos)

		elif char == "°":
			if volumesequence:
				closing.append(char_pos)
				volumesequence = False
			else:
				opening.append(char_pos)
				volumesequence = True

	closing = sorted(closing, reverse=True)

	for char_pos in closing:
		# print("".join(list_annotation), list_annotation[char_pos])
		if char_pos<len(list_annotation)-1:
			i = char_pos
			j = char_pos+1

			while j<len(list_annotation)-1 and list_annotation[j] not in [" ", "="]:
				if list_annotation[j] == inverse_map[list_annotation[i]]:
					print("ISSUE!!", list_annotation)
					break
				list_annotation[i], list_annotation[j] = list_annotation[j], list_annotation[i]

				subs += 1
				i+=1
				j+=1

			if j == len(list_annotation)-1:
				list_annotation[i], list_annotation[j] = list_annotation[j], list_annotation[i]
				subs += 1

	return subs, "".join(list_annotation)

if __name__ == "__main__":
	print(push_parentheses("c[ia]o co(me) va °qu°i"))