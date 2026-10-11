# Tachimanga existing WebView: communication feasibility (11 Oct 2026)

## User-observed result
The Comix website and its chapters load within Tachimanga's **Open in WebView** on iPhone, but normal Comix extension chapter fetching is broken. The user wants **no modifications to the iOS app itself**.

## Already-supported connection worth testing: cookies
Tachimanga announced **Advanced Cookie Support** in preview v4.3 build333 (4 April 2025), including CookieManager, CookieJar and custom Cookie headers, with an option under Settings > General > Labs. If available in the user's installed version, turn it on, open the Comix title in WebView, return to normal extension chapter view and refresh. This checks whether sharing session cookies removes an HTTP/session barrier; it does **not** supply Comix's dynamic request-signing data.

Official release notes: https://tachimanga.app/docs/changelogs.html

## Remaining limitation: JavaScript bridge
Keiyoushi's Android WebView utility uses android.webkit.WebView.addJavascriptInterface() and evaluateJavascript(). The Comix extension's runInWebView() relies on this Android-only machinery to observe the site's JavaScript-decoded signing material and deliver chapter data. Tachimanga's public extension documentation describes Kotlin/OkHttp/JSoup and HTTP source methods, and only documents Open in WebView as opening the URL. It does **not** document a callable extension-side API for evaluating JavaScript in the displayed iOS WebView or returning messages from that page.

Source: https://github.com/keiyoushi/extensions-source/blob/main/core/src/main/kotlin/keiyoushi/utils/WebView.kt
Tachimanga guide: https://tachimanga.app/help/guides/extensions_guide.html
Developer confirmation: https://github.com/keiyoushi/extensions-source/issues/15755

## Engineering consequences
- Merely setting User-Agent, sharing cookies, or switching Kotlin to Python does not execute the required site's signing JavaScript inside a supported extension context.
- An extension can communicate with a service using HTTP, if the server provides accessible authorized data; but Comix's tested **unsigned** chapter endpoint rejects these requests with HTTP 403.
- An external browser-to-HTTP relay would require an explicit mechanism to send chapter *data* out of the allowed browser, and a corresponding custom extension to consume it. It is not already built, is not seamless, could be fragile, and must not export login credentials, cookies or signing keys.
- Without app changes, the only plausible seamless path is an already exposed extension-side JavaScript execution/browser bridge (none is documented); or independently working authorized plain-HTTP endpoints (not verified). A remote helper running a supported browser is a separate, more complex architecture and has no success evidence yet.
- Don't claim that the in-app WebView and the extension already exchange chapter payloads. A webpage showing chapters does not mean the Kotlin extension can read its DOM or JavaScript memory.

## Decision
1. Test the built-in Advanced Cookie Support setting using the user's working Tachimanga WebView; no app code changes.
2. If that fails, request **documentation/confirmation of an existing extension-accessible WKWebView or JS execution interface** from Tachimanga. Do not modify the app unless user changes constraint.
3. Only build a lightweight external helper with user approval and a concrete, permitted data source, after confirming Tachimanga extension can consume its output.

No original Kotlin Comix code was changed by this research note. No iOS fix verified.
