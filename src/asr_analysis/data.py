import collections
# import re
import regex as re
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple

import asr_analysis.process_text as pt
import asr_analysis.dataflags as df

@dataclass
class turn:
	speaker: str
	transcription_units_ids: List[str] = field(default_factory=lambda: [])
	start: float = 0
	end: float = 0

	def add_tu(self, tu_id):
		self.transcription_units_ids.append(tu_id)

	def set_start(self, start):
		self.start = start

	def set_end(self, end):
		self.end = end

@dataclass
class token:
	text: str
	span: Tuple[int,int] = (0,0)
	token_type: df.tokentype = df.tokentype.linguistic
	orig_text: str = ""
	intonation_pattern: df.intonation = None
	position_in_tu: df.position = df.position.inner
	pace: df.pace = None
	volume: df.volume = None
	overlap: bool = False
	guess: bool = False
	interruption: bool = False
	truncation: bool = False
	prolongations: int = 0
	prolonged_sounds: List[str] = field(default_factory=lambda: collections.defaultdict(int))
	warnings: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
	errors: List[str] = field(default_factory=lambda: collections.defaultdict(int))
	features: Dict[str, str] = field(default_factory=lambda: {})

	def __post_init__(self):

		self.orig_text = self.text

		while self.text[0] in ["[", "(", ">", "<", "°"]:
			self.text = self.text[1:]

		while self.text[-1] in ["]", ")", ">", "<", "°"]:
			self.text = self.text[:-1]

		if len(self.text) == 0:
			print("ISSUE", self.orig_text)
			# input()

		self.orig_text = self.text

		# STEP 1: check that token has shape '?([a-z]+:*)+[-']?[.,?]
		# otherwise signal error
		matching_instance = re.fullmatch(r"'?(\p{L}+:*)*\p{L}+[-'~]?:*[.,?]?", self.text)

		if matching_instance is None:
			if self.text == "{P}":
				self.token_type = df.tokentype.shortpause
			elif self.text[0] == "{":
				self.token_type = df.tokentype.metalinguistic
			else:
				self.token_type = df.tokentype.error

			# ? maybe let's break the function here in order to avoid the else branch
		else:
			# STEP2: find final prosodic features: intonation, truncation and interruptions
			if self.text.endswith("."):
				self.intonation_pattern = df.intonation.descending
				self.text = self.text[:-1] # this line removes the last character of the string (".")
			elif self.text.endswith(","):
				self.intonation_pattern = df.intonation.weakly_ascending
				self.text = self.text[:-1]
			elif self.text.endswith("?"):
				self.intonation_pattern = df.intonation.ascending
				self.text = self.text[:-1]
			elif self.text.endswith("-") or self.text.endswith("~"):
				self.interruption = True
				# self.text = self.text[:-1]
			elif self.text.endswith("'"):
				self.truncation = True
				# self.text = self.text[:-1]

			# # !! remove prolongations. Maybe the else should be deleted here?
			# else:
			# STEP3: at this point we should be left with the bare word with only prolongations

			# replace multiple : with a single :
			new_text, substitutions = re.subn(r":{2,}", ":", self.text)
			if substitutions > 0:
				self.text = new_text
				self.warnings["PROLONGED_REPLACEMENTS"] = substitutions

			positions = [i for i, letter in enumerate(self.text) if letter==":"] # get positions of ":" in the string

			prev_letters = []
			for i in positions:
				if self.text[i-1] in ["'", "-", "~"]:
					prev_letters.append(self.text[i-2])
				else:
					prev_letters.append(self.text[i-1])
			# prev_letters = [self.text[i-1] for i in positions]

			self.prolongations = len(positions)
			self.prolonged_sounds = prev_letters

			# check for high volume
			if any(letter.isupper() for letter in self.text):
				self.volume = df.volume.high

			# ! keeping "'" but removing ":" when in the middle of the token
			self.text = self.text.lower().strip(".,?").replace(":", "")

		# TODO: x -> unknown

	def add_span(self, start, end):
		self.span = (start, end)

	def update_span(self, end):
		self.span = (self.span[0], end)

	def __str__(self):

		return self.text


	def add_info(self, field_name, field_value):
		self.features[field_name] = field_value

#TODO: creare funzioni di test

