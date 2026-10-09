/* =============================================================================
 * 家で使う時間診断 — 受入テスト（二重計上防止ほか）
 * 実行: node deploy/tests/home-time-use.test.mjs
 *
 * 正本の受入条件に対応:
 *   ② 給湯・蓄電池の余剰二重計上なし
 *   ⑥ 未入力時に削減額・回収年数非表示
 *   （加えて）便益0以下は回収年数を算出しない
 * ========================================================================== */
import {
  allocateSurplus, annualNetBenefit, paybackYears, formatAmountOrBlank,
} from '../../sotsu-fit/assets/home-time-use.js';

let pass = 0, fail = 0;
const approx = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
function ok(name, cond) {
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name); }
}

/* ---- 1. 二重計上なし：給湯割当後の残余だけが蓄電へ。合計は余剰を超えない ---- */
{
  // 発電6, 負荷1 → 余剰5。給湯に移せる3 → 給湯3, 残2 → 蓄電(空き十分)2, 逃げ0
  const r = allocateSurplus([{ generation: 6, load: 1, waterHeatingNeed: 3 }]);
  ok('余剰 = max(発電-負荷,0) = 5', approx(r.totals.surplus, 5));
  ok('給湯割当 = 3', approx(r.totals.toWaterHeating, 3));
  ok('蓄電は残余2のみ（二重計上なし）', approx(r.totals.toBattery, 2));
  ok('給湯+蓄電 <= 余剰（同一kWhを二重計上しない）',
     r.totals.toWaterHeating + r.totals.toBattery <= r.totals.surplus + 1e-9);
}

/* ---- 2. 給湯が余剰を使い切れば蓄電はゼロ（取り合いにならない） ---- */
{
  const r = allocateSurplus([{ generation: 4, load: 1, waterHeatingNeed: 10, batteryRoom: 10 }]);
  ok('給湯は余剰3まで（移せる負荷が多くても余剰で頭打ち）', approx(r.totals.toWaterHeating, 3));
  ok('残余0なので蓄電0', approx(r.totals.toBattery, 0));
}

/* ---- 3. 蓄電の空き容量で頭打ち、残りは spill（二重計上せず逃がす） ---- */
{
  const r = allocateSurplus([{ generation: 5, load: 0, waterHeatingNeed: 0, batteryRoom: 2 }]);
  ok('給湯0', approx(r.totals.toWaterHeating, 0));
  ok('蓄電は空き2まで', approx(r.totals.toBattery, 2));
  ok('余り3はspill', approx(r.totals.spilled, 3));
  ok('配分合計 = 余剰（保存則）',
     approx(r.totals.toWaterHeating + r.totals.toBattery + r.totals.spilled, r.totals.surplus));
}

/* ---- 4. 負荷が発電を上回る時間帯は余剰0（マイナスにしない） ---- */
{
  const r = allocateSurplus([{ generation: 1, load: 4, waterHeatingNeed: 2, batteryRoom: 2 }]);
  ok('夜・曇り等は余剰0', approx(r.totals.surplus, 0));
  ok('余剰0なら給湯も蓄電も0', r.totals.toWaterHeating === 0 && r.totals.toBattery === 0);
}

/* ---- 5. ランダム不変条件：どんな入力でも二重計上は起きない ---- */
{
  let invariantHeld = true;
  const rnd = (seed => () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff)(42);
  for (let trial = 0; trial < 2000; trial++) {
    const n = 1 + Math.floor(rnd() * 24);
    const slots = Array.from({ length: n }, () => ({
      generation: rnd() * 10,
      load: rnd() * 10,
      waterHeatingNeed: rnd() * 8,
      batteryRoom: rnd() * 8,
    }));
    const r = allocateSurplus(slots);
    for (let i = 0; i < n; i++) {
      const p = r.perSlot[i];
      // 給湯+蓄電は時間帯ごとの余剰を超えない（= 同じkWhを二重に使わない）
      if (p.toWaterHeating + p.toBattery > p.surplus + 1e-9) invariantHeld = false;
      // 各配分は非負
      if (p.toWaterHeating < -1e-9 || p.toBattery < -1e-9 || p.spilled < -1e-9) invariantHeld = false;
      // 保存則
      if (!approx(p.toWaterHeating + p.toBattery + p.spilled, p.surplus, 1e-6)) invariantHeld = false;
    }
  }
  ok('2000ケースで二重計上・符号・保存則の不変条件を満たす', invariantHeld);
}

/* ---- 6. 未入力時は金額・回収年数を表示しない ---- */
{
  ok('確認済み便益が未入力 → 年間正味便益は null',
     annualNetBenefit({ confirmedBenefit: null, addedCost: 1000 }) === null);
  ok('追加コスト未入力 → 年間正味便益は null',
     annualNetBenefit({ confirmedBenefit: 50000, addedCost: null }) === null);
  ok('便益が入れば差引して算出', annualNetBenefit({ confirmedBenefit: 50000, addedCost: 8000 }) === 42000);

  ok('便益0以下 → 回収年数は算出しない(null)',
     paybackYears({ initialCostNoSubsidy: 500000, netBenefit: 0 }) === null &&
     paybackYears({ initialCostNoSubsidy: 500000, netBenefit: -1 }) === null);
  ok('便益>0 → 回収年数を算出', approx(paybackYears({ initialCostNoSubsidy: 420000, netBenefit: 42000 }), 10));

  ok('金額: 未確認は空欄', formatAmountOrBlank(null) === '' && formatAmountOrBlank(NaN) === '' && formatAmountOrBlank(undefined) === '');
  ok('金額: 確認済みは整形', formatAmountOrBlank(42000) === '42,000円');
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
