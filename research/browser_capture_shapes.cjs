// Read-only browser execution probe on one public Comix title page.
// DOES NOT export, read, log or reuse byte arrays or signatures.
// Captures only the *number* of atob() decoded strings of expected sizes.
// This is a feasibility diagnostic, not an extension, scraper or challenge bypass.
const { chromium } = require("playwright-core");

async function main() {
  const target = "https://comix.ws/title/rrglg-the-great-journey-of-teenagers-folly-of-youths-arc";
  let browser;
  try {
    browser = await chromium.launch({
      channel: "chrome",
      headless: true,
      args: ["--no-sandbox"],
      timeout: 15000,
    });
    const context = await browser.newContext();
    await context.addInitScript(() => {
      const real = window.atob.bind(window);
      const sizes = { "24": 0, "32": 0, "256": 0 };
      window.atob = function(input) {
        const decoded = real(input);
        const size = decoded.length;
        if (size === 24 || size === 32 || size === 256) {
          sizes[String(size)] += 1;
        }
        return decoded;
      };
      Object.defineProperty(window, "__comixResearchCounts", {
        configurable: false,
        enumerable: false,
        get() { return { ...sizes }; },
      });
    });
    const page = await context.newPage();
    let httpStatus = null;
    let documentState = "unknown";
    try {
      const response = await page.goto(target, {
        waitUntil: "domcontentloaded",
        timeout: 25000,
      });
      httpStatus = response ? response.status() : null;
      // Let naturally loaded scripts run. No clicks, CAPTCHA, challenge bypass,
      // interception of responses, or requests to the chapter API.
      await page.waitForTimeout(7000);
      documentState = await page.evaluate(() => document.readyState);
    } catch (error) {
      documentState = "navigation-error:" + error.name;
    }
    const counts = await page.evaluate(() => {
      return window.__comixResearchCounts || null;
    }).catch(() => null);
    console.log(JSON.stringify({
      test: "one_public_browser_session",
      http_status: httpStatus,
      document_state: documentState,
      decoded_lengths_count: counts,
      signed_api_tested: false,
      reusable_key_extracted: false,
    }, null, 2));
    await context.close();
  } finally {
    if (browser) await browser.close();
  }
}

main().catch(error => {
  console.error("Probe inconclusive: " + error.name + ": " + error.message);
  process.exitCode = 2;
});
