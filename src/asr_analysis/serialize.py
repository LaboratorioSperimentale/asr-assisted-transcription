def conversation_to_csv(conversation, sep = '\t'):
	full_csv = ""

	for tu in conversation:
		s = [tu.tu_id, tu.speaker, tu.start, tu.end, tu.duration, tu.include, len(tu.tokens)]
		s = sep.join(s)
		full_csv += s+"\n"

	return full_csv


### TOKEN
		# fields = [self.token_type.name,
		# 		self.text, self.orig_text,
		# 		self.intonation_pattern.name if self.intonation_pattern else "_",
		# 		self.position_in_tu.name,
		# 		self.pace.name if self.pace else "_",
		# 		self.volume.name if self.volume else "_",
		# 		self.warnings["PROLONGED_REPLACEMENTS"] if self.warnings["PROLONGED_REPLACEMENTS"] else "_",
		# 		'|'.join(self.prolonged_sounds),
		# 		str(self.prolongations) if self.prolongations > 0 else "_",
		# 		str(self.interruption) if self.interruption else "_"]
		# return "\t".join(fields)+"\n"


##### TRANSCRIPTION UNIT
	# ret_str = (f"# unit_id = {self.tu_id}\n"
	# 				f"# speaker = {self.speaker}\n"
	# 				f"# duration = {self.duration}\n"
	# 				f"# annotation = {self.orig_annotation}\n"
	# 				f"# text = {self.annotation}\n\n")

	# 	for err_id, err_value in self.errors.items():

	# 		if err_id == "UNCAUGHT_OVERLAPS":
	# 			overlaps = "|".join(f"{x}={y:.3f}" for x, y in err_value.items())
	# 			ret_str += f"# ERROR - {err_id} = {overlaps}\n"
	# 		elif err_value:
	# 			ret_str += f"# ERROR - {err_id}\n"

	# 	for warn_id, warn_value in self.warnings.items():
	# 		if warn_value > 0:
	# 			ret_str += f"# WARNING - {warn_id} = {warn_value}\n"

	# 	ret_str+="\n\n"

	# 	for token in self.tokens:
	# 		ret_str += str(token)

	# 	ret_str+="\n\n"

	# 	return ret_str

#### TRANSCRIPTION
		# ret_str = f"# transcription_id = {self.tr_id}\n\n"

		# # TODO: print stats

		# for turn_id, turn in enumerate(self.turns):
		# 	ret_str += f"# turn_id = {turn_id}\n"
		# 	ret_str += f"# start = {turn.start}\n# end = {turn.end}\n\n"

		# 	# !ISSUE: this way we are not printing empty units
		# 	for tu_id in turn.transcription_units_ids:
		# 		tu = self.transcription_units_dict[tu_id]
		# 		ret_str += str(tu)
		# 		# print(f"# unit_id = {tu_id}")