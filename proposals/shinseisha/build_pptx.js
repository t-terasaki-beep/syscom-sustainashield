// ============================================================
// 新生社様 省エネ・創エネ ダブルプラン提案書（全19ページ）
// pptxgenjs / フォント: Noto Sans CJK JP
// ============================================================
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";          // 13.333 x 7.5 inch
pres.author = "株式会社シスコムネット 寺嵜忠弘";
pres.title  = "新生社様 省エネ・創エネ ダブルプラン提案書";

// ---- カラーパレット（Midnight Executive 系・元デザイン踏襲） ----
const NAVY   = "0F2747";   // ベース濃紺
const NAVY2  = "12305A";
const GOLD   = "C7A867";   // ゴールド
const GOLDD  = "B89A55";
const TEAL   = "1FA383";   // ティール（緑）
const BLUE   = "4A90D9";   // ブルー
const ORANGE = "E58027";   // オレンジ
const RED    = "C0392B";   // レッド
const GREY   = "8A95A5";   // グレー
const LGREY  = "F4F6F8";   // 薄グレー背景
const MGREY  = "6B7280";   // 中間グレー文字
const BORDER = "E1E5EA";   // 枠線
const WHITE  = "FFFFFF";
const INK    = "1A2B40";   // 本文濃色

const F = "Noto Sans CJK JP";  // 日本語フォント統一

const W = 13.333, H = 7.5;
const FOOT = "有限会社新生社（ボーン・アゲイン 1 号店）省エネ・創エネ ダブルプラン提案書";

// ---- ヘルパー ----
function footer(slide, page){
  slide.addText(FOOT, { x:0.5, y:7.22, w:10.5, h:0.26, fontFace:F, fontSize:8.5, color:GREY, align:"left", valign:"middle", margin:0 });
  slide.addText(`${page} / 20`, { x:11.8, y:7.22, w:1.0, h:0.26, fontFace:F, fontSize:8.5, color:GREY, align:"right", valign:"middle", margin:0 });
}
function secNum(slide, n){
  slide.addText(n, { x:0.5, y:0.34, w:1.2, h:0.35, fontFace:F, fontSize:13, bold:true, color:GOLD, align:"left", valign:"middle", margin:0 });
}
function title(slide, txt, y){
  slide.addText(txt, { x:0.5, y:(y!==undefined?y:0.7), w:12.3, h:0.85, fontFace:F, fontSize:30, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
}
function makeShadow(){ return { type:"outer", color:"000000", blur:7, offset:3, angle:135, opacity:0.12 }; }
function card(slide, x,y,w,h, fill){
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x,y,w,h, rectRadius:0.06, fill:{color:fill||LGREY}, line:{color:BORDER,width:1}, shadow:makeShadow() });
}

// ============================================================
// Slide 1 : 表紙
// ============================================================
(function(){
  const s = pres.addSlide();
  s.background = { color: NAVY };
  // 左上 装飾ブロック
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.95, h:0.55, fill:{color:TEAL}, line:{type:"none"} });
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.55, h:1.95, fill:{color:GOLD}, line:{type:"none"} });
  // 右下 装飾ブロック
  s.addShape(pres.shapes.RECTANGLE, { x:12.38, y:5.55, w:0.95, h:1.35, fill:{color:GOLD}, line:{type:"none"} });
  s.addShape(pres.shapes.RECTANGLE, { x:12.78, y:6.9, w:0.55, h:0.6, fill:{color:TEAL}, line:{type:"none"} });
  // 英字ライン
  s.addText("CHIBA  PREFECTURE  SUBSIDY  ×  ENERGY  MANAGEMENT",
    { x:1.0, y:1.95, w:11, h:0.4, fontFace:F, fontSize:13, bold:true, color:GOLD, charSpacing:3, align:"left", valign:"middle", margin:0 });
  // メインタイトル
  s.addText("省エネ・創エネ ダブルプラン",
    { x:0.97, y:2.45, w:11.5, h:1.0, fontFace:F, fontSize:46, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
  s.addText("導入ご提案書",
    { x:1.0, y:3.45, w:11, h:0.6, fontFace:F, fontSize:24, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
  // 区切り線（ゴールド・装飾線でなく区切り）
  s.addShape(pres.shapes.RECTANGLE, { x:1.0, y:4.28, w:4.0, h:0.035, fill:{color:GOLD}, line:{type:"none"} });
  // 宛先
  s.addText("有限会社 新生社 様",
    { x:1.0, y:4.55, w:11, h:0.55, fontFace:F, fontSize:24, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
  s.addText("ボーン・アゲイン 1 号店（千葉県八街市八街に 49-76 ）",
    { x:1.0, y:5.15, w:11, h:0.45, fontFace:F, fontSize:15, color:"C8D2E0", align:"left", valign:"middle", margin:0 });
  // 下部注記
  s.addText("電気代削減（創エネ） ×  建物の資産価値向上（省エネ） ×  千葉県補助金活用\n4 プラン定量比較による経営判断のための提案書",
    { x:1.0, y:6.3, w:9.5, h:0.7, fontFace:F, fontSize:11.5, color:"AEB9CC", align:"left", valign:"middle", lineSpacingMultiple:1.3, margin:0 });
  s.addText("2026 年 5 月",
    { x:10.5, y:6.55, w:2.0, h:0.4, fontFace:F, fontSize:13, bold:true, color:GOLD, align:"right", valign:"middle", margin:0 });
})();


// ============================================================
// Slide 2 : 目次
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"01"); title(s,"本日のご提案");
  const items = [
    ["01","お客様の課題 ― 冷暖房の悩み","「効かない・我慢している」をどう解消するか"],
    ["02","経営判断のポイント","A/B/C/D/E 5 プラン比較・ 2 段階作戦も提案"],
    ["03","実消費データ × 建物概況の分析","30 分単位データと面積概算"],
    ["04","サニックス提案 × 単相 vs 三相 × 各案の設計","B/C/D/E 各プランの構造と決定的な技術差"],
    ["05","20 年累計コスト × 建物維持負担比較","電気代 + メンテ + 投資の総額勝負"],
    ["06","BCP × 脱炭素 × 補助金活用","蓄電池 + ポリウレアの合算スキーム"],
    ["07","リスクと次のステップ","卒 FIT ・補助金枠・施工スケジュール"],
  ];
  const x=1.05, w=11.25, top=1.75, rh=0.685, gap=0.075;
  items.forEach((it,i)=>{
    const y = top + i*(rh+gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h:rh, fill:{color:LGREY}, line:{type:"none"} });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:0.09, h:rh, fill:{color:GOLD}, line:{type:"none"} });
    s.addText(it[0], { x:x+0.28, y, w:1.1, h:rh, fontFace:F, fontSize:24, bold:true, color:GOLD, align:"left", valign:"middle", margin:0 });
    s.addText(it[1], { x:x+1.55, y:y+0.07, w:w-1.7, h:0.36, fontFace:F, fontSize:16, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
    s.addText(it[2], { x:x+1.55, y:y+0.40, w:w-1.7, h:0.26, fontFace:F, fontSize:10.5, color:MGREY, align:"left", valign:"middle", margin:0 });
  });
  footer(s,2);
})();

// ============================================================
// Slide 3 : お客様の課題
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  title(s,"お客様の課題 ― いま解決したいこと", 0.55);
  // 引用バナー（濃紺）
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:1.5, w:12.33, h:1.65, fill:{color:NAVY}, line:{type:"none"} });
  s.addText("“", { x:0.7, y:1.5, w:0.7, h:0.9, fontFace:"Georgia", fontSize:54, bold:true, color:GOLD, align:"left", valign:"top", margin:0 });
  s.addText("冷房や暖房が効かないのが悩み。電気代がかかるので全開で使えていない。\nそもそも建物に対して空調が力不足かもしれない。\n蓄電池や太陽光の増設で、曇りの日でもしっかり貯めて、気兼ねなく使えるようにしたい。",
    { x:1.5, y:1.62, w:10.8, h:1.15, fontFace:F, fontSize:14, italic:true, color:WHITE, align:"left", valign:"middle", lineSpacingMultiple:1.3, margin:0 });
  s.addText("―  新生社 ご担当者様より", { x:9.0, y:2.78, w:3.6, h:0.3, fontFace:F, fontSize:11, color:"AEB9CC", align:"right", valign:"middle", margin:0 });
  // 課題3枚
  const probs = [
    [ORANGE,"課題 1","我慢して使っている","電気代が気になり、冷暖房を全開にできない。暑い・寒いを我慢している状態。"],
    [BLUE,"課題 2","そもそも力不足かも","建物の広さに対して、今の空調設備がアンダーパワーの可能性がある。"],
    [TEAL,"課題 3","天気に左右される","曇りの日でも安定して電気を使いたい。発電できない時間帯の備えが欲しい。"],
  ];
  const cw=3.93, cx0=0.5, cgap=0.27, cy=3.5, ch=2.35;
  probs.forEach((p,i)=>{
    const x=cx0+i*(cw+cgap);
    s.addShape(pres.shapes.RECTANGLE, { x, y:cy, w:cw, h:0.78, fill:{color:p[0]}, line:{type:"none"} });
    s.addText(p[1], { x:x+0.25, y:cy+0.1, w:cw-0.4, h:0.55, fontFace:F, fontSize:14, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
    s.addShape(pres.shapes.RECTANGLE, { x, y:cy+0.78, w:cw, h:ch-0.78, fill:{color:LGREY}, line:{color:BORDER,width:1} });
    s.addText(p[2], { x:x+0.25, y:cy+0.95, w:cw-0.5, h:0.45, fontFace:F, fontSize:17, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
    s.addText(p[3], { x:x+0.25, y:cy+1.45, w:cw-0.5, h:0.85, fontFace:F, fontSize:11.5, color:INK, align:"left", valign:"top", lineSpacingMultiple:1.25, margin:0 });
  });
  // ゴールバナー
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:6.1, w:12.33, h:0.92, fill:{color:GOLDD}, line:{type:"none"} });
  s.addText("本提案のゴール", { x:0.75, y:6.18, w:11, h:0.3, fontFace:F, fontSize:12.5, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
  s.addText("太陽光をしっかり活かして電気代を下げ、蓄電池で曇りの日や夜も電気を確保。“我慢のいらない快適さ”と“電気代の安心”を、補助金を使って同時に実現します。",
    { x:0.75, y:6.46, w:11.85, h:0.5, fontFace:F, fontSize:12, bold:true, color:NAVY, align:"left", valign:"middle", lineSpacingMultiple:1.15, margin:0 });
  footer(s,3);
})();
console.log("slides 2-3 built");

// ============================================================
// Slide 4 : 経営判断のポイント（4プラン比較）
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"02"); title(s,"経営判断のポイント ― 結論先出しの 5 プラン比較");
  // 推奨バッジ
  s.addShape(pres.shapes.RECTANGLE, { x:11.42, y:1.45, w:1.28, h:0.42, fill:{color:"E07D45"}, line:{type:"none"} });
  s.addText("最推奨", { x:11.42, y:1.45, w:1.28, h:0.42, fontFace:F, fontSize:12, bold:true, color:WHITE, align:"center", valign:"middle", margin:0 });
  const plans = [
    [GREY,"A 現状維持","全量売電",
      ["20年累計 12,244万円","電気代 5,660万","塗装+足場 6,584万★","設備投資 0円","暑さ対策ならず"],
      "最も高い", RED],
    [BLUE,"B サニックス","太陽光のみ自家消費",
      ["20年累計 10,955万円","A比 ▲1,289万","電気代のみ改善","BCP × / 補助金なし","塗装メンテ 6,584万残る"],
      "電気代のみ", BLUE],
    [TEAL,"C シスコム","蓄電池+補助金",
      ["20年累計 9,821万円","A比 ▲2,423万","オムロン国産+地元施工","BCP 54kWh / 18h","塗装メンテ 6,584万残る"],
      "電気代+BCP", TEAL],
    [GOLDD,"D ダブル","屋根外壁ポリウレア",
      ["20年累計 5,375万円","A比 ▲6,869万 ★","空調30%カット","設備 補助前4,573→実質3,573","20年メンテ 0円"],
      "建物寿命+20年", GOLDD],
    ["E07D45","E 屋根のみ先行","2年で補助金2回狙い",
      ["20年累計 4,095万円 ★最安","A比 ▲8,149万","屋根遮熱+蓄電池+太陽光","補助金1,000万 (今年)","来年外壁で実質930万"],
      "2段階で最大", "E07D45"],
  ];
  const cw=2.34, cx0=0.55, cgap=0.13, cy=1.95, ch=4.35;
  plans.forEach((p,i)=>{
    const x=cx0+i*(cw+cgap);
    s.addShape(pres.shapes.RECTANGLE, { x, y:cy, w:cw, h:0.92, fill:{color:p[0]}, line:{type:"none"} });
    s.addText(p[1], { x:x+0.12, y:cy+0.1, w:cw-0.2, h:0.4, fontFace:F, fontSize:13, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
    s.addText(p[2], { x:x+0.12, y:cy+0.48, w:cw-0.2, h:0.3, fontFace:F, fontSize:8.5, color:"F0F0F0", align:"left", valign:"middle", margin:0 });
    s.addShape(pres.shapes.RECTANGLE, { x, y:cy+0.92, w:cw, h:ch-0.92, fill:{color:WHITE}, line:{color:BORDER,width:1} });
    const bullets = p[3].map((t,j)=>({ text:t, options:{ bullet:{code:"25CF"}, breakLine:true, paraSpaceAfter:7, color:INK, fontSize:8.8 } }));
    s.addText(bullets, { x:x+0.14, y:cy+1.0, w:cw-0.28, h:2.8, fontFace:F, align:"left", valign:"top", margin:0 });
    s.addText([{text:"評価:",options:{color:MGREY,fontSize:8.5}},{text:p[4],options:{color:p[5],fontSize:11,bold:true}}],
      { x:x+0.12, y:cy+3.85, w:cw-0.24, h:0.4, fontFace:F, align:"left", valign:"middle", margin:0 });
  });
  // 結論バー
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:6.5, w:12.33, h:0.62, fill:{color:NAVY}, line:{type:"none"} });
  s.addText([
    {text:"結論：",options:{color:GOLD,bold:true}},
    {text:"D 案は20年確定で A比▲6,869万円お得。 E 案は屋根のみ先行で投資を抑えつつ補助金を2年で2回獲り、 A比▲8,149万円。 ★塗装は維持費かかっても暑さ対策にならない! ポリウレアは20年メンテ0円+遮熱で空調代も下がる二重効果",options:{color:WHITE}}
  ], { x:0.7, y:6.5, w:11.95, h:0.62, fontFace:F, fontSize:10.5, align:"left", valign:"middle", lineSpacingMultiple:1.1, margin:0 });
  footer(s,4);
})();

