import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Configuration
INPUT_DIR = "."
OUTPUT_DIR = "store_assets/output_google_play"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" # Fallback to system font

# Colors (Deep Focus Theme)
COLOR_BG_TOP = (18, 18, 18)      # #121212
COLOR_BG_BOTTOM = (38, 198, 218) # Cyan-400 (used for slight tint) but deeply darkened
COLOR_ACCENT = (38, 198, 218)    # #26C6DA
COLOR_TEXT = (255, 255, 255)

# Resolutions
RES_SCREENSHOT = (1080, 1920)
RES_FEATURE = (1024, 500)

# Config List
ASSETS = [
    # Screenshots
    {
        "type": "screenshot",
        "filename": "timer.png",
        "title": "Dive into\nDeep Focus",
        "subtitle": "Immersive timer for flow state.",
        "output": "1_timer.png"
    },
    {
        "type": "screenshot",
        "filename": "heatmap.png",
        "title": "Visualize\nYour Effort",
        "subtitle": "Track your daily progress.",
        "output": "2_heatmap.png"
    },
    {
        "type": "screenshot",
        "filename": "sound.png",
        "title": "Immersive\nSound",
        "subtitle": "Ocean ambience to block noise.",
        "output": "3_sound.png"
    },
    {
        "type": "screenshot",
        "filename": "suggest.png",
        "title": "Instant\nFocus",
        "subtitle": "Smart suggestions. No setup.",
        "output": "4_suggest.png"
    },
    # Feature Graphic
    {
        "type": "feature",
        "title": "flow",
        "subtitle": "Dive into Deep Focus",
        "output": "feature_graphic.png"
    }
]

def create_deep_sea_bg(width, height):
    # 1. Base Gradient (Deep Gray to Dark Teal)
    base = Image.new('RGB', (width, height), COLOR_BG_TOP)
    
    # Create a subtle radial gradient or bottom glow
    # For simplicity, let's do a vertical linear gradient mixed with black
    # Top: #121212, Bottom: Mix of #121212 and Cyan
    
    # Draw bottom glow
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw_glow = ImageDraw.Draw(glow)
    
    # Bottom glow ellipse
    glow_color = (*COLOR_ACCENT, 40) # Ultra sheer cyan
    draw_glow.ellipse(
        (-width * 0.2, height * 0.6, width * 1.2, height * 1.4),
        fill=glow_color
    )
    # Blur the glow
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    
    base.paste(glow, (0, 0), glow)
    
    # 2. Add Bubbles
    bubble_layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw_bubbles = ImageDraw.Draw(bubble_layer)
    
    # Random bubbles
    num_bubbles = 15
    for _ in range(num_bubbles):
        choice = random.random()
        if choice < 0.6:
            r = random.randint(10, 30) # Small
            alpha = random.randint(20, 50)
        elif choice < 0.9:
            r = random.randint(30, 80) # Medium
            alpha = random.randint(10, 30)
        else:
            r = random.randint(100, 200) # Large (Blurry foreground)
            alpha = random.randint(5, 15)
            
        x = random.randint(0, width)
        y = random.randint(0, height)
        
        draw_bubbles.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(*COLOR_ACCENT, alpha)
        )
    
    # Blur bubbles slightly
    bubble_layer = bubble_layer.filter(ImageFilter.GaussianBlur(2))
    base.paste(bubble_layer, (0,0), bubble_layer)
    
    return base

def draw_device_frame(canvas, img_path, center_y, scale_factor=0.8):
    """
    Draws the screenshot image inside a generated device frame.
    center_y: Y coordinate for the center of the device
    """
    if not os.path.exists(img_path):
        print(f"Warning: {img_path} not found.")
        return

    cw, ch = canvas.size
    
    # Load Screenshot
    screen_img = Image.open(img_path).convert("RGBA")
    
    # Target Screen Width (relative to canvas)
    target_screen_w = int(cw * scale_factor)
    aspect = screen_img.height / screen_img.width
    target_screen_h = int(target_screen_w * aspect)
    
    # Resize Screenshot
    screen_resized = screen_img.resize((target_screen_w, target_screen_h), Image.Resampling.LANCZOS)
    
    # Frame Config
    bezel = 30
    radius = 50
    frame_w = target_screen_w + (bezel * 2)
    frame_h = target_screen_h + (bezel * 2)
    
    frame_x = (cw - frame_w) // 2
    # Determine frame_y so that the visual center of the device is at center_y
    # (or simply place the top/bottom relative to text)
    # Let's align top of device to center_y to allow room for text above? 
    # Or center the device in the remaining space?
    # Let's just place it starting at center_y
    frame_y = center_y
    
    draw = ImageDraw.Draw(canvas)
    
    # 1. Shadow
    shadow_offset = 20
    draw.rounded_rectangle(
        (frame_x + shadow_offset, frame_y + shadow_offset, 
         frame_x + frame_w + shadow_offset, frame_y + frame_h + shadow_offset),
        radius=radius, fill=(0, 0, 0, 100)
    )
    
    # 2. Frame Body (Deep Grey)
    draw.rounded_rectangle(
        (frame_x, frame_y, frame_x + frame_w, frame_y + frame_h),
        radius=radius, fill=(30, 30, 30)
    )
    
    # 3. Paste Screen
    canvas.paste(screen_resized, (frame_x + bezel, frame_y + bezel), screen_resized)

def process_item(item):
    print(f"Generating {item['output']}...")
    
    is_feature = item['type'] == 'feature'
    width, height = RES_FEATURE if is_feature else RES_SCREENSHOT
    
    # 1. Background
    canvas = create_deep_sea_bg(width, height)
    draw = ImageDraw.Draw(canvas)
    
    # 2. Text
    try:
         # Title Font
        title_size = 80 if is_feature else 100
        title_font = ImageFont.truetype(FONT_PATH, title_size)
        
        # Subtitle Font (Correction: smaller)
        sub_size = 40 if is_feature else 50
        sub_font = ImageFont.truetype(FONT_PATH, sub_size)
    except:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        
    # Draw Title
    title = item['title']
    title_bbox = draw.textbbox((0, 0), title, font=title_font, align="center")
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    
    title_x = (width - title_w) // 2
    title_y = 150 # Top margin
    
    if is_feature:
        title_y = (height - title_h) // 2 - 20 # Centered-ish
    
    draw.text((title_x, title_y), title, font=title_font, fill='white', align="center")
    
    # Draw Subtitle (if screen)
    if 'subtitle' in item:
        sub = item['subtitle']
        sub_bbox = draw.textbbox((0, 0), sub, font=sub_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        
        sub_x = (width - sub_w) // 2
        sub_y = title_y + title_h + 30
        
        if is_feature:
             sub_y = title_y + title_h + 20
             
        draw.text((sub_x, sub_y), sub, font=sub_font, fill=(200, 200, 200))
        
    # 3. Device (if screenshot)
    if not is_feature:
        img_path = os.path.join(INPUT_DIR, item['filename'])
        # device starts below text
        device_y = title_y + title_h + 150
        draw_device_frame(canvas, img_path, device_y, scale_factor=0.8)
        
    # 4. Save
    out_path = os.path.join(OUTPUT_DIR, item['output'])
    canvas.save(out_path)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for item in ASSETS:
        process_item(item)
    
    print("Done.")

if __name__ == "__main__":
    main()
