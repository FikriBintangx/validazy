from PIL import Image

im = Image.open('fox-dir.webp')
w, h = im.size
cw, ch = w // 3, h // 3

# Crop all 9 frames and save to check
for r in range(3):
    for c in range(3):
        box = (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)
        cropped = im.crop(box)
        cropped.save(f'frame_{r}_{c}.png')

print("Successfully sliced 9 frames! Frame sizes:", cw, ch)