// ============================================================
// Slide 5 : 実消費データ × 建物概況
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"03"); title(s,"実消費データ × 建物概況の分析");
  // 左カード
  card(s, 0.5, 1.7, 6.0, 5.05, LGREY);
  s.addText("年間電力使用実績 (2025/4-2026/3)", { x:0.8, y:1.95, w:5.5, h:0.4, fontFace:F, fontSize:15, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
  const L = [["年間消費電力量","110,657 kWh"],["平均月間消費","9,221 kWh"],["日中使用比率","84% （理想的）"],["年間電気代 ( 現状 )","約 232 万円"],["契約電力","高圧 50kW 級"]];
  L.forEach((r,i)=>{
    const y=2.5+i*0.55;
    s.addShape(pres.shapes.RECTANGLE, { x:0.8, y, w:5.4, h:0.46, fill:{color:WHITE}, line:{color:BORDER,width:1} });
    s.addText(r[0], { x:0.95, y, w:3.0, h:0.46, fontFace:F, fontSize:12, color:INK, align:"left", valign:"middle", margin:0 });
    s.addText(r[1], { x:3.5, y, w:2.55, h:0.46, fontFace:F, fontSize:13.5, bold:true, color:NAVY, align:"right", valign:"middle", margin:0 });
  });
  s.addShape(pres.shapes.RECTANGLE, { x:0.8, y:5.45, w:5.4, h:1.05, fill:{color:TEAL}, line:{type:"none"} });
  s.addText("ポイント", { x:0.98, y:5.53, w:5, h:0.3, fontFace:F, fontSize:11, bold:true, color:"D7F2E9", align:"left", valign:"middle", margin:0 });
  s.addText("日中使用 84% の理想的な負荷プロファイル。\n太陽光自家消費と蓄電池の効果が極めて高い。",
    { x:0.98, y:5.82, w:5.05, h:0.6, fontFace:F, fontSize:12, bold:true, color:WHITE, align:"left", valign:"middle", lineSpacingMultiple:1.2, margin:0 });
  // 右カード
  card(s, 6.83, 1.7, 6.0, 5.05, LGREY);
  s.addText("建物概況 (Google Map 目視推定 )", { x:7.13, y:1.95, w:5.5, h:0.4, fontFace:F, fontSize:15, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
  const R = [["屋根面積","約 1,400 ㎡"],["外壁面積","約 1,500 ㎡"],["窓面積","約 120 ㎡"],["既設太陽光","63 kW (BYD250P×252 枚 )"],["建物用途","リサイクルショップ・ STUDIO Can!"],["立地","八街市内陸（塩害なし）"]];
  R.forEach((r,i)=>{
    const y=2.5+i*0.46;
    s.addShape(pres.shapes.RECTANGLE, { x:7.13, y, w:5.4, h:0.4, fill:{color:WHITE}, line:{color:BORDER,width:1} });
    s.addText(r[0], { x:7.28, y, w:2.0, h:0.4, fontFace:F, fontSize:11.5, color:INK, align:"left", valign:"middle", margin:0 });
    s.addText(r[1], { x:8.9, y, w:3.5, h:0.4, fontFace:F, fontSize:12, bold:true, color:NAVY, align:"right", valign:"middle", margin:0 });
  });
  s.addShape(pres.shapes.RECTANGLE, { x:7.13, y:5.42, w:5.4, h:1.08, fill:{color:NAVY}, line:{type:"none"} });
  s.addText("提案前提：消費構成は三相 30% 仮定、 D 案ポリウレア 2,900 ㎡、 A/B/C 案は屋根 1,400 ㎡塗装メンテ、窓 120 ㎡の断熱コート、既設 63kW PV を自家消費へ転換",
    { x:7.31, y:5.5, w:5.05, h:0.95, fontFace:F, fontSize:11, color:WHITE, align:"left", valign:"middle", lineSpacingMultiple:1.25, margin:0 });
  footer(s,5);
})();
console.log("slides 4-5 built");

// ============================================================
// Slide 6 : サニックス提案の評価
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"04"); title(s,"サニックス提案の評価 ― 何ができて、何が足りないか");
  // 左カード
  card(s, 0.5, 1.7, 6.0, 5.05, LGREY);
  s.addText("サニックス提案 (B 案 ) の内容", { x:0.8, y:1.9, w:5.5, h:0.38, fontFace:F, fontSize:14, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
  const rows=[["既設 PV 流用","BYD250P 252 枚 (63kW)"],["パワコン","HUAWEI SUN2000-4.95KTL ×10 台"],["AC 集電箱","単相用 1 台"],["データ収集","SmartLogger 3000A"],["自家消費 BOX","1 式"],["別途工事","配電盤改造・キュービクル工事 等"]];
  rows.forEach((r,i)=>{
    const y=2.38+i*0.43;
    s.addShape(pres.shapes.RECTANGLE, { x:0.8, y, w:1.55, h:0.37, fill:{color:NAVY}, line:{type:"none"} });
    s.addText(r[0], { x:0.8, y, w:1.55, h:0.37, fontFace:F, fontSize:9.5, bold:true, color:WHITE, align:"center", valign:"middle", margin:0 });
    s.addText(r[1], { x:2.5, y, w:3.8, h:0.37, fontFace:F, fontSize:10.5, color:INK, align:"left", valign:"middle", margin:0 });
  });
  s.addShape(pres.shapes.RECTANGLE, { x:0.8, y:5.0, w:5.4, h:0.55, fill:{color:NAVY}, line:{type:"none"} });
  s.addText("合計金額  6,160,000 円（税込）", { x:0.8, y:5.0, w:5.4, h:0.55, fontFace:F, fontSize:16, bold:true, color:GOLD, align:"center", valign:"middle", margin:0 });
  s.addText("◎ 評価できる点", { x:0.8, y:5.65, w:5.4, h:0.3, fontFace:F, fontSize:11, bold:true, color:TEAL, align:"left", valign:"middle", margin:0 });
  s.addText([
    {text:"既設 PV252 枚を活かす再活用（廃棄ロス回避）",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:3}},
    {text:"HUAWEI パワコン 20 年保証は業界水準を上回る",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:3}},
    {text:"25 年シミュレーションが詳細・透明性◎",options:{bullet:{code:"25CF"}}},
  ], { x:0.85, y:5.95, w:5.3, h:0.75, fontFace:F, fontSize:10, color:INK, align:"left", valign:"top", margin:0 });
  // 右カード
  card(s, 6.83, 1.7, 6.0, 5.05, LGREY);
  s.addText("△ 物足りない点 →  C/D  で解決", { x:7.13, y:1.9, w:5.5, h:0.38, fontFace:F, fontSize:14, bold:true, color:ORANGE, align:"left", valign:"middle", margin:0 });
  const pairs=[
    ["× 単相のみ自家消費 → 余剰 37,286kWh/ 年 (PV の 49%) を捨てる","→ C:  オムロン完全自家消費型 +PW3 で 100% 自家消費 ( 三相含む )",TEAL],
    ["× 停電時に発電を活用できない (BCP×)","→ C:  重要負荷 5kW で 11 時間 /3kW で 18 時間継続",TEAL],
    ["× 千葉県補助金の活用提案なし","→ D:  蓄電池 + ポリウレア合算で上限 1,000 万円獲得",TEAL],
    ["× 5 年後の塗装工事 800 万円 が別途発生","→ D:  ポリウレアで 20 年以上耐候 → 塗装工事不要",GOLDD],
    ["× 15 年後の塗装工事 1,200 万円 が別途発生","→ D:  千葉県補助金 1/2 で実質 600 万円のみ",GOLDD],
    ["× 屋根防水時のパネル脱着工事 63 万 ×2 回","→ D:  屋根防水とポリウレア一体施工で不要",GOLDD],
  ];
  let yy=2.4;
  pairs.forEach((p)=>{
    s.addText(p[0], { x:7.13, y:yy, w:5.55, h:0.3, fontFace:F, fontSize:10, color:INK, align:"left", valign:"middle", margin:0 });
    s.addShape(pres.shapes.RECTANGLE, { x:7.13, y:yy+0.3, w:5.55, h:0.34, fill:{color:p[2]}, line:{type:"none"} });
    s.addText(p[1], { x:7.25, y:yy+0.3, w:5.4, h:0.34, fontFace:F, fontSize:9.8, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
    yy += 0.72;
  });
  footer(s,6);
})();
console.log("slide 6 built");

// ============================================================
// Slide 7 : 自家消費パワコンの根本差【作り直し・社長承認済み数値】
//  HUAWEI単相 51%(38,714) vs オムロン三相 79%(59,861)
//  差: 年間+21,147kWh = +44.5万円/年 = 20年 約1,082万円
//  蓄電池PW3の箱は削除し「余剰16,139kWhは次ページ送り」の小注記に
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"04");
  s.addText("自家消費パワコンの根本差 ― HUAWEI 単相（サニックス様） vs オムロン単相200V→三相へ（シスコムネット）",
    { x:0.5, y:0.62, w:12.3, h:0.95, fontFace:F, fontSize:21, bold:true, color:NAVY, align:"left", valign:"middle", lineSpacingMultiple:1.05, margin:0 });
  // 上部バナー（濃紺）― 蓄電池なしでも 44.5万/年・20年1,082万
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:1.66, w:12.33, h:0.6, fill:{color:NAVY}, line:{type:"none"} });
  s.addText([
    {text:"蓄電池なしでも、",options:{color:WHITE}},
    {text:"年間 44.5 万円・ 20 年で約 1,082 万円 ",options:{color:GOLD,bold:true}},
    {text:"の自家消費差（三相 30% 仮定・歴然たる提案の差）",options:{color:WHITE}},
  ], { x:0.7, y:1.66, w:12.0, h:0.6, fontFace:F, fontSize:13.5, bold:true, align:"left", valign:"middle", margin:0 });

  // ===== 左ペイン : B案 HUAWEI 単相 =====
  const LX=0.5, LW=6.0, PY=2.45, PH=3.55;
  s.addShape(pres.shapes.RECTANGLE, { x:LX, y:PY, w:LW, h:0.5, fill:{color:RED}, line:{type:"none"} });
  s.addText("× B 案 : HUAWEI 単相パワコン", { x:LX+0.2, y:PY, w:LW-0.3, h:0.5, fontFace:F, fontSize:13.5, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
  s.addShape(pres.shapes.RECTANGLE, { x:LX, y:PY+0.5, w:LW, h:PH-0.5, fill:{color:WHITE}, line:{color:BORDER,width:1} });
  // フロー（左）
  function box(slide,x,y,w,h,fill,txt,tc,fs){ slide.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:fill},line:{type:"none"}}); slide.addText(txt,{x:x+0.03,y,w:w-0.06,h,fontFace:F,fontSize:fs||10,bold:true,color:tc||WHITE,align:"center",valign:"middle",lineSpacingMultiple:1.0,margin:0}); }
  function obox(slide,x,y,w,h,line,txt,tc,fs){ slide.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:WHITE},line:{color:line,width:1.3}}); slide.addText(txt,{x:x+0.03,y,w:w-0.06,h,fontFace:F,fontSize:fs||10,bold:true,color:tc,align:"center",valign:"middle",lineSpacingMultiple:1.0,margin:0}); }
  box(s, LX+0.35, PY+0.7, 1.7, 0.55, GOLDD, "太陽光 63kW");
  s.addText("↓", { x:LX+0.35, y:PY+1.25, w:1.7, h:0.3, fontFace:F, fontSize:13, color:INK, align:"center", valign:"middle", margin:0 });
  box(s, LX+0.35, PY+1.55, 1.7, 0.55, BLUE, "HUAWEI 単相");
  s.addText("↓", { x:LX+0.35, y:PY+2.1, w:1.7, h:0.3, fontFace:F, fontSize:13, color:INK, align:"center", valign:"middle", margin:0 });
  obox(s, LX+0.35, PY+2.4, 1.7, 0.55, BLUE, "単相負荷\n(30%)", BLUE, 9.5);
  // 右側の届かない/捨てる
  s.addShape(pres.shapes.RECTANGLE, { x:LX+2.35, y:PY+1.5, w:1.65, h:0.78, fill:{color:WHITE}, line:{color:RED,width:1.2,dashType:"dash"} });
  s.addText("三相負荷\n(70%)", { x:LX+2.35, y:PY+1.5, w:1.65, h:0.78, fontFace:F, fontSize:9.5, bold:true, color:RED, align:"center", valign:"middle", margin:0 });
  s.addText("× 届かない", { x:LX+2.35, y:PY+2.3, w:1.65, h:0.25, fontFace:F, fontSize:9, color:RED, align:"center", valign:"middle", margin:0 });
  s.addShape(pres.shapes.RECTANGLE, { x:LX+4.1, y:PY+1.5, w:1.6, h:0.78, fill:{color:WHITE}, line:{color:ORANGE,width:1.2,dashType:"dash"} });
  s.addText("余剰電力\n逆潮流 / 捨てる", { x:LX+4.1, y:PY+1.5, w:1.6, h:0.78, fontFace:F, fontSize:9, bold:true, color:ORANGE, align:"center", valign:"middle", margin:0 });
  s.addText("× 蓄電池なし", { x:LX+4.1, y:PY+2.3, w:1.6, h:0.25, fontFace:F, fontSize:9, color:ORANGE, align:"center", valign:"middle", margin:0 });
  // 左ペイン下部結論
  s.addShape(pres.shapes.RECTANGLE, { x:LX, y:PY+PH, w:LW, h:0.72, fill:{color:RED}, line:{type:"none"} });
  s.addText("自家消費 38,714 kWh/ 年（PVの51%）", { x:LX, y:PY+PH+0.05, w:LW, h:0.38, fontFace:F, fontSize:13.5, bold:true, color:WHITE, align:"center", valign:"middle", margin:0 });
  s.addText("三相負荷に流せず、PVの49%＝37,286kWh/年を捨てる", { x:LX, y:PY+PH+0.42, w:LW, h:0.28, fontFace:F, fontSize:9.5, color:"FBE0DC", align:"center", valign:"middle", margin:0 });

  // ===== 右ペイン : C案 オムロン 単相→三相→単相 =====
  const RX=6.83, RW=6.0;
  s.addShape(pres.shapes.RECTANGLE, { x:RX, y:PY, w:RW, h:0.5, fill:{color:TEAL}, line:{type:"none"} });
  s.addText("◎ C 案 : オムロン 単相200V→三相へ ( トランス昇圧 )", { x:RX+0.2, y:PY, w:RW-0.3, h:0.5, fontFace:F, fontSize:12.5, bold:true, color:WHITE, align:"left", valign:"middle", margin:0 });
  s.addShape(pres.shapes.RECTANGLE, { x:RX, y:PY+0.5, w:RW, h:PH-0.5, fill:{color:WHITE}, line:{color:BORDER,width:1} });
  // フロー（右）左列
  box(s, RX+0.3, PY+0.68, 1.55, 0.5, GOLDD, "太陽光 63kW");
  s.addText("↓ 単相", { x:RX+0.3, y:PY+1.18, w:1.55, h:0.24, fontFace:F, fontSize:8.5, color:INK, align:"center", valign:"middle", margin:0 });
  box(s, RX+0.3, PY+1.42, 1.55, 0.5, TEAL, "オムロン PCS\n( 単相出力 )", WHITE, 8.5);
  s.addText("↓ 単相", { x:RX+0.3, y:PY+1.92, w:1.55, h:0.24, fontFace:F, fontSize:8.5, color:INK, align:"center", valign:"middle", margin:0 });
  box(s, RX+0.3, PY+2.16, 1.55, 0.5, NAVY, "トランス\n単相→三相昇圧", WHITE, 8 );
  s.addText("↓ 三相", { x:RX+0.3, y:PY+2.66, w:1.55, h:0.22, fontFace:F, fontSize:8.5, color:INK, align:"center", valign:"middle", margin:0 });
  box(s, RX+0.3, PY+2.86, 1.55, 0.46, INK, "配電盤", WHITE, 9.5);
  // 右列の負荷
  s.addText("→ 三相", { x:RX+1.9, y:PY+2.16, w:0.6, h:0.5, fontFace:F, fontSize:8, color:INK, align:"center", valign:"middle", margin:0 });
  box(s, RX+2.5, PY+2.16, 1.5, 0.5, TEAL, "三相負荷 OK\n(70%)", WHITE, 8.5);
  s.addText("→ 単相", { x:RX+1.9, y:PY+2.86, w:0.6, h:0.46, fontFace:F, fontSize:8, color:INK, align:"center", valign:"middle", margin:0 });
  box(s, RX+2.5, PY+2.86, 1.5, 0.46, BLUE, "単相負荷 OK\n(30%)", WHITE, 8.5);
  // 余剰 → 次ページ送り（蓄電池PW3の箱は削除、小注記に）
  s.addShape(pres.shapes.RECTANGLE, { x:RX+4.1, y:PY+2.16, w:1.6, h:1.16, fill:{color:LGREY}, line:{color:GOLDD,width:1,dashType:"dash"} });
  s.addText("余剰 16,139kWh\nは次ページの\n蓄電池で\n夜間活用", { x:RX+4.1, y:PY+2.16, w:1.6, h:1.16, fontFace:F, fontSize:8.5, bold:true, color:GOLDD, align:"center", valign:"middle", lineSpacingMultiple:1.1, margin:0 });
  // 右ペイン下部結論
  s.addShape(pres.shapes.RECTANGLE, { x:RX, y:PY+PH, w:RW, h:0.72, fill:{color:TEAL}, line:{type:"none"} });
  s.addText("自家消費 59,861 kWh/ 年（PVの79%）", { x:RX, y:PY+PH+0.05, w:RW, h:0.38, fontFace:F, fontSize:13.5, bold:true, color:WHITE, align:"center", valign:"middle", margin:0 });
  s.addText("単相200V→トランス昇圧→三相で全負荷給電。蓄電池なしでも捨てる量が激減", { x:RX, y:PY+PH+0.42, w:RW, h:0.28, fontFace:F, fontSize:9, color:"D7F2E9", align:"center", valign:"middle", margin:0 });

  // 最下部 結論バー（ゴールド）
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:6.62, w:12.33, h:0.5, fill:{color:GOLDD}, line:{type:"none"} });
  s.addText("年間 +21,147kWh ＝ 電気代 +44.5 万円 / 年 → 20 年累計 約 1,082 万円の差（蓄電池なし・パワコンの差だけで）",
    { x:0.5, y:6.62, w:12.33, h:0.5, fontFace:F, fontSize:13, bold:true, color:NAVY, align:"center", valign:"middle", margin:0 });
  footer(s,7);
})();
console.log("slide 7 REBUILT");

