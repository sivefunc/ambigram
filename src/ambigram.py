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
            for long_char in long_chars:
                x, y, z = location

                letter_in_xline = cq.Workplane("XZ").text(
                    short_char,
                    1,
                    2,
                    halign="left",
                    valign="bottom",
                    fontPath="/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Bold.ttf"
                )

                letter_in_yline = cq.Workplane("XZ").text(
                    long_char,
                    1,
                    2,
                    halign="left",
                    valign="bottom",
                    fontPath="/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Bold.ttf"

                ).rotate([0, 0, 0], [0, 0, 1], -90)

                bbox_xline = letter_in_xline.val().BoundingBox()
                bbox_yline = letter_in_yline.val().BoundingBox()

                letter_in_xline = letter_in_xline.translate([
                    x - bbox_xline.xmin,
                    y - bbox_xline.ymin,
                    z - bbox_xline.zmin,
                ])

                letter_in_yline = letter_in_yline.translate([
                    x - bbox_yline.xmin,
                    y - bbox_yline.ymin,
                    z - bbox_yline.zmin,
                ])

                intersection = letter_in_xline.intersect(letter_in_yline)
                self.assembly.add(intersection)

                bbox = intersection.val().BoundingBox()
                location = x, y - bbox.ylen, z
            x, y, z = location
            location = x + bbox.xlen, y, z

def main():
    ambigram = Ambigram("RECURSIVE", "FUNCTION")
    show(ambigram.assembly)

if __name__ == "__main__":
    main()
