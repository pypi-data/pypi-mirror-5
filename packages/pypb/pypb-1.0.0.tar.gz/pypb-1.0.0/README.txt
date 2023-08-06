pypb
====

What it is
==========

A configurable console-based progress bar for python utilities.


Installing
==========
pip install pypb


How to use it
=============

    from pypb import ProgressBar
    pb = ProgressBar('some task', 4000)
    for i in range(4000):
      pb.draw()