// ============================================================
// Slide 8 : C案 シスコムネット案
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"04"); title(s,"C 案：シスコムネット案（自家消費＋蓄電池＋千葉県補助金）");
  // 左カード
  card(s, 0.5, 1.7, 6.0, 5.05, LGREY);
  s.addText("運用イメージ (Tesla Powerwall 3 × 4 台 )", { x:0.8, y:1.92, w:5.5, h:0.36, fontFace:F, fontSize:14, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
  function bigbox(x,y,w,h,fill,t1,t2,t1c,t2c){
    s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:fill},line:{type:"none"}});
    s.addText(t1,{x,y:y+0.1,w,h:0.32,fontFace:F,fontSize:11,bold:true,color:t1c||WHITE,align:"center",valign:"middle",margin:0});
    s.addText(t2,{x,y:y+0.42,w,h:0.42,fontFace:F,fontSize:14,bold:true,color:t2c||WHITE,align:"center",valign:"middle",margin:0});
  }
  bigbox(0.8,2.4,2.6,0.95,GOLDD,"太陽光 63kW PV","76,000 kWh/ 年");
  bigbox(3.6,2.4,2.6,0.95,TEAL,"単相自家消費 (49%)","37,240 kWh/ 年");
  bigbox(0.8,3.5,2.6,0.95,ORANGE,"蓄電池+三相へ","32,680 kWh/ 年");
  bigbox(3.6,3.5,2.6,0.95,NAVY,"蓄電池 54kWh","充電→夜間放電");
  bigbox(0.8,4.6,5.4,0.85,TEAL,"自家消費合計 ( PVの92% ≒ ほぼ使い切り )","69,920 kWh/ 年");
  s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:5.6,w:5.4,h:0.95,fill:{color:NAVY},line:{type:"none"}});
  s.addText("効果",{x:0.95,y:5.66,w:5,h:0.28,fontFace:F,fontSize:10.5,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("自家消費 PVの49% → 92% (単相→蓄電池→三相)\n年間電気代 233万 → 86万円 / BCP 54kWh ( 重要負荷 18h)",
    {x:0.95,y:5.94,w:5.1,h:0.55,fontFace:F,fontSize:11,bold:true,color:WHITE,align:"left",valign:"middle",lineSpacingMultiple:1.2,margin:0});
  // 右カード
  card(s, 6.83, 1.7, 6.0, 5.05, LGREY);
  s.addText("投資内訳・千葉県補助金活用", { x:7.13, y:1.92, w:5.5, h:0.36, fontFace:F, fontSize:14, bold:true, color:NAVY, align:"left", valign:"middle", margin:0 });
  const inv=[["オムロンPCS 自家消費工事 ( 税込 )","6,290,000 円",INK],["Tesla Powerwall 3 × 4 台 ( 税込 )","+ 9,600,000 円",INK],["補助金前 合計","15,890,000 円",NAVY],["千葉県補助金 ( 蓄電池税抜の 1/2)","▲ 4,360,000 円",BLUE]];
  inv.forEach((r,i)=>{
    const y=2.4+i*0.6;
    s.addShape(pres.shapes.RECTANGLE,{x:7.13,y,w:5.4,h:0.5,fill:{color:WHITE},line:{color:BORDER,width:1}});
    s.addText(r[0],{x:7.28,y,w:3.3,h:0.5,fontFace:F,fontSize:11,color:INK,align:"left",valign:"middle",margin:0});
    s.addText(r[1],{x:10.0,y,w:2.43,h:0.5,fontFace:F,fontSize:13,bold:true,color:r[2],align:"right",valign:"middle",margin:0});
  });
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:4.78,w:5.4,h:0.5,fill:{color:NAVY},line:{type:"none"}});
  s.addText("実質投資合計",{x:7.28,y:4.78,w:3.0,h:0.5,fontFace:F,fontSize:12,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("11,530,000 円",{x:10.0,y:4.78,w:2.43,h:0.5,fontFace:F,fontSize:14,bold:true,color:GOLD,align:"right",valign:"middle",margin:0});
  s.addText("千葉県業務用設備等脱炭素化促進事業補助金",{x:7.13,y:5.42,w:5.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  s.addText([
    {text:"対象：中小事業者の蓄電池設置（再エネ電力を蓄電）",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:4}},
    {text:"補助率： 1/2 （省エネ診断あり / 上限 1,000 万円）",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:4}},
    {text:"要件：① CO₂ スマート宣言 ②省エネ診断 ③ CO₂ 削減 3t 以上 / 年",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:4}},
    {text:"募集：例年 5 〜 10 月 / R8 年度内容は準備中・予算先着",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:4}},
    {text:"注意：交付決定前は着工不可 / 早期申請が必須",options:{bullet:{code:"25CF"}}},
  ],{x:7.2,y:5.72,w:5.4,h:1.0,fontFace:F,fontSize:9,color:INK,align:"left",valign:"top",margin:0});
  footer(s,8);
})();

