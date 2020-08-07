# -*- coding: utf-8 -*-

import sys

def progress(current, total, width=25):
    bar_width = width
    block = int(round(bar_width * current/total))
    text = "\rProcessing: [{0}] {1} of {2} lineSteps".\
             format("#"*block + "-"*(bar_width-block), current, total)

    sys.stdout.write(text)
    sys.stdout.flush()
    

    