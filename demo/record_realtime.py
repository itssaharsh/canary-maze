#!/usr/bin/env python3
"""A drop-in replacement for the demo kit's recorder, running on the WALL CLOCK.

Why this exists
---------------
The kit records on a lockstep virtual clock: it pauses page time, advances it by
exactly one frame, and waits for Chromium to say the budget expired. That gives a
perfect 30fps whatever the machine is doing, and it is the right design - until
the page awaits something that is not a timer.

This page does. Its one load-bearing button calls `crypto.subtle.digest`, whose
promise resolves off the main thread, and under paused virtual time the budget
never expired. Three attempts stalled at the same frame count, on the same click,
with memory draining until the process died. The click is the entire point of the
video, so the clock had to go rather than the shot.

What is kept: the output format, byte for byte. `rec/frames/*.jpg` plus a
`rec/events.json` holding frames, cursor, clicks, marks and scenes, so the kit's
own `cards.py` and `compose.py` run on it unchanged - and with them the design
system, the captions, the camera, the sound design and the quality checks.

What is lost: guaranteed frame pacing. A slow machine drops frames rather than
stretching time. Frames carry their real timestamp, so the edit stays in sync; the
motion is just less smooth. For a two-minute product video that is the right trade.

Usage
-----
    python3 record_realtime.py storyboard.json [--scene <id>]
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import math
import os
import sys
import time

from playwright.async_api import async_playwright

# A 1px animation so the compositor keeps producing frames on a static page, and
# so frame-aligned input such as mousemove is always dispatched. Straight from the
# kit, for the same reason.
HEARTBEAT = """() => {
  if (window.__dk) return;
  const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:2147483647;'
    + 'pointer-events:none;opacity:.02;background:#000;animation:__dkp 1s linear infinite';
  const st = document.createElement('style');
  st.textContent = '@keyframes __dkp{from{transform:translateX(0)}to{transform:translateX(1px)}}';
  document.documentElement.appendChild(st);
  document.documentElement.appendChild(d);
  window.__dk = 1;
}"""

HIDE = "*{scrollbar-width:none!important}*::-webkit-scrollbar{display:none!important}"


def ease(t: float) -> float:
    return 1 - pow(1 - t, 3)


class Recorder:
    def __init__(self, sb: dict, base: str):
        self.sb, self.base = sb, base
        st = sb.get("style", {})
        self.fps = st.get("fps", 30)
        self.vw, self.vh = st.get("viewport", [1280, 720])
        self.dsf = st.get("dsf", 1)
        self.out = os.path.join(base, "rec")
        if os.path.isdir(self.out):
            import shutil
            shutil.rmtree(self.out)
        os.makedirs(os.path.join(self.out, "frames"), exist_ok=True)
        self.frames: list[list] = []
        self.cursor_log: list[list] = []
        self.clicks: list[list] = []
        self.marks: dict[str, float] = {}
        self.scenes: dict[str, dict] = {}
        self.cursor = (self.vw * .62, self.vh * .78)
        self.visible = False
        self.n = 0
        self.t0 = 0.0
        self.capturing = False

    # ---------- clock ----------
    def vt(self) -> float:
        """Milliseconds since capture started. The only time base in the file."""
        return (time.time() - self.t0) * 1000.0

    def note_cursor(self) -> None:
        self.cursor_log.append([round(self.vt(), 1), round(self.cursor[0], 1),
                                round(self.cursor[1], 1), int(self.visible)])

    async def rest(self, ms: float) -> None:
        """Wait, logging the cursor as we go so the overlay stays continuous."""
        end = time.time() + ms / 1000.0
        while time.time() < end:
            await asyncio.sleep(min(1 / self.fps, max(0.0, end - time.time())))
            self.note_cursor()

    # ---------- capture ----------
    def on_frame(self, e) -> None:
        if not self.capturing:
            return
        with open(os.path.join(self.out, "frames", "%06d.jpg" % self.n), "wb") as f:
            f.write(base64.b64decode(e["data"]))
        self.frames.append([round(self.vt(), 2), self.n])
        self.n += 1
        asyncio.ensure_future(self.cdp.send("Page.screencastFrameAck",
                                            {"sessionId": e["sessionId"]}))

    # ---------- helpers ----------
    async def box(self, sel: str):
        loc = self.page.locator(sel).filter(visible=True).first
        await loc.wait_for(state="visible", timeout=20000)
        b = await loc.bounding_box()
        if b and (b["y"] < 0 or b["y"] + b["height"] > self.vh):
            y = await self.page.evaluate("scrollY")
            await self.smooth_scroll(max(0, y + b["y"] - self.vh * .3))
            b = await loc.bounding_box()
        return b

    async def smooth_scroll(self, y1: float, ms: float = 900) -> None:
        y0 = await self.page.evaluate("scrollY")
        steps = max(2, int(ms / (1000 / self.fps)))
        for i in range(1, steps + 1):
            await self.page.evaluate("(y)=>window.scrollTo({top:y,behavior:'instant'})",
                                     y0 + (y1 - y0) * ease(i / steps))
            await self.rest(1000 / self.fps)

    async def move(self, x: float, y: float) -> None:
        x0, y0 = self.cursor
        d = math.hypot(x - x0, y - y0)
        if d < 2:
            return
        ms = max(420, min(1000, 330 + 130 * math.log2(1 + d / 40)))
        steps = max(3, round(ms / (1000 / self.fps)))
        self.visible = True
        for i in range(1, steps + 1):
            t = ease(i / steps)
            self.cursor = ((1 - t) * x0 + t * x, (1 - t) * y0 + t * y)
            await self.page.mouse.move(*self.cursor)
            await self.rest(1000 / self.fps)

    # ---------- actions ----------
    async def act(self, a: dict, ev: dict) -> None:
        do = a["do"]
        if do in ("click", "hover"):
            b = await self.box(a["sel"])
            ev["box"] = b
            x = b["x"] + b["width"] * .46
            y = b["y"] + b["height"] * .5
            await self.move(x, y)
            await self.rest(80)
            ev["key"] = round(self.vt(), 1)
            if do == "click":
                await self.page.mouse.down()
                self.clicks.append([round(self.vt(), 1), round(x, 1), round(y, 1)])
                await self.rest(110)
                await self.page.mouse.up()
            await self.rest(120)
        elif do == "camera":
            ev["box"] = await self.box(a["focus"]) if a.get("focus") else None
            ev["key"] = round(self.vt(), 1)
        elif do == "pause":
            await self.rest(a.get("ms", 1000))
        elif do == "wait":
            # Real time, so a promise that resolves off the main thread resolves.
            f, t0 = a.get("for", 1000), time.time()
            while True:
                if isinstance(f, (int, float)):
                    if (time.time() - t0) * 1000 >= f:
                        break
                elif await self.page.locator(f).filter(visible=True).count():
                    break
                if (time.time() - t0) * 1000 > a.get("timeout", 30000):
                    raise TimeoutError(f"wait for {f!r} timed out")
                await self.rest(1000 / self.fps)
            await self.rest(300)
        elif do == "eval":
            ev["result"] = str(await self.page.evaluate(a["js"]))[:400]
            await self.rest(a.get("ms", 200))
        elif do == "scroll":
            to = a.get("to", "bottom")
            if isinstance(to, (int, float)):
                y1 = float(to)
            elif to in ("top", "bottom"):
                y1 = 0 if to == "top" else await self.page.evaluate(
                    "document.documentElement.scrollHeight-innerHeight")
            else:
                b = await self.box(to)
                y1 = max(0, await self.page.evaluate("scrollY") + b["y"] - self.vh * a.get("offset", .15))
            ev["key"] = round(self.vt(), 1)
            await self.smooth_scroll(y1, a.get("ms", 1100))
        elif do == "mark":
            self.marks[a["name"]] = round(self.vt(), 1)
        elif do == "hide_cursor":
            self.visible = False
        else:
            raise ValueError(f"unknown action {do!r}")
        if a.get("focus") and do != "camera":
            try:
                ev["focus_box"] = await self.box(a["focus"])
            except Exception:                                    # noqa: BLE001
                pass

    async def run_actions(self, actions: list, scene_id: str) -> list:
        out = []
        for i, a in enumerate(actions):
            ev = {"i": i, "do": a["do"], "t0": round(self.vt(), 1)}
            try:
                await self.act(a, ev)
                ev["ok"] = True
            except Exception as e:                               # noqa: BLE001
                ev["ok"] = False
                ev["error"] = repr(e)[:300]
                print(f"[{scene_id} #{i} {a['do']}] FAILED: {e}", file=sys.stderr)
                raise
            ev["t1"] = round(self.vt(), 1)
            if any(k in a for k in ("zoom", "spotlight", "callout")) and "key" not in ev:
                ev["key"] = ev["t0"]
            for k in ("at", "zoom", "move", "move_ms", "ease", "focus", "sel", "text",
                      "caption", "spotlight", "callout", "sfx", "hold_ms"):
                if k in a:
                    ev[k] = a[k]
            out.append(ev)
        return out

    async def main(self, only: str | None) -> None:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(args=[
                "--hide-scrollbars", "--lang=en-US", "--disable-gpu",
                "--force-device-scale-factor=%s" % self.dsf,
                "--window-size=%d,%d" % (self.vw, self.vh)])
            ctx = await browser.new_context(no_viewport=True, locale="en-US",
                                            ignore_https_errors=True)
            await ctx.add_init_script(
                "(()=>{const f=()=>{const e=document.createElement('style');"
                "e.textContent=%s;(document.head||document.documentElement).appendChild(e)};"
                "document.readyState==='loading'?"
                "document.addEventListener('DOMContentLoaded',f):f()})()" % json.dumps(HIDE))
            self.page = await ctx.new_page()
            self.cdp = await ctx.new_cdp_session(self.page)
            self.cdp.on("Page.screencastFrame", self.on_frame)

            await self.page.goto(self.sb["project"]["url"], wait_until="domcontentloaded",
                                 timeout=90000)
            try:
                await self.page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:                                    # noqa: BLE001
                pass
            await self.page.evaluate(HEARTBEAT)
            await self.run_actions(self.sb.get("setup", []), "setup")

            await self.cdp.send("Page.startScreencast", {
                "format": "jpeg", "quality": 90,
                "maxWidth": int(self.vw * self.dsf), "maxHeight": int(self.vh * self.dsf),
                "everyNthFrame": 1})
            self.t0 = time.time()
            self.capturing = True
            self.note_cursor()

            for sc in self.sb["scenes"]:
                if sc.get("type", "live") != "live" or (only and sc["id"] != only):
                    continue
                t0 = self.vt()
                acts = await self.run_actions(sc.get("actions", []), sc["id"])
                await self.rest(sc.get("tail_ms", 400))
                self.scenes[sc["id"]] = {"t0": round(t0, 1), "t1": round(self.vt(), 1),
                                         "actions": acts}
                print("scene %-12s %6.2fs of footage, %d frames so far"
                      % (sc["id"], (self.vt() - t0) / 1000, len(self.frames)))

            self.capturing = False
            try:
                await self.cdp.send("Page.stopScreencast")
            except Exception:                                    # noqa: BLE001
                pass
            await browser.close()

        json.dump({"fps": self.fps, "dsf": self.dsf, "viewport": [self.vw, self.vh],
                   "frames": self.frames, "cursor": self.cursor_log, "clicks": self.clicks,
                   "keys": [], "marks": self.marks, "scenes": self.scenes},
                  open(os.path.join(self.out, "events.json"), "w"))
        secs = self.frames[-1][0] / 1000 if self.frames else 0
        print("recorded %d frames over %.1fs (%.1f fps effective) -> %s"
              % (len(self.frames), secs, len(self.frames) / secs if secs else 0, self.out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard")
    ap.add_argument("--scene")
    o = ap.parse_args()
    sb = json.load(open(o.storyboard))
    asyncio.run(Recorder(sb, os.path.dirname(os.path.abspath(o.storyboard))).main(o.scene))
