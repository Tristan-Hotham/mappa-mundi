"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
s, c, b, g, pl, lo = R["source"], R["classes"], R["britain"], R["regions"], R["placed"], R["located"]
N = lambda v: f"{round(v):,}"
readme = f"""# The world according to the Hereford Mappa Mundi

The Hereford Mappa Mundi (about 1300), the largest surviving medieval map of the world, set against a modern map: the {N(s['n'])} names in Bevan and Phillott's 1873 index of the map, which real places they are, what share is Biblical, classical, medieval and legendary, and how the map distorts direction, distance and scale.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- Inventory: {N(s['n'])} names in the 1873 index: Asia {R['parts']['Asia']['n']}, Europe {R['parts']['Europe']['n']}, Africa {R['parts']['Africa']['n']}, seas and islands {R['parts']['Seas and islands']['n']}, British Isles {R['parts']['British Isles']['n']}, frame {R['parts']['Frame and ocean']['n']}.
- Classes (of {N(s['n_named'])} names, frame and natural history left out): classical {c['Classical']['n']} ({c['Classical']['pct']:.0f}%), medieval {c['Medieval']['n']} ({c['Medieval']['pct']:.0f}%), Biblical {c['Biblical']['n']} ({c['Biblical']['pct']:.0f}%), legendary {c['Legendary']['n']} ({c['Legendary']['pct']:.0f}%). All Biblical names are in Asia; {b['medieval_pct']:.0f}% of British names are medieval.
- Real places: {pl['n']} of {pl['n_real']} non-legendary names ({pl['pct']:.0f}%) have a real position, {pl['book']} from the book's identifications (hand-checked) and {pl['pleiades']} from Pleiades name matches. A lower bound.
- Direction: for {R['bearing']['n']} located real places, the median bearing error from Jerusalem (east up on the map) is {R['bearing']['median_abs_err']} degrees; {R['bearing']['within45_pct']:.0f}% are within 45 degrees. North Africa ({g['North Africa']['median_abs_brg_err']}) and Egypt ({g['Egypt and Sinai']['median_abs_brg_err']}) swing south.
- Distance: rank correlation {R['dist']['spearman']:.2f}; places a median {R['dist']['far_km']:,} km away are {R['dist']['km_ratio']:.1f} times farther than places a median {R['dist']['near_km']} km away, but only {R['dist']['frac_ratio']:.1f} times farther out on the map.
- Scale: the Holy Land is drawn at {g['Holy Land']['stretch']:.1f} times the map's average, Egypt {g['Egypt and Sinai']['stretch']:.1f}, British Isles {g['British Isles']['stretch']:.1f}; India and Central Asia {g['India and Central Asia']['stretch']:.2f}.
- Britain and Ireland: {b['names_pct']:.1f}% of the names, {b['area_pct']:.1f}% of the land of Africa, Asia and Europe.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded; images in `img/`). |
| `header.png` | Social card, 1200 x 630. |
| `img/miller.jpg`, `img/photo.jpg` | Konrad Miller's 1896 facsimile (cropped, 3000 px) and the photograph of the map (public domain). |
| `data/names.csv` | All {N(s['n'])} index names: index entry, type, pages, part of the map, class, located or not, position on the facsimile, the book's identification and its words, real-world position and its source (book, Pleiades, Natural Earth), Pleiades id, and the OCR text of the book where the name is discussed. |
| `data/located.csv` | The {lo['n']} inscriptions located on the facsimile: pixel positions on the facsimile and the photograph, confidence, identification, coordinates, distance and bearing from Jerusalem on the map and in reality, best-fit position and displacement. |
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
- Positions: {lo['n']} inscriptions located by eye on Miller's facsimile ({lo['high']} clear, {lo['medium']} with some doubt), carried to the photograph by an affine fit on {R['fit_photo']['n']} control features (RMS {R['fit_photo']['rms_px']:.0f} px).
- Real places: the book's identification for located inscriptions; Pleiades name matches (exact and close spellings, within the right part of the world, each checked; {pl['rejected']} rejected) for the rest.
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

- Bevan, W. L. and Phillott, H. W. (1873) Mediaeval Geography: an essay in illustration of the Hereford Mappa Mundi. London: E. Stanford. {BOOK_IA}. Public domain.
- Miller, K. (1896) facsimile of the Hereford map, Wikimedia Commons ({MILLER_URL}), public domain; Miller, K. (1903) Die Herefordkarte, {MILLER_IA}, public domain (cross-checks).
- Photograph of the map: Wikimedia Commons, {PHOTO_URL}, public domain.
- Pleiades: a gazetteer of past places, version {s['pleiades_version']}, https://pleiades.stoa.org/. CC BY 3.0.
- English Wikipedia, "Hereford Mappa Mundi" (revision {R['wiki']['revid']}), CC BY-SA 4.0, for facts quoted in the text.
- Natural Earth (public domain). Optional relief tiles on the page: Esri.

## Citation

Hotham, T. (2026) The world according to the Hereford Mappa Mundi: a medieval map of the world set against a modern one. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

lic = open("/home/claude/studies/rocket-launches/LICENSE", encoding="utf-8").read().split("\n\n\nThis licence covers")[0]
lic += """


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog post, the figures and the derived data
files in data/ are released under CC BY 4.0. The map images in img/ (Konrad
Miller's 1896 facsimile and the photograph of the Hereford Mappa Mundi, from
Wikimedia Commons) and the text of Bevan and Phillott (1873) in
data/book_pages.json.gz are in the public domain. Positions matched from the
Pleiades gazetteer are derived from Pleiades (pleiades.stoa.org), CC BY 3.0:
please credit Pleiades. Facts quoted from Wikipedia are CC BY-SA 4.0. Natural
Earth is public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)

