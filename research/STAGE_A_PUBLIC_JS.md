# Stage A follow-up — public JavaScript investigation (11 October 2026)

## Goal
Investigate whether the Comix extension can use ordinary HTTPS and public website JavaScript without requiring Android WebView on Tachimanga/iPhone.

**Result: No WebView-free signing material or working extension fix has been verified.**

## Live observations
- One public Comix title page includes 2 module script tags and an accessible main JavaScript bundle.
- The main bundle was downloaded (195,327 bytes) and references **34** JavaScript import files.
- The structural probe downloaded **all 34 of 34** imports, with no errors.
- One file, secure-tmq6ux-cJcHHB1g.js (191,484 bytes), contains 4 textual references to atob.
- The scan found no simple direct call with a fixed base64 literal yielding the 24-, 32- or 256-byte data used by the Android bridge, and no bare direct atob calls in that particular module. These syntactic findings do not prove how the site's code produces the values.
- The main bundle itself contained no atob mentions.
- Across **all 34** imported modules, only the secure module contained atob mentions; **no straightforward static atob literal matching the expected cipher data lengths** was found in this scan. This does not rule out dynamic or obfuscated initialization.
- Combined size of the 34 scanned imports was approximately 1,006,094 bytes.
- All **22 synthetic/offline tests passed** in GitHub Actions. These tests do not demonstrate working chapter loads or iPhone compatibility.

## Evidence
- Public JavaScript structure: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38123346835
- Secure module syntax: https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38123458969
- Full 34-module scan (22 offline tests passed): https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38123547272
- Previous unsigned direct API test (HTTP 403): https://github.com/afroazn/comix-tachimanga-ios/actions/runs/38122895553

## Interpretation
The copied upstream Kotlin already has direct HTTP chapter fetching, but obtains signing/decryption data from website JavaScript run inside Android WebView. This analysis did NOT identify a simple, stable static substitute. **All 34 statically referenced imports were structurally inspected**, but no executable JavaScript was run. The scan may still miss dynamic imports, indirect string creation and other initialization paths. The investigation has not executed website JavaScript or extracted dynamic keys.

## Next engineering gate
A WebView-free extension requires proof of a reproducible, permitted source for all needed chapter information and valid request material that does not depend on unsupported app functions. If that cannot be demonstrated, only Tachimanga's native WKWebView integration or a different authorized source will resolve chapter loading. Keep the original Kotlin unchanged and do not advertise an installable or fixed extension.

References:
- https://github.com/keiyoushi/extensions-source/issues/15755
- https://github.com/keiyoushi/extensions-source/issues/19830
- https://github.com/keiyoushi/extensions-source/tree/main/src/en/comix