// ============================================================
// Slide 9 : D案 ダブルプラン
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"04"); title(s,"D 案：省エネ・創エネ ダブルプラン（推奨）");
  // 戦略バナー
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.6,w:12.33,h:1.18,fill:{color:NAVY},line:{type:"none"}});
  s.addText("「使う量を減らす」省エネ × 「自分でつくる」創エネ ― 建物資産価値を両側から上げる経営戦略",
    {x:0.75,y:1.7,w:11.9,h:0.4,fontFace:F,fontSize:14,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("電気代削減（ C 案と同等）に加え、窓断熱コート + 屋根遮熱ポリウレアで空調の電気代を 30% カット。冷暖房を我慢なく使えるようになります。\n塩害・紫外線・劣化から建物を守り、修繕費を今の価格で固定。さらに補助金で半額に抑えます。",
    {x:0.75,y:2.1,w:11.9,h:0.62,fontFace:F,fontSize:11.5,color:WHITE,align:"left",valign:"middle",lineSpacingMultiple:1.25,margin:0});
  // 4枚カード
  const cards=[
    [TEAL,"SAVE ENERGY","① 窓断熱コート","概算 120 m²","約 144 万円 ( 税抜 )",BLUE,["夏の遮熱・冬の断熱","結露・ UV99% カット","業務止めず後付け施工"]],
    [TEAL,"SAVE ENERGY","② ポリウレア + 足場","屋根 + 外壁 2,900 ㎡ / 昇降足場 1 回","実質 2,277 万円 ( 税込 / 補助後 )",TEAL,["税込 2,840 万→単独補助 1,291 万","塗装 + 脱着工事 一切不要に","防水 / 防錆 10 年保証・ 20 年以上耐候"]],
    [GOLD,"CREATE ENERGY","③ 太陽光自家消費","既設 63kW 流用","629 万円 ( 税込 / シスコム )",GOLDD,["オムロン PCS 5.5kW×9 台","国産・地元施工・建設業許可","卒 FIT 前の意思決定"]],
    [GOLD,"CREATE ENERGY","④ 蓄電池 + 補助金","Powerwall 3 × 4 台 54kWh","実質 523 万円 ( 税込 )",NAVY,["夜間 +12,871kWh 置換","千葉県補助 ▲ 436 万円","BCP 重要負荷 18h"]],
  ];
  const cw=2.97, cx0=0.5, cgap=0.16, cy=2.95, ch=3.3;
  cards.forEach((c,i)=>{
    const x=cx0+i*(cw+cgap);
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy,w:cw,h:ch,fill:{color:WHITE},line:{color:BORDER,width:1},shadow:makeShadow()});
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy,w:cw,h:0.06,fill:{color:c[5]},line:{type:"none"}});
    s.addText(c[1],{x:x+0.2,y:cy+0.16,w:cw-0.3,h:0.24,fontFace:F,fontSize:9,bold:true,color:c[5],charSpacing:2,align:"left",valign:"middle",margin:0});
    s.addText(c[2],{x:x+0.2,y:cy+0.42,w:cw-0.3,h:0.36,fontFace:F,fontSize:14.5,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
    s.addText(c[3],{x:x+0.2,y:cy+0.82,w:cw-0.3,h:0.26,fontFace:F,fontSize:9,color:MGREY,align:"left",valign:"middle",margin:0});
    s.addText(c[4],{x:x+0.2,y:cy+1.1,w:cw-0.3,h:0.55,fontFace:F,fontSize:14,bold:true,color:c[5],align:"left",valign:"middle",lineSpacingMultiple:1.0,margin:0});
    const b=c[6].map((t,j)=>({text:t,options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:6,fontSize:9.5,color:INK}}));
    s.addText(b,{x:x+0.22,y:cy+1.75,w:cw-0.42,h:1.45,fontFace:F,align:"left",valign:"top",margin:0});
  });
  // 合計バー
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:6.5,w:12.33,h:0.62,fill:{color:GOLDD},line:{type:"none"}});
  s.addText("D プラン合計：設備 補助前 4,573 万円 → 補助 ▲ 1,000 万円 → 実質 3,573 万円 ／ 遮熱で空調電気代 30% カット ＋ 20 年屋根メンテ 2,439 万円不要",
    {x:0.5,y:6.5,w:12.33,h:0.62,fontFace:F,fontSize:12,bold:true,color:NAVY,align:"center",valign:"middle",margin:0});
  footer(s,9);
})();

