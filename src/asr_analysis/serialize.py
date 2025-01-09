import csv
from asr_analysis import data as d
from asr_analysis import dataflags as df
import pandas as pd
from speach import elan

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


def conversation_to_conll(transcript, output_filename, sep = '\t'):
	fieldnames = ["speaker", "tu_id", "token", "orig_token", "span",
				"type", "align", "intonation", "unknown", "interruption", "truncation",
				"prosodicLink", "prolongations", "slow_pace", "fast_pace",
				"volume", "guesses"]

	with open(output_filename, "w", encoding="utf-8", newline='') as fout:
		writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=sep, restval="_")
		writer.writeheader()

		for turn_id, turn in enumerate(transcript.turns):
			turn_speaker = turn.speaker
			for tu_id in turn.transcription_units_ids:
				tu = transcript.transcription_units_dict[tu_id]

				for tok_id, tok in tu.tokens.items():

					to_write = {"speaker": tu.speaker,
								"tu_id": tu_id,
								"token": tok.text,
								"orig_token": tok.orig_text,
								"type": tok.token_type.name,
								"intonation": tok.intonation_pattern.name if tok.intonation_pattern else "_",
								"interruption": tok.interruption,
								"truncation": tok.truncation,
								"unknown": tok.unknown,
								"prosodicLink": tok.prosodiclink
								}

					to_write["span"] = tu.annotation[tok.span[0]:tok.span[1]]

					align = []
					if df.position.start in tok.position_in_tu:
						align.append(("Begin", tu.start))
					if df.position.end in tok.position_in_tu:
						align.append(("End", tu.end))
					to_write["align"] = "|".join([f"{x[0]}={x[1]}" for x in align])

					to_write["prolongations"] = ",".join([f"{x[0]}x{x[1]}" for x in tok.prolongations.items()])

					slow_pace = []
					for span_id, span in tok.slow_pace.items():
						slow_pace.append(f"{span[0]}-{span[1]}({span_id})")
					to_write["slow_pace"] = ",".join(slow_pace)

					fast_pace = []
					for span_id, span in tok.fast_pace.items():
						fast_pace.append(f"{span[0]}-{span[1]}({span_id})")
					to_write["fast_pace"] = ",".join(fast_pace)

					to_write["volume"] = tok.volume.name if tok.volume else "_"

					guesses = []
					for span_id, span in tok.guesses.items():
						guesses.append(f"{span[0]}-{span[1]}({span_id})")
					to_write["guesses"] = ",".join(guesses)

					writer.writerow(to_write)


def conversation_to_linear(transcript, output_filename, sep = '\t'):

	fieldnames = ["tu_id", "speaker", "start", "end", "duration", "include",
				"W:normalized_spaces", "W:numbers", "W:accents", "W:non_jefferson", "W:pauses_trim", "W:prosodic_trim",
				"E:volume", "E:pace", "E:guess", "E:overlap", "E:overlap_mismatch",
				"n_overlapping_spans", "overlapping_units",
				"T:shortpauses", "T:metalinguistic", "T:errors", "T:linguistic",
				"annotation", "correct", "text"]

	with open(output_filename, "w", encoding="utf-8") as fout:
		writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=sep)
		writer.writeheader()

		for turn_id, turn in enumerate(transcript.turns):
			turn_speaker = turn.speaker
			for tu_id in turn.transcription_units_ids:
				tu = transcript.transcription_units_dict[tu_id]

				to_write = {"tu_id": tu.tu_id,
							"speaker": tu.speaker,
							"start": tu.start,
							"end": tu.end,
							"duration": tu.duration,
							"include": tu.include,
							"annotation": tu.orig_annotation,
							"correct": tu.annotation,
							"text": " ".join(str(tok) for _, tok in tu.tokens.items()),
							"W:normalized_spaces": tu.warnings["UNEVEN_SPACES"],
							"W:numbers": tu.warnings["NUMBERS"],
							"W:accents": sum(tok.warnings["ACCENTS"] for _, tok in tu.tokens.items()),
							"W:non_jefferson": tu.warnings["NON_JEFFERSON"],
							"W:pauses_trim": tu.warnings["TRIM_PAUSES"],
							"W:prosodic_trim": tu.warnings["TRIM_PROSODICLINKS"],
							"E:volume": tu.errors["UNBALANCED_DOTS"],
							"E:pace": tu.errors["UNBALANCED_PACE"],
							"E:guess": tu.errors["UNBALANCED_GUESS"],
							"E:overlap": tu.errors["UNBALANCED_OVERLAP"],
							"E:overlap_mismatch": tu.errors["MISMATCHING_OVERLAPS"],
							"T:shortpauses": sum([df.tokentype.shortpause in tok.token_type for _, tok in tu.tokens.items()]),
							"T:metalinguistic": sum([df.tokentype.metalinguistic in tok.token_type for _, tok in tu.tokens.items()]),
							"T:errors": sum([df.tokentype.error in tok.token_type for _, tok in tu.tokens.items()]),
							"T:linguistic": sum([df.tokentype.linguistic in tok.token_type for _, tok in tu.tokens.items()])}

				if tu.errors["MISMATCHING_OVERLAPS"]:
					to_write["n_overlapping_spans"] = len(tu.overlapping_spans)
					to_write["overlapping_units"] = len(tu.overlapping_times)
					# overlapping_units = []
					# for x, y in tu.overlapping_times.items():
					# 	x = [str(el) for el in x]
					# 	overlapping_units.append("+".join(x))
					# to_write["overlapping_units"] = ",".join(overlapping_units)
					# print(tu.overlapping_spans)
					# print(tu.overlapping_times)
					# input()

				writer.writerow(to_write)


def csv2eaf(input_filename, output_filename, sep="\t"):

	with open(input_filename, newline='') as csvfile:

		reader = csv.DictReader(csvfile)

		for row in reader:

			print(row['first_name'], row['last_name'])


def eaf2csv(input_filename, output_filename, sep="\t"):

	fieldnames = ["tu_id", "speaker", "start", "end", "duration", "text"]
	full_file = []

	eaf = elan.read_eaf(input_filename)
	for tier in eaf:
		for anno in tier.annotations:
			_from_ts = f"{anno.from_ts.sec:.3f}" if anno.from_ts is not None else ''
			_to_ts = f"{anno.to_ts.sec:.3f}" if anno.to_ts is not None else ''
			_duration = f"{anno.duration:.3f}" if anno.duration is not None else ''

			to_write = {"speaker": tier.ID,
						"start": _from_ts,
						"end": _to_ts,
						"duration": _duration,
						"text": anno.value.strip()
						}
			full_file.append(to_write)

	full_file = sorted(full_file, key=lambda x: x["start"])

	with open(output_filename, "w", encoding="utf-8", newline='') as fout:
		writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=sep)
		writer.writeheader()

		for el_no, to_write in full_file:
			to_write["tu_id"] = el_no
			writer.writerow(to_write)

def read_csv(input_filename):

	with open(input_filename, encoding="utf-8", newline='') as csvfile:
		reader = csv.DictReader(csvfile, delimiter="\t")

		for row in reader:
			yield int(row["tu_id"]), row["speaker"], float(row["start"]), float(row["end"]), float(row["duration"]), row["text"]
