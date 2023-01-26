# -*- coding: utf-8 -*-
from typing import Dict, List, NewType, TypeVar, Union

SampleType = TypeVar("SampleType")

StringType = str
WordType = TokenType = NewType("TokenType", str)
TokenListType = WordListType = List[TokenType]
SentenceType = Union[StringType, TokenListType]
MultiwozSampleType = Dict[str, Union[None, list, dict]]
MultiwozDatasetType = Dict[str, MultiwozSampleType]
