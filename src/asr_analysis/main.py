import asr_analysis.data as data


transcript = data.transcript("01_ParlaBOA_E")
with open("data/csv_puliti/01_ParlaBOA_E.csv", encoding="utf-8") as fin:
	tu_id = 0
	for line in fin:
		linesplit = line.strip().split("\t")
		speaker, start, end, duration, annotation = linesplit

		new_tu = data.transcription_unit(tu_id, speaker, start, end, duration, annotation)
		transcript.add(new_tu)
		tu_id += 1

transcript.create_turns()

print(len(transcript.turns))
for turn in transcript.turns:
	print(turn.speaker, turn.start, turn.end, turn.transcription_units_ids)
	input()

for tu in transcript:
	tu.strip_parentheses()
	tu.tokenize()
	# if not all(y for x, y in tu.errors.items()):
	print(tu)
	input()

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
# TODO: tokenize
