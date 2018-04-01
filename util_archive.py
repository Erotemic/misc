"""
pip install archive
import archive
pip install git+https://github.com/gdub/python-archive.git

tar -xvzf phase1-imagery.tar.gz

"""

import archive
arc = archive.Archive('phase1-imagery.tar.gz')

tar = arc._archive._archive
tar.getmembers()
tar.getnames()
