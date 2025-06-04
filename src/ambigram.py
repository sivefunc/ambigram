import cadquery as cq
from cadquery.vis import show

from utils import merge_strings
from _version import __version__

class Ambigram(object):
    assembly = None
    merged_string = None

    def __init__(self,
                 first_text: str,
                 second_text: str,
                 font_path: str = None,
                 ):

        self.first_text = first_text
        self.second_text = second_text
        self.font_path = font_path

        self.assembly = cq.Assembly()
        self.merged_string = merge_strings(self.first_text, self.second_text)

        location = (0, 0, 0)
        for (short_char, *long_chars) in self.merged_string:
            bb_int = None
            for long_char in long_chars:
                x, y, z = location

                xline = cq.Workplane("XZ").text(
                    short_char,
                    1,
                    1,
                    halign="left",
                    valign="bottom",
                    fontPath=self.font_path
                )

                yline = cq.Workplane("XZ").text(
                    long_char,
                    1,
                    1,
                    halign="left",
                    valign="bottom",
                    fontPath=self.font_path,
                ).rotate([0,0,0],[0,0,1], -90)

                bbx = xline.val().BoundingBox()
                bby = yline.val().BoundingBox()
                
                # Text() objects are away from origin (0, 0, 0) so we have to
                # do this weird trick of reversing their displacement.
                # translate(0,0,0) won't work (amazing I know)
                xline = xline.translate([-bbx.xmin,-bbx.ymin,-bbx.zmin])
                yline = yline.translate([-bby.xmin,-bby.ymin,-bby.zmin])

                intersection = xline.intersect(yline)
                bb_int = intersection.val().BoundingBox()

                location = x, y - bb_int.ylen, z
                intersection = intersection.translate(location)
                self.assembly.add(intersection)

            x, y, z = location
            location = x + bb_int.xlen, y, z

def main():
    ambigram = Ambigram(
        "HOLIWIS",
        "CAMIONX",
        font_path="/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Bold.ttf"
    )
    show(ambigram.assembly)

if __name__ == "__main__":
    main()
