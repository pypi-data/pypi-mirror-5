# py-pdf-collate

py-pdf-collate is a Python script that collates your PDF documents.

## What is it used for
Turn your single-sided scanner into a duplex!

There is currently only one sorting method, but more will be added shortly.

It will take the following page order:
1, 3, 5, 2, 4, 6
And collate it to:
1, 2, 3, 4, 5, 6

## Installation
1. Install ```py-pdf-collate` package:

    pip install py-pdf-collate

2. Run on the command line:

    pdf_collate [filename] [output filename (optional)]

If you do not provide an output filename, it will override your source file by default.

## Upcoming features

I will be adding the following sort order:
1, 3, 5, 6, 4, 2
