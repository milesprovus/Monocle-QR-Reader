import asyncio
import io
import PIL.Image as Image
import time
from brilliant import Monocle
import binascii
import cv2
import webbrowser
from urllib.parse import urlparse

remote_script = '''
import bluetooth, camera, time, led
camera.capture()
time.sleep_ms(100)
while data := camera.read(bluetooth.max_length()):
    led.on(led.GREEN)
    while True:
        try:
            bluetooth.send(data)
        except OSError:
            continue
        break
    led.off(led.GREEN)
'''

async def get_image():
    async with Monocle() as m:
        await m.send_command(remote_script)
        return await m.get_all_data()


async def detect():
    image = cv2.imread('output.jpg')

        # Create a QR code detector object
    detector = cv2.QRCodeDetector()

        # Detect and decode the QR code
    data, vertices_array, _ = detector.detectAndDecode(image)

    if data:
        print("QR Code Data:")
        print(data)
        return data
    else:
        print("No QR Code found in the image.")
        return ("no data found")

async def display(data):
    async with Monocle() as m:
        await m.send_command(f"import display \ntext = display.Text('{data}', 100, 0, display.WHITE, justify=display.TOP_LEFT) \ndisplay.show(text)")
        
async def check(data):
    try:
        result = urlparse(data)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def main():
    data = asyncio.run(get_image())
    print(data)
    img = Image.open(io.BytesIO(data))
    jpgImg = img.convert('RGB')
    jpgImg.save('output.jpg')
    qr_data = asyncio.run(detect())
    checkImg = asyncio.run(check(qr_data))
    if checkImg:
        webbrowser.open(qr_data)
        qr_data = urlparse(qr_data).netloc
        asyncio.run(display(qr_data))
    else:
        asyncio.run(display(qr_data))
        
main()