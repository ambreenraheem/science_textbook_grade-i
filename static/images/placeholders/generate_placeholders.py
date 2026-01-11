"""
Generate placeholder images for curriculum content.

Creates simple colored placeholder images for:
- Chapter cards (400x300)
- Lesson pages (600x400)

Follows child-friendly color palette from research.md
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


# Child-friendly color palette (Constitution I: bright but soft colors)
COLORS = {
    "sky_blue": "#87CEEB",
    "grass_green": "#90EE90",
    "sunshine_yellow": "#FFD700",
    "soft_pink": "#FFB6C1",
    "warm_orange": "#FFA500",
}

TEXT_COLOR = "#333333"  # Dark gray for high contrast


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_placeholder(
    width: int,
    height: int,
    bg_color: str,
    text: str,
    output_path: Path
) -> None:
    """
    Create a simple placeholder image with centered text.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        bg_color: Background color (hex string)
        text: Text to display
        output_path: Where to save the image
    """
    # Create image with background color
    bg_rgb = hex_to_rgb(bg_color)
    img = Image.new('RGB', (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # Calculate text position (centered)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # Draw text with outline for readability
    text_rgb = hex_to_rgb(TEXT_COLOR)
    draw.text((text_x, text_y), text, fill=text_rgb, font=font)

    # Save image
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"✓ Created: {output_path}")


def main():
    """Generate all placeholder images."""
    base_dir = Path(__file__).parent

    # Chapter placeholders (400x300)
    chapter_placeholders = [
        ("chapter-placeholder.png", COLORS["sky_blue"], "Chapter"),
        ("living-nonliving.png", COLORS["sky_blue"], "Living &\nNon-Living"),
        ("plants.png", COLORS["grass_green"], "Plants"),
        ("animals.png", COLORS["soft_pink"], "Animals"),
        ("food.png", COLORS["sunshine_yellow"], "Food"),
    ]

    print("\n=== Generating Chapter Placeholders (400x300) ===")
    for filename, color, text in chapter_placeholders:
        create_placeholder(
            width=400,
            height=300,
            bg_color=color,
            text=text,
            output_path=base_dir / filename
        )

    # Lesson placeholders (600x400)
    lesson_placeholders = [
        ("lesson-placeholder.png", COLORS["sky_blue"], "Lesson"),
    ]

    print("\n=== Generating Lesson Placeholders (600x400) ===")
    for filename, color, text in lesson_placeholders:
        create_placeholder(
            width=600,
            height=400,
            bg_color=color,
            text=text,
            output_path=base_dir / filename
        )

    print("\n✅ All placeholder images generated successfully!")
    print(f"📁 Location: {base_dir}\n")


if __name__ == "__main__":
    main()