// ============================================================
// Slide 10 : E案 屋根のみ先行プラン(2段階で補助金2,000万狙い)
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"04"); title(s,"E 案：屋根のみ先行プラン（最推奨・2 段階で補助金 2,000 万円狙い）");
  // 戦略バナー(オレンジ系)
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.6,w:12.33,h:1.0,fill:{color:NAVY},line:{type:"none"}});
  s.addText("「今年は屋根」「来年は外壁」 ― 補助金の上限 1,000 万円 / 年を 2 年で 2 回獲りに行く経営戦略",
    {x:0.75,y:1.65,w:11.9,h:0.35,fontFace:F,fontSize:13,bold:true,color:"E07D45",align:"left",valign:"middle",margin:0});
  s.addText("D 案は一気に 2,900 ㎡を施工し補助金 1,000 万円を 1 回獲得。 E 案は 1,400 ㎡の屋根を今年、 1,500 ㎡の外壁を翌年に分け、補助金を 2 回獲得することを狙います。投資の平準化＋補助金最大化のシナリオです。",
    {x:0.75,y:1.98,w:11.9,h:0.6,fontFace:F,fontSize:11,color:WHITE,align:"left",valign:"middle",lineSpacingMultiple:1.25,margin:0});
  // 2列(今年/来年)
  // 今年カード(左)
  card(s, 0.5, 2.78, 6.0, 3.95, LGREY);
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:2.78,w:6.0,h:0.5,fill:{color:"E07D45"},line:{type:"none"}});
  s.addText("【今年】屋根 1,400 ㎡ ＋ 創エネ",{x:0.7,y:2.78,w:5.7,h:0.5,fontFace:F,fontSize:14,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  const this_year=[["窓断熱コート 120 ㎡","144 万円"],
                   ["屋根ポリウレア 1,400 ㎡","1,232 万円"],
                   ["昇降足場・パネル脱着","93 万円"],
                   ["太陽光自家消費(オムロン)","629 万円"],
                   ["蓄電池 Powerwall 3×4台","960 万円"]];
  let yy=3.45;
  this_year.forEach((r)=>{
    s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:yy,w:5.4,h:0.35,fill:{color:WHITE},line:{color:BORDER,width:1}});
    s.addText(r[0],{x:0.95,y:yy,w:3.7,h:0.35,fontFace:F,fontSize:10,color:INK,align:"left",valign:"middle",margin:0});
    s.addText(r[1],{x:4.7,y:yy,w:1.45,h:0.35,fontFace:F,fontSize:11,bold:true,color:NAVY,align:"right",valign:"middle",margin:0});
    yy += 0.4;
  });
  s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:yy+0.05,w:5.4,h:0.4,fill:{color:NAVY},line:{type:"none"}});
  s.addText("補助前合計",{x:0.95,y:yy+0.05,w:3.7,h:0.4,fontFace:F,fontSize:11,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("3,058 万円",{x:4.5,y:yy+0.05,w:1.65,h:0.4,fontFace:F,fontSize:12,bold:true,color:GOLD,align:"right",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:yy+0.5,w:5.4,h:0.35,fill:{color:WHITE},line:{color:BLUE,width:1.2}});
  s.addText("千葉県補助金 (上限)",{x:0.95,y:yy+0.5,w:3.7,h:0.35,fontFace:F,fontSize:10,bold:true,color:BLUE,align:"left",valign:"middle",margin:0});
  s.addText("▲ 1,000 万円",{x:4.5,y:yy+0.5,w:1.65,h:0.35,fontFace:F,fontSize:11,bold:true,color:BLUE,align:"right",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:yy+0.92,w:5.4,h:0.45,fill:{color:"E07D45"},line:{type:"none"}});
  s.addText("実質投資 (今年)",{x:0.95,y:yy+0.92,w:3.7,h:0.45,fontFace:F,fontSize:12,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("2,058 万円",{x:4.4,y:yy+0.92,w:1.75,h:0.45,fontFace:F,fontSize:14,bold:true,color:WHITE,align:"right",valign:"middle",margin:0});

  // 来年カード(右)
  card(s, 6.83, 2.78, 6.0, 3.95, LGREY);
  s.addShape(pres.shapes.RECTANGLE,{x:6.83,y:2.78,w:6.0,h:0.5,fill:{color:GOLDD},line:{type:"none"}});
  s.addText("【来年】外壁 1,500 ㎡(補助金チャレンジ)",{x:7.03,y:2.78,w:5.7,h:0.5,fontFace:F,fontSize:14,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  const next_year=[["外壁ポリウレア 1,500 ㎡","1,320 万円"],
                   ["全面足場 1,800 ㎡(3,000円/㎡)","540 万円"],
                   ["― 屋根は20年耐候のため不要","―"],
                   ["― 物価高騰の影響を回避","―"],
                   ["来年度 R9 補助金 申請","対象"]];
  yy=3.45;
  next_year.forEach((r,i)=>{
    s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:yy,w:5.4,h:0.35,fill:{color:WHITE},line:{color:BORDER,width:1}});
    s.addText(r[0],{x:7.28,y:yy,w:3.7,h:0.35,fontFace:F,fontSize:10,color:(r[0].startsWith("―")?MGREY:INK),align:"left",valign:"middle",margin:0});
    s.addText(r[1],{x:11.0,y:yy,w:1.45,h:0.35,fontFace:F,fontSize:11,bold:true,color:(r[1].startsWith("―")?MGREY:NAVY),align:"right",valign:"middle",margin:0});
    yy += 0.4;
  });
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:yy+0.05,w:5.4,h:0.4,fill:{color:NAVY},line:{type:"none"}});
  s.addText("補助前合計",{x:7.28,y:yy+0.05,w:3.7,h:0.4,fontFace:F,fontSize:11,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("1,860 万円",{x:10.85,y:yy+0.05,w:1.6,h:0.4,fontFace:F,fontSize:12,bold:true,color:GOLD,align:"right",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:yy+0.5,w:5.4,h:0.35,fill:{color:WHITE},line:{color:BLUE,width:1.2}});
  s.addText("補助金 1/2 (想定)",{x:7.28,y:yy+0.5,w:3.7,h:0.35,fontFace:F,fontSize:10,bold:true,color:BLUE,align:"left",valign:"middle",margin:0});
  s.addText("▲ 930 万円",{x:10.85,y:yy+0.5,w:1.6,h:0.35,fontFace:F,fontSize:11,bold:true,color:BLUE,align:"right",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:yy+0.92,w:5.4,h:0.45,fill:{color:GOLDD},line:{type:"none"}});
  s.addText("実質投資 (来年)",{x:7.28,y:yy+0.92,w:3.7,h:0.45,fontFace:F,fontSize:12,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("930 万円",{x:10.7,y:yy+0.92,w:1.75,h:0.45,fontFace:F,fontSize:14,bold:true,color:WHITE,align:"right",valign:"middle",margin:0});

  // 下部結論バー
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:6.85,w:12.33,h:0.42,fill:{color:"E07D45"},line:{type:"none"}});
  s.addText("E プラン 2 年合計：実質投資 2,988 万円 (D 比 ▲585万) ／ 補助金 計 1,930 万円獲得 ／ 20 年累計 4,095 万円 (A 比 ▲8,149万)",
    {x:0.5,y:6.85,w:12.33,h:0.42,fontFace:F,fontSize:11,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  footer(s,10);
})();
console.log("slides 8-9 built");

// ============================================================
// Slide 10 : 20年累計支出比較（4列内訳）
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"05"); title(s,"20 年累計支出比較 ― 電気代＋建物メンテ＋設備投資");
  const cols=[
    [GREY,"A 現状","12,244 万円",["└ 電気代 5,660","└ 塗装+足場 6,584★","└ 設備 0"],"─",MGREY],
    [BLUE,"B サニックス","10,955 万円",["└ 電気代 3,755","└ 塗装+足場 6,584","└ 設備 616"],"▲ 1,289 万",BLUE],
    [TEAL,"C シスコム","9,821 万円",["└ 電気代 2,084","└ 塗装+足場 6,584","└ 設備 実質 1,153"],"▲ 2,423 万",TEAL],
    [GOLDD,"D ダブル","5,375 万円",["└ 電気代 1,802","└ メンテ 0 ★","└ 設備 実質 3,573"],"▲ 6,869 万",GOLDD],
    ["E07D45","E 屋根先行","4,095 万円★",["└ 電気代 2,037","└ メンテ 0 ★","└ 設備 実質 2,058"],"▲ 8,149 万","E07D45"],
  ];
  const cw=2.34, cx0=0.55, cgap=0.13, cy=1.9, ch=4.0;
  cols.forEach((c,i)=>{
    const x=cx0+i*(cw+cgap);
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy,w:cw,h:0.55,fill:{color:c[0]},line:{type:"none"}});
    s.addText(c[1],{x:x+0.1,y:cy,w:cw-0.15,h:0.55,fontFace:F,fontSize:12.5,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy+0.55,w:cw,h:ch-0.55,fill:{color:LGREY},line:{color:BORDER,width:1}});
    s.addText("20年累計",{x:x+0.12,y:cy+0.7,w:cw-0.2,h:0.28,fontFace:F,fontSize:9,color:MGREY,align:"left",valign:"middle",margin:0});
    s.addText(c[2],{x:x+0.1,y:cy+0.98,w:cw-0.2,h:0.55,fontFace:F,fontSize:16,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
    const b=c[3].map((t)=>({text:t,options:{breakLine:true,paraSpaceAfter:6,fontSize:9,color:INK}}));
    s.addText(b,{x:x+0.12,y:cy+1.6,w:cw-0.2,h:1.45,fontFace:F,align:"left",valign:"top",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+0.12,y:cy+3.2,w:cw-0.24,h:0.55,fill:{color:WHITE},line:{color:c[5],width:1.3}});
    s.addText(c[4],{x:x+0.12,y:cy+3.2,w:cw-0.24,h:0.55,fontFace:F,fontSize:9.5,bold:true,color:c[5],align:"center",valign:"middle",margin:0});
  });
  // 下部結論
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:6.1,w:12.33,h:0.95,fill:{color:NAVY},line:{type:"none"}});
  s.addText("初期投資が一番高そうに見える D プランが、 20 年で最も安い",{x:0.7,y:6.16,w:12,h:0.36,fontFace:F,fontSize:13,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("理由：①窓断熱 + 屋根遮熱ポリウレアで空調電気代を 30% カット ②塗装+足場は20年で 6,584万かかる。 D/E案はポリウレアで20年メンテ0+遮熱で空調代も下がる ③ 20 年塗装 + 足場 2,439 万円が不要 ④補助金 1,000 万円 ( 上限 ) で設備費圧縮、外壁ポリウレア化で資産価値も向上",
    {x:0.7,y:6.5,w:11.95,h:0.5,fontFace:F,fontSize:10,color:WHITE,align:"left",valign:"middle",lineSpacingMultiple:1.15,margin:0});
  footer(s,11);
})();

// ============================================================
// Slide 11 : 棒グラフ比較
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"05"); title(s,"20 年累計コスト 棒グラフ比較 ― D と E の戦略比較");
  // 積み上げ棒グラフ（電気代/建物メンテ/設備投資）単位:万円
  // A: 電気5660 メンテ2439 投資0 / B: 3680 2439 616 / C:1773 2439 1153 / D:1009 0 3588
  const data=[
    {name:"電気代", labels:["A 現状","B サニ","C シスコム","D ダブル","E 屋根先行"], values:[5660,3755,2084,1802,2037]},
    {name:"建物メンテ", labels:["A 現状","B サニ","C シスコム","D ダブル","E 屋根先行"], values:[6584,6584,6584,0,0]},
    {name:"設備投資", labels:["A 現状","B サニ","C シスコム","D ダブル","E 屋根先行"], values:[0,616,1153,3573,2058]},
  ];
  s.addChart(pres.charts.BAR, data, {
    x:0.6, y:1.85, w:9.3, h:4.5, barDir:"col", barGrouping:"stacked",
    chartColors:["5B7A95", ORANGE, NAVY],
    showLegend:false, showValue:false,
    valAxisMinVal:0, valAxisMaxVal:13500, valAxisMajorUnit:2250,
    valAxisLabelColor:"64748B", valAxisLabelFontSize:10, valAxisLabelFontFace:F,
    catAxisLabelColor:"1A2B40", catAxisLabelFontSize:11, catAxisLabelFontFace:F, catAxisLabelFontBold:true,
    valGridLine:{color:"E8ECF1",size:0.5}, catGridLine:{style:"none"},
    valAxisLabelFormatCode:'#,##0"万円"',
    chartArea:{fill:{color:"FFFFFF"}},
  });
  // 合計ラベル（手動オーバーレイ）
  const totals=[["12,244 万",0.95],["10,955 万",2.85],["9,821 万",4.75],["5,375 万",6.65],["4,095 万",8.55]];
  const topY=[2.22,2.65,3.03,4.51,4.93]; // 5本 軸13500
  totals.forEach((t,i)=>{
    s.addShape(pres.shapes.RECTANGLE,{x:t[1],y:topY[i],w:1.35,h:0.42,fill:{color:NAVY},line:{type:"none"}});
    s.addText(t[0],{x:t[1],y:topY[i],w:1.35,h:0.42,fontFace:F,fontSize:11,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  });
  // ★マーク（D）
  s.addShape(pres.shapes.OVAL,{x:8.95,y:4.38,w:0.55,h:0.55,fill:{color:GOLD},line:{type:"none"}});
  s.addText("★",{x:8.95,y:4.38,w:0.55,h:0.55,fontFace:F,fontSize:16,bold:true,color:NAVY,align:"center",valign:"middle",margin:0});
  // 凡例カード
  card(s, 10.15, 2.4, 2.68, 3.45, LGREY);
  s.addText("内訳",{x:10.4,y:2.6,w:2.3,h:0.35,fontFace:F,fontSize:13,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  const leg=[["5B7A95","電気代","20 年累計・年 2% 上昇"],[ORANGE,"建物メンテ","塗装 + パネル脱着"],[NAVY,"設備投資","実質負担 ( 補助後 )"]];
  leg.forEach((l,i)=>{
    const y=3.05+i*0.9;
    s.addShape(pres.shapes.RECTANGLE,{x:10.4,y,w:0.3,h:0.3,fill:{color:l[0]},line:{type:"none"}});
    s.addText(l[1],{x:10.8,y:y-0.03,w:1.95,h:0.3,fontFace:F,fontSize:11.5,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
    s.addText(l[2],{x:10.4,y:y+0.32,w:2.3,h:0.4,fontFace:F,fontSize:9,color:MGREY,align:"left",valign:"top",lineSpacingMultiple:1.1,margin:0});
  });
  // 下部結論バー
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:6.55,w:12.33,h:0.55,fill:{color:GOLDD},line:{type:"none"}});
  s.addText("D は確定で A比 ▲6,869 万。 E は来年外壁の補助金成功で最安 A比 ▲8,149 万。 ★A/B/C のオレンジ部分(塗装+足場)は暑さ対策にならず物価で雪だるま式に増える ／ D/E はポリウレアでメンテ0+遮熱二重効果★",
    {x:0.5,y:6.55,w:12.33,h:0.55,fontFace:F,fontSize:12.5,bold:true,color:NAVY,align:"center",valign:"middle",margin:0});
  footer(s,12);
})();
console.log("slides 10-11 built");

// ============================================================
// Slide 12 : 建物維持負担タイムライン
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"05"); title(s,"建物維持負担 ― 通常塗装は20年で6,584万円 ★暑さ対策にならない!");
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.55,w:12.33,h:0.55,fill:{color:RED},line:{type:"none"}});
  s.addText("★ 塗装は維持費をかけても暑さ対策にならない! ／ 物価高騰6%/年で工事費は雪だるま式に上がる",
    {x:0.7,y:1.55,w:12,h:0.55,fontFace:F,fontSize:13.5,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("A ・ B ・ C 案 共通：通常塗装メンテ計画(20年で2回・物価6%/年複利)",
    {x:0.5,y:2.3,w:10,h:0.35,fontFace:F,fontSize:13,bold:true,color:INK,align:"left",valign:"middle",margin:0});
  const axY=3.55;
  s.addShape(pres.shapes.LINE,{x:1.3,y:axY,w:10.7,h:0,line:{color:INK,width:2}});
  const pts=[[2.0,GREY,"今","─","1回現価 1,763 万円",MGREY],
             [6.3,ORANGE,"5 年後","▲ 2,359 万円","塗装1,160+足場540+脱着63",ORANGE],
             [10.5,RED,"15 年後","▲ 4,225 万円","物価高騰6%/年×15年累積",RED]];
  pts.forEach((p)=>{
    s.addText(p[2],{x:p[0]-1.0,y:axY-0.65,w:2.0,h:0.3,fontFace:F,fontSize:13,bold:true,color:INK,align:"center",valign:"middle",margin:0});
    s.addShape(pres.shapes.OVAL,{x:p[0]-0.18,y:axY-0.18,w:0.36,h:0.36,fill:{color:p[1]},line:{color:WHITE,width:2}});
    s.addText(p[3],{x:p[0]-1.3,y:axY+0.35,w:2.6,h:0.4,fontFace:F,fontSize:17,bold:true,color:p[5],align:"center",valign:"middle",margin:0});
    s.addText(p[4],{x:p[0]-1.7,y:axY+0.83,w:3.4,h:0.4,fontFace:F,fontSize:9,color:MGREY,align:"center",valign:"top",lineSpacingMultiple:1.1,margin:0});
  });
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.0,w:12.33,h:0.5,fill:{color:LGREY},line:{color:BORDER,width:1}});
  s.addText("1回あたり: 塗装(4,000円×2,900㎡=1,160万) + 全面足場(3,000円×1,800㎡=540万) + パネル脱着 63万 = 1,763万円(現価)",
    {x:0.7,y:5.0,w:12,h:0.5,fontFace:F,fontSize:10.5,bold:true,color:INK,align:"left",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.6,w:12.33,h:0.6,fill:{color:RED},line:{type:"none"}});
  s.addText("→ A・B・C 案では20年で 6,584 万円 のメンテ費用が必ず発生し、 ★暑さは1ミリも改善しない★",
    {x:0.7,y:5.6,w:12,h:0.6,fontFace:F,fontSize:13,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:6.3,w:12.33,h:0.95,fill:{color:GOLDD},line:{type:"none"}});
  s.addText("D / E 案：脱炭素化促進事業の補助金活用で「メンテ自体が無くなる + 暑さも下がる」",
    {x:0.7,y:6.35,w:12,h:0.32,fontFace:F,fontSize:13,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  s.addText([
    {text:"D 案: 屋根+外壁ポリウレア2,900㎡(税込2,840万) → 補助金▲1,000万 → 実質1,840万。20年で6,584万のメンテが0円に",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:4}},
    {text:"E 案: 今年屋根のみ施工し補助金1,000万、来年外壁施工で補助金930万追加 ★ 補助金を2回獲りに行く2段階作戦",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:4}},
    {text:"加えて、屋根5%+窓25%=空調30%カット効果。 ★塗装にはない遮熱効果で電気代も下がる二重効果★",options:{bullet:{code:"25CF"},bold:true}},
  ],{x:0.75,y:6.65,w:12,h:0.55,fontFace:F,fontSize:10,color:NAVY,align:"left",valign:"top",margin:0});
  footer(s,13);
})();

