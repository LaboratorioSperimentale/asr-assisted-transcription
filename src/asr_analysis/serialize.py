from asr_analysis import data as d


def print_full_statistics(list_of_transcripts, output_filename):
	pass


def conversation_to_csv(transcript, output_filename, sep = '\t'):

	with open(output_filename, "w", encoding="utf-8") as fout:

		for turn_id, turn in enumerate(transcript.turns):
			turn_speaker = turn.speaker
			# turn_id = None
			for tu_id in turn.transcription_units_ids:
				# print(tu_id)
				transcription_unit = transcript.transcription_units_dict[tu_id]
				# print(transcription_unit)
				tu_start = transcription_unit.start
				tu_end = transcription_unit.end
				# print(transcription_unit.tokens)

				for token_id, token in enumerate(transcription_unit.tokens):

					infos = [str(turn_id),
							str(tu_id),
							turn_speaker,
							str(token_id),
							token.token_type.name,
							token.text,
							token.orig_text,
							# tu_start if token_id==0 else "_",
							# tu_end if token_id == len(transcription_unit.tokens)-1 else "_",
							# token.intonation_pattern,
							# token.position_in_tu,
							# token.pace,
							# token.volume,
							# token.prolongations,
							# "|".join(token.prolonged_sounds),
							# token.interrupted,
							# token.guess,
							# token.overlap
							]

					print(sep.join(infos), file=fout)



# ID_TURNO
# ID_TRANSCRIPTIONUNIT
# SPEAKER

# TOKENTYPE
# TOKEN_TEXT
# TOKEN_ORIG_TEXT
# TOKEN_START
# TOKEN_END
# TOKEN_INTONATION_PATTERN
# TOKEN_POSITION
# TOKEN_PACE
# TOKEN_VOLUME
# TOKEN_PROLONGATIONS
# TOKEN_PROLONGED_SOUNDS
# TOKEN_INTERRUPTED

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