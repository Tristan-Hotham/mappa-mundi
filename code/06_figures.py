"""Header card, blog figures (release/blog/b_*.png, 1800 px wide) and paper figures (release/paper/f_*.png).
Numbers from data/results.json; positions from data/located.csv and data/site.json."""
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch
from figstyle import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
os.makedirs(BL, exist_ok=True); os.makedirs(PA, exist_ok=True)
LC = {k: i for i, k in enumerate(SITE["loc_cols"])}
LOC = pd.DataFrame(SITE["located"], columns=SITE["loc_cols"])
LOC["klass"] = LOC.cls.map(lambda c: KL[c])
REAL = LOC[LOC.lat.notna()].drop_duplicates(["lat", "lon"])
REAL = REAL[REAL.true_km > 1]
REGS = [r["region"] for r in SITE["regions"]]; RC = dict(zip(REGS, RCOL))
FAC = facsimile(); FW, FH = FAC.size
HALO = [pe.withStroke(linewidth=3.2, foreground="#FFFCF4")]
JER = SITE["jer"]


def both(fig, name, blog=True):
    fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    if blog:
        fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def dots_fac(ax, df, s=26, lw=.7):
    for c in KL:
        d = df[df.klass == c]
        ax.scatter(d.x, d.y, s=s, c=KC[c], edgecolors="white", linewidths=lw, zorder=5)


def dots_geo(ax, df, s=26, lw=.7):
    for c in KL:
        d = df[(df.klass == c) & df.lat.notna()]
        ax.scatter(d.lon, d.lat, s=s, c=KC[c], edgecolors="white", linewidths=lw, zorder=5)


def label(ax, x, y, t, dx=0, dy=0, ha="left", fs=10, col=FG, weight=None):
    ax.annotate(t, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=fs, color=col, path_effects=HALO, zorder=8,
                fontweight=weight)


def find(name, page=None):
    d = LOC[(LOC["name"] == name) & ((LOC.page == page) if page else True)]
    return d.iloc[0]


GEOEXT = (-26, 98, -1, 68)
LAB = [("Jerusalem", None, "Jerusalem"), ("Londonia", None, "London"), ("Roma", None, "Rome"), ("Babel Tttkris", None, "Babylon"), ("Samarcan", None, "Samarkand"),
       ("Tapbana", None, "Sri Lanka"), ("Parisius", None, "Paris"), ("Constantinopolis", None, "Constantinople"), ("Babylonia", 86, "Cairo"), ("Ysland", None, "Iceland"),
       ("Polibrota", None, "Patna"), ("Cartago", None, "Carthage"), ("Compostella", None, "Santiago")]
# label offsets (points) on the facsimile (east up) and on the modern map, chosen to sit on plain paper or sea
OFF_F = {"Jerusalem": (9, -10, "left"), "London": (-9, 10, "right"), "Rome": (9, 0, "left"), "Babylon": (10, 0, "left"), "Samarkand": (0, 11, "center"),
         "Sri Lanka": (10, 0, "left"), "Paris": (9, 6, "left"), "Constantinople": (-9, 9, "right"), "Cairo": (10, 0, "left"), "Iceland": (10, 0, "left"),
         "Patna": (-10, 0, "right"), "Carthage": (10, 0, "left"), "Santiago": (8, -8, "left")}
OFF_G = {"Jerusalem": (8, -10, "left"), "London": (-8, 8, "right"), "Rome": (6, 8, "left"), "Babylon": (8, 4, "left"), "Samarkand": (0, 10, "center"),
         "Sri Lanka": (-8, -6, "right"), "Paris": (-8, -4, "right"), "Constantinople": (6, 9, "left"), "Cairo": (-8, -6, "right"), "Iceland": (8, 0, "left"),
         "Patna": (6, 8, "left"), "Carthage": (-6, -9, "right"), "Santiago": (-8, 0, "right")}

