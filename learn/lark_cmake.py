"""
References:
    https://github.com/dubrousky/CMaker/blob/master/grammar/cmake.bnf
    https://lark-parser.readthedocs.io/en/latest/json_tutorial.html
    https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark
"""

import lark
import ubelt as ub
GRAMMAR = ub.codeblock(
    r'''
    ?start: body

    %import common.WS
    %import common.NEWLINE
    %import common.NUMBER

    endfunction       : "endfunction"i
    function          : "function"i
    elseif            : "elseif"i
    else              : "else"i
    endif             : "endif"i
    if                : "if"i
    endmacro          : "endmacro"i
    macro             : "macro"i
    endforeach        : "endforeach"i
    foreach           : "foreach"i
    endwhile          : "endwhile"i
    while             : "while"i
    bracket_comment   : /(\#\[=*\[)([^\]]|\n)*?(\]=*\])/
    bracket_argument  : /(\[=*\[)([^\]]|\n)*?(\]=*\])/
    line_comment      : /\#.*/
    quoted_argument   : /(")([^"]\\\n|[^"])*(")/
    unquoted_argument : /([^\(\)\#\"\\ ]|\\\( | \\\) | \\\# | \\\" | (\\ ) | \\\\ | \\\$ | \\\@ | \\\^ | \\t | \\r | \\n| \\;)+/
    identifier        : /[A-Za-z_][A-Za-z0-9_]*/


    file         : file_element*
    file_element : (funmacro | loop | cond | cmd | line_comment | bracket_comment)

    eol: ( bracket_comment | line_comment )?

    line_ending  :  ( bracket_comment | line_comment )

    // Function/macro definition need to be separated

    funmacro  : (fbegin body fend) | (mbegin body mend)
    fbegin : function "(" arguments ")"
    fend   : endfunction "(" arguments ")"
    mbegin : macro "(" arguments ")"
    mend   : endmacro "(" arguments ")"

    // Loops and conditions can nest
    // Loop block
    loop       : forbegin body forend | whilebegin body whileend
    forbegin   : foreach "(" arguments ")"
    forend     : endforeach "(" arguments ")"
    whilebegin : while "(" arguments ")"
    whileend   : endwhile "(" arguments ")"

    // Condition block
    cond             : (if_expr body (elseif_expr body)* (elseif_expr|else_expr) body endif_expr) | (if_expr body endif_expr)

    if_expr          : if "(" arguments ")" eol
    elseif_expr      : elseif "(" arguments ")" eol
    else_expr        : else "(" arguments ")" eol
    endif_expr       : endif "(" arguments ")" eol

    // Body
    // Allow nested functions
    body                :  file_element+
    // Single command invocation
    cmd                 : command_name  "(" arguments ")"
    command_name        : identifier
    // Arguments
    arguments           :  argument? bracket_comment*  separated_argument*
    //separated_argument  :  argument | "(" arguments ")"
    separated_argument  :  argument (argument)*

    // Single argument
    // argument            :  bracket_argument | quoted_argument  | unquoted_argument
    argument            :  quoted_argument  | unquoted_argument

    %ignore WS
    ''')


def main():
    parser = lark.Lark(GRAMMAR,  start='start', parser='earley')

    text = ub.codeblock(
        '''
        cmake_minimum_required(VERSION 3.1.0)
        set(CMAKE_CXX_STANDARD 11)
        # #######################################
        if (APPLE)
            set(CMAKE_MACOSX_RPATH 1)
            message(STATUS "Detected APPLE system")
            SET(CLANG2 Off)
        endif()
        ''')

    try:
        parsed = parser.parse(text)
    except lark.exceptions.LarkError as ex:
        print(f'ex={ex}')
        raise
    print(parsed.pretty())

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/lark_cmake.py
    """
    main()
