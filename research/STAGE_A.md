# Stage A — WebView-free Comix feasibility (11 October 2026)

## Goal
Determine whether Comix chapter lists and pages can be fetched by ordinary HTTPS and parsed without Android WebView, for potential Tachimanga/iOS compatibility.

**Status: BLOCKED ON LIVE VALIDATION. No working iOS extension has been produced.**

## Confirmed observations from copied upstream Comix 1.6.44
- Comix.kt lines 692–712: getNativeChapterList calls /api/v1/manga/{mangaId}/chapters.
- Comix.kt lines 794–797: getNativePageList calls /api/v1/chapters/{chapterId}.
- Comix.kt lines 802–831: getSigned requires ComixCipher for signing and response decryption. If cipher is null, it returns null.
- Comix.kt lines 467–476 and 725–729: missing native results fall back to Android WebView.
- Comix.kt lines 861–951: runInWebView initializes the cipher from JavaScript data captured within an Android WebView. The source has no other fresh-start cipher initialization route.
- Comix.kt lines 320–325: the extension can parse script#initial-data queries in normal HTML, but their inclusion of complete chapter lists has NOT been confirmed.
- The October 10 upstream PR #19791 fixed renamed JavaScript bundles, not the WebView bootstrap dependence.

## Live-validation limitation
The research environment retrieved an empty extracted text result for Comix home/browse. Direct API URLs were inaccessible using the website-reading tool. This is not a verified HTTP 403 and cannot prove that all API requests require WebView. No current JS bundle or chapter API response was captured.

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
