# Comix iOS failure diagnosis from user-provided Tachimanga log (11 Oct 2026)

**Sensitive diagnostic handling:** Original ZIP includes cookies, session/Cloudflare credentials, other-app cookies, HTTP data, and private local settings. The raw ZIP and all credential values MUST NOT be committed, quoted, or redistributed. This file contains only sanitized technical observations.

## Repro and confirmed timeline (approximate)
- 21:59:01 — The ordinary chapter HTML GET started.
- 21:59:02 — Native networking reported success for that HTML GET (around 437 ms, no transport error).
- 21:59:02 — The iOS runtime created a NativeWeb object and registered **two** JavaScript interfaces with random bridge names.
- 21:59:02 — Tachimanga called NativeWeb `loadDataWithBaseURL` using the actual chapter URL and an HTML document containing the extension's injected Comix capture script.
- 21:59:02 — NativeWeb reported navigation commit, progress 100%, and didFinishNavigation.
- For ~120 seconds, the extension repeatedly invoked NativeWeb `evaluateJavascript` (about **997** calls; all return null and no JavaScript exception is logged). Null is expected because Comix's async capture script explicitly returns null immediately.
- **22:01:02 — `java.lang.Exception: Timed out waiting for WebView`**, propagated to Tachimanga's local chapter endpoint with **HTTP 500**. The NativeWeb object was destroyed.

## What this rules out
- It is *not* simply HTTP 403 for the chapter HTML: that GET succeeded.
- It is *not* absence of any browser API on iOS: in this version, NativeWeb supports an apparent compatibility shim for `addJavascriptInterface`, `loadDataWithBaseURL` and `evaluateJavascript`. This updates earlier research notes that implied the browser bridge was entirely absent.
- There is no captured evidence that Comix returned the page image list through the bridge.
- The null JavaScript evaluation results are **not** evidence of a JavaScript crash; the embedded script is designed to return null while starting asynchronous work.

## Most likely failure boundary
In copied Comix.kt's getPageList(), getNativePageList() was unavailable or failed. The fallback loads chapter HTML then waits for a JavaScript object matching `{ result: { pages: ... } }`. It only checks embedded `script#initial-data` and intercepts *global* `JSON.parse` results. It does not intercept the results of `Response.prototype.json`, or chapter JSON observed through normal `fetch`/XHR response reading. Modern browser APIs may parse JSON without calling the global JSON.parse function. **This is a plausible, not confirmed, cause** of the timeout. Other possibilities include a failure inside the website scripts, a mismatch in the message bridge, or a changed payload shape.

## Experimental extension-only patch
Branch `fix/comix-ios-page-capture-prototype` extends the page capture script to observe resolved `Response.json()` results and chapter JSON fetched by `fetch` or XHR. It preserves and forwards original responses unchanged and only calls the existing bridge for a valid `result.pages` object. The Android-specific Kotlin source on research branches was otherwise preserved.

**Do not merge, distribute, or install as fixed until tests pass and a real iPhone chapter image list loads.** The regression test source is saved in research/test_page_capture.cjs; GitHub workflow creation was blocked so CI confirmation is not yet available. The copied extension is not independently buildable as an iOS package yet.

## Recommended verification
1. Offline JS fixtures: page HTML embedded JSON; `Response.json()`; `fetch` chapter API JSON; unrelated network responses; XHR; repeated polling.
2. Build extension with appropriate Keiyoushi toolchain after a full project is prepared.
3. Test on a real iPhone without changing the app: chapter must return page URLs within a short time. If it still hangs, add safe, count-only bridge diagnostics to differentiate no chapter API output versus message delivery failure.

Original website session data was intentionally excluded.
