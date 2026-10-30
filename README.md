# notebook-pdf

A tiny `noarch` conda package that makes Jupyter's **Export → PDF** (in VS Code, JupyterLab or
`jupyter nbconvert --to pdf`) work without a TeX Live install. It configures nbconvert to compile
with [tectonic](https://tectonic-typesetting.github.io/), which downloads only the LaTeX files
a notebook actually needs.

```bash
conda install -c https://prefix.dev/notebook-pdf -c conda-forge notebook-pdf
```

With pixi: `pixi workspace channel add https://prefix.dev/notebook-pdf`, then `pixi add notebook-pdf`.

> **The first export needs internet.** In a fresh user account it downloads ~50 MB of TeX support
> files into tectonic's cache and takes a few minutes. Later exports take seconds and work offline,
> unless a notebook needs a TeX file that is not cached yet.

## How it works

The package installs one file, `$PREFIX/etc/jupyter/jupyter_nbconvert_config.json`
([recipe/jupyter_nbconvert_config.json](recipe/jupyter_nbconvert_config.json)), and depends on
`nbconvert-core`, `pandoc` and `tectonic`.

```json
{
  "PDFExporter": {
    "latex_command": ["tectonic", "-X", "compile", "-Z", "continue-on-errors", "{filename}"],
    "latex_count": 1,
    "bib_command": ["tectonic", "--version"]
  }
}
```

- `latex_command` replaces the default `xelatex`.
- `-Z continue-on-errors` makes tectonic produce a PDF even when the LaTeX has errors (see below).
- `latex_count: 1` because tectonic does its own reruns (the default is 3).
- `bib_command` is a no-op that exists on every OS: tectonic handles bibliographies itself, and
  the default `bibtex` is not installed.

nbconvert merges config from these directories (highest priority first; see `jupyter --paths`):

1. `$JUPYTER_CONFIG_PATH`
2. `~/.jupyter` (user)
3. `{sys.prefix}/etc/jupyter` (env, where this package puts its file)
4. system dirs (`/usr/local/etc/jupyter`, `/etc/jupyter`; none on Windows by default)

Merging is per key, so a user's own `~/.jupyter/jupyter_nbconvert_config.py` only overrides this
package if it sets the same `PDFExporter` options. Run `jupyter nbconvert --show-config` to see
what is loaded. VS Code's export runs nbconvert with the selected kernel's interpreter, so the
config of that env applies. nbconvert finds `pandoc` and `tectonic` via `PATH`, so the env has to
be activated (VS Code normally does this for conda envs).

## When things go wrong

| Situation | Result |
|---|---|
| First export ever, no internet | ❌ no PDF: `this bundle isn't cached, and we couldn't get it from the internet` |
| LaTeX error in a markdown cell (e.g. `$` + line break + math + line break + `$`) | ✅ PDF; the broken part is mangled or missing, **without a warning** |
| Offline, notebook needs a TeX file that is not cached (rare: only raw TeX in markdown) | ✅ PDF; the affected text is missing, **without a warning** |

Stock nbconvert with xelatex fails on LaTeX errors instead. `-Z continue-on-errors` trades that
for always getting a PDF. It is an unstable tectonic option, which is why `tectonic` is pinned to
`>=0.17,<0.18`; re-run the tests before widening the range.

## Development

Needs [pixi](https://pixi.sh). The workspace depends on its own package
(`notebook-pdf = { path = "." }` in [pixi.toml](pixi.toml)), so pixi builds
[recipe/recipe.yaml](recipe/recipe.yaml) with
[pixi-build](https://pixi.prefix.dev/latest/build/getting_started/) and rebuilds it whenever
`recipe/` changes.

```bash
pixi run e2e                     # export tests/notebooks/*.ipynb to PDF with the package installed
pixi publish --target-dir dist   # build the .conda file into ./dist
```

Local builds are versioned `0.0.0.dev0`. To build a specific version, set
`NOTEBOOK_PDF_VERSION=1.2.3` and pass `--clean`; without it, pixi reuses a cached build
because it doesn't notice environment variable changes.

The test notebooks are pre-executed, so no kernel is needed:
[sample.ipynb](tests/notebooks/sample.ipynb) (math, æøå, a plot, a table) and
[broken_math.ipynb](tests/notebooks/broken_math.ipynb) (must still produce a PDF).

## CI and releases

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs on pushes to `main`, PRs and tags:

- **e2e**: runs `pixi run e2e` on Linux, macOS and Windows.
- **publish**: on `v*` tags only. The tag is the version (`v1.2.3` → `1.2.3`, passed to
  [recipe/recipe.yaml](recipe/recipe.yaml) as `NOTEBOOK_PDF_VERSION`, the way Miniforge uses
  `MINIFORGE_VERSION`). Runs `pixi publish --clean` to build and upload to prefix.dev with
  trusted publishing.

To release:

1. One-time setup: create the channel on prefix.dev, then add a trusted publisher for repo
   `philipnickel/notebook-pdf`, workflow `ci.yml`. Set the repository variable `PREFIX_CHANNEL`
   to the channel name.
2. Tag and push: `git tag v<version> && git push origin v<version>`. No file needs editing.
