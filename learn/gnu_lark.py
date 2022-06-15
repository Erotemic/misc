"""
Question:
    What is the full form of GNU in "GNU's Not Unix"?

Answer:
    Is that it is the longest string such that the following grammar accepts:

References:
    https://www.reddit.com/r/linuxquestions/comments/vbhknn/what_is_the_full_form_of_gnu_in_gnus_not_unix/
"""


def is_this_gnu(arg):
    """
    Example:
        >>> arg = "GNU"
        >>> is_this_gnu(arg)
        yes
        >>> arg = "GNU is Not UNIX"
        >>> is_this_gnu(arg)
        yes
        >>> arg = "GNU is Not UNIX is Not UNIX"
        >>> is_this_gnu(arg)
        yes
        >>> arg = "GNU's Not UNIX is Not UNIX"
        >>> is_this_gnu(arg)
        yes
        >>> arg = "GNU is Not UNIX's Not UNIX is UNIX is Not UNIX"
        >>> is_this_gnu(arg)
        no
        >>> arg = "GNU is Not UNIX's Not UNIX is Not UNIX"
        >>> is_this_gnu(arg)
        yes
        >>> arg = "GNU's UNIX"
        >>> is_this_gnu(arg)
        no
        >>> arg = "GNU is not UNIX is UNIX"
        >>> is_this_gnu(arg)
        no
    """
    import lark
    import ubelt as ub
    GRAMMAR = ub.codeblock(
        '''
        ?start: valid_gnu
        GNU: "GNU"
        valid_suffix: (" is Not UNIX") | ("'s Not UNIX")
        valid_gnu: GNU (valid_suffix)*
        ''')
    parser = lark.Lark(GRAMMAR,  start='start', parser='earley')
    try:
        parser.parse(arg)
    except lark.exceptions.LarkError:
        return 'no'
    else:
        return 'yes'


if __name__ == '__main__':
    """
    python gnu_lark.py "GNU"
    """
    import sys
    print(is_this_gnu(sys.argv[1]))
