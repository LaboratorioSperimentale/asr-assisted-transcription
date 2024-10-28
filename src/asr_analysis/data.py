import collections
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class transcription_unit:
	tu_id : int
	speaker: str
	start: float
	end: float
	duration: float
	annotation: str
	orig_annotation: str = ""
	include: bool = True
	split: bool = False
	warnings: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
	errors: List[str] = field(default_factory=lambda: collections.defaultdict(int))
	parentheses: List[str] = field(default_factory=lambda: [])
	tokens: List[str] = field(default_factory=lambda: [])
	valid_tokens: List[bool] = field(default_factory=lambda: [])

	def __post_init__(self):
		self.start = float(self.start)
		self.end = float(self.end)
		self.duration = float(self.duration)

		jefferson_symbols = {"\.", ",", "\?", "~", "'", "-", "\[", "\]", "\(", "\)", ">", "<", "°"}

		self.orig_annotation = self.annotation

		# removing tabs
		new_string, subs_made = re.subn("\t", "", self.annotation)
		if subs_made > 0:
			self.warnings["SPACES_REMOVED"] += subs_made
			self.annotation = new_string

		# removing newlines
		new_string, subs_made = re.subn("\n", "", self.annotation)
		if subs_made > 0:
			self.warnings["SPACES_REMOVED"] += subs_made
			self.annotation = new_string

		# removing double spaces
		new_string, subs_made = re.subn("\s\s+", " ", self.annotation)
		if subs_made > 0:
			self.warnings["SPACES_REMOVED"] += subs_made
			# logging.info(f"TU n. {self.tu_id} - replaced {subs_made} multiple spaces in annotation")
			self.annotation = new_string

		for sym in jefferson_symbols:
			regex_str = f"^\s*{sym}\s*$"
			# print(re.compile(regex_str))
			# input()
			new_string, subs_made = re.subn(regex_str, "", self.annotation)
			if subs_made > 0:
				self.warnings["ONLY_CHAR"] += subs_made
				self.annotation = new_string

		self.annotation = self.annotation.strip()
		if len(self.annotation) == 0:
			self.include = False
			self.warnings["EMPTY_ANNOTATION"] += 1

	def check_normal_parentheses(self, open_char, close_char):
		is_open = False

		for char in self.annotation:
			if char == open_char:
				if is_open:
					self.errors["UNBALANCED_PARENTHESES"] += 1
					return
				else:
					is_open = True

			if char == close_char:
				if not is_open:
					self.errors["UNBALANCED_PARENTHESES"] += 1
					return
				else:
					is_open = False

		if is_open:
			self.errors["UNBALANCED_PARENTHESES"] += 1

	def check_angular_parentheses(self):
		openlist = {"left": False,
			 	"right": False}

		for char in self.annotation:
			if char == ">":
				if openlist["left"]:
					openlist["left"] = False
				elif not openlist["right"]:
					openlist["right"] = True

			if char == "<":
				if openlist["right"]:
					openlist["right"] = False
				elif not openlist["left"]:
					openlist["left"] = True

		if openlist["left"] or openlist["right"]:
			self.errors["UNBALANCED_PARENTHESES"] += 1


@dataclass
class transcript:
	tr_id: str
	speakers: Dict[str, int] = field(default_factory=lambda: {})
	tiers: Dict[str, bool] = field(default_factory=lambda: collections.defaultdict(bool))
	last_speaker_id: int = 0
	transcription_units: List[transcription_unit] = field(default_factory=lambda: [])
	overlaps: Dict[str, Set[str]] = field(default_factory=lambda: {})

	def add(self, tu:transcription_unit):

		if not tu.speaker in self.speakers:
			self.speakers[tu.speaker] = 0

		if tu.include:
			self.speakers[tu.speaker] += 1


		self.transcription_units.append(tu)

	def sort(self):
		self.transcription_units = sorted(self.transcription_units, key=lambda x: x.start)

	def purge_speakers(self):
		speakers_to_remove = []
		for speaker in self.speakers:
			if self.speakers[speaker] == 0:
				speakers_to_remove.append(speaker)

		for speaker in speakers_to_remove:
			del self.speakers[speaker]

	def check_parentheses(self):

		for annotation in self.transcription_units:
			annotation.check_normal_parentheses("(", ")")
			annotation.check_normal_parentheses("[", "]")
			annotation.check_angular_parentheses()

	def find_overlaps(self):

		for tu1 in self.transcription_units:
			for tu2 in self.transcription_units:
				if tu2.tu_id > tu1.tu_id:
					if not tu1.tu_id in self.overlaps:
						self.overlaps[tu1.tu_id] = set()
					if not tu2.tu_id in self.overlaps:
						self.overlaps[tu2.tu_id] = set()

					if tu1.end > tu2.start and tu2.end > tu1.start:  #De Morgan on tu1.end <= tu2.start or tu2.end <= tu1.start
						self.overlaps[tu1.tu_id].add(tu2.tu_id)
						self.overlaps[tu2.tu_id].add(tu1.tu_id)


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


def f():
	return 3