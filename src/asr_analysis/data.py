import collections
from enum import Flag, auto
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple


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
        tokens = self.annotation.split(" ")
        for tok in tokens:
            self.tokens.append(token(tok))
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

   # some calculations

    import statistics #imported for statistics.mean
    import pandas as pd 

    def get_stats (self):
        num_speakers = len(self.speakers) # calculate how many speakers
        num_tu = len(self.transcription_units) # calculate how many TUs
        num_total_tokens = sum(len(tu.tokens) for tu in transcript.transcription_units)

    # average duration of TUs
        duration = [tu.duration for tu in transcript.transcription_units]
       # average_duration = statistics.mean(duration) 
    
    # calculate turns 
       # num_turns
    
    # creating a df with pandas

        stats = {
            "num_speakers": num_speakers,
            "num_tu": num_tu,
            "num_total_tokens": num_total_tokens,
            "average_duration": average_duration,
            "num_turns": num_turns
        }
        
        df = pd.DataFrame(stats.items()), columns=["statistic", "value"]
        


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

    def __iter__(self):
        for tu in self.transcription_units:
            yield tu
