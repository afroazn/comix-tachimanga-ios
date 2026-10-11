# Comix signing material investigation — 11 October 2026

## Question
Can we reverse engineer the public Comix website JavaScript to obtain chapter API signing/decryption material without modifying Tachimanga on iPhone?

**Outcome: The extension's key-capture method is understood, but no reusable key or browser-free acquisition path was demonstrated.**

## What the original Kotlin code actually does
See the source snapshot under upstream/comix/src/eu/kanade/tachiyomi/extension/en/comix/.

- Comix.kt lines ~861–949 create Android WebView, inject a script before other website scripts, and run the public Comix webpage.
- That script wraps the browser's atob() decoder and watches for decoded buffers of **three 256-byte tables**, plus **three 24- or 32-byte key arrays**.
- When the website's JS produces chapter/page data, the injected bridge sends the data plus the six captured arrays back to the Android extension.
- Cipher.kt accepts these as three substitution tables and three keys. Its sign() and decrypt() methods work locally after material exists.
- getNativeChapterList/getSigned can make direct HTTP requests **only if** a valid ComixCipher has been initialized.
- Therefore, solving this for iPhone is primarily a **bootstrap acquisition** problem, not a missing URL or a need to rewrite the signing algorithm.

## Public JavaScript static inspection
- The live title page's main JavaScript referenced 34 import modules; all 34 were retrievable with ordinary public HTTPS requests.
- Static code inspection identified a 191,484-byte secure module, secure-tmq6ux-cJcHHB1g.js, SHA-256 prefix 7de4289d73d5. It uses obfuscated VM-like variable names (e.g. vmX7_86fdc9) and references atob through property getters/setters.
- Those occurrences did NOT expose any obvious fixed literal arrays. We did not demonstrate whether the material is generated, downloaded, or assembled during runtime.
- The other checked modules did not have the same atob references. Static absence of a literal is **not** proof that no static material exists.

Evidence: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38124309576

## Ordinary browser session feasibility
A single headless Chrome session was launched on GitHub Actions. It added the same *shape counting* decoder wrapper before navigating to one public Comix title page, and waited briefly for natural website JavaScript. It did not collect data values, sign API requests, or bypass any challenge.

- Browser navigation returned **HTTP 403**.
- Number of decoded buffers of length 24: **0**.
- Length 32: **0**.
- Length 256: **0**.
- This run could not confirm runtime key acquisition because the browser session was refused; it is **not evidence that a normal allowed browser session does not create the material**.
- This result is different from the successful plain HTML GET on the same title path in earlier GitHub Actions runs; the site may handle automated browsers differently.

Evidence: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38124409839

## What we can and cannot claim
**Established:** The Android extension has a mechanism to observe six dynamically decoded byte buffers and uses them to initialize local signing/decryption. Its native request path is already implemented. The public Comix JS is accessible, but heavily obfuscated.

**Not established:** a reusable key, the actual current byte values, whether those byte values rotate per deployment or session, or a standalone function that safely generates them without a browser. We also have not verified if a valid signed request would require further cookies, authorization or challenge state, or if Tachimanga can execute a compatible JavaScript runtime.

**Decision:** Do not hard-code guessed keys or promise a working iPhone extension. Only pursue an extension-only implementation if an authorized browser-independent method of obtaining required material can be demonstrated and Tachimanga's supported extension APIs can run it. The next most useful engineering check is Tachimanga's supported extension runtime/capabilities; Apple's WKWebView cannot be instantiated by the existing Keiyoushi Kotlin extension without app-side support.

## Test artifacts
- research/inspect_public_key_origin.py: bounded structural static analysis of public JS.
- research/browser_capture_shapes.cjs: single-session browser probe that counts expected decoded lengths only.
- tests/test_stage_a_key_origin.py: synthetic redaction tests.
- .github/workflows/comix-key-origin-once.yml and comix-browser-key-shape-once.yml: one-shot research workflows.
- No original Comix Kotlin files changed and no iOS extension built.

For references see https://github.com/keiyoushi/extensions-source/issues/15755 and https://github.com/keiyoushi/extensions-source/issues/19830 .
