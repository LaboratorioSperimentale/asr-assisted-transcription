import collections
from enum import Flag, auto
from dataclasses import dataclass, field
from typing import List, Dict, Set

import asr_analysis.process_text as pt

class intonation(Flag):
    ascending = auto()
    descending = auto()
    question = auto()

class position(Flag):
	tu_start = auto()
	tu_end = auto()
	tu_inner = auto()

@dataclass
class token:
	text: str
	intonation_pattern: intonation = None
	position_in_tu: position = position.tu_inner


@dataclass
class transcription_unit:
	tu_id : int
	speaker: str
	start: float
	end: float
	duration: float
	annotation: str
	dialect: bool = False
	orig_annotation: str = ""
	include: bool = True
	split: bool = False
	warnings: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
	errors: List[str] = field(default_factory=lambda: collections.defaultdict(int))
	parentheses: List[str] = field(default_factory=lambda: [])
	tokens: List[token] = field(default_factory=lambda: [])
	valid_tokens: List[bool] = field(default_factory=lambda: [])

	def __post_init__(self):
		self.start = float(self.start)
		self.end = float(self.end)
		self.duration = float(self.duration)

		self.orig_annotation = self.annotation

		# remove double spaces
		substitutions, new_transcription = pt.remove_spaces(self.annotation)
		self.warnings["SPACES"] = substitutions
		self.annotation = new_transcription

		new_transcription = pt.meta_tag(self.annotation)
		self.annotation = new_transcription

		if len(self.annotation) == 0:
			self.include = False

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
