from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import markdown as md
import codecs
import sys
import os
import re
import zlib
import base64
import string
from .env import css_path, ms_encoding, markdown_type, \
    html_dir, html_extension


class MarkdownConverter(object):
    def __init__(self):
        css = codecs.open(css_path, encoding=ms_encoding, mode="r")
        self.html_header = (
            """
            <html>
            <head>
            <style type='text/css'>
            <!--
            """
            + css.read()
            + """
            //-->
            </style>
            </head>
            <body>
            <div class='markdown-body'>
            """
        )
        self.html_footer = """
            </div>
            </body>
            </html>
            """

    def convert(self, src, dst=""):
        code = md.markdown(self.md_plantuml_adapt(self.read_md(src)), extensions=[markdown_type])
        return self.write_html(code, src, dst)

    def read_md(self, file_name):
        workingdir = os.getcwd()
        md_file = codecs.open(
            os.path.join(workingdir, file_name),
            encoding=ms_encoding,
            mode="r"
        )
        return md_file.read()


    def md_plantuml_adapt(self, md_text):
        matches = re.findall(r'```plantuml.*?```', md_text, re.DOTALL|re.MULTILINE)
        mduml_text=md_text
        for m in matches:
            encode=self.plantuml_encode("\n".join(m.split("\n")[1:-1]))
            mduml_text = mduml_text.replace(m, f"![plantuml](http://www.plantuml.com/plantuml/png/{encode})" )
        return mduml_text


    def plantuml_encode(self, plantuml_text):
        """zlib compress the plantuml text and encode it for the plantuml server"""
        zlibbed_str = zlib.compress(plantuml_text.encode('utf-8'))
        compressed_string = zlibbed_str[2:-4]

        plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
        base64_alphabet   = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
        b64_to_plantuml = bytes.maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))
        return base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')


    def write_html(self, body, file_name, dst):
        html_path = os.path.join(html_dir, file_name + html_extension)

        if dst != "":
            html_path = dst
        try:
            os.makedirs("/".join(html_path.replace("\\", "/").split("/")[:-1]))
        except OSError:
            pass

        html_file = codecs.open(html_path, encoding=ms_encoding, mode="w")
        html_file.write(self.html_header + body + self.html_footer)
        return html_path


def main():
    args = sys.argv
    if len(args) != 3:
        print("usage: convert source_md_file target_html_file")
    else:
        converter = MarkdownConverter()
        converter.convert(args[1], args[2])


if __name__ == "__main__":
    main()
