// 프리미엄 챕터(tier>=1)의 body/quiz를 HTML에서 분리해 api/_premium.js(서버 전용)로 이동.
// 실행: node scripts-split-content.js <html경로> <api디렉터리>
const fs = require("fs");
const [,, htmlPath, apiDir] = process.argv;

const html = fs.readFileSync(htmlPath, "utf8");
const s = html.indexOf("const CHAPTERS = [");
const e = html.indexOf("];", s);
const CHAPTERS = eval(html.slice(s, e + 2) + ";CHAPTERS");

const premium = {};
const publicChapters = CHAPTERS.map(c => {
  if (c.tier >= 1) {
    premium[c.id] = { tier: c.tier, body: c.body, quiz: c.quiz };
    return { ...c, body: "", quiz: [], remote: true };
  }
  return c;
});

// 서버 전용 모듈 (api/ 에서 밑줄 파일은 엔드포인트로 노출되지 않음)
fs.writeFileSync(
  apiDir + "/_premium.js",
  "// 프리미엄 챕터 본문·퀴즈 — 서버 전용. 클라이언트 번들/정적 서빙에 포함되지 않음.\n" +
  "// 재생성: node scripts-split-content.js (원본은 git 히스토리의 전체본 참조)\n" +
  "export const PREMIUM = " + JSON.stringify(premium, null, 1) + ";\n"
);

// HTML의 CHAPTERS를 공개판(프리미엄 body 제거)으로 교체
const newArray = "const CHAPTERS = [\n" +
  publicChapters.map(c => JSON.stringify(c)).join(",\n") + "\n]";
const out = html.slice(0, s) + newArray + html.slice(e + 1);
fs.writeFileSync(htmlPath, out);

const kept = publicChapters.filter(c => !c.remote).length;
console.log("premium:", Object.keys(premium).length, "| inline(free):", kept,
  "| html size:", out.length, "| premium size:", JSON.stringify(premium).length);
