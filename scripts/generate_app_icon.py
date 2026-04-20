from PIL import Image, ImageDraw


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (8, 22, 40, 255))
    draw = ImageDraw.Draw(img)

    draw.polygon([(0, 0), (size, 0), (0, size)], fill=(16, 56, 95, 255))
    draw.polygon([(size, 0), (size, size), (0, size)], fill=(9, 122, 157, 255))

    margin = max(2, size // 24)
    shield = [
        (size * 20 // 64, size * 10 // 64),
        (size * 44 // 64, size * 10 // 64),
        (size * 52 // 64, size * 20 // 64),
        (size * 49 // 64, size * 40 // 64),
        (size * 32 // 64, size * 54 // 64),
        (size * 15 // 64, size * 40 // 64),
        (size * 12 // 64, size * 20 // 64),
    ]
    draw.polygon(shield, fill=(245, 249, 252, 240), outline=(10, 44, 77, 255), width=max(1, margin))

    top = size * 22 // 64
    left = size * 20 // 64
    right = size * 44 // 64
    bottom = size * 34 // 64
    draw.rounded_rectangle((left, top, right, bottom), radius=max(2, size // 18), fill=(14, 71, 118, 255))

    slot_width = max(2, size // 10)
    center = size // 2
    draw.rectangle(
        (center - slot_width // 2, top + max(1, margin), center + slot_width // 2, bottom - max(1, margin)),
        fill=(230, 244, 255, 255),
    )

    stem_top = bottom
    stem_bottom = size * 45 // 64
    draw.rectangle((center - max(1, margin), stem_top, center + max(1, margin), stem_bottom), fill=(14, 71, 118, 255))

    radius = max(2, size // 14)
    draw.ellipse((center - radius, stem_bottom - radius, center + radius, stem_bottom + radius), fill=(14, 71, 118, 255))
    draw.ellipse(
        (
            center - radius + max(1, margin),
            stem_bottom - radius + max(1, margin),
            center + radius - max(1, margin),
            stem_bottom + radius - max(1, margin),
        ),
        fill=(230, 244, 255, 255),
    )

    return img


def main() -> None:
    png = draw_icon(512)
    png.save("assets/app_icon.png")

    ico = draw_icon(256)
    ico.save("assets/app_icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    print("Updated assets/app_icon.png and assets/app_icon.ico")


if __name__ == "__main__":
    main()
