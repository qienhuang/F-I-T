# Grokking Hard Indicators (arXiv/SSRN LaTeX source)

This folder contains an arXiv-ready LaTeX source for the canonical markdown:

- `../grokking_hard_indicators_v0_3.md`

## Build locally

From this folder:

```bash
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## Create an arXiv upload zip (PowerShell)

From this folder:

```powershell
.\make_arxiv_zip.ps1
```

This creates `grokking_hard_indicators_arxiv_v0.3.zip` containing:
- `main.tex`
- `abstract.tex`
- `content.tex`

If the zip already exists and cannot be overwritten, the script writes
`grokking_hard_indicators_arxiv_v0.3_YYYYMMDD_HHMMSS.zip` instead.
