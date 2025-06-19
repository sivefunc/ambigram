"""Utility functions used for Ambigram creation."""
def merge_strings(
    string1: str,
    string2: str,
    ignore_delimiter: bool = False,
    delimiter: str = ' ',
    allow_delimiter_column: bool = False,
    ) -> list[list[str]]:
    """ Place longest string chars behind the shortest string

    Two non-empty unsorted strings gets sorted (by length) and the
    longest gets merged into the shortest one by placing their chars
    behind in a secuential and equally distributed way.

    Think of it like adding blocks to each column until all columns
    are equal.

    Parameters
    ----------
    string1 : str
              Non-empty unsorted string.

    string2 : str
              Non-empty unsorted string.
    
    ignore_delimiter : bool, default=False
                       Determines whether or not to place the longest
                       string characters into the delimiters of the
                       shortest word.

                       If True, the leading and trailing delimiter
                       chars in the strings must be removed.

    delimiter : str, default=' '
                The character that should be ignored and no characters
                must be placed behind of it.

    allow_delimiter_column : bool, default=False
                             Determines whether or not a short character
                             != delimiter could have a column of chars
                             behind that are only equal to delimiter.

                             If false then long chars of the columns that
                             are before the shortest word will be 
                             moving until the column has atleast one
                             char != delimiter.

    Returns
    -------
    values : list[list[str]]
             List of List[str] where each List[str] represents 
             the shortest letter (in position) and then
             the longest characters (in order)
    Notes
    -----
    Secuential direction is left to right.

    Equal distribution is by placing Floor(Long / Short)
    chars secuentially behind shortest string, in the first
    Long % Short Columns take one more character. 

    Take for instance the following:

        String1 (Lenght 19): HIJKLMNOPQRSTUVWXYZ
        String2 (Lenght 07): ABCDEFG

        Place Floor(19/7) = 2 chars per each letter in shortest string,
        during the first (19 % 7) = 5 rows take one more character.

        HKNQT
        ILORUWY
        JMPSVXZ
        ABCDEFG

    Why it Works?
        Long / Short is a rational number that indicates
        splitting the longest word into Short Sections.

        We take Floor(Long/Short) because there are no
        rational characters, we need integers to be exact.

        Obviously a remainder now exist (Long % Short) <= Short
        so these characters must be placed in the first 
        (Long % Short) columns.

        Floor(Long / Short) * Short + (Long % Short) = Long

    Examples
    --------
    Shortest is "Function" and Longest is "Recursive"
    >>> merge_strings("function", "recursive")
    ... # doctest: +NORMALIZE_WHITESPACE
    [['f', 'r', 'e'],
     ['u', 'c'],
     ['n', 'u'],
     ['c', 'r'],
     ['t', 's'],
     ['i', 'i'],
     ['o', 'v'],
     ['n', 'e']]
    
    Shortest is "ABCDEFG" and Longest is "HIJKLMNOPQRSTUVWXYZ"
    >>> merge_strings("ABCDEFG", "HIJKLMNOPQRSTUVWXYZ")
    ... # doctest: +NORMALIZE_WHITESPACE
    [['A', 'H', 'I', 'J'],
     ['B', 'K', 'L', 'M'],
     ['C', 'N', 'O', 'P'],
     ['D', 'Q', 'R', 'S'],
     ['E', 'T', 'U', 'V'],
     ['F', 'W', 'X'],
     ['G', 'Y', 'Z']]
    """
    # Do not allow leading nor Trailling Delimiter Characters
    if (ignore_delimiter
            and delimiter in (string1[0]
                              + string1[-1]
                              + string2[0]
                              + string2[-1])):
        raise ValueError(
            "Strings with leading and trailing delimiters chars are not valid"
            "," "do str.strip(chars=delimiter)"
        )

    merged_strings = []

    # Sort by len taking in account the delimiter chars if ignore_delimiter.
    shortest, longest = sorted(
        [string1, string2],
        key=lambda x: len(x) - (x.count(delimiter) if ignore_delimiter else 0)
    )

    shortest_len, longest_len = len(shortest), len(longest)

    # Do not count because chars will be placed in no delimiter chars
    if ignore_delimiter:
        shortest_len -= shortest.count(delimiter)

    # Longest Chars behind each Short Char.
    column_height = longest_len // shortest_len
    current_longest = 0

    # Start Distributing Equally
    column_extra_added = 0
    for short_char in shortest:
        # The first character is always the one from the shortest string
        column = [short_char]

        # Add column_height chars to column if char is not delimiter.
        if not (short_char == delimiter and ignore_delimiter):
            for long_char in longest[current_longest:
                                     current_longest + column_height]:
                column.append(long_char)

            current_longest += column_height

            # First columns add one more row
            if column_extra_added < longest_len % shortest_len:
                column.append(longest[current_longest])
                current_longest += 1
                column_extra_added += 1

        # Add merged string to result
        merged_strings.append(column)

    if ignore_delimiter and not allow_delimiter_column:

        # Move words from column untill all columns has atleast one char
        # different than deimiter.
        idx = 0
        while idx < len(merged_strings) - 1:
            column = merged_strings[idx]

            # Short char with a column of long chars that are only = delimiter.
            if (column[0] != delimiter
                and column[1:]
                and not any(letter != delimiter for letter in column[1:])):

                # Move the last character of the short word before and
                # Place it into the current word.
                merged_strings[idx].insert(1, merged_strings[idx-1].pop())
                idx = 0

            else:
                idx += 1

    return merged_strings

if __name__ == "__main__":
    import doctest
    doctest.testmod()
