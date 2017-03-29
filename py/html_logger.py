"""
HTML logger inspired by the Horde3D logger.

Usage:

 - call setup and specify the filename, title, version and level
 - call dbg, info, warn or err to log messages.
"""
import logging

#: HTML header (starts the document
_START_OF_DOC_FMT = """<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.2.0/jquery.mobile-1.2.0.min.css">
<script src="https://code.jquery.com/jquery-1.7.1.min.js"></script>
<script src="https://code.jquery.com/mobile/1.2.0/jquery.mobile-1.2.0.min.js"></script>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>%(title)s</title>
</head>

<body>
<h1>%(title)s</h1>
<div>
"""

_END_OF_DOC_FMT = """
</div>
</body>
</html>
"""

_MSG_FMT = """
<div data-role="collapsible" data-theme="%(theme)s">
<h1>%(title)s</h1>
<p>%(content)s</p>
</div>
"""


class HTMLFileHandler(logging.FileHandler):
    """
    File handler specialised to write the start of doc as html and to close it
    properly.
    """
    def __init__(self, title, version, *args):
        super(HTMLFileHandler, self).__init__(*args)
        assert self.stream is not None
        # Write header
        self.stream.write(_START_OF_DOC_FMT % {"title": title,
                                    "version": version})

    def close(self):
        # finish document
        self.stream.write(_END_OF_DOC_FMT)
        super(HTMLFileHandler, self).close()


class HTMLFormatter(logging.Formatter):
    """
    Formats each record in html
    a: black
    b: blue
    c: white
    e: yellow
    """
    CSS_CLASSES = {'WARNING': 'b',
                   'INFO': 'c',
                   'DEBUG': 'a',
                   'CRITICAL': 'e',
                   'ERROR': 'e'}

    def __init__(self):
        super(HTMLFormatter, self).__init__()

    def format(self, record):
        try:
            theme = self.CSS_CLASSES[record.levelname]
        except KeyError:
            theme = "info"
        
        # handle '<' and '>' (typically when logging %r)
        msg = record.msg
        msg = msg.replace("<", "&#60").replace(">", "&#62").replace("&#60br&#62","<br>")

        index = msg.index('\n')

        return _MSG_FMT % {"theme": theme, "title": msg[:index],
                       "content": msg[index+1:]}


class HTMLLogger(logging.Logger):
    """
    Log records to html using a custom HTML formatter and a specialised
    file stream handler.
    """
    def __init__(self,
                 name="html_logger",
                 level=logging.DEBUG,
                 filename="log.html", mode='w',
                 title="Transaction Generated", version="1.0.0"):
        super(HTMLLogger, self).__init__(name, level)
        f = HTMLFormatter()
        h = HTMLFileHandler(title, version, filename, mode)
        h.setFormatter(f)
        self.addHandler(h)


# Example of usage
if __name__ == "__main__":
    logger = HTMLLogger(title="Transaction Generated for Lottery contract")
    logger.info("An information messageaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nblahblahblah")
    logger.debug("A debug message\nblahblahblah")
    logger.warning("A warning message\nblahblahblah")
    logger.error("An error message\nblahblahblah")
