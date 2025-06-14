""" 3D Ambigram Generation using CadQuery """
from typing import Self

import cadquery as cq
from cadquery.vis import show

from utils import merge_strings
from _version import __version__

class Ambigram:
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
                 font_size: float = 16,
                 letter_spacing: float = None,
                 font_path: str = None,
                 ):
        """Creates the 3D Ambigram in a Cadquery Assembly Object

        The placement of letter is diagonally, but if one string is shorter
        than the other, the long string chars are placed behind the
        shortest.

        2D View of an Ambigram:
        first_text: VERYLONG
        second_text: SHORT

        merged_string = VRL
                        EYONG
                        SHORT
        y(+)
        |     G
        |     T
        |    N
        |    R
        |   O
        |   L
        |   O 
        |  Y
        |  R  
        |  H   
        | E   
        | V    
        | S    
        ._______x(+)

        Parameters
        ----------
        first_text : str
                     Non-empty unsorted string without leading nor trailing
                     chars.

        second_text : str
                      Non-empty unsorted string without leading nor
                      trailing chars.

        font_size : float, default=16
                    The height of the letters in the Z direction.

        font_path : str, optional
                    Path to the font that the text is going to use

        letter_spacing : float, default=font_size / 16
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

        `StackOverflow<https://stackoverflow.com/questions/3495872/how-is-font-size-calculated>`_

        Whitespaces are allowed between letters, but there are still edge
        cases to cover.
        
        See Also
        --------
        utils.merge_strings : Function that is used to create the 2D view
                              of the Ambigram and is used to make it 3D.
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

        # X, Y and Z Location of the current Letter that will placed
        # and will grow +X and +Y
        location = [0.0, 0.0, 0.0]
        idx = 0
        for (short_char, *long_chars) in self.merged_string:
            bb_int = None

            # Dimensions of the current column
            current_column = [0, 0, 0]

            # Intersect each pair of letters
            # It's possible to not have long_chars, that is when
            # the short character has a whitespace.
            for long_char in long_chars:
                # A intersection of a whitespace with a letter does not exist
                # Just move
                if long_char == " ":
                    bb_int = bb_whitespace

                else:
                    intersection = self.intersect_letters(short_char,
                                                          long_char)
                    bb_int = intersection.val().BoundingBox()
                    intersection = intersection.translate(location)
                    self.assembly = self.assembly.add(
                        intersection,
                        name=str(idx)
                    )

                location[1] += bb_int.ylen + self.letter_spacing

                # Dimensions of the current column
                current_column[0] = max(current_column[0], bb_int.xlen)
                current_column[1] += bb_int.ylen + self.letter_spacing
                current_column[2] = max(current_column[2], bb_int.zlen)

                idx += 1

            if short_char == " ":
                bb_int = bb_whitespace

            location[0] += bb_int.xlen + self.letter_spacing
            if short_char == " " and long_chars:
                location[1] += bb_int.ylen

            # For each component [X, Y, Z] choose the maximum length.
            self.max_column = list(map(max, zip(self.max_column,
                                                current_column)))

    def intersect_letters(
        self,
        short_char: str,
        long_char: str,
    ) -> cq.Workplane:
        """ Intersect the short char and the long char

        Parameters
        ----------
        short_char : str
                    Letter visible at the Positive X Line

        long_char : str
                    Letter visible at the Positive Y Line
        
        Returns
        -------
        intersection : cq.Workplane

        Notes
        -----
        The long char will be rotated 90 degrees.

        The reason this works to create two perspectives is due
        to the intersection seletings the 3D points that only belongs
        to both, so if you in a Letter you won't see the other letter.
        """
        # Letter that will be visible in the Positive X Line
        xline = cq.Workplane("XZ").text(
            txt=short_char,
            fontsize=self.font_size,
            distance=self.font_size,
            halign="left",
            valign="bottom",
            fontPath=self.font_path
        )

        # Letter that will be visible in the Positive Y Line
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

    def add_base_rectangle(self, height: float, padding: float = 0.0) -> Self:
        """Rectangle base that goes from Xmin, Ymin to Xmax, Ymax

        Parameters
        ----------
        height : float
                 Rectangle extrude height at the Z Direction.

        padding : float, optional
                  Space added to the border at the X and Y direction.

        Returns
        -------
        self : Ambigram
               The object returns itself for method chaining.

        Notes
        -----
                  Padding(+)       Padding(+)
        Padding(-)+-------------------------+ Padding(+)
                  |              Ymax       |
                  |      #-----------+ Xmax |
                  |      |           |      |
                  |      |           |      |
                  |      |           |      |
                  |      |           |      |
                  |      |           |      |
                  | Ymin +-----------#      |
                  |     Xmin                |
        Padding(-)+-------------------------+ Padding(+)
                  Padding(-)       Padding(-)
        """

        bb = self.assembly.toCompound().BoundingBox()
        self.base = (cq.Workplane("XY").polyline([
            [bb.xmin - padding, bb.ymin - padding], # Bottom Left Corner
            [bb.xmin - padding, bb.ymax + padding], # Top Left Corner
            [bb.xmax + padding, bb.ymax + padding], # Top Right Corner
            [bb.xmax + padding, bb.ymin - padding], # Bottom Right Corner
            ])
            .close()
            .extrude(height)
            .translate([bb.xmin, bb.ymin, bb.zmin - height])
        )
        self.assembly = self.assembly.add(self.base, name="base")
        return self

    def add_base_p2p(self, height: float, padding: float = 0.0):
        """ Base that goes from Xmin, Ymin to Xmax, Ymax

        Parameters
        ----------
        height : float
                 Rectangle extrude height at the Z Direction.

        padding : float, optional
                  Space added to the border at the X and Y direction.

        Returns
        -------
        self : Ambigram
               The object returns itself for method chaining.

        Notes
        -----
        The base is a closed polygon made of points which is done in the
        following five steps:

        1. Start at the bottom left corner (Xmin, Ymax)

        2. for each letter (bottom to top and left to right)
            Connect the coordinate (Xmin, Ymax) from the current letter to
            the last point.

            (Xmin, Ymax) is the Top left corner.

        3. You are currently at the last letter (Xmin, Ymax) move now to
            (Xmax, Ymax) this is also the top right corner of the assembly.

        4. for each letter (top to bottom, right to left)
            Connect the coordinate (Xmax, Ymin) from the current letter to
            the last point.

            (Xmax, Ymin) is the Bottom right corner.

        5. You are currently at the last letter (Xmax, Ymin) move now to
            (Xmax, Ymax) this is also the bottom left corner of the
            assembly.
           
                +--+
              / |  |
             /  |  |
            /   +--+
            +--+   /
          / |  |  /
         /  |  | /
        /   +--+
        +--+   /
        |  |  /
        |  | /
        +--+

        See Also
        --------
        Ambigram.add_base_rectangle: To visually understand how padding
                                      is added
        """
        base_points = []
        bb = self.assembly.toCompound().BoundingBox()

        # Remove anything but letters.
        letters = sorted(filter(
            lambda letter_name:
                letter_name not in ['root', 'base']
                    and 'support' not in letter_name,
            self.assembly.objects.keys()
        ), key=lambda letter_name: int(letter_name))

        # Start at the bottom left corner
        base_points.append([bb.xmin - padding, bb.ymin - padding])

        # Go from bottom to top and then left to right
        for letter_name in letters:
            letter = self.assembly.objects[letter_name]
            letter = letter.toCompound().BoundingBox()
            base_points.append([letter.xmin - padding, letter.ymax + padding])

        # Start at the top right corner
        base_points.append([bb.xmax + padding, bb.ymax + padding])

        # Go from top to bottom and then right to left
        for letter_name in reversed(letters):
            letter = self.assembly.objects[letter_name]
            letter = letter.toCompound().BoundingBox()
            base_points.append([letter.xmax + padding, letter.ymin - padding])

        self.base = (cq.Workplane("XY")
                     .polyline(base_points)
                     .close()
                     .extrude(height)
                     .translate([bb.xmin, bb.ymin, bb.zmin - height])
                     )
        self.assembly = self.assembly.add(self.base, name="base")
        return self

    def add_letter_support(
        self,
        letter_name: str,
        cylinder_height: float = None,
        cylinder_radius: float = None,
        rect_height: float = None
    ) -> Self:
        """Add a Letter Support to a letter in an assembly

        The letter sits ontop of a support that consists of a cylinder
        and a rectangle where the rectangle sits ontop of the cylinder.

        Parameters
        ----------
        letter_name : str
                      Unique Identifier of the Letter Object added to the
                      self.assembly.

        cylinder_height : float, optional
                          Cylinder extrude height at the Z direction.

        cylinder_radius : float, optional
                          Cylinder radius at the X and Y direction.

        rect_height     : float, optional
                          Rectangle extrude height at the Z direction.

        Returns
        -------
        self : Ambigram
               The object returns itself for method chaining.

        Notes
        -----
        It's not necessary to have both the cylinder and rectangle, you
        could have a cylinder without the rectangle sitting ontop of it.
        """
        if cylinder_height == cylinder_radius == rect_height == None:
            raise ValueError("Neither the Cylinder nor rect. were provided.")

        if rect_height is None and None in [cylinder_height, cylinder_radius]:
            raise ValueError("Cylinder needs both a height and a radius.")

        # Dimensions and Position of the Letter
        letter = self.assembly.objects[letter_name].toCompound().BoundingBox()
        rectangle_support = (cq.Workplane("XY")
            .box(letter.xlen, letter.ylen, rect_height, centered=False)
            .translate([
                letter.xmin,
                letter.ymin,
                letter.zmin - rect_height
            ])
            if rect_height is not None else None
        )
        cylinder_support = (
            cq.Workplane("XY")
            .cylinder(cylinder_height, cylinder_radius, centered=[
                True, True, False
            ])
            .translate([
                letter.center.x,
                letter.center.y,
                letter.zmin - cylinder_height - (
                    # Place it under the rectangle if exists
                    0 if rect_height is None else rect_height
                )
            ])
            if None not in [cylinder_radius, cylinder_height] else None
        )

        # Both supports were created
        if None not in [cylinder_support, rectangle_support]:
            support_base = rectangle_support.union(cylinder_support)

        # Only cylinder support was created
        elif cylinder_support is not None:
            support_base = cylinder_support

        # Only rectangle support was created
        else:
            support_base = rectangle_support

        self.assembly = self.assembly.add(
            support_base,
            name=f"support-{letter_name}"
        )

        return self

    def add_letter_support_to_all(
        self,
        cylinder_height: float = None,
        cylinder_radius: float = None,
        rect_height: float = None
    ) -> Self:
        """ Add a Letter Support to each letter in the whole Assembly

        Parameters
        ----------
        cylinder_height : float, optional
                          Cylinder extrude height at the Z direction.

        cylinder_radius : float, optional
                          Cylinder radius at the X and Y direction.

        rect_height     : float, optional
                          Rectangle extrude height at the Z direction.

        Returns
        -------
        self : Ambigram
               The object returns itself for method chaining.

        Notes
        -----
        Whitespaces, Root and Base are ignored.

        It's not necessary to have both the cylinder and rectangle, you
        could have a cylinder without the rectangle sitting ontop of it.

        See Also
        --------
        Ambigram.add_letter_support : Ambigram Method to add a support to
                                      a single object.
        """
        for letter_name in list(self.assembly.objects.keys()):
            # Whitespaces are also ignored because they are not objects
            # added in self.assembly.
            if letter_name in ['root', 'base']:
                continue

            self.add_letter_support(
                letter_name,
                cylinder_height,
                cylinder_radius,
                rect_height
            )
        return self

def main():
    """ Example Program """
    ambigram = Ambigram(
        #"AAA",
        #"FFF",
        #"AAAAAAAA",
        #"F F F",
        #"FFFF FFF FFFFF FFF",
        #"AA AAAAAA AAA",
        #"FFFFFFFFFFFFFFF",
        #"AAAAAAAAAAA",
        #"AAAAA",
        #"FFF",
        #"F   FF",
        #"AA",
        #"FFFF",
        #"AAAA",
        #"FFFFFFFF" * 3,
        #"AAAAAAAA",
        #"FFF" * 2 + "FF",
        #"AAA",
        "AMBIGRAM",
        "CADQUERY",
        font_path="/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Bold.ttf",
    )
    ambigram = ambigram.add_letter_support_to_all(
        cylinder_height=ambigram.font_size / 4.0,
        cylinder_radius=ambigram.font_size / 4.0,
        rect_height=ambigram.font_size / 16.0,
    )

    ambigram = ambigram.add_base_p2p(
        height=ambigram.font_size / 10.0,
        padding=ambigram.font_size / 10.0,
    )
    show(ambigram.assembly)

if __name__ == "__main__":
    main()
