def conversation_to_csv(conversation, sep = '\t'):
	full_csv = ""

	for tu in conversation:
		s = [tu.tu_id, tu.speaker, tu.start, tu.end, tu.duration, tu.include, len(tu.tokens)]
		s = sep.join(s)
		full_csv += s+"\n"

	return full_csv
