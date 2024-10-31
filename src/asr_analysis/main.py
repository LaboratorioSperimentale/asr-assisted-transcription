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

print(transcript)

i 
# DONE: read transcript from csv
# DONE: remove spaces (see init function --- done)

###### PRELIMINAR CLEANING STEPS -- > AIM: get to tokenization with tagged information

# TODO: transform "pò" into "po'" (keep count)
# TODO: transform "perchè" into "perché" (keep count)
# TODO: remove initial and final pauses (keep count)
# TODO: remove symbols that are not part of jefferson (keep count)
# TODO: correct unbalanced parentheses (keep count)
# TODO: remove "=" symbol, transform into space (--manual??)
# TODO: check orphan symbols
# TODO: correzione spazi (keep count) ( es. sempre spazio prima di "{" e dopo"}" )
# TODO: tokenize
