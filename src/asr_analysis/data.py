import collections
import re
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

# Defining intonation patterns
# ! spostati nel file dataflags.py
# discendente = "discendente"
# ascendente = "ascendente"
# debolmente_ascendente = "debolmente ascendente"
# suono_prolungato = "suono prolungato"
# parola_interrotta = "parola interotta"
# error = "error" # problematic_punctuation_patterns

@dataclass
class token:
	text: str
	orig_text: str = ""
	intonation_pattern: df.intonation = None                     # ? do we want to add an intonation.normal case?
	position_in_tu: df.position = df.position.tu_inner
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

	def __post_init__(self):

		self.orig_text = self.text

		# STEP 1: check that token has shape ([a-z]+:*)+[-']?[.,?]
		# otherwise signal error
		matching_instance = re.fullmatch(r"([a-z]+:*)+[-']?[.,?]?", self.text) # TODO: update regex to also allow one-letter words

		if matching_instance is None:
			self.errors["TOKEN_FORMAT"] = 1
			# ! questo sostituisce il print
			# ! self.intonation_pattern = error
			# !	print(f"Intonation pattern problematico nel token: {self.text}")

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
			elif self.text.endswith("-"):
				self.interruption = True
				self.text = self.text[:-1]
			elif self.text.endswith("'"):
				self.truncation = True
				self.text = self.text[:-1]

			else:
				# STEP3: at this point we should be left with the bare word with only prolongations

				# replace multiple : with a single :
				new_text, substitutions = re.subn(r":{2,}", ":", self.text)
				if substitutions > 0:
					self.text = new_text
					self.warnings["PROLONGED_REPLACEMENTS"] = substitutions

				positions = [i for i, letter in enumerate(self.text) if letter==":"] # get positions of ":" in the string
				prev_letters = [self.text[i-1] for i in positions]

				self.prolongations = len(positions)
				self.prolonged_sounds = prev_letters

				# check for high volume
				if any(letter.isupper() for letter in self.text):
					self.volume = df.volume.high

				self.text = self.text.lower().strip(".,?-':")

