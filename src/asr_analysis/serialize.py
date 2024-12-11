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
							str(token_id+1),
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
