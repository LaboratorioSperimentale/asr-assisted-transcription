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
    new_string, subs_made = re.subn(r"^\(\.\)\s*|\s*\(\.\)$", "", transcription)

    if subs_made > 0:
        tot_subs += subs_made
        transcription = new_string

    return tot_subs, transcription.strip()

# remove symbols that are not part of jefferson (keep count)

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
          return "Balanced"
      else:
          return "Not balanced"
      
  
# correct unbalanced parentheses (keep count)

def check_parentheses(self):
    for annotation in self.transcription_units:
        annotation.check_normal_parentheses("(", ")") # checks that each open round bracket has a corresponding closed round bracket
        annotation.check_normal_parentheses("[", "]") # checks that each open square bracket has a corresponding closed square bracket
        annotation.check_angular_parentheses("<", ">") 
        annotation.check_angular_parentheses(">", "<") 

def check_normal_parentheses(annotation, open_char, close_char):
    count = 0
    for char in annotation:
        if char == open_char:
            count += 1
        elif char == close_char:
            count -= 1
            if count < 0:
                return "Not balanced"
    
    if count == 0:
        return "Balanced"
    else:
        return "Not balanced"

# def check_normal_parentheses(self, open_char, close_char):
 #		is_open = False
   # for char in self.annotation:
	# if char == open_char:
 		#	if is_open:
 		#		self.errors["UNBALANCED_PARENTHESES"] += 1
# return
 #   else:
 	#		    is_open = True

# 			if char == close_char:
# 				if not is_open:
# 					self.errors["UNBALANCED_PARENTHESES"] += 1
# 					return
# 				else:
# 					is_open = False

# 		if is_open:
# 			self.errors["UNBALANCED_PARENTHESES"] += 1


def check_angular_parentheses(annotation):
    count = 0
    for char in annotation:
    # increment count if the character is "<"
        if char == "<":
            count += 1  
        
        # decrement count if the character is ">"
        elif char == ">":
            count -= 1  
            
            # if the count is negative, parentheses are not balances
            if count < 0:
                return "Not balanced"
    
  # if count is zero, there are as many "<" as ">"
    
    if count == 0:
        return "Balanced"
    else:
        return "Not balanced"

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
