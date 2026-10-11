# Comix upstream snapshot and iOS compatibility

## Provenance
Copied from [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source), `src/en/comix` (Comix versionCode 44, library version 1.6), 11 October 2026. Upstream source uses the Apache License, Version 2.0 (see root LICENSE). Maintain upstream attribution and notices.

## State
This is a **research-only source snapshot**, not a standalone Gradle project, APK, or Tachimanga-compatible extension feed. The original Keiyoushi build uses a shared Gradle plugin and extension libraries not included here.

## Confirmed code-level problem
`Comix.kt`, `getWebViewChapterList`, imports JavaScript modules referenced by the site's main bundle, then looks for a module export with a callable `chapters` property. If nothing matches, it throws `Could not find manga API`. Upstream issue: https://github.com/keiyoushi/extensions-source/issues/19830

## iOS compatibility concerns
The source is Android Kotlin and imports `android.webkit.WebResourceResponse`. It calls `runWebView` and uses an Android-style injected JavaScript bridge. A Tachimanga iOS integration must provide compatible behavior. Neither the API fix nor the required iOS runtime features has been verified.

## Next checkpoint
1. Inspect the current Comix website module loading/API shape and confirm which part of API discovery fails.
2. Inspect the Tachimanga extension runtime for supported Android APIs/WebView bridge behavior.
3. Add regression tests and implement the smallest provable correction.
4. Test in the actual iOS client before releasing or publishing a repository feed.

Do not install this repository URL as an extension source. No installable artifacts are published.
