# pySNVCovid 
Python program to generate dynamic network graph from a given dataset. It also creates PDF report from generated static graphs. Tkinter provides a GUI for the program.

## Python packages
* Pandas: Data manipulation
* NetworkX: Graph generation
* Tkinter: GUI generation
* ReportLab: PDF Report generation

## Usage
`python -m main.py`

1. Input dataset link in DOWNLOAD tab. View downloaded dataframe in table view. Save data in CSV format.
2. Select graph type and color field & generate graph in SELECT tab. Select colors for each unique value or get randomly generated color. Provide date range & create dynamic network graph using NetworkX. Save graph in GEPHI compatible GEXF format.
3. Run graph in gephi using DISPLAY tab. View graph's stats and open it directly in GEPHI.
4. Generate static graph in STATIC GRAPH tab. Select static graph type, columns, and color fields for the graph. Specify graph options to generate graph. View and save using double click as PDF report.

Example link: https://api.covid19india.org/raw_data1.json

## Release
v4.5: EXE Program generated by pyinstaller python package.
https://github.com/sakshamsneh/pySNVCovid/releases/tag/v4.5
