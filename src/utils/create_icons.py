"""
Create PNG icons using Pillow
"""

from PIL import Image, ImageDraw
import os

def create_icons():
    """Create PNG icons for player controls"""
    icons_dir = os.path.join("src", "resources", "images", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # Icon size and colors
    size = (48, 48)
    bg_color = (0, 0, 0, 0)  # Transparent background
    fg_color = (255, 255, 255, 255)  # White foreground
    
    # Create play icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    points = [(16, 12), (16, 36), (36, 24)]  # Triangle
    draw.polygon(points, fill=fg_color)
    img.save(os.path.join(icons_dir, "play.png"))
    
    # Create pause icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([14, 12, 20, 36], fill=fg_color)  # Left bar
    draw.rectangle([28, 12, 34, 36], fill=fg_color)  # Right bar
    img.save(os.path.join(icons_dir, "pause.png"))
    
    # Create stop icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([14, 14, 34, 34], fill=fg_color)
    img.save(os.path.join(icons_dir, "stop.png"))
    
    # Create previous frame icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    points = [(32, 12), (32, 36), (20, 24)]  # Triangle
    draw.polygon(points, fill=fg_color)
    draw.rectangle([14, 12, 18, 36], fill=fg_color)  # Bar
    img.save(os.path.join(icons_dir, "prev_frame.png"))
    
    # Create next frame icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    points = [(16, 12), (16, 36), (28, 24)]  # Triangle
    draw.polygon(points, fill=fg_color)
    draw.rectangle([30, 12, 34, 36], fill=fg_color)  # Bar
    img.save(os.path.join(icons_dir, "next_frame.png"))
    
    # Create rewind icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    points1 = [(34, 12), (34, 36), (22, 24)]  # Right triangle
    points2 = [(22, 12), (22, 36), (10, 24)]  # Left triangle
    draw.polygon(points1, fill=fg_color)
    draw.polygon(points2, fill=fg_color)
    img.save(os.path.join(icons_dir, "rewind.png"))
    
    # Create forward icon
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    points1 = [(14, 12), (14, 36), (26, 24)]  # Left triangle
    points2 = [(26, 12), (26, 36), (38, 24)]  # Right triangle
    draw.polygon(points1, fill=fg_color)
    draw.polygon(points2, fill=fg_color)
    img.save(os.path.join(icons_dir, "forward.png"))
    
    print("All icons created successfully")

if __name__ == "__main__":
    create_icons() 