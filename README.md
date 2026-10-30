# notebook-pdf

Makes Jupyter's **Export → PDF** (VS Code, JupyterLab, `jupyter nbconvert --to pdf`) work without
a TeX Live install. It installs an nbconvert config that compiles PDFs with
[tectonic](https://tectonic-typesetting.github.io/) instead of xelatex.

```bash
conda install -c https://prefix.dev/philipnickel/notebook-pdf -c conda-forge notebook-pdf
```

or with pixi: `pixi workspace channel add https://prefix.dev/philipnickel/notebook-pdf && pixi add notebook-pdf`.

- **The first export needs internet.** tectonic downloads the TeX files it needs (~50 MB) and the
  first export takes a few minutes. Later exports take seconds and work offline.
- **LaTeX errors still give a PDF.** Broken math in a markdown cell is mangled or left out, without
  a warning.

## Development

```bash
pixi run e2e   # build the package and export tests/notebooks/*.ipynb to PDF
```
