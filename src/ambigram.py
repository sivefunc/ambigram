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

    max_column : list[float, float, float]
                 Dimensions of the possible maximum column, what this
                 mean is that each component (Xlen, Ylen and Zlen) are
                 independent so that each one could come from a different
                 column.

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

        The placement of letter is diagonally, but if one string is shorter
        than the other, the long string chars are placed behind the
        shortest.

        2D View of an Ambigram:
        first_text: VERYLONG
        second_text: SHORT

        y(+)
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
        ._______x(+)

        Parameters
        ----------
        first_text : str
                     Non-empty unsorted string without leading nor trailing
                     chars.

        second_text : str
                      Non-empty unsorted string without leading nor
                      trailing chars.

        font_size : int, default=16
                    The height of the letters in the Z direction.

        font_path : str, optional
                    Path to the font that the text is going to use

        letter_spacing : int, default=font_size / 16
                         The space between letters.
        Notes
        -----
        The Ambigram has two perspectives the Positive X Line and the
        Positive Y Line, each one displays a different string.

        The Algorithms works by intersecting a pair of letters at a time
        and placing them at the assembly instead of placing all letters and
        then intersecting at once.

        The Insersectiong of a Pair of Letters is by rotating 90 deg a
        letter in the Z direction and then extruding both letters.

        Font Sizes are a weird thing that I don't understand, so I'm going
        to place this:

        `StackOverflow<https://stackoverflow.com/questions/3495872/how-is-font-size-calculated
>`_
        See Also
        --------
        utils.merge_strings : Function that is used to create the 2D view
                              of the Ambigram.
        """

        self.first_text = first_text
        self.second_text = second_text
        self.font_size = font_size
        self.font_path = font_path

        self.letter_spacing = letter_spacing
        if letter_spacing is None:
            self.letter_spacing = self.font_size / 16

        self.assembly = cq.Assembly(loc=cq.Location(0,0,0), name="root")

        # 2D View of the Ambigram
        self.merged_string = merge_strings(self.first_text,
                                           self.second_text,
                                           ignore_delimiter=True,
                                           allow_delimiter_column=False,
                                           delimiter=" ")

        if (' ' in first_text or ' ' in second_text):
            bb_whitespace = self.intersect_letters('A','A').val().BoundingBox()

        location = (0, 0, 0)
        for (short_char, *long_chars) in self.merged_string:
            bb_int = None

            # Dimensions of the current column
            current_column = [0, 0, 0] 

            # Intersect each pair of letters
            for long_char in long_chars:
                x, y, z = location

                # A intersection of a whitespace with a letter does not exist
                # Just move
                if long_char == " ":
                    bb_int = bb_whitespace

                else:
                    intersection = self.intersect_letters(short_char,
                                                          long_char)
                    bb_int = intersection.val().BoundingBox()
                    intersection = intersection.translate(location)
                    self.assembly = self.assembly.add(intersection)

                location = x, y + bb_int.ylen + self.letter_spacing, z

                # Dimensions of the current column
                current_column[0] = max(current_column[0], bb_int.xlen)
                current_column[1] += bb_int.ylen + self.letter_spacing
                current_column[2] = max(current_column[2], bb_int.zlen)

            if short_char == " ":
                bb_int = bb_whitespace

            x, y, z = location
            location = (
                x + bb_int.xlen + self.letter_spacing,
                y + (bb_int.ylen if short_char == " " and long_chars else 0),
                z)

            # For each component [X, Y, Z] choose the maximum length.
            self.max_column = list(map(max, zip(self.max_column,
                                                current_column)))

    def intersect_letters(self, short_char, long_char):
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
        return intersection

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
        self.assembly = self.assembly.add(self.base, name="base")
        return self


    def add_letter_support(self,
                           letter_id: str,
                           cylinder_height: int = None,
                           cylinder_radius: int = None,
                           square_height: int = None):

        letter = self.assembly.objects[letter_id].toCompound().BoundingBox()
        cylinder_support = (
            cq.Workplane("XY")
            .cylinder(cylinder_height, cylinder_radius, centered=[
                True, True, False
            ])
            .translate([
                letter.center.x,
                letter.center.y,
                letter.zmin - cylinder_height - (
                    0 if square_height is None else square_height 
                )
            ])
            if None not in [cylinder_radius, cylinder_height] else None
        )

        rectangle_support = (
            cq.Workplane("XY")
            .box(letter.xlen, letter.ylen, square_height, centered=False)
            .translate([
                letter.xmin,
                letter.ymin,
                letter.zmin - square_height
            ])
            if square_height is not None else None
        )

        if None not in [cylinder_support, rectangle_support]:
            support_base = rectangle_support.union(cylinder_support)

        elif cylinder_support is not None:
            support_base = cylinder_support

        else:
            support_base = rectangle_support

        self.assembly = self.assembly.add(support_base)
        return self
    
    def add_letter_support_to_all(self,
                                  cylinder_height: int = None,
                                  cylinder_radius: int = None,
                                  square_height: int = None
                                  ):
        for letter_id in list(self.assembly.objects.keys()):
            if letter_id in ['root', 'base', 'blank_space']:
                continue

            self.add_letter_support(letter_id,
                                    cylinder_height,
                                    cylinder_radius,
                                    square_height)
        return self

def main():
    ambigram = Ambigram(
        #"AAAAAAAA",
        #"F F F",
        #"FFFF FFF FFFFF FFF",
        #"AA AAAAAA AAA",
        #"FFFFFFFFFFFFFFF",
        #"AAAAAAAAAAA",
        #"F   FF",
        #"AA",
        #"FFFF",
        #"AAAA",
        #"FFFFFFFF" * 3,
        #"AAAAAAAA",
        "FFF" * 2 + "FF",
        "AAA",
        font_path="/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Bold.ttf",
    )
    
    ambigram = ambigram.add_letter_support_to_all(
        cylinder_height=ambigram.font_size / 4,
        cylinder_radius=ambigram.font_size / 4,
        square_height=ambigram.font_size / 16,
    )

    ambigram = ambigram.add_base(height=ambigram.font_size / 10).assembly

    show(ambigram)
if __name__ == "__main__":
    main()
