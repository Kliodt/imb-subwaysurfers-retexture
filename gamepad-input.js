/* First visible gamepad -> existing Digit1..Digit9 keyboard remapping. */
(() => {
    "use strict";
    const mapping = new Map([
        [6, "Digit7"], [2, "Digit8"], [7, "Digit9"],
        [0, "Digit4"], [3, "Digit6"],
        [5, "Digit1"], [1, "Digit2"], [4, "Digit3"]
    ]);
    if (typeof navigator.getGamepads !== "function") {
        console.warn("Gamepad API is not available in this browser.");
        return;
    }
    let pressed = new Set();
    let selected = null;
    let active = true;
    let warned = false;

    function release() {
        for (const key of pressed) {
            if (document.querySelector("canvas")) window.gameInput.sendKeyEvent(key, false);
        }
        pressed.clear();
        selected = null;
    }

    function poll() {
        try {
            if (!active || document.hidden || !document.querySelector("canvas")) {
                release();
                return;
            }
            const pad = Array.from(navigator.getGamepads()).filter(Boolean)[0];
            const identity = pad ? `${pad.index}:${pad.id}` : null;
            if (identity !== selected) release();
            selected = identity;
            const next = new Set();
            if (pad) {
                for (const [button, key] of mapping) {
                    if (pad.buttons[button]?.pressed) next.add(key);
                }
                if (pad.axes[1] >= 1) next.add("Digit5");
            }
            for (const key of pressed) {
                if (!next.has(key)) window.gameInput.sendKeyEvent(key, false);
            }
            for (const key of next) {
                if (!pressed.has(key)) window.gameInput.sendKeyEvent(key, true);
            }
            pressed = next;
        } catch (error) {
            if (!warned) console.warn("Gamepad input failed:", error);
            warned = true;
        } finally {
            requestAnimationFrame(poll);
        }
    }
    window.addEventListener("blur", () => { active = false; release(); });
    window.addEventListener("focus", () => { active = true; });
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) release();
    });
    window.addEventListener("gamepaddisconnected", event => {
        if (selected === `${event.gamepad.index}:${event.gamepad.id}`) release();
    });
    requestAnimationFrame(poll);
})();
