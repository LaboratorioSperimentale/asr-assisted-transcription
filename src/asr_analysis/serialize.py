import csv
from asr_analysis import data as d
from asr_analysis import dataflags as df
import pandas as pd

# Creating a file that contains statistics for each transcript
def print_full_statistics(list_of_transcripts, output_filename):
	full_statistics = [] # list that contains all transcripts
	for transcript in list_of_transcripts: # iterating each transcript
		transcript.get_stats () # calculating statistics
		stats_dict = transcript.statistics.set_index("Statistic")["Value"].to_dict() # converting statistics into a dictionary
		stats_dict["Transcript_ID"] = transcript.tr_id	# adding the transcript id
		full_statistics.append(stats_dict)

	# Creating a df with all statistics
	statistics_complete = pd.DataFrame(full_statistics) # creating the dataframe
	statistics_complete.to_csv(output_filename, index=False, sep="\t") # converting the df to csv


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

				for token_id, token in transcription_unit.tokens.items():

					infos = [str(turn_id),
							str(tu_id),
							turn_speaker,
							str(token_id+1),
							token.token_type.name,
							token.text,
							token.orig_text,
							str(tu_start) if token_id==0 else "_",
							str(tu_end) if token_id == len(transcription_unit.tokens)-1 else "_",
							token.intonation_pattern.name if token.intonation_pattern else "_",
							token.position_in_tu.name if token.position_in_tu else "_",
							# token.pace,
							# token.volume,
							# str(token.prolongations),
							# "|".join(token.prolonged_sounds),
							# token.interrupted,
							# token.guess,
							# token.overlap
							]

					print(sep.join(infos), file=fout)


def conversation_to_linear(transcript, output_filename, sep = '\t'):

	fieldnames = ["speaker", "start", "end", "duration", "include",
				"W:normalized_spaces", "W:numbers", "W:accents", "W:non_jefferson", "W:pauses_trim", "W:prosodic_trim",
				"E:volume", "E:pace", "E:guess", "E:overlap", "E:overlap_mismatch",
				"T:shortpauses", "T:metalinguistic", "T:errors", "T:linguistic",
				"annotation", "correct", "text"]

	with open(output_filename, "w", encoding="utf-8") as fout:
		writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=sep)
		writer.writeheader()

		for turn_id, turn in enumerate(transcript.turns):
			turn_speaker = turn.speaker
			for tu_id in turn.transcription_units_ids:
				tu = transcript.transcription_units_dict[tu_id]

				to_write = {"speaker": tu.speaker,
							"start": tu.start,
							"end": tu.end,
							"duration": tu.duration,
							"include": tu.include,
							"annotation": tu.orig_annotation,
							"correct": tu.annotation,
							"text": " ".join(str(tok) for tok_id, tok in tu.tokens.items()),
							"W:normalized_spaces": tu.warnings["UNEVEN_SPACES"],
							"W:numbers": tu.warnings["NUMBERS"],
							"W:accents": sum(tok.warnings["ACCENTS"] for tok_id, tok in tu.tokens.items()),
							"W:non_jefferson": tu.warnings["NON_JEFFERSON"],
							"W:pauses_trim": tu.warnings["TRIM_PAUSES"],
							"W:prosodic_trim": tu.warnings["TRIM_PROSODICLINKS"],
							"E:volume": tu.errors["UNBALANCED_DOTS"],
							"E:pace": tu.errors["UNBALANCED_PACE"],
							"E:guess": tu.errors["UNBALANCED_GUESS"],
							"E:overlap": tu.errors["UNBALANCED_OVERLAP"],
							"E:overlap_mismatch": tu.errors["MISMATCHING_OVERLAPS"],
							"T:shortpauses": sum([df.tokentype.shortpause in tok.token_type for tok_id, tok in tu.tokens.items()]),
							"T:metalinguistic": sum([df.tokentype.metalinguistic in tok.token_type for tok_id, tok in tu.tokens.items()]),
							"T:errors": sum([df.tokentype.error in tok.token_type for tok_id, tok in tu.tokens.items()]),
							"T:linguistic": sum([df.tokentype.linguistic in tok.token_type for tok_id, tok in tu.tokens.items()])}
				writer.writerow(to_write)

			# print("", file=fout)


def csv2eaf(input_filename, output_filename, sep="\t"):

	with open(input_filename, newline='') as csvfile:

		reader = csv.DictReader(csvfile)

		for row in reader:

			print(row['first_name'], row['last_name'])