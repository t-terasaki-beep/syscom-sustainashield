/* =============================================================================
 * 家で使う時間診断 — 余剰電力の時間帯別配分（二重計上防止）リファレンス実装
 *
 * 正本：Notion「2026-10-02 完成施策A｜卒FIT住宅『家で使う時間』診断」
 *   ・時間帯tごとに「余剰候補 = max(発電 − 既存負荷, 0)」を求める
 *   ・給湯へ割り当てた分を差し引いた後だけ蓄電候補へ回す
 *   ・同じkWhを給湯効果と蓄電効果へ二重計上しない
 *   ・便益0以下は回収年数を算出しない／未確認値は空欄（非表示）
 *
 * 本モジュールは端末内処理のみを想定し、入力値を外部送信しない（PII非送信）。
 * 数値はすべて利用者入力の確認済み値に依存する。未確認・未入力は null を返す。
 * ========================================================================== */

/**
 * 時間帯別の余剰電力を「給湯 → 蓄電」の順に、重複なく配分する。
 * @param {Array<{generation:number, load:number, waterHeatingNeed?:number, batteryRoom?:number}>} slots
 *   generation: 発電kWh / load: 既存負荷kWh / waterHeatingNeed: 給湯に移せる負荷kWh（任意）
 *   batteryRoom: その時間帯に充電できる空きkWh（任意, 省略時は無制限）
 * @returns {{perSlot:Array, totals:{surplus:number, toWaterHeating:number, toBattery:number, spilled:number}}}
 */
export function allocateSurplus(slots) {
  if (!Array.isArray(slots)) throw new TypeError('slots must be an array');
  const perSlot = [];
  const totals = { surplus: 0, toWaterHeating: 0, toBattery: 0, spilled: 0 };

  for (let i = 0; i < slots.length; i++) {
    const s = slots[i] || {};
    const gen = num(s.generation);
    const load = num(s.load);
    // 余剰候補 = max(発電 − 既存負荷, 0)
    const surplus = Math.max(gen - load, 0);

    // 給湯へ先に割り当て（移せる負荷の範囲、かつ余剰の範囲）
    const whNeed = s.waterHeatingNeed == null ? 0 : Math.max(num(s.waterHeatingNeed), 0);
    const toWaterHeating = Math.min(whNeed, surplus);

    // 残余（= 給湯割当を差し引いた後）だけが蓄電候補
    const remainingAfterWater = surplus - toWaterHeating;
    const room = s.batteryRoom == null ? Infinity : Math.max(num(s.batteryRoom), 0);
    const toBattery = Math.min(room, remainingAfterWater);

    // どこにも使われず逃げた余剰
    const spilled = remainingAfterWater - toBattery;

    perSlot.push({ surplus, toWaterHeating, toBattery, spilled });
    totals.surplus += surplus;
    totals.toWaterHeating += toWaterHeating;
    totals.toBattery += toBattery;
    totals.spilled += spilled;
  }
  return { perSlot, totals };
}

/**
 * 年間正味便益 = 確認済み便益 − 追加コスト。確認済み便益が未入力なら null（算出しない）。
 * @param {{confirmedBenefit:?number, addedCost:?number}} p
 * @returns {?number}
 */
export function annualNetBenefit({ confirmedBenefit, addedCost } = {}) {
  if (confirmedBenefit == null || addedCost == null) return null; // 未確認は空欄
  return num(confirmedBenefit) - num(addedCost);
}

/**
 * 回収年数 = 補助なし初期費用 ÷ 年間正味便益。
 * 便益0以下、または費用/便益が未入力なら null（表示しない）。
 * @returns {?number}
 */
export function paybackYears({ initialCostNoSubsidy, netBenefit } = {}) {
  if (initialCostNoSubsidy == null || netBenefit == null) return null;
  const b = num(netBenefit);
  if (b <= 0) return null; // 便益0以下は算出しない
  return num(initialCostNoSubsidy) / b;
}

/** 金額表示：確認済みの数値のみ文字列化。未確認(null/undefined/NaN)は空欄。 */
export function formatAmountOrBlank(v) {
  if (v == null || Number.isNaN(Number(v))) return '';
  return Math.round(Number(v)).toLocaleString('ja-JP') + '円';
}

function num(v) {
  const n = Number(v);
  if (Number.isNaN(n)) throw new TypeError('expected a number, got ' + JSON.stringify(v));
  return n;
}
