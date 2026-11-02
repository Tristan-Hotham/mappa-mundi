"""The two images of the map, and positions on them.

  * Positions were located by eye on Konrad Miller's 1896 facsimile (raw/hereford_miller_1896.jpg, 3840 x 4708 px):
    data/map_positions.csv gives the pixel position of each inscription's town picture or, where there is none, the
    middle of its label, with my confidence (high: label read clearly; medium: label worn, crowded or ambiguous).
  * The photograph of the original (raw/hereford_1300.jpg) is a low-resolution image enlarged to 3840 x 4339 px, so
    its labels cannot be read. Positions are carried over to it by an affine fit (least squares) on nine features
    that are clear on both images (data/control_points.csv). The fit's residuals are reported: the facsimile is a
    hand-made copy, and the vellum has shrunk and buckled, so a straight affine fit is only approximate.
  * Web images: img/miller.jpg (the facsimile, cropped to the map and reduced) and img/photo.jpg (the photograph),
    plus small previews. Their pixel frames are recorded in data/fit.json for the page."""
import numpy as np, pandas as pd
from PIL import Image
from common import *

Image.MAX_IMAGE_PIXELS = None
CP = pd.read_csv(f"{DATA}/control_points.csv")
A = np.c_[CP.x_miller, CP.y_miller, np.ones(len(CP))]
cx, *_ = np.linalg.lstsq(A, CP.x_photo, rcond=None)
cy, *_ = np.linalg.lstsq(A, CP.y_photo, rcond=None)
res = np.hypot(A @ cx - CP.x_photo, A @ cy - CP.y_photo)
# leave-one-out error: how far each control point lands when it is left out of the fit
loo = []
for i in range(len(CP)):
    m = np.arange(len(CP)) != i
    ax, *_ = np.linalg.lstsq(A[m], CP.x_photo[m], rcond=None); ay, *_ = np.linalg.lstsq(A[m], CP.y_photo[m], rcond=None)
    loo.append(float(np.hypot(A[i] @ ax - CP.x_photo[i], A[i] @ ay - CP.y_photo[i])))
fit = {"ax": [round(float(v), 6) for v in cx], "ay": [round(float(v), 6) for v in cy], "n": len(CP),
       "rms_px": round(float(np.sqrt((res ** 2).mean())), 1), "max_px": round(float(res.max()), 1), "loo_median_px": round(float(np.median(loo)), 1),
       "photo_w": 3840, "photo_h": 4339}
print("affine miller->photo", fit)

# ---------- web images ----------
MC = (40, 200, 3800, 4400)                      # crop of the facsimile sheet to the map and its frame
M = Image.open(f"{RAW}/hereford_miller_1896.jpg").convert("RGB").crop(MC)
MW = 3000; mh = round(M.height * MW / M.width)
M.resize((MW, mh), Image.LANCZOS).save(f"{IMG}/miller.jpg", quality=80, optimize=True, progressive=True)
M.resize((900, round(M.height * 900 / M.width)), Image.LANCZOS).save(f"{IMG}/miller_small.jpg", quality=80, optimize=True)
P = Image.open(f"{RAW}/hereford_1300.jpg").convert("RGB")
PW = 1500; ph = round(P.height * PW / P.width)
P.resize((PW, ph), Image.LANCZOS).save(f"{IMG}/photo.jpg", quality=82, optimize=True, progressive=True)
fit.update({"miller_crop": MC, "miller_web": [MW, mh], "photo_web": [PW, ph], "miller_full": [3840, 4708]})
jsave(fit, f"{DATA}/fit.json", indent=1)
print({f: os.path.getsize(f"{IMG}/{f}") // 1024 for f in os.listdir(IMG)})
