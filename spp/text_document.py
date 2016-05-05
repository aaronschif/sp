from enum import Enum
from blist import blist
from pprint import pformat
import pickle


class DocPartsEnum(object):
    H1 = (0, 0)
    H2 = (0, 1)
    H3 = (0, 2)
    H4 = (0, 3)
    H5 = (0, 4)
    H6 = (0, 5)
    P = (1, 6)
    BK = (1, 7)


class Document(object):
    def __init__(self):
        self.parts = blist()

    def __str__(self):
        return pformat(self.parts)

    def as_text(self):
        return pickle.dumps(self.parts)

    def from_text(self, text):
        self.parts = pickle.loads(text)

    def as_tree(self):
        root = []
        current_level = (DocPartsEnum.H1, [])
        # for kind, text in self.parts:
        #     nestable, rank = kind
        #     if nestable:
        #         if rank > current_level[0]:

        



parts = [
    (DocPartsEnum.H1, "asdf"),
    (DocPartsEnum.H2, "2345")
]

parts = [
    ("asdf", [
        ("2345", [

        ])
    ])
]
