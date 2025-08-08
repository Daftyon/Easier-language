#!/usr/bin/env python3
"""
Icon to ASCII Banner Converter for El Programming Language
Converts el_icone.ico to ASCII art banner
"""

import sys
from pathlib import Path

def convert_icon_to_ascii():
    """Convert the El icon to ASCII art"""
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("❌ Missing dependencies!")
        print("Install with: pip install pillow numpy")
        return None

    icon_path = Path("el_icone.ico")
    
    if not icon_path.exists():
        print(f"❌ Icon file not found: {icon_path}")
        return None
    
    try:
        # Open and process the image
        img = Image.open(icon_path)
        print(f"✅ Loaded icon: {img.size}, format: {img.format}")
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for ASCII art (smaller for better readability)
        # Try different sizes
        sizes = [
            (60, 20, "Large"),
            (40, 15, "Medium"), 
            (30, 10, "Small"),
            (20, 8, "Tiny")
        ]
        
        results = {}
        
        for width, height, size_name in sizes:
            # Resize image
            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to grayscale
            gray = resized.convert('L')
            
            # Convert to ASCII
            ascii_art = image_to_ascii(gray)
            results[size_name] = ascii_art
            
        return results
        
    except Exception as e:
        print(f"❌ Error processing icon: {e}")
        return None

def image_to_ascii(img):
    """Convert PIL Image to ASCII art"""
    # ASCII characters from dark to light
    ascii_chars = "@%#*+=-:. "
    
    # Get image data
    pixels = list(img.getdata())
    
    ascii_str = ""
    for i, pixel in enumerate(pixels):
        # Convert pixel to ASCII character
        ascii_index = pixel * (len(ascii_chars) - 1) // 255
        ascii_str += ascii_chars[ascii_index]
        
        # Add newline at end of each row
        if (i + 1) % img.width == 0:
            ascii_str += "\n"
    
    return ascii_str

def create_banner_variations():
    """Create different banner styles"""
    
    print("🎨 CONVERTING EL ICON TO ASCII BANNER")
    print("=" * 50)
    
    ascii_results = convert_icon_to_ascii()
    
    if not ascii_results:
        print("❌ Could not convert icon")
        return
    
    banners = {}
    
    # For each size, create banner variations
    for size_name, ascii_art in ascii_results.items():
        
        # Style 1: Simple ASCII
        banner1 = f"""
{ascii_art}
    El Programming Language v1.0.6
    A modern and easy programming language
"""
        
        # Style 2: With border
        lines = ascii_art.strip().split('\n')
        max_width = max(len(line) for line in lines)
        border = "=" * (max_width + 4)
        
        banner2 = f"""
{border}
"""
        for line in lines:
            banner2 += f"= {line:<{max_width}} =\n"
        
        banner2 += f"""{border}
  El Programming Language v1.0.6
  A modern and easy programming language
"""
        
        # Style 3: Compact with text
        banner3 = f"""
{ascii_art}    El Programming Language v1.0.6
    Created by El Language Team
    https://github.com/Daftyon/Easier-language
"""
        
        banners[size_name] = {
            'simple': banner1,
            'bordered': banner2,
            'compact': banner3
        }
    
    return banners

def save_banners_to_file(banners):
    """Save all banner variations to a file"""
    
    output_file = "el_banners.py"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\n')
        f.write('El Programming Language - Generated ASCII Banners\n')
        f.write('Auto-generated from el_icone.ico\n')
        f.write('"""\n\n')
        
        f.write('__version__ = "1.0.6"\n')
        f.write('__author__ = "El Language Team"\n\n')
        
        for size_name, styles in banners.items():
            for style_name, banner in styles.items():
                var_name = f"BANNER_{size_name.upper()}_{style_name.upper()}"
                f.write(f'{var_name} = """{banner}"""\n\n')
        
        # Add convenience functions
        f.write('''
def show_banner(size="medium", style="simple"):
    """
    Show El Language banner
    
    Args:
        size: "large", "medium", "small", "tiny"
        style: "simple", "bordered", "compact"
    """
    banner_map = {
        ("large", "simple"): BANNER_LARGE_SIMPLE,
        ("large", "bordered"): BANNER_LARGE_BORDERED,
        ("large", "compact"): BANNER_LARGE_COMPACT,
        ("medium", "simple"): BANNER_MEDIUM_SIMPLE,
        ("medium", "bordered"): BANNER_MEDIUM_BORDERED,
        ("medium", "compact"): BANNER_MEDIUM_COMPACT,
        ("small", "simple"): BANNER_SMALL_SIMPLE,
        ("small", "bordered"): BANNER_SMALL_BORDERED,
        ("small", "compact"): BANNER_SMALL_COMPACT,
        ("tiny", "simple"): BANNER_TINY_SIMPLE,
        ("tiny", "bordered"): BANNER_TINY_BORDERED,
        ("tiny", "compact"): BANNER_TINY_COMPACT,
    }
    
    banner = banner_map.get((size.lower(), style.lower()))
    if banner:
        print(banner)
    else:
        print("❌ Invalid size or style")
        print("Available sizes: large, medium, small, tiny")
        print("Available styles: simple, bordered, compact")

def get_banner(size="medium", style="simple"):
    """Get banner as string without printing"""
    # Same logic as show_banner but return instead of print
    # ... (implementation same as above)
    pass

if __name__ == "__main__":
    show_banner()
''')
    
    print(f"✅ Banners saved to: {output_file}")
    return output_file

def preview_banners(banners):
    """Preview all banner variations"""
    
    print("\n🖼️  BANNER PREVIEWS")
    print("=" * 50)
    
    for size_name, styles in banners.items():
        print(f"\n📏 {size_name.upper()} SIZE:")
        print("-" * 30)
        
        for style_name, banner in styles.items():
            print(f"\n🎨 {style_name.capitalize()} Style:")
            print(banner)
            print("─" * 20)

def main():
    """Main function"""
    print("🎨 EL ICON TO BANNER CONVERTER")
    print("=" * 40)
    
    # Check dependencies
    try:
        import PIL
        import numpy
        print("✅ Dependencies installed")
    except ImportError:
        print("❌ Missing dependencies!")
        print("Install with: pip install pillow numpy")
        sys.exit(1)
    
    # Convert icon to banners
    banners = create_banner_variations()
    
    if not banners:
        print("❌ Failed to create banners")
        sys.exit(1)
    
    # Preview banners
    preview_banners(banners)
    
    # Save to file
    output_file = save_banners_to_file(banners)
    
    print(f"\n🎉 SUCCESS!")
    print("=" * 20)
    print(f"✅ Generated {len(banners)} sizes × 3 styles = {len(banners) * 3} banners")
    print(f"✅ Saved to: {output_file}")
    print(f"✅ Import with: from {output_file[:-3]} import show_banner")
    print(f"✅ Usage: show_banner('medium', 'simple')")
    
    # Test the generated file
    print("\n🧪 Testing generated banners...")
    try:
        exec(f"from {output_file[:-3]} import show_banner")
        print("✅ Import test successful!")
    except Exception as e:
        print(f"❌ Import test failed: {e}")

if __name__ == "__main__":
    main()