@dataclass
class transcription_unit:
	tu_id : int
	speaker: str
	start: float
	end: float
	duration: float
	annotation: str
	# TODO: handle dialect presence
	# dialect: bool = False
	orig_annotation: str = ""
	include: bool = True
	# split: bool = False
	overlapping_spans: Dict[Tuple[int, int], str] = field(default_factory=lambda: {})
	low_volume_spans: List[Tuple[int, int]] = field(default_factory=lambda: {})
	guessing_spans: List[Tuple[int, int]] = field(default_factory=lambda: [])
	warnings: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
	errors: List[str] = field(default_factory=lambda: collections.defaultdict(bool))
	parentheses: List[Tuple[int, str]] = field(default_factory=lambda: [])
	splits: List[int] = field(default_factory=lambda: [])
	tokens: List[token] = field(default_factory=lambda: [])
	ntokens: int = 0
	# valid_tokens: List[bool] = field(default_factory=lambda: [])

	def __post_init__(self):
		self.start = float(self.start)
		self.end = float(self.end)
		self.duration = float(self.duration)
		self.annotation = self.annotation.strip()
		self.orig_annotation = self.annotation

		# non jefferson
		substitutions, new_transcription = pt.clean_non_jefferson_symbols(self.annotation)
		self.warnings["NON_JEFFERSON"] = substitutions
		self.annotation = new_transcription

		# transform metalinguistic annotations and pauses
		new_transcription = pt.meta_tag(self.annotation)
		self.annotation = new_transcription

		# spaces before and after parentheses
		substitutions, new_transcription = pt.check_spaces(self.annotation)
		self.warnings["UNEVEN_SPACES"] += substitutions
		self.annotation = new_transcription

		#pò, perché etc..
		substitutions, new_transcription = pt.replace_che(self.annotation)
		self.warnings["ACCENTS"] = substitutions
		self.annotation = new_transcription

		substitutions, new_transcription = pt.replace_po(self.annotation)
		self.warnings["ACCENTS"] += substitutions
		self.annotation = new_transcription

		# leading and trailing pauses
		substitutions, new_transcription = pt.remove_pauses(self.annotation)
		self.warnings["TRIM_PAUSES"] += substitutions
		self.annotation = new_transcription

		# leading and trailing prosodic links
		substitutions, new_transcription = pt.remove_prosodiclinks(self.annotation)
		self.warnings["TRIM_PROSODICLINKS"] += substitutions
		self.annotation = new_transcription

		# remove double spaces
		substitutions, new_transcription = pt.remove_spaces(self.annotation)
		self.warnings["SPACES"] = substitutions
		self.annotation = new_transcription

		self.errors["UNBALANCED_DOTS"] = not pt.check_even_dots(self.annotation)
		self.errors["UNBALANCED_OVERLAP"] = not pt.check_normal_parentheses(self.annotation, "[", "]")
		self.errors["UNBALANCED_GUESS"] = not pt.check_normal_parentheses(self.annotation, "(", ")")
		self.errors["UNBALANCED_PACE"] = not pt.check_angular_parentheses(self.annotation)
		self.errors["CONTAINS_NUMBERS"] = pt.check_numbers(self.annotation) # TODO add num2words

		# fix spaces before and after dots
		if "°" in self.annotation and not self.errors["UNBALANCED_DOTS"]:
			substitutions, new_transcription = pt.check_spaces_dots(self.annotation)
			self.warnings["UNEVEN_SPACES"] += substitutions
			self.annotation = new_transcription

		# fix spaces before and after angular
		if "<" in self.annotation and not self.errors["UNBALANCED_PACE"]:
			substitutions, new_transcription = pt.check_spaces_angular(self.annotation)
			self.warnings["UNEVEN_SPACES"] += substitutions
			self.annotation = new_transcription

		# check how many varying pace spans have been transcribed
		if "<" in self.annotation and not self.errors["UNBALANCED_PACE"]:
			matches_left = list(re.finditer(r"<[^ )\]][^><]*[^ (\[]>", self.annotation))
			matches_right = list(re.finditer(r">[^ )\]][^><]*[^ (\[]<", self.annotation))
			tot_spans = (self.annotation.count("<") + self.annotation.count(">"))/2

			if not len(matches_left) + len(matches_right) == tot_spans:
				print(self.annotation)
				print(matches_left)
				print(matches_right)
				input()
			# TODO @Martina check se ho beccato slow e fast bene!
			self.slow_pace_spans = [match.span() for match in matches_left]
			self.fast_pace_spans = [match.span() for match in matches_right]

		# check how many low volume spans have been transcribed
		if "°" in self.annotation and not self.errors["UNBALANCED_DOTS"]:
			matches = list(re.finditer(r"°[^°]+°", self.annotation))
			if len(matches)>0:
				self.low_volume_spans = [match.span() for match in matches]

		# check how many overlapping spans have been transcribed
		if "[" in self.annotation and not self.errors["UNBALANCED_OVERLAP"]:
			matches = list(re.finditer(r"\[[^\]]+\]", self.annotation))
			if len(matches)>0:
				self.overlapping_spans = {match.span():None for match in matches}

		# check how many guessing spans have been transcribed
		if "(" in self.annotation and not self.errors["UNBALANCED_GUESS"]:
			matches = list(re.finditer(r"\([^)]+\)", self.annotation))
			if len(matches)>0:
				self.guessing_spans = [match.span() for match in matches]

		swaps, new_transcription = pt.push_parentheses(self.annotation)
		if swaps > 0:
			self.warnings["PARENTHESES SWAPS"] += swaps
			self.annotation = new_transcription

		# remove unit if it only includes non-alphabetic symbols
		if all(c in ["[", "]", "(", ")", "°", ">", "<", "-", "'", "#"] for c in self.annotation):
			self.include = False

		if len(self.annotation) == 0:
			self.include = False

		# TODO: gestire cancelletto

	# def strip_parentheses(self):
	# 	# splits = []
	# 	new_string = ""

	# 	for i, c in enumerate(self.annotation):
	# 		if c in [" ", "="]:
	# 			self.splits.append(i)
	# 		if i > 0 and i < len(self.annotation)-1:
	# 			if c in ["'"] and self.annotation[i-1].isalpha() and self.annotation[i+1].isalpha():
	# 				self.splits.append(i)

	# 		if c in ["(", ")", "[", "]", ">", "<", "°"]:
	# 			self.parentheses.append((i, c))
	# 		else:
	# 			new_string+=c

	# 	self.annotation = new_string

	def tokenize(self):

		# print(self.annotation)
		# ! split on space, apostrophe between words and prosodic links
		tokens = re.split(r"( |(?<=\w)'(?=\w)|=)", self.annotation)
		# tokens = re.split(r"( |(?<=\w)'(?=\w)|=)", self.annotation)
		# print(tokens)
		# input()

		start_pos = 0
		end_pos = 0
		for i, tok in enumerate(tokens):
			if len(tok)>0 and not tok == " ":
				end_pos += len(tok)
				if tok == "'":
					if len(self.tokens) == 0:
						self.warnings["SKIPPED_TOKEN"] += 1
					else:
						self.tokens[-1] = token(tokens[i-1]+tok)
						self.tokens[-1].add_info("SpaceAfter", "No")
						self.tokens[-1].update_span(end_pos)
						start_pos = end_pos+1

				elif tok == "=":
					if len(self.tokens) == 0:
						self.warnings["SKIPPED_TOKEN"] += 1
					else:
						self.tokens[-1].add_info("ProsodicLink", "Yes")
					start_pos = end_pos+1

				else:
					new_token = token(tok)
					new_token.add_span(start_pos, end_pos)
					self.tokens.append(new_token)
					start_pos = end_pos +1
					end_pos+=1

		# add position of token in TU
		if len(self.tokens) > 0:
			self.tokens[0].position_in_tu = df.position.start
			self.tokens[-1].position_in_tu = df.position.end

		self.ntokens = len([x for x in self.tokens if x.token_type == df.tokentype.linguistic])

