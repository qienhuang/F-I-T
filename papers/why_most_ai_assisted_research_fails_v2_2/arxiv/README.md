# arXiv LaTeX source (v2.2)

This folder contains an arXiv-style LaTeX source package for:

**Why Most AI-Assisted Research Fails (and How to Fix It)**  
*A Structural Account of Fluent Stagnation and the Conditions for Cumulative Discovery*

## Build

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

If your environment uses `latexmk`:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

