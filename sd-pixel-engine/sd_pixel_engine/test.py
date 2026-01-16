from mss import mss
from PIL import Image
 
with mss() as sct:
    monitor = sct.monitors[0]  # all monitors combined
    screenshot = sct.grab(monitor)
    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    img.save("all_monitors3.png")