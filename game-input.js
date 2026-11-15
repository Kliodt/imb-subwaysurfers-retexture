/* Browser-side input for the Unity canvas. Coordinates are CSS pixels. */
(() => {
    "use strict";
    // Unity creates its canvas asynchronously. Keep it out of Tab navigation,
    // while retaining focus() for keyboard input and programmatic controls.
    function disableCanvasTabFocus() {
        for (const element of document.querySelectorAll("canvas")) {
            if (element.tabIndex !== -1) element.tabIndex = -1;
        }
    }
    disableCanvasTabFocus();
    new MutationObserver(disableCanvasTabFocus).observe(document.documentElement, {
        childList: true, subtree: true, attributes: true, attributeFilter: ["tabindex"]
    });
    // Poki reports gameplay transitions; null until the first observed event.
    let gameRunning = null;
    window.isGameRunning = () => gameRunning;
    const gameplayHooks = new WeakSet();
    function watchGameplay() {
        const sdk = window.PokiSDK;
        if (!sdk) return;
        for (const [name, running] of [["gameplayStart", true], ["gameplayStop", false]]) {
            const original = sdk[name];
            if (typeof original !== "function" || gameplayHooks.has(original)) continue;
            const wrapped = function (...args) {
                gameRunning = running;
                return original.apply(this, args);
            };
            gameplayHooks.add(wrapped);
            sdk[name] = wrapped;
        }
    }
    watchGameplay();
    // SDK loads asynchronously and may replace its initial stub methods.
    window.addEventListener("load", watchGameplay, true);
    setInterval(watchGameplay, 250);
    // Replace this function to remap every keydown/keyup before Unity sees it.
    // Keys use KeyboardEvent.code (KeyA, ArrowLeft, Space), independent of layout.
    let digit5EscapeDown = false;
    window.keyPressed = window.keyPressed || (({ key, isDown, repeat }) => {
        // 7 8 9
        // 4 5 6 
        // 1 2 3
        // console.log(key);
        const mapping = Object.freeze({
            Digit1: (isDown, repeat) => {
                if (isDown && !repeat) setTimeout(() => window.gameInput.sendKey('ArrowDown'), 0);
                return {key: 'ArrowLeft', isDown, repeat};
            },
            Digit2: (isDown, repeat) => ({key: 'ArrowDown', isDown, repeat}),
            Digit3: (isDown, repeat) => {
                if (isDown && !repeat) setTimeout(() => window.gameInput.sendKey('ArrowDown'), 0);
                return {key: 'ArrowRight', isDown, repeat};
            },
            Digit4: (isDown, repeat) => ({key: 'ArrowLeft', isDown, repeat}),
            Digit5: (isDown, repeat) => {
                if (!isDown) {
                    if (!digit5EscapeDown) return null;
                    digit5EscapeDown = false;
                    return {key: 'Escape', isDown, repeat};
                }
                if (isDown && !repeat) {
                    // const cnv = canvas();
                    // const { width, height } = cnv.getBoundingClientRect();
                    // // check is we are on the start screen by checking the purple "top run" button
                    // getPixelColor(width / 2 - 120, height - 60)
                    //     .then((rgba) => {
                    //         const etalon = [80, 43, 139, 255];
                    //         for (let i = 0; i < 4; i++) {
                    //             if (Math.abs(rgba[i] - etalon[i]) > 5) {
                    //                 // we are not on home screen
                    //                 window.gameInput.sendClick(width / 2 - 155, height - 60);
                    //                 return;
                    //             }
                    //         }
                    //         // we are on home screen
                    //     });
                    if (window.isGameRunning()) {
                        setTimeout(() => window.gameInput.sendClick(200, 2), 0);
                        return;
                    } else {
                        digit5EscapeDown = true;
                        return {key: 'Escape', isDown, repeat};
                    }
                }
                return null;
            },
            Digit6: (isDown, repeat) => ({key: 'ArrowRight', isDown, repeat}),
            Digit7: (isDown, repeat) => {
                if (isDown && !repeat) setTimeout(() => window.gameInput.sendKey('ArrowUp'), 0);
                return {key: 'ArrowLeft', isDown, repeat};
            },
            Digit8: (isDown, repeat) => ({key: 'ArrowUp', isDown, repeat}),
            Digit9: (isDown, repeat) => {
                if (isDown && !repeat) setTimeout(() => window.gameInput.sendKey('ArrowUp'), 0);
                return {key: 'ArrowRight', isDown, repeat};
            },
        });
        if (mapping[key]) {
            return mapping[key](isDown, repeat);
        }
        return {key, isDown, repeat};
    });
    const forwarded = new WeakSet();
    const aliases = { Left: "ArrowLeft", Right: "ArrowRight", Up: "ArrowUp", Down: "ArrowDown", " ": "Space", Spacebar: "Space", Esc: "Escape" };
    const special = { ArrowLeft: 37, ArrowUp: 38, ArrowRight: 39, ArrowDown: 40, Space: 32, Enter: 13, Escape: 27, Tab: 9, Backspace: 8, ShiftLeft: 16, ShiftRight: 16, ControlLeft: 17, ControlRight: 17, AltLeft: 18, AltRight: 18, MetaLeft: 91, MetaRight: 92, CapsLock: 20, Delete: 46, Insert: 45, Home: 36, End: 35, PageUp: 33, PageDown: 34, Pause: 19, PrintScreen: 44, ScrollLock: 145, NumLock: 144, ContextMenu: 93 };
    const names = { Space: " ", ShiftLeft: "Shift", ShiftRight: "Shift", ControlLeft: "Control", ControlRight: "Control", AltLeft: "Alt", AltRight: "Alt", MetaLeft: "Meta", MetaRight: "Meta" };
    const punctuation = { Backquote: ["`", 192], Minus: ["-", 189], Equal: ["=", 187], BracketLeft: ["[", 219], BracketRight: ["]", 221], Backslash: ["\\", 220], Semicolon: [";", 186], Quote: ["'", 222], Comma: [",", 188], Period: [".", 190], Slash: ["/", 191], NumpadAdd: ["+", 107], NumpadSubtract: ["-", 109], NumpadMultiply: ["*", 106], NumpadDivide: ["/", 111], NumpadDecimal: [".", 110], NumpadEnter: ["Enter", 13] };
    let pending = Promise.resolve();
    const enqueue = action => {
        const result = pending.then(action);
        pending = result.catch(() => {});
        return result;
    };
    function duration(value) {
        if (!Number.isFinite(value) || value < 0) throw new TypeError("durationMs must be a finite nonnegative number");
        return value;
    }
    function canvas() {
        const element = document.querySelector("#unity-canvas, #canvas, canvas");
        if (!element) throw new Error("Game canvas is not ready");
        return element;
    }
    function focus(element) {
        element.tabIndex = -1;
        element.focus({ preventScroll: true });
    }
    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
    function keyInfo(value) {
        if (typeof value !== "string") throw new TypeError("key must be a string, e.g. ArrowLeft, Space or KeyA");
        const code = aliases[value] || (/^[a-z]$/i.test(value) ? "Key" + value.toUpperCase() : /^[0-9]$/.test(value) ? "Digit" + value : value);
        if (Object.hasOwn(special, code)) return { code, key: names[code] || code, number: special[code] };
        if (Object.hasOwn(punctuation, code)) return { code, key: punctuation[code][0], number: punctuation[code][1] };
        if (/^F([1-9]|1[0-9]|2[0-4])$/.test(code)) return { code, key: code, number: 111 + Number(code.slice(1)) };
        if (/^Numpad[0-9]$/.test(code)) return { code, key: code.slice(6), number: 96 + Number(code.slice(6)) };
        if (/^Key[A-Z]$/.test(code)) return { code, key: code.slice(3).toLowerCase(), number: code.charCodeAt(3) };
        if (/^Digit[0-9]$/.test(code)) return { code, key: code.slice(5), number: code.charCodeAt(5) };
        throw new TypeError("Unsupported key: " + value);
    }
    function keyboard(target, type, info, original = {}, repeat = original.repeat) {
        const event = new KeyboardEvent(type, { key: info.key, code: info.code, bubbles: true, cancelable: true, view: window,
            repeat: type === "keydown" && !!repeat,
            location: original.location || (/^Numpad/.test(info.code) ? 3 : /Right$/.test(info.code) && !info.code.startsWith("Arrow") ? 2 : 0),
            shiftKey: !!original.shiftKey || (type === "keydown" && info.key === "Shift"), ctrlKey: !!original.ctrlKey || (type === "keydown" && info.key === "Control"), altKey: !!original.altKey || (type === "keydown" && info.key === "Alt"), metaKey: !!original.metaKey || (type === "keydown" && info.key === "Meta") });
        // Unity's legacy input bridge reads these alongside key and code.
        for (const name of ["keyCode", "which"]) Object.defineProperty(event, name, { value: info.number });
        forwarded.add(event);
        target.dispatchEvent(event);
    }
    function remap(target, key, isDown, original) {
        const repeat = isDown && !!original?.repeat;
        const result = window.keyPressed({ key, isDown, repeat });
        if (result == null) return; // No return (undefined), or null: send nothing.
        if (typeof result.key !== "string" || typeof result.isDown !== "boolean") throw new TypeError("keyPressed must return {key: string, isDown: boolean} or null");
        if (result.repeat !== undefined && typeof result.repeat !== "boolean") throw new TypeError("repeat must be a boolean");
        let info;
        // Preserve every physical key, even ones not in our sendKey shorthand table.
        if (original && result.key === key) info = { code: original.code, key: original.key, number: original.keyCode || original.which || 0 };
        else info = keyInfo(result.key);
        keyboard(target, result.isDown ? "keydown" : "keyup", info, original, result.repeat ?? repeat);
    }
    // async function getPixelColor(x, y) {
    //     const module = window.unityGame.Module;
    //     const canvas = module.canvas;
    
    //     return new Promise((resolve, reject) => {
    //         const previous = module.postMainLoop;
    
    //         module.postMainLoop = function (...args) {
    //             module.postMainLoop = previous;
    
    //             try {
    //                 previous?.apply(this, args);
    
    //                 const gl = canvas.getContext("webgl2")
    //                     || canvas.getContext("webgl");
    //                 const rect = canvas.getBoundingClientRect();
    
    //                 if (x < 0 || y < 0 || x >= rect.width || y >= rect.height)
    //                     throw new RangeError("Точка вне canvas");
    
    //                 const px = Math.floor(x * gl.drawingBufferWidth / rect.width);
    //                 const py = gl.drawingBufferHeight - 1
    //                     - Math.floor(y * gl.drawingBufferHeight / rect.height);
    
    //                 const target = gl.READ_FRAMEBUFFER ?? gl.FRAMEBUFFER;
    //                 const binding = gl.READ_FRAMEBUFFER_BINDING
    //                     ?? gl.FRAMEBUFFER_BINDING;
    //                 const oldFramebuffer = gl.getParameter(binding);
    //                 const rgba = new Uint8Array(4);
    
    //                 try {
    //                     gl.bindFramebuffer(target, null);
    //                     gl.readPixels(px, py, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, rgba);
    //                 } finally {
    //                     gl.bindFramebuffer(target, oldFramebuffer);
    //                 }
    
    //                 resolve([...rgba]);
    //             } catch (error) {
    //                 reject(error);
    //             }
    //         };
    //     });
    // }
    for (const type of ["keydown", "keyup", "keypress"]) window.addEventListener(type, event => {
        if (forwarded.has(event)) return;
        const target = document.querySelector("#unity-canvas, #canvas, canvas");
        if (!target) return;
        // Keep native browser shortcuts trusted and uncancelled. Stop Unity's
        // listeners from cancelling them, but allow the browser's default action.
        if (event.ctrlKey || event.metaKey || event.code === "F5" || event.code === "F12" || event.code === "Tab") {
            event.stopImmediatePropagation();
            return;
        }
        // Capture before Unity: it must receive only the returned key, never both.
        event.preventDefault();
        event.stopImmediatePropagation();
        if (type !== "keypress") remap(target, event.code || event.key, type === "keydown", event);
    }, true);
    window.gameInput = Object.freeze({
        // Immediate press/release through the same keyPressed hook as keyboard.
        sendKeyEvent(key, isDown) {
            if (typeof isDown !== "boolean") throw new TypeError("isDown must be a boolean");
            const info = keyInfo(key);
            const target = canvas();
            if (isDown) focus(target);
            remap(target, info.code, isDown);
        },
        sendKey(key, durationMs = 80) {
            const info = keyInfo(key), ms = duration(durationMs);
            return enqueue(async () => {
                const target = canvas(); focus(target);
                try { remap(target, info.code, true); await wait(ms); }
                finally { remap(target, info.code, false); }
            });
        },
        sendClick(x, y, durationMs = 50) {
            if (!Number.isFinite(x) || !Number.isFinite(y)) throw new TypeError("x and y must be finite numbers");
            const ms = duration(durationMs);
            return enqueue(async () => {
                const target = canvas(), rect = target.getBoundingClientRect();
                if (x < 0 || y < 0 || x >= rect.width || y >= rect.height) throw new RangeError("Click is outside the visible canvas (CSS pixels)");
                focus(target);
                const mouse = (type, buttons) => target.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window,
                    clientX: rect.left + x, clientY: rect.top + y, button: 0, buttons, detail: type === "mousemove" ? 0 : 1 }));
                mouse("mousemove", 0);
                try { mouse("mousedown", 1); await wait(ms); }
                finally { mouse("mouseup", 0); }
                mouse("click", 0);
            });
        }
    });
})();
