"use client";

import { useEffect, useRef } from "react";

/**
 * マウント直後に1回、その後 intervalMs ごとに callback を実行する。前回の実行中は重ねない。
 *
 * @param callback - 定期実行する非同期処理。
 * @param intervalMs - 実行間隔（ミリ秒）。
 */
export function usePolling(callback: () => Promise<void>, intervalMs: number): void {
  const callbackRef = useRef(callback);

  // 最新の callback の保持（タイマーを張り直さないため）
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // タイマーの開始と、アンマウント時の停止
  useEffect(() => {
    let running = false;
    const tick = async () => {
      if (running) return;
      running = true;
      try {
        await callbackRef.current();
      } catch {
        // 一時的な失敗は無視し、次回の実行で回復
      } finally {
        running = false;
      }
    };
    void tick();
    const timerId = setInterval(tick, intervalMs);
    return () => clearInterval(timerId);
  }, [intervalMs]);
}