post = f"""## Title

[OC] I put the Hereford Mappa Mundi (c. 1300) next to a real map. Its directions from Jerusalem are mostly right, but it draws the Holy Land {g['Holy Land']['stretch']:.1f}x bigger than the rest and Britain gets {b['names_pct']:.0f}% of its names

## Body

The Hereford Mappa Mundi is the largest medieval map of the world that survives: Jerusalem in the centre, east at the top, Paradise at the edge. I used the index of {N(s['n'])} names that two Victorian clergymen compiled in 1873 as its inventory, located {lo['n']} of the clearest inscriptions by eye on an 1896 facsimile, and put the {lo['real']} real places they identify on a modern map. Turned so east is up, {R['bearing']['within45_pct']:.0f}% of places point within 45 degrees of the right way from Jerusalem. But distance collapses: places {R['dist']['km_ratio']:.0f} times farther away are only {R['dist']['frac_ratio']:.1f} times farther out on the map. {c['Classical']['pct']:.0f}% of the names come from Greek and Roman books, {c['Biblical']['pct']:.0f}% from the Bible and {c['Legendary']['pct']:.0f}% are legend (dog-headed men, Gog and Magog); only Britain is mostly drawn from contemporary knowledge, with {b['names_pct']:.0f}% of the names on {b['area_pct']:.1f}% of the land. Caveats: positions located by eye; the classes are my judgement under a stated rule. Interactive side-by-side map: {PAGE}

## Source comment

Sources: Bevan and Phillott (1873) Mediaeval Geography (Internet Archive, public domain) for the index and identifications; Konrad Miller's 1896 facsimile and a photograph of the map (Wikimedia Commons, public domain); Pleiades gazetteer (CC BY 3.0); Natural Earth.

Tools: Python (pandas, scipy, pyproj, matplotlib); MapLibre for the interactive maps.

Interactive version: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}
"""
for t in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in t.replace("```", "").replace("|---|---|", ""), bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("readme, licence, post ok")
