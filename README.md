Easy Markdown formatter and converter
=========================

&copy; 2018 SiLeader and Cerussite.

## Overview
Markdown formatting and converter.

### Features
+ Convert markdown file (PDF, HTML, Markdown)
+ Add title
+ Add section number

## Usage
### Show command help

```sh
ezmd --help
```

### Convert to PDF, HTML or Markdown

```sh
ezmd --type=html --output=out.html in.md
```

if you want to set output file type, please set `--type` option.

this option supporting

+ pdf (default)
+ html
+ markdown

### Add title

```sh
ezmd --title="Document Title"
ezmd --title="Document Title" --author="SiLeader" --date
ezmd --title="Document Title" --author="SiLeader" --date-as-today
ezmd --title="Document Title" --author="SiLeader" --date-as-today --title-page
```

replace &lt;x-title/&gt; tag to title.

`--title-page` option generate single page title.


## License
Apache License 2.0