// ============================================================
// Slide 13 : BCP × CO2削減価値
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"06"); title(s,"BCP ・レジリエンス × 脱炭素・ CO₂ 削減価値");
  // 左カード
  card(s, 0.5, 1.7, 6.0, 5.05, LGREY);
  s.addText("BCP 価値（停電時の事業継続力）",{x:0.8,y:1.92,w:5.5,h:0.36,fontFace:F,fontSize:14,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  s.addText("Powerwall 3 × 4 台 54kWh で耐えられる時間",{x:0.8,y:2.3,w:5.5,h:0.3,fontFace:F,fontSize:11,color:MGREY,align:"left",valign:"middle",margin:0});
  const bcp=[[TEAL,"全負荷 5kW 運転","11 時間"],[BLUE,"重要 3kW 運転","18 時間"],[GOLDD,"最低限 1.5kW 運転","36 時間"],[NAVY,"+ 日中の太陽光発電","数日継続"]];
  bcp.forEach((b,i)=>{
    const y=2.7+i*0.62;
    s.addShape(pres.shapes.RECTANGLE,{x:0.8,y,w:0.12,h:0.5,fill:{color:b[0]},line:{type:"none"}});
    s.addShape(pres.shapes.RECTANGLE,{x:0.92,y,w:5.28,h:0.5,fill:{color:WHITE},line:{color:BORDER,width:1}});
    s.addText(b[1],{x:1.1,y,w:3.3,h:0.5,fontFace:F,fontSize:12,color:INK,align:"left",valign:"middle",margin:0});
    s.addText(b[2],{x:4.3,y,w:1.75,h:0.5,fontFace:F,fontSize:15,bold:true,color:b[0]==NAVY?NAVY:b[0],align:"right",valign:"middle",margin:0});
  });
  s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:5.3,w:5.4,h:1.2,fill:{color:WHITE},line:{color:RED,width:1.3}});
  s.addText("千葉県のレジリエンスリスク",{x:0.95,y:5.4,w:5,h:0.3,fontFace:F,fontSize:11.5,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  const risk=[["93 万戸","2019 年台風 15 号 停電被害"],["最大 2 週間","千葉県内の停電継続"],["60 万円〜","1 日休業 + 冷凍商品損失"]];
  risk.forEach((r,i)=>{
    const y=5.72+i*0.25;
    s.addText(r[0],{x:0.95,y,w:1.5,h:0.25,fontFace:F,fontSize:11,bold:true,color:RED,align:"left",valign:"middle",margin:0});
    s.addText(r[1],{x:2.5,y,w:3.6,h:0.25,fontFace:F,fontSize:9.5,color:INK,align:"left",valign:"middle",margin:0});
  });
  // 右カード
  card(s, 6.83, 1.7, 6.0, 5.05, LGREY);
  s.addText("脱炭素・ CO₂ 削減価値",{x:7.13,y:1.92,w:5.5,h:0.36,fontFace:F,fontSize:14,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:2.35,w:5.4,h:0.95,fill:{color:TEAL},line:{type:"none"}});
  s.addText("初年度 26.57 t-CO₂ 削減",{x:7.13,y:2.45,w:5.4,h:0.45,fontFace:F,fontSize:20,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  s.addText("(C/D 共通 / 杉の木 約 4,500 本 / 年 に相当 )",{x:7.13,y:2.9,w:5.4,h:0.3,fontFace:F,fontSize:10.5,color:"D7F2E9",align:"center",valign:"middle",margin:0});
  // テーブル
  const tbl=[
    [{text:"",options:{fill:{color:NAVY}}},{text:"A",options:{fill:{color:NAVY},color:GOLD,bold:true,align:"center"}},{text:"B",options:{fill:{color:NAVY},color:GOLD,bold:true,align:"center"}},{text:"C/D",options:{fill:{color:NAVY},color:GOLD,bold:true,align:"center"}}],
    ["再エネ比率","0%","47.2%","58.8%"],
    ["CO₂ 削減 ( 年 )","0 t","21.3 t","26.6 t"],
    ["CO₂ 削減 (25 年 )","0 t","501 t","564 t"],
    ["余剰電力","売電","捨てる","蓄電池へ"],
  ];
  s.addTable(tbl,{x:7.13,y:3.4,w:5.4,colW:[2.1,1.1,1.1,1.1],rowH:[0.32,0.34,0.34,0.34,0.34],
    fontFace:F,fontSize:10.5,color:INK,align:"center",valign:"middle",border:{pt:0.5,color:BORDER},fill:{color:WHITE}});
  // 表の1列目左寄せ上書きは省略（中央でも可読）
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:5.4,w:5.4,h:1.1,fill:{color:NAVY},line:{type:"none"}});
  s.addText("ESG ・ SDGs 文脈での価値",{x:7.3,y:5.48,w:5,h:0.3,fontFace:F,fontSize:11,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText([
    {text:"取引先の脱炭素要請に対応 (Scope2 排出量削減 )",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:3}},
    {text:"再エネ比率 59% は中小事業者として極めて高水準",options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:3}},
    {text:"RE100 関連の取引拡大を狙える定量実績",options:{bullet:{code:"25CF"}}},
  ],{x:7.32,y:5.78,w:5.1,h:0.68,fontFace:F,fontSize:9.5,color:WHITE,align:"left",valign:"top",margin:0});
  footer(s,14);
})();
console.log("slides 12-13 built");

