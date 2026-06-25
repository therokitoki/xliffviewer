# <img src="data/viewer.ico" width="64" height="64"> xliffviewer
A lightweight viewer for XLIFF files.

I've always encountered a situation where I needed to take a quick peek at an .xliff file, and I would either have to open Trados (which can take a while), MemoQ, go to the online CAT tool, or use some random website. Because of this, I prepared a simple viewer, that shows ID (if available), Source, Target and Status. Since XLIFF state attributes vary significantly across platforms, the status column uses a fallback logic to capture as much metadata as possible, though it may vary depending on the file's origin.

The reader supports these formats: `.xliff (1.2 & 2.0)`, `.sdlxliff`, `.mqxliff`, and `.mxliff`.

## How to use it

To launch the application, run the following command from your terminal:
```
python viewer.py
```
## Requirements & Tech
Python 3.11+

Libraries: lxml for XML/XLIFF parsing, and tkinter for the interface.
