# Stage A — WebView-free Comix feasibility (11 October 2026)

## Goal
Determine whether Comix chapter lists and pages can be fetched by ordinary HTTPS and parsed without Android WebView, for potential Tachimanga/iOS compatibility.

**Status: Stage A live probes completed; the tested WebView-free routes are NOT sufficient. No working iOS extension has been produced.**

## Confirmed observations from copied upstream Comix 1.6.44
- Comix.kt lines 692–712: getNativeChapterList calls /api/v1/manga/{mangaId}/chapters.
- Comix.kt lines 794–797: getNativePageList calls /api/v1/chapters/{chapterId}.
- Comix.kt lines 802–831: getSigned requires ComixCipher for signing and response decryption. If cipher is null, it returns null.
- Comix.kt lines 467–476 and 725–729: missing native results fall back to Android WebView.
- Comix.kt lines 861–951: runInWebView initializes the cipher from JavaScript data captured within an Android WebView. The source has no other fresh-start cipher initialization route.
- Comix.kt lines 320–325: the extension can parse script#initial-data queries in normal HTML, but their inclusion of complete chapter lists has NOT been confirmed.
- The October 10 upstream PR #19791 fixed renamed JavaScript bundles, not the WebView bootstrap dependence.

## Live tests completed 11 October 2026 (GitHub Actions)
1. **Unsigned direct chapter API:** One ordinary GET to /api/v1/manga/rrglg/chapters?limit=1&order[number]=desc&page=1 on comix.ws returned **HTTP 403** with no usable chapter JSON. No retries, token/signature extraction, or challenge bypass was performed. This is evidence for the tested route only, not proof that all requests fail.
   - Run: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38122895553
2. **Public title HTML:** One normal GET to a publicly indexed Comix title page returned valid script#initial-data JSON with **four query entries** but **zero chapter-list candidates** matching the upstream Chapter DTO.
   - Run: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38122701093
3. **Query structure of the same title:** Embedded JSON query keys were manga detail, recommended, groups, and collections. There was **no chapter-list query** in this particular page's embedded data. The detail object exposes latest/first chapter links, not the full chapter catalogue.
   - Run: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38122784905
4. **Offline validation:** **16 synthetic/unit tests passed** for read-only HTML extraction, structure inspection, and API response classification; these do not test the current website or iOS app.
   - Run: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38122895503

**Interpretation:** For the tested page and unsigned request, native HTTP does not provide the complete chapter list. The existing Kotlin native path already knows the API endpoint and signing algorithm, but bootstraps dynamic cipher material through Android WebView. There is no verified standalone Stage A fix at present. Additional changes must be backed by a reproducible legitimate response; no hard-coded signing keys, guessed endpoints, or invented working extension.

## Native HTML diagnostic
research/stage_a_native_http_probe.py inspects HTML for script#initial-data JSON and recognizes arrays whose objects contain numeric chapter id and number fields, matching the upstream Chapter DTO. It does not execute JavaScript, reproduce browser challenges, sign requests, or log chapter text.

Offline, with a sample you are authorized to inspect:

    python research/stage_a_native_http_probe.py --html-file /path/to/title.html

Optional one-GET public URL check:

    python research/stage_a_native_http_probe.py --url https://comix.to/title/VALID-TITLE-SLUG

Synthetic offline tests:

    python -m unittest discover -s tests -p "test_stage_a*.py" -v

Even a positive result does not establish that all chapters/pages are present or usable.

## Decision gates
1. **SSR path:** Live title HTML embeds sufficient structured chapter entries. If true, port an evidenced native parser into Kotlin with fixture tests.
2. **Direct-API path:** An authorized ordinary GET produces chapter JSON without dynamic browser signing. If true, isolate and test a Kotlin implementation.
3. **Signing requirement:** If current API requires browser-generated, rotating cipher material, a WebView-free initial request remains blocked. Confirm supported iOS integration rather than hard-coding guessed signatures or endpoints.
4. **iPhone verification:** Never mark repaired until a new manga title, chapter listing, and pages load inside Tachimanga on a real iPhone.

## Sources
- https://github.com/keiyoushi/extensions-source/tree/main/src/en/comix
- https://github.com/keiyoushi/extensions-source/issues/19830
- https://github.com/keiyoushi/extensions-source/issues/15755
- https://github.com/keiyoushi/extensions-source/pull/19791

Root LICENSE preserves Apache 2.0 terms. Original Kotlin extension code has intentionally NOT been modified.
