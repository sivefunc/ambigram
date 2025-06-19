from ._version import __version__

from .ambigram import Ambigram
from .utils import merge_strings

__all__ = [
    "merge_strings",
    "Ambigram",
]
