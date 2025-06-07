def merge_strings(
    string1: str,
    string2: str,
    ignore_delimiter: bool = False,
    delimiter: str = ' ',
    ) -> list[list[str]]:
    """ Place longest string chars behind the shortest string

    Two unsorted strings gets sorted (by length) and the longest gets
    merged into the shortest one by placing their chars behind in a
    secuential and equally distributed way.

    Think of it like adding blocks to each column until all columns
    are equal.

    Parameters
    ----------
        first_text : str
                     Non-empty unsorted string.

        second_text : str
                      Non-empty unsorted string.

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
    merged_strings = []
    shortest, longest = sorted(
        [string1, string2],
        key=lambda x: len(x) - (x.count(delimiter) if ignore_delimiter else 0)
    )

    shortest_len, longest_len = len(shortest), len(longest)

    if ignore_delimiter:
        shortest_len -= shortest.count(delimiter)

    column_height = longest_len // shortest_len
    current_longest = 0

    # Start Distributing Equally
    column_extra_added = 0
    for short_char in shortest:
        
        # The first character is always the one from the shortest string
        column = [short_char]

        # Add column_height chars to column
        if short_char != delimiter:
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

    idx = 0
    while idx < len(merged_strings) - 1:
        column = merged_strings[idx]
        if (column[0] != delimiter 
            and column[1:] 
            and not any(letter != delimiter for letter in column[1:])):
            merged_strings[idx].insert(1, merged_strings[idx-1].pop())
            idx = 0

        else:
            idx += 1

    return merged_strings
