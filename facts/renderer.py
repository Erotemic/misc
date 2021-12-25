"""
Does nice rendering of the fact database

Requires:
    pip install toml
    pip install pylatex
    pip install pyqrcode pylatex pypng

CommandLine:
    python ~/misc/facts/renderer.py print_facts
    python ~/misc/facts/renderer.py render_facts
"""
import os
import pathlib
import re
import toml
import ubelt as ub


class _ExtendedPathMixin(object):
    """
    An extension of :class:`pathlib.Path` with extra convinience methods
    """

    def ensuredir(self, mode=0o777):
        """
        Concise alias of `self.mkdir(parents=True, exist_ok=True)`
        """
        self.mkdir(mode=mode, parents=True, exist_ok=True)
        return self

    def expandvars(self):
        """
        As discussed in CPythonIssue21301_, CPython wont be adding expandvars
        to pathlib. I think this is a mistake, so I added it in this extension.

        References:
            .. [CPythonIssue21301] https://bugs.python.org/issue21301
        """
        return self.__class__(os.path.expandvars(self))

    def expand(self):
        """
        Expands user tilde and environment variables.

        Concise alias of `Path(os.path.expandvars(self.expanduser()))`

        Example:
            >>> print(Path('$HOME').expand())
            >>> print(Path('~/').expand())
        """
        return self.expandvars().expanduser()


class Path(pathlib.Path, _ExtendedPathMixin):
    """
    An extension of :class:`pathlib.Path` with extra convinience methods
    """

    def __new__(cls, *args, **kwargs):
        if cls is Path:
            cls = WindowsPath2 if os.name == 'nt' else PosixPath2
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        return self


class WindowsPath2(pathlib.WindowsPath, _ExtendedPathMixin):
    pass


class PosixPath2(pathlib.PosixPath, _ExtendedPathMixin):
    pass


def load_facts():
    fact_fpath = Path('~/misc/facts/facts.toml').expand()
    with open(fact_fpath, 'r') as file:
        fact_data = toml.load(file)

    if 1:
        with open(Path('~/misc/facts/internal.toml').expand(), 'r') as file:
            fact_data['facts'].extend(toml.load(file)['facts'])
    return fact_data


def print_facts():
    """
    Print facts with rich
    """
    from rich.panel import Panel
    from rich.console import Console

    fact_data = load_facts()

    console = Console()
    for fact in fact_data['facts']:
        text = ub.codeblock(
            '''
            {}

            References:
            {}
            ''').format(
                ub.paragraph(fact['text']),
                ub.indent(fact['references']),
            )
        fact_panel = Panel(text, title='FACT')
        console.print(fact_panel)


def render_facts():
    """
    Render facts to a latex document
    """
    import pylatex
    from pylatex.base_classes.command import Options  # NOQA
    import pyqrcode

    fact_data = load_facts()

    class MDFramed(pylatex.base_classes.Environment):
        _latex_name = 'mdframed'
        packages = [pylatex.Package('mdframed')]

    class SamePage(pylatex.base_classes.Environment):
        _latex_name = 'samepage'

    class ComposeContexts:
        def __init__(self, *contexts):
            self.contexts = contexts

        def __enter__(self):
            return [c.__enter__() for c in self.contexts]

        def __exit__(self, a, b, c):
            return [c.__exit__(a, b, c) for c in self.contexts[::-1]]

    # class NewUnicodeChar(pylatex.base_classes.CommandBase):
    #     pass

    # Dont use fontenc, lmodern, or textcomp
    # https://tex.stackexchange.com/questions/179778/xelatex-under-ubuntu
    doc = pylatex.Document('fact_document', inputenc=None,
                           page_numbers=False, indent=False, fontenc=None,
                           lmodern=False, textcomp=False)

    doc.preamble.append(pylatex.Package('graphicx'))  # For PNG images
    # doc.preamble.append(pylatex.Package('svg', options=dict(inkscapearea='page')))
    # doc.preamble.append(pylatex.Command('title', 'Facts'))
    # doc.preamble.append(pylatex.Command('author', 'Anonymous author'))
    # doc.preamble.append(pylatex.Command('date', pylatex.NoEscape(r'\today')))
    # doc.append(pylatex.NoEscape(r'\maketitle'))

    # doc.preamble.append(pylatex.Package('newunicodechar'))
    # doc.preamble.append(pylatex.NoEscape(r'\newunicodechar{±}{$\pm$}'))

    # doc.append(pylatex.NoEscape('13.787±0.020'))
    # print(doc.dumps())
    # doc.generate_pdf(clean_tex=False, compiler='xelatex')
    # return

    QR_REFERENCE = True
    stop_flag = 0

    image_dpath = Path('~/misc/facts/images').expand().ensuredir()
    # image_dpath =

    for fact in ub.ProgIter(fact_data['facts']):
        contexts = ComposeContexts(
            # doc.create(SamePage()),
            doc.create(MDFramed()),
            doc.create(pylatex.MiniPage(width=r'0.99\textwidth'))
        )
        # with doc.create(pylatex.MiniPage(width=r'\textwidth')):
        with contexts:
            doc.append(pylatex.NoEscape(r'\paragraph{Fact:}'))
            text = ub.paragraph(fact['text'])

            if r'\[' in text:
                found = list(re.finditer('(' + re.escape(r'\[') + '|' + re.escape(r'\]') + ')', text))
                prev_x = 0
                for a, b in ub.iter_window(found, step=2):
                    part = text[prev_x:a.span()[0]]
                    doc.append(part)
                    ax, bx = a.span()[1], b.span()[0]
                    part = pylatex.NoEscape(r'$' + text[ax:bx] + r'$ ')
                    doc.append(part)
                    prev_x = b.span()[1]
                part = text[prev_x:]
                doc.append(part)
            else:
                # if '$' in text:
                #     parts = text.split('$')
                #     for idx, p in enumerate(parts):
                #         if idx % 2 == 1:
                #             doc.append(pylatex.NoEscape('$' + p + '$ '))
                #         else:
                #             doc.append(p)
                # else:
                doc.append(text)
            if QR_REFERENCE:
                doc.append('\n')
                num_refs = 0
                for refline in fact['references'].split('\n'):
                    if refline.startswith('http'):
                        found = refline
                        image_fname = ub.hash_data(found, base='abc')[0:16] + '.png'
                        image_fpath = image_dpath / image_fname
                        if not image_fpath.exists():
                            # pyqrcode.create(found).svg(fpath, scale=6)
                            pyqrcode.create(found).png(str(image_fpath), scale=2)
                        doc.append(pylatex.NoEscape(r'\includegraphics[width=90px]{' + str(image_fpath) + '}'))
                        # doc.append(pylatex.NoEscape(r'\includesvg[width=120px]{' + fpath + '}'))
                        num_refs += 1
                        if num_refs > 3:
                            break
            else:
                doc.append(pylatex.NoEscape(r'\paragraph{References:}'))
                with doc.create(pylatex.Itemize()) as itemize:
                    for refline in fact['references'].split('\n'):
                        if refline:
                            refline = refline.strip()
                            itemize.add_item(refline)

        doc.append(pylatex.NoEscape(r'\bigskip'))
        if stop_flag:
            break

    print(doc.dumps())
    print('generate pdf')
    doc.generate_pdf(str(Path('~/misc/facts/fact_document').expand()), clean_tex=True)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/facts/renderer.py print_facts
        python ~/misc/facts/renderer.py render_facts
    """
    import sys
    if len(sys.argv) > 1:
        import fire
        fire.Fire()
    else:
        print_facts()