// ============================================================
// Slide 14 : 補助金活用スキーム
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"06"); title(s,"千葉県補助金活用スキーム ― 蓄電池 + ポリウレア の合算ストーリー");
  // 左カード
  card(s, 0.5, 1.7, 6.0, 5.05, LGREY);
  s.addText("千葉県業務用設備等脱炭素化促進事業補助金",{x:0.8,y:1.92,w:5.5,h:0.36,fontFace:F,fontSize:13.5,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  const sub=[
    ["対象","県内の中小事業者等（中小企業・個人事業者・ NPO 等）",0.46],
    ["対象設備","再エネ発電電力を蓄電する蓄電池の設置 ほか",0.46],
    ["補助率","省エネ診断あり ➡ 1/2 ( 上限 1,000 万円 )\n簡易自己診断のみ ➡ 1/4 ( 上限 500 万円 )",0.74],
    ["要件","①CO₂ スマート宣言事業所登録 ②省エネ診断受診\n③CO₂ 削減 3t 以上 / 年 ④交付決定前に未着手",0.74],
    ["対象経費","設備費・工事費（撤去 / 消費税相当除く）",0.46],
    ["募集時期","例年 5 〜 10 月 (R8 年度内容は準備中・予算先着順 )",0.46],
  ];
  let sy=2.4;
  sub.forEach((r)=>{
    s.addShape(pres.shapes.RECTANGLE,{x:0.8,y:sy,w:1.45,h:r[2],fill:{color:NAVY},line:{type:"none"}});
    s.addText(r[0],{x:0.8,y:sy,w:1.45,h:r[2],fontFace:F,fontSize:10,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
    s.addText(r[1],{x:2.4,y:sy,w:3.9,h:r[2],fontFace:F,fontSize:10,color:INK,align:"left",valign:"middle",lineSpacingMultiple:1.2,margin:0});
    sy += r[2]+0.07;
  });
  // 右カード
  card(s, 6.83, 1.7, 6.0, 5.05, LGREY);
  s.addText("補助金活用の試算 ( 蓄電池 + ポリウレア )",{x:7.13,y:1.92,w:5.5,h:0.36,fontFace:F,fontSize:13.5,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
  function calcRow(y,label,val,vc,boxLine){
    s.addShape(pres.shapes.RECTANGLE,{x:7.13,y,w:5.4,h:0.5,fill:{color:WHITE},line:{color:boxLine||BORDER,width:boxLine?1.3:1}});
    s.addText(label,{x:7.28,y,w:3.6,h:0.5,fontFace:F,fontSize:10.5,color:INK,align:"left",valign:"middle",margin:0});
    s.addText(val,{x:10.0,y,w:2.43,h:0.5,fontFace:F,fontSize:13,bold:true,color:vc,align:"right",valign:"middle",margin:0});
  }
  calcRow(2.4,"蓄電池 税抜 (Powerwall 3 × 4 台 )","8,730,000 円",INK,INK);
  calcRow(2.95,"  → 単独補助 (1/2)","▲ 4,365,000 円",BLUE,BLUE);
  calcRow(3.55,"ポリウレア + 昇降足場 税抜 (2,900 ㎡ + 足場 1 回 )","25,820,000 円",INK,INK);
  calcRow(4.1,"  → 単独補助 (1/2)","▲ 12,910,000 円",BLUE,BLUE);
  calcRow(4.75,"単純合計","▲ 17,275,000 円",INK);
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:5.3,w:5.4,h:0.5,fill:{color:WHITE},line:{color:ORANGE,width:1.3}});
  s.addText("⚠ 補助金 上限キャップ",{x:7.28,y:5.3,w:3.0,h:0.5,fontFace:F,fontSize:11,bold:true,color:ORANGE,align:"left",valign:"middle",margin:0});
  s.addText("▲ 1,000 万円 ( 上限 )",{x:10.0,y:5.3,w:2.43,h:0.5,fontFace:F,fontSize:12,bold:true,color:ORANGE,align:"right",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:5.85,w:5.4,h:0.55,fill:{color:NAVY},line:{type:"none"}});
  s.addText("実獲得補助金",{x:7.28,y:5.85,w:3.0,h:0.55,fontFace:F,fontSize:12.5,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("▲ 10,000,000 円",{x:9.7,y:5.85,w:2.73,h:0.55,fontFace:F,fontSize:16,bold:true,color:GOLD,align:"right",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:7.13,y:6.48,w:5.4,h:0.4,fill:{color:WHITE},line:{color:ORANGE,width:1}});
  s.addText("予算先着順 / 交付決定前は着工不可 / 早期申請必須",{x:7.13,y:6.48,w:5.4,h:0.4,fontFace:F,fontSize:9.5,bold:true,color:ORANGE,align:"center",valign:"middle",margin:0});
  footer(s,15);
})();

// ============================================================
// Slide 15 : 蓄電池容量の最適化検討
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"06"); title(s,"蓄電池容量の最適化検討 ― 3 台 / 4 台 / 6 台の比較");
  const cards=[
    [ORANGE,"3 台 (40.5kWh)",["投資 655 万 → 補助後 327 万","実投資合計 1,022 万円","自家消費 +11,108 kWh/ 年","BCP 5kW 運転 → 8 時間","塗装 + 脱着 別途 2,439 万円"],"BCP 不足",ORANGE,false],
    [GOLDD,"4 台 (54.0kWh)",["投資 873 万 → 補助後 436 万","実投資合計 1,153 万円","自家消費 +12,871 kWh/ 年","BCP 5kW 運転 11h/3kW 運転 18h","塗装 + 脱着 別途 2,439 万円"],"推奨・最適",GOLDD,true],
    [RED,"6 台 (81.0kWh)",["投資 1,310 万 → 補助後 655 万","実投資合計 1,415 万円","自家消費 +14,466 kWh/ 年","BCP 5kW 運転 → 16 時間","塗装 + 脱着 別途 2,439 万円"],"投資効率悪",RED,false],
  ];
  const cw=3.95, cx0=0.5, cgap=0.27, cy=2.05, ch=3.6;
  cards.forEach((c,i)=>{
    const x=cx0+i*(cw+cgap);
    if(c[6]){ s.addShape(pres.shapes.RECTANGLE,{x:x+cw-1.0,y:cy-0.35,w:1.0,h:0.35,fill:{color:NAVY},line:{type:"none"}}); s.addText("推奨",{x:x+cw-1.0,y:cy-0.35,w:1.0,h:0.35,fontFace:F,fontSize:11,bold:true,color:WHITE,align:"center",valign:"middle",margin:0}); }
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy,w:cw,h:0.62,fill:{color:c[0]},line:{type:"none"}});
    s.addText(c[1],{x:x+0.25,y:cy,w:cw-0.4,h:0.62,fontFace:F,fontSize:16,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy+0.62,w:cw,h:ch-0.62,fill:{color:WHITE},line:{color:c[6]?GOLDD:BORDER,width:c[6]?1.5:1}});
    const b=c[2].map((t)=>({text:t,options:{bullet:{code:"25CF"},breakLine:true,paraSpaceAfter:10,fontSize:11,color:INK}}));
    s.addText(b,{x:x+0.25,y:cy+0.82,w:cw-0.45,h:2.1,fontFace:F,align:"left",valign:"top",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x,y:cy+ch-0.5,w:cw,h:0.5,fill:{color:LGREY},line:{type:"none"}});
    s.addText(c[3],{x,y:cy+ch-0.5,w:cw,h:0.5,fontFace:F,fontSize:14,bold:true,color:c[4],align:"center",valign:"middle",margin:0});
  });
  // なぜ4台が最適
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.95,w:12.33,h:1.05,fill:{color:NAVY},line:{type:"none"}});
  s.addText("なぜ 4 台が最適か",{x:0.7,y:6.02,w:11,h:0.3,fontFace:F,fontSize:12,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("店舗の冷凍庫・冷蔵設備を停電中に運転継続するには連続 11 時間が安全圏。 3 台の 8 時間では深夜から早朝の停電が一日続いた場合に商品損失リスク。\n6 台は過剰投資で 4 台比 +262 万円多い投資 ( 投資効率悪化 ) 。 4 台が経済性と BCP 耐久性のバランス最適",
    {x:0.7,y:6.32,w:12,h:0.62,fontFace:F,fontSize:10.5,color:WHITE,align:"left",valign:"middle",lineSpacingMultiple:1.2,margin:0});
  footer(s,16);
})();
console.log("slides 14-15 built");

// ============================================================
// Slide 16 : リスクと注意事項（2×2）
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"07"); title(s,"リスクと注意事項");
  const items=[
    [RED,"!","補助金枠の予算先着","千葉県補助金は予算到達次第終了。 R7 年度は 9 月末で予算枠到達。 R8 年度開始 (5 〜 6 月想定 ) 後の早期申請が必須","事前に省エネ診断と CO₂ スマート宣言登録を完了させ、募集開始即日に申請"],
    [ORANGE,"↓","卒 FIT 後の売電単価急減","現状の全量売電は買取期間満了後、再生可能エネルギー市場価格 (8 〜 10 円 /kWh 程度 ) への移行が見込まれる","本提案は買取期間内であっても自家消費へ切替が経済合理的。卒 FIT 前の意思決定が望ましい"],
    [BLUE,"↺","蓄電池の運用年数と PCS","Powerwall 3 は LFP で設計寿命 15-20 年。 10 年保証 (70% 容量 ) 。 PCS は内蔵のため別途交換不要","本試算では蓄電池を 20 年運用前提。容量低下が進んだ場合は PV 自家消費のみに切替も可能"],
    [TEAL,"?","省エネ診断の所要時間","補助率 1/2 ( 上限 1,000 万 ) の獲得には省エネ診断の受診が必須。申込から診断完了まで 1 〜 2 ヶ月を要する","R8 年度補助金募集 (5 〜 6 月想定 ) に間に合わせるには、今月中の登録・診断申込開始が必須。順序が遅れると補助率 1/4 ( 上限 500 万 ) に降格"],
  ];
  const cw=6.0, cgap=0.33, ch=2.35, cy0=1.7;
  items.forEach((it,i)=>{
    const x = 0.5 + (i%2)*(cw+cgap);
    const y = cy0 + Math.floor(i/2)*(ch+0.28);
    s.addShape(pres.shapes.RECTANGLE,{x,y,w:cw,h:ch,fill:{color:WHITE},line:{color:it[0],width:1.3}});
    s.addShape(pres.shapes.OVAL,{x:x+0.3,y:y+0.28,w:0.6,h:0.6,fill:{color:it[0]},line:{type:"none"}});
    s.addText(it[1],{x:x+0.3,y:y+0.28,w:0.6,h:0.6,fontFace:F,fontSize:20,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
    s.addText(it[2],{x:x+1.1,y:y+0.3,w:cw-1.3,h:0.55,fontFace:F,fontSize:15,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
    s.addText(it[3],{x:x+0.3,y:y+1.0,w:cw-0.6,h:0.62,fontFace:F,fontSize:10,color:INK,align:"left",valign:"top",lineSpacingMultiple:1.2,margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+0.3,y:y+1.62,w:cw-0.6,h:0.6,fill:{color:LGREY},line:{color:BORDER,width:1}});
    s.addText("対策",{x:x+0.42,y:y+1.66,w:cw-0.8,h:0.22,fontFace:F,fontSize:9,bold:true,color:ORANGE,align:"left",valign:"middle",margin:0});
    s.addText(it[4],{x:x+0.42,y:y+1.86,w:cw-0.85,h:0.34,fontFace:F,fontSize:8.8,color:INK,align:"left",valign:"top",lineSpacingMultiple:1.1,margin:0});
  });
  footer(s,17);
})();

// ============================================================
// Slide 17 : 次のステップ（ロードマップ）
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  secNum(s,"07"); title(s,"次のステップ ― Roadmap to Implementation");
  const steps=[
    [TEAL,"01","CO₂ スマート宣言事業所登録","千葉県の脱炭素事業所登録制度。補助金申請の前提条件。 Web 申請で完結","今月中・無料・即日完了"],
    [BLUE,"02","省エネ診断 申込","( 一財 ) 省エネルギーセンター等に申込。補助率 1/2 ( 上限 1,000 万 ) のため必須要件","今月〜来月・ 2 万円前後ご負担あり ( 中小企業 )"],
    [GOLDD,"03","省エネ診断 受診","電力使用状況の現地調査と改善提案を受診。診断報告書を補助金申請書類として活用","1 〜 2 ヶ月・現地調査含む"],
    [ORANGE,"04","補助金申請","千葉県業務用設備等脱炭素化促進事業補助金 申請。交付決定前は着工不可","R8 年度募集開始即日 (5 〜 6 月想定 )"],
    [NAVY,"05","工事・運用開始","自家消費切替工事 / 蓄電池 4 台設置 / 系統連系 / 運用開始 (D プランは省エネ施工も並行 )","交付決定後 3 〜 4 ヶ月"],
  ];
  const top=1.7, rh=0.86, gap=0.1, x=0.5;
  steps.forEach((st,i)=>{
    const y=top+i*(rh+gap);
    s.addShape(pres.shapes.RECTANGLE,{x,y,w:1.1,h:rh,fill:{color:st[0]},line:{type:"none"}});
    s.addText(st[1],{x,y,w:1.1,h:rh,fontFace:F,fontSize:22,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+1.1,y,w:8.0,h:rh,fill:{color:LGREY},line:{color:BORDER,width:1}});
    s.addText(st[2],{x:x+1.35,y:y+0.1,w:7.6,h:0.36,fontFace:F,fontSize:14,bold:true,color:NAVY,align:"left",valign:"middle",margin:0});
    s.addText(st[3],{x:x+1.35,y:y+0.44,w:7.6,h:0.36,fontFace:F,fontSize:10,color:INK,align:"left",valign:"middle",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+9.3,y,w:3.5,h:rh,fill:{color:WHITE},line:{color:st[0],width:1.3}});
    s.addText(st[4],{x:x+9.4,y,w:3.3,h:rh,fontFace:F,fontSize:10.5,bold:true,color:st[0]==NAVY?NAVY:st[0],align:"left",valign:"middle",lineSpacingMultiple:1.1,margin:0});
  });
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:6.55,w:12.33,h:0.5,fill:{color:GOLDD},line:{type:"none"}});
  s.addText("まずは「 CO₂ スマート登録」と「省エネ診断申込」から ― 補助金 1,000 万円 ( 上限 ) 獲得＋ 2,439 万円屋根メンテ削減＋外壁資産価値向上の起点",
    {x:0.5,y:6.55,w:12.33,h:0.5,fontFace:F,fontSize:11.5,bold:true,color:NAVY,align:"center",valign:"middle",margin:0});
  footer(s,18);
})();
console.log("slides 16-17 built");

