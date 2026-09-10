"""
Generates the resized, EXIF-stripped derivatives of the homepage pictures.

The originals in static/images/homepage/ are straight off a Pixel 6 (~4000px
wide, ~4MB each) and are never touched. This writes two smaller WebP copies of
each one:

  static/images/homepage_web/    1600px wide, for the homepage hero image
  static/images/homepage_thumbs/  600px wide, for the grid on /pictures

Both derivative sets have their metadata stripped, so the GPS and camera tags
only exist in the originals that /pictures links out to.

Re-run after adding pictures, it skips anything already up to date:

    python3 compress_images.py
"""

import os
import subprocess
import sys

SOURCE_DIRECTORY = "static/images/homepage"

# (output directory, width in pixels, webp quality)
DERIVATIVES = [
    ("static/images/homepage_web", 1600, 78),
    ("static/images/homepage_thumbs", 600, 75),
]


def convert(source, destination, width, quality):
    """Resizes one image to width and writes it as WebP with no metadata."""

    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y",
            "-i", source,
            # -2 keeps the aspect ratio and lands on an even number of pixels,
            # the min() stops anything narrower than width being upscaled
            "-vf", f"scale='min({width},iw)':-2",
            "-map_metadata", "-1",
            "-c:v", "libwebp",
            "-q:v", str(quality),
            "-frames:v", "1",
            destination,
        ],
        check=True,
    )


def main():
    sources = sorted(f for f in os.listdir(SOURCE_DIRECTORY) if f.endswith(".jpg"))
    converted, skipped = 0, 0

    for directory, width, quality in DERIVATIVES:
        os.makedirs(directory, exist_ok=True)

        for filename in sources:
            source = os.path.join(SOURCE_DIRECTORY, filename)
            destination = os.path.join(directory, os.path.splitext(filename)[0] + ".webp")

            if os.path.exists(destination) and os.path.getmtime(destination) >= os.path.getmtime(source):
                skipped += 1
                continue

            print(f"{source} -> {destination}")
            convert(source, destination, width, quality)
            converted += 1

    print(f"\n{converted} converted, {skipped} already up to date")


if __name__ == "__main__":
    if not os.path.isdir(SOURCE_DIRECTORY):
        sys.exit(f"Run this from the repository root, {SOURCE_DIRECTORY} not found")

    main()
