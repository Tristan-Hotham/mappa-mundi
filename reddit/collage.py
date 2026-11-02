"""Reddit collage (2400 x 3200): the Hereford map beside a modern map, how big each region is drawn, and the four kinds
of material. Light background; labels sit on plain sea or paper; numbers from data/results.json."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from figstyle import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
LOC = pd.DataFrame(SITE["located"], columns=SITE["loc_cols"]); LOC["klass"] = LOC.cls.map(lambda c: KL[c])
FAC = facsimile(); FW, FH = FAC.size
HALO = [pe.withStroke(linewidth=4, foreground=SEA)]
fig = plt.figure(figsize=(8, 32 / 3), dpi=300, facecolor=BG)
fig.text(.05, .955, "The world according to the", fontproperties=DISPB, fontsize=22, color=FG)
fig.text(.05, .918, "Hereford Mappa Mundi, about 1300", fontproperties=DISP, fontsize=28, color=RED)
fig.text(.05, .893, f"The largest medieval world map that survives, set against a modern one:", fontsize=8.6, color=MUT)
fig.text(.05, .878, f"{R['located']['n']} inscriptions located by eye, {R['source']['n']:,} names from an 1873 index.", fontsize=8.6, color=MUT)

# the medieval map
a1 = fig.add_axes([.03, .44, .47, .43]); a1.imshow(FAC); a1.set_xlim(0, FW); a1.set_ylim(FH, 0); a1.axis("off")
for c in KL:
    d = LOC[LOC.klass == c]; a1.scatter(d.x, d.y, s=7, c=KC[c], edgecolors="white", linewidths=.3, zorder=5)
fig.text(.04, .432, "The map (Konrad Miller's 1896 facsimile)", fontproperties=DISPB, fontsize=11, color=FG)
fig.text(.04, .418, "east is up: Asia on top, Europe bottom left, Africa", fontsize=7.4, color=MUT)
fig.text(.04, .406, "bottom right, Britain squeezed into the corner", fontsize=7.4, color=MUT)

# the modern map
a2 = fig.add_axes([.52, .56, .46, .31]); world(a2, (-25, 92, 3, 68), aspect_lat=38); a2.set_anchor("N")
for c in KL:
    d = LOC[(LOC.klass == c) & LOC.lat.notna()]; a2.scatter(d.lon, d.lat, s=7, c=KC[c], edgecolors="white", linewidths=.3, zorder=5)
for t, lo, la, ha in (("London", 3.5, 56.5, "left"), ("Iceland", -21, 60.8, "center"), ("Santiago", -15, 42.5, "center"), ("Rome", 12.5, 39.7, "center"),
                      ("Carthage", 2.5, 38.0, "center"), ("Constantinople", 34.6, 43.3, "center"), ("Jerusalem", 30.5, 33.0, "right"), ("Sri Lanka", 79, 4.6, "center")):
    a2.text(lo, la, t, ha=ha, va="center", fontsize=5.4 if t == "Constantinople" else 6.6, color=FG, path_effects=HALO, zorder=8)
fig.text(.53, .605, "The same places today", fontproperties=DISPB, fontsize=11, color=FG)
fig.text(.53, .591, f"{R['located']['real']} identified with a real place by the 1873 book", fontsize=7.4, color=MUT)
fig.legend(handles=[Line2D([], [], marker="o", ls="", mfc=KC[c], mec="white", ms=6, label=f"{c} ({R['classes'][c]['pct']:.0f}% of all names)") for c in KL],
           loc="upper left", bbox_to_anchor=(.52, .585), ncol=1, frameon=False, fontsize=7.4)

# stretch bars
D = sorted([r for r in SITE["regions"] if r["stretch"]], key=lambda r: r["stretch"])
a3 = fig.add_axes([.27, .1, .3, .26]); a3.set_facecolor(BG)
for i, r in enumerate(D):
    s = r["stretch"]; a3.barh(i, np.log(s), color=RED if s >= 1 else BLUE, height=.66, alpha=.9)
    a3.text(np.log(s) + (.04 if s >= 1 else -.04), i, f"x{s:.1f}" if s >= 1 else f"x{s:.2f}", va="center", ha="left" if s >= 1 else "right", fontsize=6.6, color=FG)
a3.axvline(0, color=FG, lw=.8); a3.set_yticks(range(len(D))); a3.set_yticklabels([r["region"] for r in D], fontsize=6.8); a3.tick_params(axis="y", length=0)
a3.set_xticks(np.log([.5, 1, 2, 4])); a3.set_xticklabels(["half", "average", "x2", "x4"], fontsize=6.5); a3.set_xlim(np.log(.45), np.log(6.5))
for s_ in ("top", "right", "left"): a3.spines[s_].set_visible(False)
fig.text(.04, .385, "How big each region is drawn", fontproperties=DISPB, fontsize=11, color=FG)
fig.text(.04, .371, "relative to the map as a whole (pairs of located places)", fontsize=7.4, color=MUT)

# stat column
st = [(f"{R['bearing']['within45_pct']:.0f}%", "of located places point the right way\nfrom Jerusalem, within 45 degrees"),
      (f"{R['dist']['km_ratio']:.0f}x vs {R['dist']['frac_ratio']:.1f}x", "far places are 29 times farther away\nbut only 4.8 times farther out on the map"),
      (f"{R['britain']['names_pct']:.0f}%", f"of the names are in Britain and Ireland,\n{R['britain']['area_pct']:.1f}% of the land of the three continents"),
      (f"{R['classes']['Classical']['pct']:.0f}%", "of the names come from Greek and Roman\nbooks; only Britain is mostly medieval")]
for i, (big, small) in enumerate(st):
    y = .47 - i * .095
    fig.text(.6, y, big, fontproperties=DISP, fontsize=20, color=[RED, BLUE, KC["Medieval"], GOLD][i], va="top")
    fig.text(.6, y - .036, small, fontsize=7.2, color=FG, va="top", linespacing=1.35)
fig.text(.05, .045, "Sources: Bevan and Phillott (1873) Mediaeval Geography; K. Miller (1896) facsimile, Wikimedia Commons (public domain); Pleiades (CC BY 3.0);",
         fontsize=6.4, color=MUT)
fig.text(.05, .033, "Natural Earth. Positions on the map located by eye. Dr Tristan Hotham · maps.tristanhotham.com/mappa-mundi", fontsize=6.4, color=MUT)
out = os.path.join(ROOT, "reddit", "hereford_mappa_mundi.png")
fig.savefig(out, dpi=300, facecolor=BG); plt.close(fig)
from PIL import Image
assert Image.open(out).size == (2400, 3200), Image.open(out).size
assert round(R["dist"]["km_ratio"]) == 29 and round(R["dist"]["frac_ratio"], 1) == 4.8
print("collage", out)