# ---------- 1. the two maps ----------
fig = plt.figure(figsize=(12, 6.4), facecolor=BG)
a1 = fig.add_axes([.01, .02, .40, .87]); a2 = fig.add_axes([.43, .12, .56, .74])
a1.imshow(FAC, zorder=1); a1.set_xlim(0, FW); a1.set_ylim(FH, 0); a1.axis("off")
dots_fac(a1, LOC, s=16, lw=.5)
for n, pg, t in LAB:
    r = find(n, pg); dx, dy, ha = OFF_F[t]; label(a1, r.x, r.y, t, dx, dy, ha, fs=8.5)
world(a2, GEOEXT, aspect_lat=35)
dots_geo(a2, LOC, s=16, lw=.5)
for n, pg, t in LAB:
    r = find(n, pg); dx, dy, ha = OFF_G[t]; label(a2, r.lon, r.lat, t, dx, dy, ha, fs=8.5)
fig.text(.01, .955, "The Hereford map, about 1300 (east at the top)", fontproperties=DISPB, fontsize=15, color=FG)
fig.text(.43, .955, "The same places today (north at the top)", fontproperties=DISPB, fontsize=15, color=FG)
fig.legend(handles=[Line2D([], [], marker="o", ls="", mfc=KC[c], mec="white", ms=8, label=c) for c in KL], loc="lower left", bbox_to_anchor=(.43, .02), ncol=4, frameon=False, fontsize=10)
fig.text(.43, .905, f"{R['located']['n']} inscriptions located by eye on Miller's facsimile; {R['located']['real']} are real places", fontsize=9, color=MUT)
both(fig, "maps")

# ---------- 2. names by part and class ----------
P = [p for p in PARTS if p != "Frame and ocean"]
fig, ax = plt.subplots(figsize=(12, 5.2), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.17, right=.97, top=.84, bottom=.12)
for i, p in enumerate(P[::-1]):
    left = 0
    for c in KL:
        v = R["part_class"][p][c]
        ax.barh(i, v, left=left, color=KC[c], height=.62, edgecolor=BG, lw=.6); left += v
    ax.text(left + 4, i, f"{R['part_class'][p]['n']}", va="center", fontsize=11, color=FG)
ax.set_yticks(range(len(P))); ax.set_yticklabels(P[::-1], fontsize=12); spines(ax); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=RULE); ax.set_axisbelow(True); ax.set_xlabel("names in Bevan and Phillott's index")
fig.text(.02, .93, "A thousand names, by part of the world and where they come from", fontproperties=DISPB, fontsize=17, color=FG)
fig.legend(handles=[Patch(color=KC[c], label=f"{c} ({R['classes'][c]['pct']:.0f}%)") for c in KL], loc="upper right", bbox_to_anchor=(.97, .9), ncol=4, frameon=False, fontsize=10.5)
both(fig, "parts")

# ---------- 3. bearings ----------
fig, ax = plt.subplots(figsize=(12, 7.2), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.08, right=.7, top=.88, bottom=.1)
jx, jy = SITE["jer_px"]
tb = lambda r: float(bearing(JER[0], JER[1], r.lat, r.lon))
mb = lambda r: float((np.degrees(np.arctan2(-(r.y - jy), -(r.x - jx))) + 360) % 360)
for g in REGS:
    d = REAL[REAL.region == g]
    xs, ys = [], []
    for _, r in d.iterrows():
        a, b = tb(r), mb(r)
        if b - a > 180: b -= 360
        if a - b > 180: b += 360
        xs.append(a); ys.append(b)
    ax.scatter(xs, ys, s=34, c=RC[g], edgecolors="white", linewidths=.6, label=g, zorder=3)
ax.plot([0, 360], [0, 360], ls="--", color=MUT, lw=1, zorder=2)
for v in (0, 90, 180, 270, 360):
    ax.axhline(v, color=RULE, lw=.8, zorder=1); ax.axvline(v, color=RULE, lw=.8, zorder=1)
ax.set_xticks([0, 90, 180, 270, 360]); ax.set_xticklabels(["N", "E", "S", "W", "N"]); ax.set_yticks([0, 90, 180, 270, 360]); ax.set_yticklabels(["N", "E", "S", "W", "N"])
ax.set_xlim(-5, 365); ax.set_ylim(-5, 365); spines(ax)
ax.set_xlabel("true bearing from Jerusalem"); ax.set_ylabel("bearing on the map (east at the top)")
ax.legend(loc="center left", bbox_to_anchor=(1.02, .5), frameon=False, fontsize=10)
fig.text(.02, .94, f"Which way from Jerusalem: {R['bearing']['within45_pct']:.0f}% of located places point within 45 degrees of the right way", fontproperties=DISPB, fontsize=16, color=FG)
both(fig, "bearing")

