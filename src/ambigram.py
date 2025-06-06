import cadquery as cq
from cadquery.vis import show

from utils import merge_strings
from _version import __version__

class Ambigram(object):
    """3D Ambigram Generation using CadQuery

    A 3D Ambigram is a optical illusion where two texts gets merged
    and depending of the perspective one text appears and the other
    don't.

    Attributes
    ----------
    assembly : None | cadquery.Assembly
               3D Ambigram of Two Strings

    merged_string : None | list[list[str]]
                    The merged string that was used to create the ambigram

    See Also
    --------
    utils.merge_strings : Function that merges two strings
    """

    assembly = None
    merged_string = None
    base = None
    max_column = [0, 0, 0]
    
    def __init__(self,
                 first_text: str,
                 second_text: str,
                 font_size: int = 16,
                 letter_spacing: int = None,
                 font_path: str = None,
                 ):
        """Creates the 3D Ambigram in a Cadquery Assembly Object

        2D View of an Ambigram:
        first_text: VERYLONG
        second_text: SHORT

        y(+)
        ._______x(+)
        | V
        | E
        | S
        |  R
        |  Y
        |  H
        |   L
        |   O
        |   O
        |    N
        |    R
        |     G
        |     T
        y(-)

        Parameters
        ----------
        first_text : str
                     Non-empty unsorted string.

        second_text : str
                      Non-empty unsorted string.

        font_path : str, optional
                    Path to the font that the text is going to use

        Notes
        -----
        The Ambigram has two perspectives the Positive X Line and the
        Negative Y Line, each one displays a different string.

        The Algorithms works by intersecting a pair of letters at a time
        and placing them at the assembly instead of placing all letters and
        then intersecting at once.

        The Insersectiong of a Pair of Letters is by rotating 90 deg a
        letter in the Z direction and then extruding both letters.

        See Also
        --------
        utils.merge_strings : Function that merges two strings

        """

        self.first_text = first_text
        self.second_text = second_text
        self.font_size = font_size
        self.font_path = font_path

        self.letter_spacing = letter_spacing
        if letter_spacing is None:
            self.letter_spacing = self.font_size / 16

        self.assembly = cq.Assembly(loc=cq.Location(0,0,0))
        self.merged_string = merge_strings(self.first_text, self.second_text)

        location = (0, 0, 0)
        for (short_char, *long_chars) in self.merged_string:
            bb_int = None
            current_column = [0, 0, 0] 
            # Intersect each pair of letters
            for long_char in long_chars:
                x, y, z = location

                # Letter that will be visible in the Positive X Line
                xline = cq.Workplane("XZ").text(
                    txt=short_char,
                    fontsize=self.font_size,
                    distance=self.font_size,
                    halign="left",
                    valign="bottom",
                    fontPath=self.font_path
                )

                # Letter that will be visible in the Negative Y Line
                yline = cq.Workplane("XZ").text(
                    txt=long_char,
                    fontsize=self.font_size,
                    distance=self.font_size,
                    halign="left",
                    valign="bottom",
                    fontPath=self.font_path,
                ).rotate([0,0,0],[0,0,1], 90)

                # All Intersections are done at [0, 0, 0] then are translated
                # to their corresponding position, forming a diagonal.
                # y(+)
                # |
                # |
                # |
                # |_______ x(+)
                # 0

                # Bounding Box
                bbx = xline.val().BoundingBox()
                bby = yline.val().BoundingBox()

                # Text() objects are away from origin (0, 0, 0) so we have to
                # do this weird trick of reversing their displacement.
                # translate(0,0,0) won't work (amazing I know)
                xline = xline.translate([-bbx.xmin,-bbx.ymin,-bbx.zmin])
                yline = yline.translate([-bby.xmin,-bby.ymin,-bby.zmin])
                
                intersection = xline.intersect(yline)

                bb_int = intersection.val().BoundingBox()

                intersection = intersection.translate(location)
                location = x, y + bb_int.ylen + self.letter_spacing, z

                self.assembly = self.assembly.add(intersection)

                current_column[0] = max(current_column[0], bb_int.xlen)
                current_column[1] += bb_int.ylen + self.letter_spacing
                current_column[2] = max(current_column[2], bb_int.zlen)

            x, y, z = location
            location = x + bb_int.xlen + self.letter_spacing, y, z

            self.max_column = list(map(max, zip(self.max_column,
                                                current_column)))

    def add_base(self, height: int):
        bb = self.assembly.toCompound().BoundingBox()
        self.base = (cq.Workplane("XY").polyline([
            [bb.xmin + self.max_column[0], bb.ymin],
            [bb.xmin, bb.ymin],
            [bb.xmin, bb.ymin + self.max_column[1]],

            [bb.xmax - self.max_column[0], bb.ymax],
            [bb.xmax, bb.ymax],
            [bb.xmax, bb.ymax - self.max_column[1]]
            ])
            .close()
            .extrude(height)
            .translate([bb.xmin, bb.ymin, bb.zmin - height])
        )
        self.assembly = self.assembly.add(self.base)
        return self

def main():
    ambigram = Ambigram(
        "AAAAA",
        "AAAAA",
        font_path="/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Bold.ttf"
    )

    show(ambigram.add_base(height=ambigram.font_size / 10).assembly)

if __name__ == "__main__":
    main()
