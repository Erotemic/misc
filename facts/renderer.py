"""
Does nice rendering of the fact database

Requires:
    pip install toml
    pip install pylatex
    pip install pyqrcode pylatex pypng
    pip install pyqrcode pylatex pypng toml pylatex

CommandLine:
    python ~/misc/facts/renderer.py print_facts
    python ~/misc/facts/renderer.py render_facts
"""
# import os
# import pathlib
import re
import toml
import ubelt as ub


def load_facts():
    fact_table = []

    fact_paths = [
        ub.Path('~/misc/facts/facts-2021.toml').expand(),
        ub.Path('~/misc/facts/facts-2024.toml').expand(),
    ]
    for fact_fpath in fact_paths:
        with open(fact_fpath, 'r') as file:
            fact_data = toml.load(file)
        fact_list = fact_data.pop('facts', [])

        for num, item in enumerate(fact_list, start=1):
            item = {**item, **fact_data}
            item['num'] = num
            item['total'] = len(fact_list)
            item['stamp'] = f"{item['year']} - {item['num']:02d} of {item['total']}"
            fact_table.append(item)

    if 0:
        with open(ub.Path('~/misc/facts/internal.toml').expand(), 'r') as file:
            fact_data['facts'].extend(toml.load(file)['facts'])

    return fact_table


def print_facts():
    """
    Print facts with rich
    """
    from rich.panel import Panel
    from rich.console import Console

    fact_table = load_facts()
    print(f'fact_table = {ub.urepr(fact_table, nl=1)}')

    console = Console()
    for fact in fact_table:
        text = ub.codeblock(
            '''
            {}

            References:
            {}
            ''').format(
                ub.paragraph(fact['text']),
                ub.indent(fact['references']),
            )
        fact_panel = Panel(text, title='FACT ' + fact['stamp'])
        console.print(fact_panel)


def render_facts():
    """
    Render facts to a latex document
    """
    import pylatex
    from pylatex.base_classes.command import Options  # NOQA

    fact_table = load_facts()

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

    image_dpath = ub.Path('~/misc/facts/images').expand().ensuredir()
    # image_dpath =

    for fact in ub.ProgIter(fact_table):
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
                        if not image_fpath.exists() or True:
                            # pyqrcode.create(found).svg(fpath, scale=6)
                            url = found
                            if 0:
                                import pyqrcode
                                pyqrcode.create(url).png(str(image_fpath), scale=2)
                            else:
                                import qrcode
                                import kwimage
                                import qrcode.image
                                from qrcode.image.styledpil import StyledPilImage

                                qr = qrcode.QRCode(
                                    version=1,
                                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                                    box_size=10,
                                    border=4,
                                )
                                qr.add_data(url)
                                qr.make(fit=True)
                                img = qr.make_image(fill_color="black", back_color="white")
                                if 'wikipedia.org' in url:
                                    # chrfpath = '/home/joncrall/misc/facts/wiki-logo.png'
                                    chrfpath = '/home/joncrall/misc/facts/wiki-logo-3.jpg'
                                elif 'youtube.com' in url:
                                    chrfpath = '/home/joncrall/misc/facts/YouTube-logo.png'
                                else:
                                    chrfpath = None
                                    parts = url.split('/')
                                    base = parts[2]
                                    base = base.replace('www.', '')
                                    base = base.replace('.com', '')
                                    base = base.replace('.org', '')
                                    base = base.replace('.ca', '')
                                    base = base.replace('.gov', '')
                                    if len(base) > 12:
                                        chrfpath = None
                                    else:
                                        flair_dpath = ub.Path.appdir('facts/flair').ensuredir()
                                        chrimg = kwimage.draw_text_on_image({'color': 'white'}, base, color='black')
                                        chrfpath = flair_dpath / f'{base}.png'
                                        if not chrfpath.exists():
                                            # chrimg = kwimage.imresize(chrimg, dsize=(512, 512))
                                            kwimage.imwrite(chrfpath, chrimg)

                                if chrfpath is None:
                                    img = qr.make_image(
                                        image_factory=StyledPilImage,
                                        fill_color="black", back_color="white",
                                    )
                                else:
                                    img = qr.make_image(
                                        image_factory=StyledPilImage,
                                        # fill_color="black", back_color="white",
                                        embeded_image_path=chrfpath
                                    )
                                img.save(image_fpath)

                        doc.append(pylatex.NoEscape(r'\includegraphics[width=90px]{' + str(image_fpath) + '}'))
                        # doc.append(pylatex.NoEscape(r'\includesvg[width=120px]{' + fpath + '}'))
                        num_refs += 1
                        if num_refs > 3:
                            break
                # doc.append(pylatex.NoEscape(r'\\'))
                batch = fact['stamp']
                doc.append(pylatex.NoEscape(fr'\hfill \tiny {batch}'))
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
    print('Num facts: ', len(fact_table))
    out_dpath = ub.Path('~/misc/facts/fact_document').expand()
    import rich
    rich.print(f'[link={out_dpath.parent}]{out_dpath.parent}[/link]')
    doc.generate_pdf(str(out_dpath), clean_tex=True)


def qrcode_orig():
    import pyqrcode
    pyqrcode.create(found).png(str(image_fpath), scale=2)

def qrcode_v1():
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data('Some data')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = qr.make_image(fill_color="black", back_color="white")
    import kwimage
    import numpy as np
    img = np.array(img).astype(np.uint8) * 255
    kwimage.imwrite('foo.png', img)

    img_1 = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
    img_2 = qr.make_image(image_factory=StyledPilImage, color_mask=RadialGradiantColorMask())
    img_3 = qr.make_image(image_factory=StyledPilImage, embeded_image_path="/path/to/image.png") # this one



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
