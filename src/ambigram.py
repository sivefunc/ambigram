import cadquery as cq
from cadquery.vis import show

from utils import merge_strings
from _version import __version__

class Ambigram(object):
    assembly = None
    merged_string = None

    def __init__(self, first_text: str, second_text: str):
        self.assembly = cq.Assembly()
        self.merged_string = merge_strings(first_text, second_text)

        location = (0, 0, 0)
        for (short_char, *long_chars) in self.merged_string:
            bbox = None
            for char in long_chars + [short_char]:
                x, y, z = location

                letter = cq.Workplane("XZ").text(
                    char,
                    1,
                    0.5,
                    halign="left",
                    valign="bottom"
                )

                bbox = letter.val().BoundingBox()

                self.assembly.add(
                    letter,
                    loc=cq.Location(*[
                        x - bbox.xmin,
                        y - bbox.ymin,
                        z - bbox.zmin
                    ])
                )

                location = x, y - bbox.ylen, z

            x, y, z = location
            location = x + bbox.xlen, y, z

def main():
    ambigram = Ambigram("recursive", "function")
    show(ambigram.assembly)

if __name__ == "__main__":
    main()
