// Synthetic browser tests for the JavaScript embedded in Comix.kt.
// Does NOT access Comix or any outside website, tokens or live sessions.
// This checks the *real Kotlin embedded script*, not a duplicated mock.
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const kotlin = fs.readFileSync(
  path.join(__dirname, "../upstream/comix/src/eu/kanade/tachiyomi/extension/en/comix/Comix.kt"),
  "utf8",
);
function extractEmbeddedJs() {
  const methodStart = kotlin.indexOf("override suspend fun getPageList(");
  const scriptStart = kotlin.indexOf("(function () {", methodStart);
  const scriptEnd = kotlin.indexOf('""".trimIndent()', scriptStart);
  assert.ok(methodStart > 0 && scriptStart > methodStart && scriptEnd > scriptStart,
    "Must find real embedded page capture JS in Comix.kt");
  return kotlin.slice(scriptStart, scriptEnd).replaceAll("window.$passPayloadName", "window.report");
}
const source = extractEmbeddedJs();
const sample = {result:{pages:{baseUrl:"https://example.test",items:[{url:"synthetic.jpg"}]}}};

function harness({ResponseClass, fetchFn, XhrClass, initial = null} = {}) {
  const reported = [];
  const window = {
    location:{href:"https://comix.ws/title/synthetic/123-chapter-1"},
    report(json){reported.push(JSON.parse(json));},
    fetch:fetchFn,
  };
  const document = {
    querySelector(selector){
      assert.equal(selector,"script#initial-data");
      return initial == null ? null : {textContent:JSON.stringify(initial)};
    },
  };
  const globals={window,document,Response:ResponseClass,XMLHttpRequest:XhrClass,URL,Promise};
  const ctx = vm.createContext(globals);
  vm.runInContext(source,ctx, {timeout:1000});
  return {reported,window,globals,ctx};
}
async function tests() {
  // The existing initial-data shortcut is preserved.
  {
    const h=harness({initial:{queries:{q:sample}}});
    assert.equal(h.reported.length,1);
  }
  // WKWebView Response.json() may not invoke global JSON.parse.
  {
    class FakeResponse {
      json(){return Promise.resolve(sample);}
    }
    const h=harness({ResponseClass:FakeResponse});
    assert.deepEqual(await new FakeResponse().json(),sample);
    assert.equal(h.reported.length,1, "Response.json results should reach the bridge");
  }
  // fetch clone fallback catches JSON returned by the page API.
  {
    let wasCloned=false;
    const fakeResp={
      url:"https://comix.ws/api/v1/chapters/123",
      clone(){wasCloned=true;return {text:async()=>JSON.stringify(sample)};},
    };
    const h=harness({fetchFn:()=>Promise.resolve(fakeResp)});
    assert.equal(await h.window.fetch("/api/v1/chapters/123"),fakeResp);
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(wasCloned,true);
    assert.equal(h.reported.length,1);
  }
  // Do not consume unrelated fetch response bodies.
  {
    let cloned=false;
    const fakeResp={url:"https://comix.ws/dist/main-abc.js",clone(){cloned=true;}};
    const h=harness({fetchFn:()=>Promise.resolve(fakeResp)});
    assert.equal(await h.window.fetch("/dist/main-abc.js"),fakeResp);
    assert.equal(cloned,false);
    assert.equal(h.reported.length,0);
  }
  // XHR callback fallback works on an API response.
  {
    class FakeXhr {
      constructor(){this.handlers={};this.responseText=JSON.stringify(sample);}
      open(method,url){this.requestUrl=url;}
      addEventListener(name,callback){this.handlers[name]=callback;}
      send(){this.handlers.load.call(this);}
    }
    const h=harness({XhrClass:FakeXhr});
    const xhr=new FakeXhr();
    xhr.open("GET", "/api/v1/chapters/123");
    xhr.send();
    assert.equal(h.reported.length,1);
  }
  // Repeated polling does not stack duplicate wrappers.
  {
    class FakeResponse {json(){return Promise.resolve(sample);}}
    const h=harness({ResponseClass:FakeResponse});
    const wrapped=FakeResponse.prototype.json;
    vm.runInContext(source,h.ctx,{timeout:1000});
    assert.equal(FakeResponse.prototype.json,wrapped);
  }
  console.log("PASS: 6 browser-capture fixture tests from Comix.kt");
}
tests().catch(error=>{console.error(error);process.exitCode=1;});