# Function to determine the position of the token in the tu
# ! moved inside transcription unit methods
# ! (the transcription units knows about the position of its tokens)
# def token_position_in_tu(tokens):
# 	for i in tokens:
# 		if i == 0:
# 			token_position_in_tu = df.position.tu_start
# 		elif i == len(token_position_in_tu) -1:
# 			token_position_in_tu = df.position.tu_end
# 		else:
# 			token_position_in_tu = df.position.tu_inner


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
	overlaping_spans: List[str] = field(default_factory=lambda: [])
	warnings: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
	errors: List[str] = field(default_factory=lambda: collections.defaultdict(int))
	parentheses: List[Tuple[int, str]] = field(default_factory=lambda: [])
	tokens: List[token] = field(default_factory=lambda: [])
	valid_tokens: List[bool] = field(default_factory=lambda: [])

	def __post_init__(self):
		self.start = float(self.start)
		self.end = float(self.end)
		self.duration = float(self.duration)
		self.annotation = self.annotation.strip()
		self.orig_annotation = self.annotation

		#non jefferson
		substitutions, new_transcription = pt.clean_non_jefferson_symbols(self.annotation)
		self.warnings["NON_JEFFERSON"] = substitutions
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

		# spaces before and after parentheses
		substitutions, new_transcription = pt.check_spaces(self.annotation)
		self.warnings["UNEVEN_SPACES"] += substitutions
		self.annotation = new_transcription

		self.errors["BALANCED_DOTS"] = pt.check_even_dots(self.annotation)
		self.errors["BALANCED_OVERLAP"] = pt.check_normal_parentheses(self.annotation, "[", "]")
		# print(self.errors["BALANCED_OVERLAP"])
		# input()
		self.errors["BALANCED_GUESS"] = pt.check_normal_parentheses(self.annotation, "(", ")")
		self.errors["BALANCED_PACE"] = pt.check_angular_parentheses(self.annotation)
		self.errors["CONTAINS_NUMBERS"] = pt.check_numbers(self.annotation)

		# remove double spaces
		substitutions, new_transcription = pt.remove_spaces(self.annotation)
		self.warnings["SPACES"] = substitutions
		self.annotation = new_transcription

		# transform metalinguistic annotations and pauses
		new_transcription = pt.meta_tag(self.annotation)
		self.annotation = new_transcription

		# check how many overlapping spans have been transcribed
		if "[" in self.annotation or "]" in self.annotation:
			matches = re.findall(r"\[[^\]]+\]", self.annotation)
			if len(matches)>0:
				self.overlaping_spans = [(match, None) for match in matches]

		if len(self.annotation) == 0:
			self.include = False

	def strip_parentheses(self):
		new_string = ""

		for i, c in enumerate(self.annotation):
			if c in ["(", ")", "[", "]", ">", "<", "°"]:
				self.parentheses.append((i, c))
			else:
				new_string+=c

		self.annotation = new_string

	def tokenize(self):
		tokens = self.annotation.split(" ") # TODO: gestire caso di apostrofo tra articolo e parola e simili
		for tok in tokens:
			self.tokens.append(token(tok))

		# add position of token in TU
		self.tokens[0].position_in_tu = df.position.tu_start
		self.tokens[-1].position_in_tu = df.position.tu_end

	def __str__(self):

		ret_str = (f"# unit_id = {self.tu_id}\n"
			 		f"# speaker = {self.speaker}\n"
					f"# duration = {self.duration}\n"
					f"# annotation = {self.orig_annotation}\n"
					f"# text = {self.annotation}\n\n")

		for err_id, err_value in self.errors.items():

			if err_id == "UNCAUGHT_OVERLAPS":
				overlaps = "|".join(f"{x}={y:.3f}" for x, y in err_value.items())
				ret_str += f"# ERROR - {err_id} = {overlaps}\n"
			elif err_value:
				ret_str += f"# ERROR - {err_id}\n"

		for warn_id, warn_value in self.warnings.items():
			if warn_value > 0:
				ret_str += f"# WARNING - {warn_id} = {warn_value}\n"

		ret_str+="\n\n"

		return ret_str


	# start: float
	# end: float
	# duration: float
	# annotation: str
	# # TODO: handle dialect presence
	# # dialect: bool = False
	# orig_annotation: str = ""
	# include: bool = True
	# # split: bool = False
	# overlaping_spans: List[str] = field(default_factory=lambda: [])
	# warnings: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
	# errors: List[str] = field(default_factory=lambda: collections.defaultdict(int))
	# parentheses: List[Tuple[int, str]] = field(default_factory=lambda: [])
	# tokens: List[token] = field(default_factory=lambda: [])
	# valid_tokens: List[bool] = field(default_factory=lambda: [])


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

	def check_overlaps(self):

		for tu in self.transcription_units:
			if tu.include:
				textual_spans = len(tu.overlaping_spans)
				time_overlaps = len(self.time_based_overlaps[tu.tu_id])

				if textual_spans == time_overlaps:
					# easy case scenario
					tu.overlaping_spans = list(zip([x for x, y in tu.overlaping_spans], self.time_based_overlaps[tu.tu_id]))
					# TODO: check boundaries of overlaping spans

				elif time_overlaps == 0:
					# there's at least one parenthesis transcribed but no time-based span
					tu.errors["EXTRA_OVERLAPS"] = True

				elif textual_spans == 0:
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
					# ? maybe the overlap concerns metalinguistic annotation, can we add it automatically?
					# ? if the overlap is very very small, we should move boundaries

				else:
					# print(textual_spans, time_overlaps)
					# print([self.transcription_units[overlapping_tu_id] for overlapping_tu_id in self.time_based_overlaps[tu.tu_id]])
					tu.errors["MISMATCHING_OVERLAPS"] = True
					# print(tu)

					# input()


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
		num_total_tokens = sum(len(tu.tokens) for tu in transcript.transcription_units) # total number of tokens

		# average duration of TUs
		duration = [tu.duration for tu in transcript.transcription_units]
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


	def __str__(self):
		ret_str = f"# transcription_id = {self.tr_id}\n\n"

		# TODO: print stats

		for turn_id, turn in enumerate(self.turns):
			ret_str += f"# turn_id = {turn_id}\n"
			ret_str += f"# start = {turn.start}\n# end = {turn.end}\n\n"

			# !ISSUE: this way we are not printing empty units
			for tu_id in turn.transcription_units_ids:
				tu = self.transcription_units_dict[tu_id]
				ret_str += str(tu)
				# print(f"# unit_id = {tu_id}")

		return ret_str