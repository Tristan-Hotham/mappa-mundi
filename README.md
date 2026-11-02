# The world according to the Hereford Mappa Mundi

The Hereford Mappa Mundi (about 1300), the largest surviving medieval map of the world, set against a modern map: the 1,025 names in Bevan and Phillott's 1873 index of the map, which real places they are, what share is Biblical, classical, medieval and legendary, and how the map distorts direction, distance and scale.

Interactive page: https://maps.tristanhotham.com/mappa-mundi/
Paper: https://doi.org/10.5281/zenodo.23878612
Blog post: https://blog.tristanhotham.com/2026/10/31/mappa-mundi/

## Headline results

- Inventory: 1,025 names in the 1873 index: Asia 371, Europe 324, Africa 117, seas and islands 105, British Isles 83, frame 25.
- Classes (of 985 names, frame and natural history left out): classical 714 (72%), medieval 121 (12%), Biblical 93 (9%), legendary 57 (6%). All Biblical names are in Asia; 92% of British names are medieval.
- Real places: 337 of 928 non-legendary names (36%) have a real position, 143 from the book's identifications (hand-checked) and 194 from Pleiades name matches. A lower bound.
- Direction: for 140 located real places, the median bearing error from Jerusalem (east up on the map) is 19 degrees; 81% are within 45 degrees. North Africa (69) and Egypt (72) swing south.
- Distance: rank correlation 0.90; places a median 3,747 km away are 29.3 times farther than places a median 128 km away, but only 4.8 times farther out on the map.
- Scale: the Holy Land is drawn at 4.5 times the map's average, Egypt 1.9, British Isles 1.5; India and Central Asia 0.71.
- Britain and Ireland: 8.1% of the names, 0.4% of the land of Africa, Asia and Europe.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded; images in `img/`). |
| `header.png` | Social card, 1200 x 630. |
| `img/miller.jpg`, `img/photo.jpg` | Konrad Miller's 1896 facsimile (cropped, 3000 px) and the photograph of the map (public domain). |
| `data/names.csv` | All 1,025 index names: index entry, type, pages, part of the map, class, located or not, position on the facsimile, the book's identification and its words, real-world position and its source (book, Pleiades, Natural Earth), Pleiades id, and the OCR text of the book where the name is discussed. |
| `data/located.csv` | The 164 inscriptions located on the facsimile: pixel positions on the facsimile and the photograph, confidence, identification, coordinates, distance and bearing from Jerusalem on the map and in reality, best-fit position and displacement. |
| `data/map_positions.csv` | My by-eye positions on the facsimile (input). |
| `data/control_points.csv` | Features used to fit the facsimile to the photograph. |
| `data/regions.csv` | Distortion by region. |
| `data/book_pages.json.gz` | OCR text of Bevan and Phillott (1873), pages 1 to 174 (public domain). |
| `data/results.json`, `data/site.json`, `data/world.json`, `data/fit.json`, `data/sources.json`, `data/names.json` | Every number used; page data; outlines; fit; source facts; all names (JSON). |
| `code/` | Scripts, run in order, the page, paper and blog templates, `reading.py` (hand decisions: identifications, classes, rejected matches) and `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Inventory: the book's "Index of the names of places and objects [on the] Hereford Mappa Mundi", parsed from the Internet Archive OCR, OCR errors in names and ten page numbers corrected. Part of the map = the chapter of the first page cited.
- Classes: the book's four kinds of material (Introduction, section 11) by a fixed rule: frame and natural history excluded; legendary list; Biblical sections (pp. 25 to 26, 77 to 81, 85 to 86) plus named Biblical places; medieval = British Isles (except five Roman-derived names), a list of post-Roman European places, and six names in Asia; classical = the rest. Lists in `code/reading.py`.
- Positions: 164 inscriptions located by eye on Miller's facsimile (119 clear, 45 with some doubt), carried to the photograph by an affine fit on 9 control features (RMS 44 px).
- Real places: the book's identification for located inscriptions; Pleiades name matches (exact and close spellings, within the right part of the world, each checked; 78 rejected) for the rest.
- Distortion: bearings and distances from Jerusalem on the map (east up; radius = Jerusalem to Paradise and to the Pillars of Hercules) and on the globe; regional scale from pairs of located places at least 100 km apart; best-fit similarity transform onto an azimuthal equidistant projection centred on Jerusalem.
- Caveats: the index records names, not pictures; classes are judgements under a stated rule; the 1873 identifications are the Victorians'; located places favour legible, well-known towns; the photograph is low resolution.

## How to rerun

Needs Python 3 with numpy, pandas, scipy, shapely, pyproj, matplotlib, Pillow and fontTools, xelatex and pdftotext; node with Playwright for `code/qa.js`. Steps 01 to 03 read `raw/` (not published: the Internet Archive and Wikimedia texts in `hereford_texts.json`, the two map images, Pleiades CSVs) and Natural Earth from `/home/claude/newdata/raw/geo/`; from step 04 on only `data/` and `img/` are needed. Intermediate files go to `/dev/shm/mappamundi/work` (set `MMTMP` to change).

```
python3 code/01_parse.py        # book pages, index, where each name is discussed
python3 code/02_geo.py          # outlines, classes, real-world positions, names.json
python3 code/03_fit.py          # facsimile to photograph fit, web images
python3 code/04_results.py      # results.json, tables, page data
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 reddit/collage.py       # collage
python3 code/08_readme.py       # README, LICENSE, Reddit post
python3 code/09_release.py      # blog post, Zenodo files
```

## Sources and licences

- Bevan, W. L. and Phillott, H. W. (1873) Mediaeval Geography: an essay in illustration of the Hereford Mappa Mundi. London: E. Stanford. https://archive.org/details/medivalgeograph00unkngoog. Public domain.
- Miller, K. (1896) facsimile of the Hereford map, Wikimedia Commons (https://commons.wikimedia.org/wiki/File:1896_facsimile_of_the_Hereford_Mappa_Mundi_by_Konrad_Miller.jpg), public domain; Miller, K. (1903) Die Herefordkarte, https://archive.org/details/bub_gb_yJzVAAAAMAAJ, public domain (cross-checks).
- Photograph of the map: Wikimedia Commons, https://commons.wikimedia.org/wiki/File:Hereford_Mappa_Mundi_1300.jpg, public domain.
- Pleiades: a gazetteer of past places, version 4.1, https://pleiades.stoa.org/. CC BY 3.0.
- English Wikipedia, "Hereford Mappa Mundi" (revision 1381220355), CC BY-SA 4.0, for facts quoted in the text.
- Natural Earth (public domain). Optional relief tiles on the page: Esri.

## Citation

Hotham, T. (2026) The world according to the Hereford Mappa Mundi: a medieval map of the world set against a modern one. Zenodo. https://doi.org/10.5281/zenodo.23878612

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
