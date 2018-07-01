#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    Copyright 2018 SiLeader and Cerussite.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import argparse
import typing
import markdown2
import pdfkit
from datetime import datetime
import re
import os
import uuid


CSS = "github-pygments.css"
ADDITIONAL_STYLE = """
pre {
    background: #eee;
    padding: 5px;
    border-radius: 5px;
}
html {
    background: #fff;
}
"""


def args_parse():
    parser = argparse.ArgumentParser(prog="ezmd", usage="", description="Easy markdown compiler")
    parser.add_argument("--number", "--section-number", action="store_true", help="Add number to sections")
    parser.add_argument("--type", "--output-type",
                        action="store", choices=["html", "pdf", "markdown"], help="Output type (pdf)", default="pdf")
    parser.add_argument("input", action="store", help="Input file name")
    parser.add_argument("--output", "-o", action="store", help="Output file", default=None)

    parser.add_argument("--title-header", action="store_true", help="Put title as header")
    parser.add_argument("--title", action="store", help="Document title", default=None)
    parser.add_argument("--title-page", action="store_true", help="generate independent title page")
    parser.add_argument("--author", action="store", help="Document author")
    parser.add_argument("--date", action="store", help="Create data")
    parser.add_argument("--date-as-today", action="store_true", help="--date treat as today")
    parser.add_argument("--date-format", action="store", default="%Y/%m/%d", help="Datetime format")

    parser.add_argument("--centering-picture", action="store_true", help="Centering pictures")
    parser.add_argument("--centering-table", action="store_true", help="Centering tables")
    parser.add_argument("--centering", action="store_true", help="Centering pictures and tables")

    parser.add_argument("--figure-caption-string", action="store", help="figure caption [figure 1]", default="Figure")
    parser.add_argument("--figure-caption", action="store_true", help="put figure caption")

    parser.add_argument("--mathjax", "--enable-mathjax", action="store_true", help="use mathjax (not supported option)")
    # index
    args = parser.parse_args()
    if args.mathjax:
        print("--mathjax and --enable-mathjax options are ignored.")

    return args


def yes_no_input(prompt: str, default_yes=True) -> bool:
    if default_yes:
        yn = " [Y/n] "
    else:
        yn = " [y/N] "
    i = input(prompt + yn)

    if default_yes:
        if i.lower().startswith("n"):
            return False
        return True
    if i.lower().startswith("y"):
        return True
    return False


def check_extension(output: typing.Optional[str], output_type: str, input_file: str) -> str:
    if output is None:
        file, ext = os.path.splitext(input_file)
        return file + {"pdf": ".pdf", "html": ".html", "markdown": ".md"}[output_type]

    def different():
        print("Output file extension is different from output type. file: {}, type: {}".format(output, output_type))

    def rename(exts: typing.List[str]) -> str:
        if ext not in exts:
            different()
            if yes_no_input("Rename output file name to {}?".format(file + exts[0])):
                return file + exts[0]
        return output
    file, ext = os.path.splitext(output)
    if output_type == "pdf":
        return rename([".pdf"])
    elif output_type == "html":
        return rename([".html", ".htm"])
    elif output_type == "markdown":
        return rename([".md", ".markdown"])

    return output


def main():
    args = args_parse()

    output = check_extension(args.output, args.type, args.input)

    with open(args.input) as fp:
        lines = fp.readlines()

    if args.title_header:
        ll = ["<x-title/>\n"]
        ll.extend(lines)
        lines = ll

    if args.number:
        lines = add_section_number(lines)

    lines = process_pictures(
        lines,
        args.centering or args.centering_pictures,
        args.figure_caption,
        args.figure_caption_string
    )
    lines = process_table(lines, args.mathjax, args.centering or args.centering_table, True, "Table")

    if args.title is not None:
        date = args.date
        if args.date_as_today:
            date = datetime.now().strftime(args.date_format)
        lines = add_title(lines, create_title(args.title, args.author, date, args.title_page))

    if args.type == "html":
        lines = convert_to_html(lines, args.mathjax)
    elif args.type == "markdown":
        lines = "".join(lines)
    elif args.type == "pdf":
        convert_to_pdf(lines, args.mathjax, output)
        return

    with open(output, "w") as fp:
        fp.write(lines)


def convert_to_pdf(lines: typing.List[str], mathjax, output: str):
    lines = convert_to_html(lines, mathjax)
    pdfkit.from_string(lines, output)


def convert_partial(lines: typing.List[str], mathjax: bool) -> str:
    lines = "".join(lines)
    mj = []  # None
    if mathjax:
        # mj = sanitizeInput(lines)
        # lines = mj[0]
        pass
    html = markdown2.markdown(lines, extras=["footnotes", "fenced-code-blocks", "tables"])

    if mathjax:
        if mj is None:
            print("error: internal logic error")
            exit(1)
        # html = reconstructMath(html, mj[1])

    return html


def convert_to_html(lines: typing.List[str], mathjax: bool) -> str:
    html = convert_partial(lines, mathjax)
    with open(CSS) as fp:
        css = fp.read()
    html = """<html>
    <head>
        <meta charset="utf-8">
        <style>{style}{additional_style}</style>
    </head>
    <body>{body}</body>
</html>""".format(style=css, additional_style=ADDITIONAL_STYLE, body=html)
    return html