@dataclass
class transcript:
	tr_id: str
	speakers: Dict[str, int] = field(default_factory=lambda: {})
	tiers: Dict[str, bool] = field(default_factory=lambda: collections.defaultdict(bool))
	last_speaker_id: int = 0
	transcription_units_dict: Dict[str, transcription_unit] = field(default_factory=lambda: collections.defaultdict(list))
	transcription_units: List[transcription_unit] = field(default_factory=lambda: [])
	turns: List[turn] = field(default_factory=lambda: [])
	time_based_overlaps: Dict[str, Set[str]] = field(default_factory=lambda: {})
	statistics: pd.DataFrame = None

	def add(self, tu:transcription_unit):

		if not tu.speaker in self.speakers:
			self.speakers[tu.speaker] = 0

		if tu.include:
			self.speakers[tu.speaker] += 1

		self.transcription_units_dict[tu.tu_id] = tu
		# self.transcription_units.append(tu)


	def sort(self):
		self.transcription_units = sorted(self.transcription_units_dict.items(), key=lambda x: x[1].start)
		self.transcription_units = [y for x, y in self.transcription_units]


	def purge_speakers(self):
		speakers_to_remove = []
		for speaker in self.speakers:
			if self.speakers[speaker] == 0:
				speakers_to_remove.append(speaker)

		for speaker in speakers_to_remove:
			del self.speakers[speaker]


	def find_overlaps(self):

		for tu1 in self.transcription_units:
			for tu2 in self.transcription_units:
				if tu1.include and tu2.include and tu2.tu_id > tu1.tu_id:
					if not tu1.tu_id in self.time_based_overlaps:
						self.time_based_overlaps[tu1.tu_id] = set()
					if not tu2.tu_id in self.time_based_overlaps:
						self.time_based_overlaps[tu2.tu_id] = set()

					# De Morgan on tu1.end <= tu2.start or tu2.end <= tu1.start
					# the two units overlap in time
					if tu1.end > tu2.start and tu2.end > tu1.start:
						self.time_based_overlaps[tu1.tu_id].add(tu2.tu_id)
						self.time_based_overlaps[tu2.tu_id].add(tu1.tu_id)

		for tu_id in self.time_based_overlaps:
			self.time_based_overlaps[tu_id] = list(sorted(self.time_based_overlaps[tu_id],
											key=lambda x: self.transcription_units[x].start))

	def check_overlaps(self):

		for tu in self.transcription_units:

			n_textual_spans = len(tu.overlapping_spans)
			n_time_overlaps = len(self.time_based_overlaps[tu.tu_id])

			if n_textual_spans == n_time_overlaps:
				# easy case scenario
				tu.overlapping_spans = dict(zip([x for x, y in tu.overlapping_spans.items()],
												self.time_based_overlaps[tu.tu_id]))
				# print(self.time_based_overlaps[tu.tu_id])

				# input()
				# TODO: check boundaries of overlaping spans

			elif n_time_overlaps == 0:
			# 	# there's at least one parenthesis transcribed but no time-based span
				tu.errors["EXTRA_OVERLAPS"] = n_textual_spans

			elif n_textual_spans == 0:
				# there's at least one overlapping unit but no span transcribed
				tu.errors["UNCAUGHT_OVERLAPS"] = {}
				for overlapping_tu_id in self.time_based_overlaps[tu.tu_id]:
					overlapping_tu = self.transcription_units[overlapping_tu_id]

					min_end = min(tu.end, overlapping_tu.end)
					max_start = max(tu.start, overlapping_tu.start)

					# X ---xxxxxx
					# Y yyyyy----

					# X xxxxx-----
					# Y ---yyyyyyy

					# X ----xxx---
					# Y --yyyyyyy-

					# X --xxxxxxx-
					# Y ---yyyy---

					tu.errors["UNCAUGHT_OVERLAPS"][overlapping_tu_id] = min_end-max_start
			# 	# ? if the overlap is very very small, we should move boundaries

			else:

				speakers = [self.transcription_units_dict[id].speaker for id in self.time_based_overlaps[tu.tu_id]]
				n_unique_speakers = len(set(speakers))
				if n_unique_speakers == 1:
					ids = [id for id in self.time_based_overlaps[tu.tu_id]]
					for x in tu.overlapping_spans:
						tu.overlapping_spans[x] = "/".join(str(x) for x in ids)

					tu.errors["OVERLAP_NEEDS_SPLITTING"] = True

				else:
					tu.errors["MISMATCHING_OVERLAPS"] = True


	def create_turns(self):

		# calculate turns
		# SP1 : [(T1)-][--][--] ----- [(T3)]-[----]------
		# SP2 : .........      [(T2)  ]............

		prev_speaker = self.transcription_units[0].speaker
		curr_turn = turn(prev_speaker)
		curr_turn.add_tu(self.transcription_units[0].tu_id)
		curr_turn.set_start(self.transcription_units[0].start)
		curr_turn.set_end(self.transcription_units[0].end) # per ottenere anche la fine del primo turno, altrimenti in mancanza di questo ci restituisce solo lo start

		for tu in self.transcription_units[1:]:

			if tu.include:
				speaker = tu.speaker

				if speaker == prev_speaker:
					curr_turn.add_tu(tu.tu_id)
				else:
					self.turns.append(curr_turn)
					curr_turn = turn(tu.speaker)
					curr_turn.add_tu(tu.tu_id)
					curr_turn.set_start(tu.start)
					prev_speaker = speaker

				curr_turn.set_end(tu.end)

		self.turns.append(curr_turn)

	# Statistic calculations
	def get_stats (self):
		num_speakers = len(self.speakers) # number of speakers
		num_tu = len(self.transcription_units) # number of TUs
		num_total_tokens = sum(len(tu.tokens) for tu in self.transcription_units) # total number of tokens

		# average duration of TUs
		duration = [tu.duration for tu in self.transcription_units]
		average_duration = sum(duration)/num_tu

		# number of turns
		num_turns = len(self.turns)

		stats = {
			"num_speakers": num_speakers,
			"num_tu": num_tu,
			"num_total_tokens": num_total_tokens,
			"average_duration": average_duration,
			"num_turns": num_turns,
		}

		# ! removed the return and assigned result to a class parameter
		self.statistics = pd.DataFrame(stats.items(), columns=["Statistic", "Value"])
		# return df


	def to_csv(self, delimiter = "\t"):

		lines = []
		for tier in self.speakers:
			lines.append(f"# {tier}{delimiter}{tier}")

		lines.append("\n")

		for tu in self.transcription_units:
			elements = [tu.tu_id, tu.speaker, tu.include, len(tu.warnings), len(tu.errors),
						tu.start, tu.end, tu.duration, tu.orig_annotation, tu.annotation]
			elements_str = delimiter.join(str(x) for x in elements)
			lines.append(elements_str)

		return "\n".join(lines)

	def __iter__(self):
		for tu in self.transcription_units:
			yield tu