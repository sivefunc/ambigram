import cadquery as cq
from cadquery.vis import show

from _version import __version__

class Ambigram(object):
    workplane = None
    def __init__(self, first_text: str, second_text: str):
        pass

def main():
    show(cq.Workplane("XY").text(f"{__version__}", 10, 2))

if __name__ == "__main__":
    main()