def create_title(title, author=None, date=None, single_page=False):
    if single_page:
        title_size = "style=\"font-size: 64px;\""
        other_size = "style=\"font-size: 40px;\""
    else:
        title_size = ""
        other_size = ""
    title = "<h1 {}>{}</h1>\n".format(title_size, title)
    if author is not None:
        title += "<h2 {}>{}</h2>\n".format(other_size, author)
    if date is not None:
        title += "<h2 {}>{}</h2>\n<br/>\n<br/>\n".format(other_size, date)
    if single_page:
        title += """<div style="page-break-after: always;"></div>"""
    return title


def process_pictures(lines: typing.List[str], centering=True, with_title=True, caption=""):
    if not centering and not with_title:
        return lines

    picture_id = {}
    attribute = ""
    if centering:
        attribute = 'style="width: 100vw; text-align: center;"'

    for i in range(len(lines)):
        match = re.match("(!\s*\[([^\]]+)\]\s*\(([^)]+)\))", lines[i])
        if match is not None:
            lines[i] = markdown2.markdown(match.group(0).strip())
            lines[i] = lines[i].replace("<p>", '<p {}>'.format(attribute))

            if with_title:
                title = match.group(2)
                if "|" in title:
                    pid = len(picture_id) + 1
                    t = [tt.strip() for tt in title.split("|")]
                    picture_id[t[0]] = pid
                    title = t[1]
                title = caption + str(len(picture_id)) + " " + title
                lines[i] = lines[i].replace("</p>", "<br/>{}</p>".format(title))

    if with_title:
        regex = "<\s*p\s*:\s*([^/\s]+)\s*/\s*>"
        for i in range(len(lines)):
            match = re.match(regex, lines[i])
            if match is not None:
                title = match.group(1)
                if title not in picture_id:
                    print("error: picture title cannot find. title: {}".format(title))
                    exit(1)
                lines[i] = re.sub(regex, "{} {}".format(caption, picture_id[title]), lines[i])

    return lines


def process_table(lines: typing.List[str], mathjax: bool, centering=True, with_title=True, caption=""):
    if not centering and not with_title:
        return lines

    table_id = {}
    attribute = ""
    if centering:
        attribute = 'style="width: 100vw; text-align: center;"'

    table_regex = "<\s*T\s*:\s*([^/]+)\s*/\s*>"

    i = 0
    while True:
        if len(lines) <= i:
            break

        match = re.match(table_regex, lines[i])

        if match is not None:
            title = match.group(1)

            tid = len(table_id) + 1
            if "|" in title:
                title = [t.strip() for t in title.split("|")]
                table_id[title[0]] = tid
                title = title[1]
            else:
                table_id[str(uuid.uuid4())] = 0

            lines[i] = re.sub(table_regex, "<p {}>{} {}<br/>\n".format(attribute, caption + str(tid), title), lines[i])

            is_table_started = False
            start_index = None
            while True:
                if len(lines) <= i:
                    if not is_table_started:
                        print("error: table title tag exists, but table is not existed.")
                        exit(1)
                    break

                if is_table_started and len(lines[i].strip()) == 0:
                    lines[i] = "\n</p>\n\n"
                    if start_index is not None:
                        table = convert_partial(lines[start_index:i], mathjax)
                        if centering:
                            table = table.replace(
                                "<table>",
                                '<table style="margin-left: auto; margin-right: auto;" rules="all" border="1">'
                            )
                        ll = lines[0:start_index]
                        ll.append(table)
                        ll.extend(lines[i:])
                        lines = ll
                    break

                if not is_table_started and lines[i].startswith("|"):
                    is_table_started = True
                    start_index = i

                i += 1

        i += 1

    if with_title:
        regex = "<\s*t\s*:\s*([^/\s]+)\s*/\s*>"
        for i in range(len(lines)):
            match = re.match(regex, lines[i])
            if match is not None:
                title = match.group(1)
                if title not in table_id:
                    print("error: table title cannot find. title: {}".format(title))
                    exit(1)
                lines[i] = re.sub(regex, "{} {}".format(caption, table_id[title]), lines[i])

    lines = [l + "\n" for l in "".join(lines).split("\n")]
    return lines


def add_title(lines: typing.List[str], title_markdown):

    for i in range(len(lines)):
        lines[i] = re.sub("(<x-title\s*>[^<]*</x-title>|<x-title\s*/?>)", title_markdown, lines[i])
    return lines


def add_section_number(lines: typing.List[str]):
    depth = [0]

    for i in range(len(lines)):
        current = "".join(["#" for _ in range(len(depth))])
        nex = "".join(["#" for _ in range(len(depth) + 1)])

        if lines[i].startswith(nex):
            depth.append(1)
            current = nex

        elif lines[i].startswith(current):
            depth[-1] += 1

        elif lines[i].startswith("#"):
            index = lines[i].find(" ")
            for _ in range(len(depth) - index):
                depth.pop()
            depth[-1] += 1
            current = lines[i].split(" ")[0]

        lines[i] = lines[i].replace(current + " ", current + " " + ".".join([str(d) for d in depth]) + " ")

    return lines


if __name__ == '__main__':
    main()
