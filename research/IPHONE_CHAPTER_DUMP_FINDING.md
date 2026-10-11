# iPhone Comix chapter-page HTTP dump — sanitized observation (11 Oct 2026)

User provided a diagnostic dump from Tachimanga on iPhone, requesting help with chapter access. **Do not commit, reprint, or reuse any Cookie/session/cf_clearance values from that dump. Those are sensitive credentials and have deliberately been excluded here.**

## Confirmed observations
- Method: GET
- Host: comix.ws
- Path: /title/0080d-the-unlimited-bacteriomancer/11464659-chapter-15
- HTTP status: **200**
- Content-Type: text/html
- Returned content includes server-rendered manga metadata, chapter page identity, and script#initial-data with a "read" object containing mangaId 121745 and chapterId 11464659.
- **No result.pages or image-page list** is present in the provided HTML's initial-data.
- The user reports the same page loads successfully in Tachimanga Open in WebView and in Brave.

## Meaning in upstream code
See copied Comix.kt lines ~725–773:
1. getNativePageList() is attempted when cipher != null, calling a signed GET to /api/v1/chapters/{chapterId}.
2. If that path cannot be used, the extension GETs getChapterUrl() and parses it as HTML.
3. **The observed HTTP 200 is consistent with this HTML GET succeeding.**
4. Next, getPageList() invokes runInWebView() to wait for a JS-parsed object with result.pages and pass the payload to Kotlin.
5. runInWebView() in copied Comix.kt lines ~861–951 uses Android-only WebView APIs from Keiyoushi. Current Tachimanga's iOS extension runtime has no documented equivalent accessible to Keiyoushi Kotlin extensions.
6. Thus the failing stage may be the WebView-to-extension bridge, despite the HTML HTTP 200; not yet confirmed by an exception log.

## What this dump does NOT prove
- It does not show any call to /api/v1/chapters/11464659 or the HTTP status of such a call.
- It does not prove that cookies solve the separately signed chapter API; an HTML 200 is not an image API success.
- It does not identify the exact exception thrown by Tachimanga.

## Next noninvasive checkpoint
With HTTP dumping OFF when no longer needed, inspect *redacted* errors/stack traces in Enable log -> Export log after triggering the chapter-loading failure. Look for the failure at runWebView, or search existing dump list for the separately signed /api/v1/chapters/11464659 request. User should never share Cookies, cf_clearance, Authorization, API signatures, full request/response bodies, or private identifiers. If raw cookies have been shared, clear/reset those site cookies and sign in afresh if appropriate.

## Conclusion
The supplied proof changes the earlier assessment: the **chapter HTML request was accepted (200)**. Investigate JavaScript execution/data transfer first; do not claim the entire chapter-reading request was rejected.
