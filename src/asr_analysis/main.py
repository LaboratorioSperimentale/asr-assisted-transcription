import asr_analysis.data as data
import asr_analysis.serialize as serialize
import pandas as pd
import os

# Funzione che apre tutti i file transcript e genera un file di output per ognuno
def process_all_transcripts(input_dir="data/csv_puliti", output_dir="data/output"):
	transcripts_list = []

	if not os.path.exists(output_dir): # non abbiamo cartella di output, quindi la creiamo
		os.makedirs(output_dir)

	# Iterare attraverso tutti i file .csv
	for filename in os.listdir(input_dir):
		if filename.endswith(".csv"):
			transcript_name = filename.replace(".csv", "") # rimuove .csv (prendendo come esempio 01_ParlaBOA_E)
			transcript = data.transcript(transcript_name)

			with open(os.path.join(input_dir, filename), encoding="utf-8") as fin:
				print(f"Processing {filename}")
				tu_id = 0
				for line in fin:
					linesplit = line.strip().split("\t")
					if len(linesplit) == 5:
						speaker, start, end, duration, annotation = linesplit
					else:
						print(f"Issue with line {line}")
						continue

					new_tu = data.transcription_unit(tu_id, speaker, start, end, duration, annotation)
					transcript.add(new_tu)
					tu_id += 1

			transcript.sort()
			transcript.create_turns()
			# transcript.find_overlaps()
			# transcript.check_overlaps()
			for tu in transcript:
				# print(tu.annotation)
				tu.strip_parentheses()
				# print(tu.parentheses)
				# print(tu.splits)
				# input()
				tu.tokenize()

	# if not all(y for x, y in tu.errors.items()):
	# print(tu)
	# input()

#serialize.conversation_to_csv(transcript, "data/output/01_ParlaBOA_E.conll")

			output_filename = os.path.join(output_dir,f"{transcript_name}.conll")
			serialize.conversation_to_csv(transcript, output_filename)
			serialize.conversation_to_linear(transcript, os.path.join(output_dir,f"{transcript_name}.tsv"))
			transcripts_list.append(transcript)

	return transcripts_list


# print(transcript)
# input()
# transcript.create_turns()

# print(len(transcript.turns))
# for turn in transcript.turns:
# 	print(turn.speaker, turn.start, turn.end, turn.transcription_units_ids)
# 	input()

# for tu in transcript:
# 	tu.strip_parentheses()
# 	tu.tokenize()
# 	# if not all(y for x, y in tu.errors.items()):
# 	print(tu)
# 	input()

#
# print(transcript)

# DONE: read transcript from csv
# DONE: remove spaces (see init function --- done)

###### PRELIMINAR CLEANING STEPS -- > AIM: get to tokenization with tagged information

# DONE: transform "pò" into "po'" (keep count)
# DONE: transform "perchè" into "perché" (keep count)
# DONE: remove initial and final pauses (keep count)
# DONE: remove symbols that are not part of jefferson (keep count)
# DONE: correct unbalanced parentheses (keep count)
# DONE: remove "=" symbol, transform into space (--manual??)
# TODO: check orphan symbols
# DONE: correzione spazi (keep count) ( es. sempre spazio prima di "{" e dopo"}" )
# DONE: tokenize




if __name__ == "__main__":
	transcripts_list = process_all_transcripts("dati/sample", "dati/output")

	# TODO: inserire dati trascrittori nelle statistiche

	serialize.print_full_statistics(transcripts_list, "dati/output/statistics.csv")
