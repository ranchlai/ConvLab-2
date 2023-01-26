# -*- coding: utf-8 -*-
import os
from os.path import abspath, dirname

from convlab2.dialog_agent import (
    Agent,
    BiSession,
    DealornotSession,
    PipelineAgent,
    Session,
)
from convlab2.dst import DST
from convlab2.nlg import NLG
from convlab2.nlu import NLU
from convlab2.policy import Policy


def get_root_path():
    return dirname(dirname(abspath(__file__)))


DATA_ROOT = os.path.join(get_root_path(), "data")
