def main():
    """
    pip install toml
    pip install pylatex
    """
    fact_data = load_facts()
    print_facts(fact_data)


def load_facts():
    import toml
    import pathlib
    fact_fpath = pathlib.Path('~/misc/facts/facts.toml').expanduser()
    with open(fact_fpath, 'r') as file:
        fact_data = toml.load(file)
    return fact_data


def print_facts(fact_data):
    from rich.panel import Panel
    from rich.console import Console
    import ubelt as ub
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
    pip install pyqrcode pylatex pypng

    pyqrcode.create('google.com').png('foo.png', scale=4)
    """
    import pylatex
    import os
    from pylatex.base_classes.command import Options  # NOQA
    import pyqrcode
    import ubelt as ub

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
    doc = pylatex.Document('fact_document', inputenc='utf8',
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
            doc.append(text)
            if QR_REFERENCE:
                doc.append('\n')
                num_refs = 0
                for refline in fact['references'].split('\n'):
                    if refline.startswith('http'):
                        found = refline
                        fpath = ub.hash_data(found, base='abc')[0:16] + '.png'
                        fpath = os.path.abspath(fpath)
                        # pyqrcode.create(found).svg(fpath, scale=6)
                        pyqrcode.create(found).png(fpath, scale=2)
                        doc.append(pylatex.NoEscape(r'\includegraphics[width=90px]{' + fpath + '}'))
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

    # print(doc.dumps())
    print('generate pdf')
    doc.generate_pdf(clean_tex=True)
    # compiler='lualatex')


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/facts/parser.py render_facts
    """
    import sys
    if len(sys.argv) > 1:
        import fire
        fire.Fire()
    else:
        main()
