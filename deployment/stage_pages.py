from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parents[1]
bundle = root / "dashboard" / "dist"
manifest = json.loads((bundle / "data-app-build.json").read_text(encoding="utf-8"))
output = root / "_site"
output.mkdir(exist_ok=True)

for key in ("html", "snapshot"):
    item = manifest[key]
    relative = Path(item["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Invalid bundle path")
    source = bundle / relative
    if source.is_symlink() or not source.is_file():
        raise ValueError("Expected a regular bundle file")
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != item["sha256"]:
        raise ValueError("Bundle integrity mismatch: " + relative.as_posix())
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

(output / ".nojekyll").write_text("", encoding="utf-8")
print("Verified and staged the existing dashboard bundle.")
