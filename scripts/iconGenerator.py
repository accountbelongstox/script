import os
from PIL import Image, ImageOps, IcnsImagePlugin
from datetime import datetime

class IconGenerator:

    def __init__(self):
        pass

    def resize_image(self, size):
        with Image.open(self.input_image) as image:
            image = image.resize(size, Image.Resampling.LANCZOS)
            return image

    def create_icns(self, output_path):
        sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
        
        icon_images = []
        for size in sizes:
            icon_images.append(self.resize_image(size))

        icon_images[0].save(output_path, format='ICNS', append_images=icon_images[1:])

    def generate_icons(self,input_image):
        self.input_image = input_image
        sizes = {
            '128x128.png': (128, 128),
            '16x16.png': (16, 16),
            '128x128@2x.png': (256, 256),
            '256x256.png': (256, 256),
            '200x200.png': (200, 200),
            '512x512.png': (512, 512),
            '32x32.png': (32, 32),
            '64x64.png': (64, 64),
            'favicon.png': (32, 32),
            'icon.ico': (256, 256),  
            'icon.png': (512, 512),  
            'Square107x107Logo.png': (107, 107),
            'Square142x142Logo.png': (142, 142),
            'Square150x150Logo.png': (150, 150),
            'Square284x284Logo.png': (284, 284),
            'Square30x30Logo.png': (30, 30),
            'Square310x310Logo.png': (310, 310),
            'Square44x44Logo.png': (44, 44),
            'Square71x71Logo.png': (71, 71),
            'Square89x89Logo.png': (89, 89),
            'StoreLogo.png': (50, 50) 
        }

        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        output_dir = f".icons_design_{current_time}"  # Add current time to the output directory name
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename, size in sizes.items():
            output_path = os.path.join(output_dir, filename)
            img = self.resize_image(size)
            img.save(output_path)

        self.create_icns(os.path.join(output_dir, "icon.icns"))

if __name__ == "__main__":
    input_image="logo-ct.png"
    generator = IconGenerator()
    generator.generate_icons(input_image)