// ============================================================
// Slide 18 : ポリウレア動画リンク集
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:WHITE};
  title(s,"ご参考：脂肪族ポリウレア普及推進協議会 動画リンク集", 0.55);
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.45,w:12.33,h:1.0,fill:{color:NAVY},line:{type:"none"}});
  s.addText("脂肪族ポリウレアとは",{x:0.7,y:1.52,w:11,h:0.3,fontFace:F,fontSize:12,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("従来の塗料・防水材を超える耐久性・遮熱断熱性能を持つ次世代コーティング材。 D プラン②の核となる素材で、屋根・外壁の劣化を抜本的に抑え、建物寿命を 15 〜 20 年延伸します。協議会の公式動画で技術的根拠と施工事例をご確認ください。",
    {x:0.7,y:1.82,w:12,h:0.58,fontFace:F,fontSize:10.5,color:WHITE,align:"left",valign:"middle",lineSpacingMultiple:1.2,margin:0});
  const vids=[
    [TEAL,"第 3 世代国産脂肪族ポリウレアとは？","協議会による技術概要 (5 分 57 秒 )","https://youtu.be/EBqWMWrUGMs","公式紹介"],
    [BLUE,"第 3 章：脂肪族ポリウレアの特徴と既存建物の問題解決","建物の劣化と修繕の本質的な解決策 (8 分 18 秒 )","https://youtu.be/adNSbemAS4w","建物課題編"],
    [GOLDD,"スケッチ製造、脂肪族ポリウレア商品紹介","本提案で使用する材料の解説 (3 分 19 秒 )","https://youtu.be/fcB2JqLO7BU","商品紹介"],
    [ORANGE,"UV シールド Pu とは？","看板メンテナンス・ UV カット 95% の革新的素材 (5 分 17 秒 )","https://youtu.be/_r3tEsR2F5M","看板・外装"],
  ];
  const cw=6.0, cgap=0.33, ch=1.95, cy0=2.65;
  vids.forEach((v,i)=>{
    const x = 0.5 + (i%2)*(cw+cgap);
    const y = cy0 + Math.floor(i/2)*(ch+0.25);
    s.addShape(pres.shapes.RECTANGLE,{x,y,w:cw,h:ch,fill:{color:WHITE},line:{color:v[0],width:1.3}});
    s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.08,h:ch,fill:{color:v[0]},line:{type:"none"}});
    s.addShape(pres.shapes.OVAL,{x:x+0.35,y:y+0.55,w:0.85,h:0.85,fill:{color:v[0]},line:{type:"none"}});
    s.addText("▶",{x:x+0.35,y:y+0.55,w:0.85,h:0.85,fontFace:F,fontSize:18,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
    s.addText(v[1],{x:x+1.4,y:y+0.22,w:cw-1.6,h:0.6,fontFace:F,fontSize:13,bold:true,color:NAVY,align:"left",valign:"middle",lineSpacingMultiple:1.05,margin:0});
    s.addText(v[2],{x:x+1.4,y:y+0.85,w:cw-1.6,h:0.3,fontFace:F,fontSize:10,color:MGREY,align:"left",valign:"middle",margin:0});
    s.addText(v[3],{x:x+1.4,y:y+1.25,w:cw-1.6,h:0.3,fontFace:F,fontSize:10.5,bold:true,color:v[0],align:"left",valign:"middle",hyperlink:{url:v[3]},margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+cw-1.4,y:y+ch-0.42,w:1.4,h:0.42,fill:{color:v[0]},line:{type:"none"}});
    s.addText(v[4],{x:x+cw-1.4,y:y+ch-0.42,w:1.4,h:0.42,fontFace:F,fontSize:10,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  });
  footer(s,19);
})();

// ============================================================
// Slide 19 : 裏表紙
// ============================================================
(function(){
  const s = pres.addSlide(); s.background={color:NAVY};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.95,h:0.55,fill:{color:TEAL},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.55,h:1.95,fill:{color:GOLD},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:12.78,y:5.4,w:0.55,h:1.5,fill:{color:GOLD},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:12.38,y:6.9,w:0.95,h:0.6,fill:{color:TEAL},line:{type:"none"}});
  s.addText("THANK  YOU  FOR  YOUR  CONSIDERATION",{x:1.0,y:1.95,w:11,h:0.4,fontFace:F,fontSize:13,bold:true,color:GOLD,charSpacing:3,align:"left",valign:"middle",margin:0});
  s.addText("ご検討、ありがとうございます",{x:0.97,y:2.45,w:11.5,h:0.9,fontFace:F,fontSize:40,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:1.0,y:3.5,w:4.0,h:0.035,fill:{color:GOLD},line:{type:"none"}});
  s.addText("建物の価値を、上げる。",{x:1.0,y:3.7,w:11,h:0.5,fontFace:F,fontSize:20,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("省エネ・創エネを同時に走らせ、月々のキャッシュアウトを抑えながら建物そのものの資産価値を引き上げる経営戦略をご提案します。",
    {x:1.0,y:4.25,w:11.3,h:0.4,fontFace:F,fontSize:12,color:"C8D2E0",align:"left",valign:"middle",margin:0});
  // CONTACT枠
  s.addShape(pres.shapes.RECTANGLE,{x:1.0,y:4.85,w:11.3,h:2.0,fill:{color:NAVY2},line:{color:GOLD,width:1}});
  s.addText("CONTACT",{x:1.25,y:5.0,w:10,h:0.3,fontFace:F,fontSize:11,bold:true,color:GOLD,charSpacing:2,align:"left",valign:"middle",margin:0});
  s.addText("株式会社シスコムネット 特販営業部 寺嵜 忠弘",{x:1.25,y:5.3,w:10.5,h:0.4,fontFace:F,fontSize:17,bold:true,color:WHITE,align:"left",valign:"middle",margin:0});
  s.addText("省エネアドバイザー ／ シスコムサステナシールド代表",{x:1.25,y:5.72,w:10.5,h:0.3,fontFace:F,fontSize:11,color:"C8D2E0",align:"left",valign:"middle",margin:0});
  s.addText("建設業許可：千葉県知事 ( 般 -2) 第 46651 号",{x:1.25,y:6.0,w:10.5,h:0.3,fontFace:F,fontSize:10.5,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  // リンク2列
  s.addText("LINE 公式：",{x:1.25,y:6.4,w:1.5,h:0.28,fontFace:F,fontSize:9.5,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("https://page.line.me/829oslez",{x:2.85,y:6.4,w:3.0,h:0.28,fontFace:F,fontSize:9.5,color:"AEB9CC",align:"left",valign:"middle",hyperlink:{url:"https://page.line.me/829oslez"},margin:0});
  s.addText("シスコムネット：",{x:6.6,y:6.4,w:1.8,h:0.28,fontFace:F,fontSize:9.5,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("https://syscomnet.co.jp/",{x:8.5,y:6.4,w:3.0,h:0.28,fontFace:F,fontSize:9.5,color:"AEB9CC",align:"left",valign:"middle",hyperlink:{url:"https://syscomnet.co.jp/"},margin:0});
  s.addText("脂肪族ポリウレア協議会：",{x:1.25,y:6.62,w:2.6,h:0.28,fontFace:F,fontSize:9.5,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("https://www.s-pua.net/",{x:3.7,y:6.62,w:2.5,h:0.28,fontFace:F,fontSize:9.5,color:"AEB9CC",align:"left",valign:"middle",hyperlink:{url:"https://www.s-pua.net/"},margin:0});
  s.addText("BNI 千葉セントラルクリエーションズ：",{x:6.6,y:6.62,w:3.6,h:0.28,fontFace:F,fontSize:9.5,bold:true,color:GOLD,align:"left",valign:"middle",margin:0});
  s.addText("https://chiba-c.bni.jp/creations/ja/",{x:10.0,y:6.62,w:2.3,h:0.28,fontFace:F,fontSize:8.5,color:"AEB9CC",align:"left",valign:"middle",hyperlink:{url:"https://chiba-c.bni.jp/creations/ja/"},margin:0});
  s.addText("19 / 19  /  © 2026 シスコムサステナシールド",{x:0.5,y:7.12,w:7,h:0.3,fontFace:F,fontSize:8.5,color:GREY,align:"left",valign:"middle",margin:0});
})();
console.log("slides 18-19 built");

// ---- 出力 ----
pres.writeFile({ fileName: "新生社様_省エネ創エネダブルプラン提案書.pptx" })
  .then(()=>console.log("=== ALL 19 SLIDES WROTE ==="));
