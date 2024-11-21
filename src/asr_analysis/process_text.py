import re

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
	new_string, subs_made = re.subn(r"^\s*\(\.\)\s*|\s*\(\.\)\s*$", "", transcription)

	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

# remove symbols that are not part of jefferson (keep count)
# TODO: numeri?
def clean_non_jefferson_symbols(transcription):
	tot_subs = 0
	new_string, subs_made = re.subn(r"[^,\?.:=°><\[\]\(\)\w\s'$#]", "", transcription) # keeping also the apostrophe, # and $

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
	count = 0
	for char in annotation:
		if char == open_char:
			count += 1
		elif char == close_char:
			count -= 1
			if count < 0:
				return False

	if count == 0:
		return True
	else:
		return False

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
	new_string, subs_made = re.subn(r"[\[\(] ([^ ])", "\1\2", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# "([^ ]) ]" -> $1]
	new_string, subs_made = re.subn(r"([^ ]) [\)\]]", "\1\2", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	# "[^ ] [.,:?]" -> $1$2
	new_string, subs_made = re.subn(r"[^ ] [.,:?]", "\1\2)", transcription)
	if subs_made > 0:
		tot_subs += subs_made
		transcription = new_string

	return tot_subs, transcription.strip()

def check_numbers(transcription):

	if any(c.isdigit() for c in transcription):
		return False
	else:
		return True

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