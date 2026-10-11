#!/usr/bin/env python3
"""Drive the freenet debug app on a CI emulator and capture screenshots.

No app-code hooks: pure adb + uiautomator. Each step dumps the UI and logs
what it finds, so failures are diagnosable from the run log. Best-effort:
always saves whatever screenshots exist at the end.
"""
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

OUT = os.environ.get("SHOT_OUT", "screenshots")
PKG = "org.breezyweather.debug"
MAIN = f"{PKG}/org.breezyweather.ui.main.MainActivity"


def run(*args, check=False, capture=True, timeout=60):
    p = subprocess.run(["adb"] + list(args), capture_output=capture,
                       text=True, timeout=timeout)
    if check and p.returncode != 0:
        print("CMD FAILED:", args, p.stderr[-500:] if p.stderr else "")
    return p


def shot(name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "wb") as fh:
        p = subprocess.run(["adb", "exec-out", "screencap", "-p"],
                           stdout=fh, stderr=subprocess.PIPE, timeout=60)
    print("shot:", name, os.path.getsize(path), "bytes")
    return path


def dump():
    run("shell", "uiautomator", "dump", "/sdcard/ui.xml", timeout=60)
    p = run("shell", "cat", "/sdcard/ui.xml", timeout=60)
    return p.stdout


def nodes(xml):
    try:
        root = ET.fromstring(xml[xml.index("<hierarchy"):])
    except Exception as e:
        print("dump parse failed:", e)
        return []
    out = []
    for n in root.iter("node"):
        out.append({k: n.get(k, "") for k in
                    ("text", "content-desc", "resource-id", "class",
                     "clickable", "bounds", "enabled", "focused")})
    return out


def center(bounds):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap(node):
    c = center(node["bounds"])
    if c:
        run("shell", "input", "tap", str(c[0]), str(c[1]))
        print("tapped:", node["text"] or node["content-desc"] or node["resource-id"], c)
        return True
    return False


def find(ns, *needles, clickable_only=True):
    for n in ns:
        if clickable_only and n["clickable"] != "true":
            continue
        hay = (n["text"] + " " + n["content-desc"] + " " + n["resource-id"]).lower()
        if all(x.lower() in hay for x in needles):
            return n
    return None


def wait_for(needle, timeout_s=90, poll=5):
    end = time.time() + timeout_s
    while time.time() < end:
        ns = nodes(dump())
        hits = [n for n in ns
                if needle.lower() in (n["text"] + " " + n["content-desc"]).lower()]
        if hits:
            print(f"found '{needle}':", [(h["text"], h["content-desc"]) for h in hits[:3]])
            return ns
        time.sleep(poll)
    print(f"TIMEOUT waiting for '{needle}'")
    return nodes(dump())


def main():
    run("wait-for-device", timeout=300)
    for s in ("window_animation_scale", "transition_animation_scale",
              "animator_duration_scale"):
        run("shell", "settings", "put", "global", s, "0")
    run("install", "-r", os.environ["APK"], check=True, timeout=180)

    run("shell", "am", "start", "-n", MAIN)
    time.sleep(10)
    shot("01-launch.png")

    # --- add a UK location ---
    ns = nodes(dump())
    print("launch nodes:", len(ns))
    btn = (find(ns, "add") or find(ns, "search") or find(ns, "+"))
    if btn and tap(btn):
        time.sleep(5)
    else:
        print("no add button; dumping clickables:")
        for n in ns:
            if n["clickable"] == "true":
                print("  clickable:", repr(n["text"]), repr(n["content-desc"]),
                      repr(n["resource-id"]))
    shot("02-after-add-tap.png")

    ns = nodes(dump())
    field = None
    for n in ns:
        if n["class"] in ("android.widget.EditText", "android.widget.AutoCompleteTextView") \
                or "search" in (n["resource-id"] + n["content-desc"]).lower():
            field = n
            break
    if field and tap(field):
        time.sleep(2)
        run("shell", "input", "text", "Exeter")
        time.sleep(8)
        shot("03-search.png")
        ns = nodes(dump())
        # tap the first result that mentions Exeter/Devon/UK
        hit = (find(ns, "exeter", clickable_only=False)
               or find(ns, "devon", clickable_only=False))
        if hit:
            # tap nearest clickable ancestor-ish: just tap its center if clickable else first clickable below
            if hit["clickable"] == "true":
                tap(hit)
            else:
                c = center(hit["bounds"])
                if c:
                    run("shell", "input", "tap", str(c[0]), str(c[1]))
                    print("tapped result center", c)
            time.sleep(5)
            shot("04-after-result.png")
            # confirm/add button if any
            ns = nodes(dump())
            for needle in ("add", "confirm", "done", "save", "ok"):
                b = find(ns, needle)
                if b:
                    tap(b)
                    time.sleep(3)
                    break
            shot("05-after-confirm.png")
    else:
        print("no search field found")

    # back to main, wait for data
    run("shell", "am", "start", "-n", MAIN)
    ns = wait_for("°", timeout_s=120)
    time.sleep(5)
    shot("06-main-day.png")

    # --- open radar card ---
    ns = nodes(dump())
    radar = find(ns, "radar", clickable_only=False)
    print("radar node:", radar)
    if radar:
        c = center(radar["bounds"])
        if c:
            run("shell", "input", "tap", str(c[0]), str(c[1]))
            print("tapped radar card", c)
    time.sleep(12)
    shot("07-detail-day.png")

    # --- night mode ---
    run("shell", "cmd", "uimode", "night", "yes")
    time.sleep(5)
    shot("08-detail-night.png")
    run("shell", "input", "keyevent", "4")  # back
    time.sleep(5)
    shot("09-main-night.png")

    print("done. files:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    sys.exit(main())
