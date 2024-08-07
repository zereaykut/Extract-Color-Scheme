import argparse
import subprocess as sp
import os
import json
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.image as mpimg

class ColorSchemeExtractor:
    def __init__(self, colors, image_path, output_name):
        self.n_colors = colors
        self.image_path = image_path
        self.output_name = output_name
        self.image = self.load_image()
        self.colour_palette = self.extract_colors()
        self.colour_palette_hex = self.convert_palette_to_hex()

    def load_image(self):
        image = mpimg.imread(self.image_path)
        if image.shape[2] == 4:  # Check if the image is in RGBA format and convert to RGB
            image = image[:, :, :3]
        if image.max() <= 1.0:  # Convert the image values to RGB
            image = (image * 255).astype(np.uint8)
        return image

    def extract_colors(self):
        w, h, d = tuple(self.image.shape)
        pixel = np.reshape(self.image, (w * h, d))
        model = KMeans(n_clusters=self.n_colors, random_state=42).fit(pixel)
        colour_palette = np.uint8(model.cluster_centers_)
        sorted_indices = np.argsort(colour_palette.sum(axis=1))
        return colour_palette[sorted_indices]

    def convert_palette_to_hex(self):
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
        
        return [rgb_to_hex(color)[:7] for color in self.colour_palette]

    def save_as_json(self):
        dictionary = {f"color{index}": color for index, color in enumerate(self.colour_palette_hex)}
        with open(f"{self.output_name}.json", "w") as f:
            f.write(json.dumps(dictionary, indent=4))

    def execute(self):
        self.save_as_json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract dominant colors from given .jpg or .png image file.")
    parser.add_argument("-c", "--colors", help="Number of colors", required=True)
    parser.add_argument("-i", "--image", help="Exact location of image", required=True)
    parser.add_argument("-n", "--name", help="Name of output file", required=True)

    args = parser.parse_args()

    extractor = ColorSchemeExtractor(int(args.colors), args.image, args.name)
    extractor.execute()
