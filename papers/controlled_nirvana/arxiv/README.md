# Controlled Nirvana (arXiv source)

This folder contains an arXiv-ready LaTeX source (v1.5) generated from the canonical markdown:

- `../controlled_nirvana.v1.3.teece_style.md`

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

This creates `controlled_nirvana_arxiv_v1.4.zip` containing:
- `main.tex`
- `abstract.tex`
- `content.tex`

This creates `controlled_nirvana_arxiv_v1.5.zip` containing:
- `main.tex`
- `abstract.tex`
- `content.tex`

If the zip already exists and cannot be overwritten, the script writes `controlled_nirvana_arxiv_v1.5_YYYYMMDD_HHMMSS.zip` instead.
