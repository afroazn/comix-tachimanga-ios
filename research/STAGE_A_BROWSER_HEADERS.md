# Stage A — Browser disguise experiment (11 October 2026)

**Question:** Can we make an ordinary direct Comix API request look like iPhone Safari, without running WebView?

## Test
Sent exactly one ordinary HTTPS request from a GitHub Actions runner to the same publicly documented chapter-list API route used in the Keiyoushi extension, with a Safari-style User-Agent, JSON Accept header, language header, and a Comix title-page Referer.

No browser session cookies, JavaScript execution, request signing, challenge solving, retries, or API credential capture were used.

## Verified outcome
**HTTP 403; no chapter JSON.**

GitHub Actions evidence:
https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38123992674

## What this does and does not prove
- Basic browser identification headers are **not enough** for the tested Comix chapter endpoint from this GitHub environment.
- The result is consistent with the existing Comix Kotlin source, which uses a browser-created signing/decryption context.
- We cannot attribute the refusal solely to signature validation: the service might also consider runner IP, browser session, or other criteria.
- This does **not** prove that a valid browser's own request would fail; no valid session was tested.
- It does **not** produce a Tachimanga iPhone fix.

No upstream Comix source was modified; this is research only. Do not publish it as an installable extension.
