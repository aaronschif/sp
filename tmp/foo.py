from enum import Enum
from blist import blist
from pprint import pformat
import pickle


class DocPartsEnum(object):
    H1 = 0
    H2 = 1
    H3 = 2
    H4 = 3
    H5 = 4
    H6 = 5
    P = 6


class Document(object):
    def __init__(self):
        self.parts = blist()

    def __str__(self):
        return pformat(self.parts)

    def as_text(self):
        return pickle.dumps(self.parts)

    def from_text(self, text):
        self.parts = pickle.loads(text)
