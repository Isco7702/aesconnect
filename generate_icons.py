#!/usr/bin/env python3
"""
Generate placeholder PNG icons for PWA
This is a simple script that creates colored placeholder icons
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Icon sizes required for PWA
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors (East Africa theme)
BACKGROUND_COLOR = (34, 197, 94)  # Green #22c55e
CIRCLE_COLOR = (251, 191, 36)     # Yellow #fbbf24
CENTER_COLOR = (239, 68, 68)       # Red #ef4444

def create_icon(size):
    """Create a simple icon with East Africa colors"""
    # Create image
    img = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw circles representing connectivity
    padding = size // 10
    
    # Main circle
    draw.ellipse([padding, padding, size-padding, size-padding], 
                 fill=None, outline=CIRCLE_COLOR, width=size//20)
    
    # Draw three smaller circles (nodes)
    node_size = size // 8
    positions = [
        (size//3, size//3),          # Top left
        (2*size//3, size//3),        # Top right
        (size//2, 2*size//3)         # Bottom center
    ]
    
    for x, y in positions:
        draw.ellipse([x-node_size, y-node_size, x+node_size, y+node_size], 
                     fill=CIRCLE_COLOR)
    
    # Draw lines connecting nodes
    draw.line([(size//3, size//3), (2*size//3, size//3)], 
              fill=CIRCLE_COLOR, width=size//40)
    draw.line([(size//3, size//3), (size//2, 2*size//3)], 
              fill=CIRCLE_COLOR, width=size//40)
    draw.line([(2*size//3, size//3), (size//2, 2*size//3)], 
              fill=CIRCLE_COLOR, width=size//40)
    
    # Draw center highlight
    center_size = size // 12
    draw.ellipse([size//2-center_size, size//2-center_size, 
                  size//2+center_size, size//2+center_size], 
                 fill=CENTER_COLOR)
    
    return img

def main():
    # Create icons directory if it doesn't exist
    icons_dir = './static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    print("🎨 Génération des icônes PWA...")
    
    for size in SIZES:
        filename = f'icon-{size}x{size}.png'
        filepath = os.path.join(icons_dir, filename)
        
        try:
            icon = create_icon(size)
            icon.save(filepath, 'PNG', optimize=True)
            print(f"✅ {filename} créé")
        except Exception as e:
            print(f"❌ Erreur pour {filename}: {e}")
    
    print(f"\n✅ {len(SIZES)} icônes générées dans {icons_dir}/")
    print("🌍 Thème: Couleurs de l'Afrique de l'Est (Vert, Jaune, Rouge)")

if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw
        main()
    except ImportError:
        print("❌ Pillow n'est pas installé")
        print("📦 Installation : pip install Pillow")
        print("\n💡 Alternative : Les icônes SVG fonctionnent aussi pour le PWA")
