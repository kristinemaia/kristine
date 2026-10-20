"""Decupează bolul cu salata (PNG transparent) din poza originală, pentru pagina 25 din e-book.
Rulezi: python3 brand/ebook/bol/cutout.py  (poza sursă: calea SRC)"""
import cv2, numpy as np
SRC = '/root/.claude/uploads/76209f14-ae6c-52ab-b9be-ac2315dadd03/d69ed469-image.jpg'
img = cv2.imread(SRC); h, w = img.shape[:2]
# lingura de la marginea de jos și vârful furculiței de sus: șterse din interior
sp = np.zeros((h, w), np.uint8); cv2.ellipse(sp, ((778, 668), (190, 200), 0), 255, -1); cv2.rectangle(sp, (790, 150), (900, 215), 255, -1)
bowl = np.zeros((h, w), np.uint8); cv2.ellipse(bowl, ((776, 418), (632, 552), -4), 255, -1)
# nu atinge salata: jos, zona ștearsă se oprește la marginea bolului
sp[:610, :] = 0; sp[150:215, 790:900] = 255
# în afara bolului punem gri de oțel, ca lemnul să nu intre în zonele șterse
steel = img.copy(); steel[bowl == 0] = (120, 120, 125)
steel = cv2.inpaint(steel, cv2.bitwise_and(sp, bowl), 11, cv2.INPAINT_TELEA)
img = np.where(bowl[..., None] > 0, steel, img)
# conturul bolului, ușor tras înăuntru, cu margine fină
m = np.zeros((h, w), np.uint8); cv2.ellipse(m, ((776, 418), (626, 546), -4), 255, -1)
m = cv2.GaussianBlur(m, (0, 0), 1.4)
rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA); rgba[..., 3] = m
ys, xs = np.where(m > 10); pad = 10
crop = rgba[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]
cv2.imwrite('bol-ton-fasole-transparent.png', crop)
ch, cw = crop.shape[:2]
bg = np.full((ch, cw, 3), (225, 225, 225), np.uint8); bg[::40, :] = 245
a = crop[..., 3:4] / 255.0; prev = (crop[..., :3] * a + bg * (1 - a)).astype(np.uint8)
cv2.imwrite('/tmp/claude-0/-home-user-kristine/76209f14-ae6c-52ab-b9be-ac2315dadd03/scratchpad/bol-prev.png', prev); print(crop.shape)
