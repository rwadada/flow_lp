import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Configuration
INPUT_DIR = "store_assets/raw"
OUTPUT_DIR = "store_assets/output"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# Target Resolution (iPhone 6.7" - 1290 x 2796)
CANVAS_WIDTH = 1290
CANVAS_HEIGHT = 2796

# Theme Colors
BG_COLOR_TOP = (20, 24, 35)    # Dark Blue/Grey
BG_COLOR_BOTTOM = (30, 40, 60) # Lighter Blue/Grey

# Screenshots Config
SCREENS = [
    {
        "filename": "screen_flow.png",
        "title": "Manage Tasks\nEffectively",
        "caption_y": 150
    },
    {
        "filename": "screen_reflect.png",
        "title": "Focus On\nThe Moment",
        "caption_y": 150
    },
    {
        "filename": "screen_settings.png",
        "title": "Customize\nYour Experience",
        "caption_y": 150
    }
]

def create_gradient(width, height, top_color, bottom_color):
    base = Image.new('RGB', (width, height), top_color)
    top = Image.new('RGB', (width, height), top_color)
    bottom = Image.new('RGB', (width, height), bottom_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(bottom, (0, 0), mask)
    return base

def draw_device_frame(draw, x, y, w, h, radius=60, color=(40, 40, 40)):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=color)

def process_screen(config):
    filename = config["filename"]
    input_path = os.path.join(INPUT_DIR, filename)
    
    if not os.path.exists(input_path):
        print(f"Skipping {filename}: Not found")
        return

    # 1. Create Canvas
    canvas = create_gradient(CANVAS_WIDTH, CANVAS_HEIGHT, BG_COLOR_TOP, BG_COLOR_BOTTOM)
    draw = ImageDraw.Draw(canvas)

    # 2. Draw Text
    try:
        font = ImageFont.truetype(FONT_PATH, 100)
    except:
        font = ImageFont.load_default()
        print("Warning: Custom font not found, using default.")

    text = config["title"]
    # Centered Text
    # Multiline support
    lines = text.split('\n')
    text_y = config["caption_y"]
    
    for line in lines:
        try:
            # bbox is (left, top, right, bottom)
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            text_w = right - left
            text_h = bottom - top
        except AttributeError:
            # Fallback for older Pillow
            text_w, text_h = draw.textsize(line, font=font)
            
        text_x = (CANVAS_WIDTH - text_w) // 2
        draw.text((text_x, text_y), line, font=font, fill=(255, 255, 255))
        text_y += text_h + 20

    # 3. Prepare Screenshot & Device Frame
    # Target Screen Area in the Frame
    # Let's say device width is 80% of canvas
    device_w = int(CANVAS_WIDTH * 0.8)
    
    # Load Screenshot
    raw_img = Image.open(input_path).convert("RGBA")
    
    # Calculate aspect ratio
    aspect = raw_img.height / raw_img.width
    
    # Resize screenshot to fit device width (minus bezel)
    bezel = 40
    screen_w = device_w - (bezel * 2)
    screen_h = int(screen_w * aspect)
    
    resized_screen = raw_img.resize((screen_w, screen_h), Image.LANCZOS)
    
    # Device Frame Dimensions
    device_h = screen_h + (bezel * 2)
    
    device_x = (CANVAS_WIDTH - device_w) // 2
    device_y = text_y + 100 # Place below text
    
    # Draw Shadow (simple offset rect)
    shadow_offset = 30
    draw.rounded_rectangle(
        (device_x + shadow_offset, device_y + shadow_offset, device_x + device_w + shadow_offset, device_y + device_h + shadow_offset),
        radius=60, fill=(0, 0, 0, 100)
    )

    # Draw Device Body
    draw.rounded_rectangle(
        (device_x, device_y, device_x + device_w, device_y + device_h),
        radius=60, fill=(30, 30, 30) # Dark frame
    )
    
    # Paste Screenshot
    canvas.paste(resized_screen, (device_x + bezel, device_y + bezel), resized_screen)

    # 4. Save
    output_filename = f"store_{filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    canvas.save(output_path)
    print(f"Generated {output_path}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for config in SCREENS:
        process_screen(config)

if __name__ == "__main__":
    main()
