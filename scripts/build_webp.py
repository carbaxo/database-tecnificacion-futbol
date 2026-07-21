"""Convierte los GIF animados a WebP animado (~70 % más ligeros, misma animación).

Uso: OUTPUT_DIR=. python3 scripts/build_webp.py
"""
import os

from PIL import Image, ImageFile

# Algunos GIF de la colección están truncados; decodifica lo que haya.
ImageFile.LOAD_TRUNCATED_IMAGES = True

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def convert(src, dst):
    image = Image.open(src)
    frames, durations = [], []
    try:
        while True:
            frames.append(image.convert("RGB").copy())
            durations.append(image.info.get("duration", 80))
            image.seek(image.tell() + 1)
    except EOFError:
        pass
    except Exception as error:
        # GIF truncado: descarta el último fotograma (puede estar corrupto)
        # y conserva los anteriores.
        frames, durations = frames[:-1], durations[:-1]
        print(f"  ⚠ {src}: se conservan {len(frames)} fotogramas ({error})")
    frames = [frame for frame in frames if frame.size == frames[0].size]
    durations = durations[: len(frames)]
    frames[0].save(
        dst,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        quality=70,
        method=6,
    )


def main():
    src_dir = os.path.join(OUTPUT_DIR, "gif")
    dst_dir = os.path.join(OUTPUT_DIR, "webp")
    os.makedirs(dst_dir, exist_ok=True)
    total_src = total_dst = 0
    for name in sorted(os.listdir(src_dir)):
        if not name.endswith(".gif"):
            continue
        src = os.path.join(src_dir, name)
        dst = os.path.join(dst_dir, name[:-4] + ".webp")
        convert(src, dst)
        total_src += os.path.getsize(src)
        total_dst += os.path.getsize(dst)
        print(f"✔ {dst} ({os.path.getsize(src) // 1024} KB → {os.path.getsize(dst) // 1024} KB)")
    print(f"Total: {total_src // 1024 // 1024} MB → {total_dst // 1024 // 1024} MB")


if __name__ == "__main__":
    main()
