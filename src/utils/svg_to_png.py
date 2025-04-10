"""
SVG to PNG converter utility
"""

import os
from cairosvg import svg2png

def convert_svg_to_png():
    """Convert all SVG icons to PNG format"""
    icons_dir = os.path.join("src", "resources", "images", "icons")
    
    # Get all SVG files
    svg_files = [f for f in os.listdir(icons_dir) if f.endswith('.svg')]
    
    for svg_file in svg_files:
        svg_path = os.path.join(icons_dir, svg_file)
        png_path = os.path.join(icons_dir, svg_file.replace('.svg', '.png'))
        
        # Convert SVG to PNG
        with open(svg_path, 'rb') as svg_data:
            svg2png(file_obj=svg_data,
                   write_to=png_path,
                   output_width=48,
                   output_height=48)
        print(f"Converted {svg_file} to PNG")

if __name__ == "__main__":
    convert_svg_to_png() 