# ---------- 4. distances ----------
fig, ax = plt.subplots(figsize=(12, 6.6), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.08, right=.7, top=.86, bottom=.12)
RAD = SITE["radius_px"]
for g in REGS:
    d = REAL[REAL.region == g]
    f = np.hypot(d.x - jx, d.y - jy) / RAD
    ax.scatter(d.true_km.clip(lower=5), f, s=34, c=RC[g], edgecolors="white", linewidths=.6, label=g, zorder=3)
ax.set_xscale("log"); ax.set_xlim(5, 8000); ax.set_ylim(0, 1.08); spines(ax); ax.grid(color=RULE); ax.set_axisbelow(True)
ax.axhline(1, color=FG, lw=1); ax.text(6, 1.02, "edge of the world", fontsize=10, color=MUT)
ax.set_yticks([0, .25, .5, .75, 1]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.set_xticks([10, 100, 1000, 5000]); ax.set_xticklabels(["10 km", "100 km", "1,000 km", "5,000 km"])
ax.set_xlabel("true distance from Jerusalem (log scale)"); ax.set_ylabel("share of the way to the map's rim")
ax.legend(loc="center left", bbox_to_anchor=(1.02, .5), frameon=False, fontsize=10)
fig.text(.02, .93, f"Distance from Jerusalem: {R['dist']['km_ratio']:.0f} times farther in reality, {R['dist']['frac_ratio']:.1f} times farther on the map", fontproperties=DISPB, fontsize=16, color=FG)
both(fig, "distance")

# ---------- 5. stretch ----------
D = sorted([r for r in SITE["regions"] if r["stretch"]], key=lambda r: r["stretch"])
fig, ax = plt.subplots(figsize=(12, 5.6), facecolor=BG); ax.set_facecolor(BG); fig.subplots_adjust(left=.25, right=.95, top=.86, bottom=.12)
for i, r in enumerate(D):
    s = r["stretch"]; ax.barh(i, np.log(s), color=RED if s >= 1 else BLUE, height=.62, alpha=.88)
    ax.text(np.log(s) + (.03 if s >= 1 else -.03), i, f"x{s:.2f}" if s < 1 else f"x{s:.1f}", va="center", ha="left" if s >= 1 else "right", fontsize=11, color=FG)
ax.axvline(0, color=FG, lw=1); ax.set_yticks(range(len(D))); ax.set_yticklabels([r["region"] for r in D], fontsize=11.5); ax.tick_params(axis="y", length=0)
ax.set_xticks(np.log([.5, 1, 2, 4])); ax.set_xticklabels(["half", "average", "double", "four times"]); spines(ax); ax.spines["left"].set_visible(False)
ax.set_xlim(np.log(.45), np.log(6)); ax.set_xlabel("scale relative to the map as a whole (log)")
fig.text(.02, .93, "How big each region is drawn: the Holy Land swells, India shrinks", fontproperties=DISPB, fontsize=17, color=FG)
both(fig, "stretch")

# ---------- 6. displacement arrows ----------
fig = plt.figure(figsize=(12, 7.2), facecolor=BG); ax = fig.add_axes([.01, .08, .98, .8])
world(ax, (-26, 98, -2, 68), aspect_lat=35)
for _, r in REAL.iterrows():
    if pd.isna(r.imp_lat): continue
    ax.add_patch(FancyArrowPatch((r.lon, r.lat), (r.imp_lon, r.imp_lat), arrowstyle="-|>", mutation_scale=7, color=RC[r.region], lw=.9, alpha=.85, zorder=4))
    ax.scatter([r.lon], [r.lat], s=12, c=RC[r.region], zorder=5, edgecolors="white", linewidths=.4)
ax.scatter([JER[1]], [JER[0]], s=60, facecolors="none", edgecolors=RED, linewidths=2, zorder=6)
label(ax, JER[1], JER[0], "Jerusalem", 8, -10, fs=9.5, weight="bold")
fig.text(.01, .935, "If the Hereford map were an ordinary map: from each real place to where the map puts it", fontproperties=DISPB, fontsize=16, color=FG)
fig.text(.01, .9, f"Best rotation and scale fitted to {len(REAL)} located places; median shift {R['fit']['median_disp_km']} km. Colours as in the bearing chart.", fontsize=9.5, color=MUT)
both(fig, "arrows")

# ---------- 7. Britain, close up ----------
B = LOC[(LOC.part == PARTS.index("British Isles")) | (LOC["name"] == "Orcades")]
fig = plt.figure(figsize=(12, 6.4), facecolor=BG)
a1 = fig.add_axes([.01, .07, .46, .8]); a2 = fig.add_axes([.52, .07, .47, .8])
x0, x1, y0, y1 = B.x.min() - 40, B.x.max() + 40, B.y.min() - 40, B.y.max() + 40
a1.imshow(FAC.crop((int(x0), int(y0), int(x1), int(y1))), extent=(x0, x1, y1, y0)); a1.set_xlim(x0, x1); a1.set_ylim(y1, y0); a1.axis("off")
dots_fac(a1, B, s=34)
world(a2, (-11, 3, 49.6, 59.6))
dots_geo(a2, B, s=34)
BL_ = [("Londonia", "London"), ("Eboracum", "York"), ("Lincoln", "Lincoln"), ("Hreford", "Hereford"), ("Cadan", "Caen"), ("Divelin", "Dublin"), ("Edenburgh", "Edinburgh"), ("Excestria", "Exeter")]
OF1 = {"London": (8, 8, "left"), "York": (8, 8, "left"), "Lincoln": (8, -6, "left"), "Hereford": (-8, -8, "right"), "Caen": (8, 0, "left"), "Dublin": (-8, 6, "right"), "Edinburgh": (0, 11, "center"), "Exeter": (8, -6, "left")}
OF2 = {"London": (8, -4, "left"), "York": (8, 4, "left"), "Lincoln": (8, -2, "left"), "Hereford": (-8, 0, "right"), "Caen": (8, 0, "left"), "Dublin": (-8, 0, "right"), "Edinburgh": (8, 4, "left"), "Exeter": (-8, -4, "right")}
for n, t in BL_:
    r = find(n); dx, dy, ha = OF1[t]; label(a1, r.x, r.y, t, dx, dy, ha, fs=9.5)
    dx, dy, ha = OF2[t]; label(a2, r.lon, r.lat, t, dx, dy, ha, fs=9.5)
fig.text(.01, .93, "Britain and Ireland on the map (east at the top) and today", fontproperties=DISPB, fontsize=17, color=FG)
fig.text(.01, .02, "Caen, in Normandy, is drawn in Devon, 'by a strange blunder' (Bevan and Phillott 1873).", fontsize=9, color=MUT)
both(fig, "britain")

# ---------- header card 1200 x 630 ----------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
a1 = fig.add_axes([.56, .02, .42, .96]); a1.imshow(FAC); a1.set_xlim(0, FW); a1.set_ylim(FH, 0); a1.axis("off"); dots_fac(a1, LOC, s=10, lw=.35)
fig.text(.04, .8, "Mappa", fontproperties=DISP, fontsize=64, color=FG)
fig.text(.04, .64, "Mundi", fontproperties=DISP, fontsize=64, color=RED)
fig.text(.045, .52, "The world according to the Hereford map, about 1300,", fontproperties=SERP, fontsize=17, color=FG)
fig.text(.045, .465, "set against a modern one", fontproperties=SERP, fontsize=17, color=FG)
a3 = fig.add_axes([.04, .07, .48, .34]); world(a3, (-20, 92, 5, 66), aspect_lat=35); dots_geo(a3, LOC, s=7, lw=.3)
fig.text(.045, .43, f"{R['source']['n']:,} names  ·  Jerusalem at the centre  ·  east at the top", fontsize=10.5, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)
from PIL import Image as _I
assert _I.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
print("figures", sorted(os.listdir(BL)))
