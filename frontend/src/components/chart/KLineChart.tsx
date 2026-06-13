"use client";

import { useEffect, useRef, useMemo } from "react";
import { init, dispose } from "klinecharts";
import type { Chart, KLineData, DataLoader, PeriodType } from "klinecharts";
import type { Candle } from "@/lib/api";

interface KLineChartProps {
  candles: Candle[];
  height?: number;
}

/** Count decimal places of a finite number */
function decimals(v: number): number {
  if (!isFinite(v)) return 0;
  const s = String(v);
  const dot = s.indexOf(".");
  return dot >= 0 ? s.length - dot - 1 : 0;
}

/**
 * Guess candle period from the first two timestamps.
 * Falls back to 1h when we can't infer.
 */
function guessPeriod(candles: Candle[]): { type: PeriodType; span: number } {
  if (candles.length < 2) return { type: "hour", span: 1 };
  const diff = Math.abs(Number(candles[1]!.timestamp) - Number(candles[0]!.timestamp));
  const sec = Math.round(diff);
  if (sec < 90) return { type: "minute", span: 1 };
  if (sec < 3600) return { type: "minute", span: Math.max(1, Math.round(sec / 60)) };
  if (sec < 86400) return { type: "hour", span: Math.max(1, Math.round(sec / 3600)) };
  if (sec < 604800) return { type: "day", span: Math.max(1, Math.round(sec / 86400)) };
  return { type: "week", span: Math.max(1, Math.round(sec / 604800)) };
}

export default function KLineChart({ candles, height = 500 }: KLineChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<Chart | null>(null);
  /** Mutable ref so the DataLoader closure always sees the latest data. */
  const dataRef = useRef<KLineData[]>([]);

  // Convert API Candle[] → klinecharts KLineData[]
  const klineData = useMemo<KLineData[]>(
    () =>
      candles.map((c) => ({
        timestamp: new Date(c.timestamp).getTime(),
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
        volume: c.volume,
      })),
    [candles],
  );

  // Keep the ref in sync
  dataRef.current = klineData;

  // Derive price & volume precision from the first candle
  const precision = useMemo(() => {
    if (klineData.length === 0) return { price: 2 as number, volume: 0 as number };
    const d = klineData[0]!;
    return {
      price: Math.max(
        decimals(d.open),
        decimals(d.high),
        decimals(d.low),
        decimals(d.close),
      ),
      volume: decimals(d.volume ?? 0),
    };
  }, [klineData]);

  // ── Mount chart instance once ──────────────────────────────────
  useEffect(() => {
    const container = containerRef.current;
    if (!container || chartRef.current) return;

    const chart = init(container, {
      styles: {
        grid: {
          show: true,
          horizontal: { color: "#27272a", size: 1 },
          vertical: { color: "#27272a", size: 1 },
        },
        candle: {
          bar: {
            upColor: "#22c55e",
            downColor: "#ef4444",
            noChangeColor: "#a1a1aa",
            upBorderColor: "#22c55e",
            downBorderColor: "#ef4444",
            upWickColor: "#22c55e",
            downWickColor: "#ef4444",
          },
          priceMark: {
            show: true,
            last: {
              show: true,
              upColor: "#22c55e",
              downColor: "#ef4444",
              noChangeColor: "#a1a1aa",
              line: { show: true, size: 1, dashedValue: [2, 2] },
              text: { show: true, color: "#a1a1aa", size: 10 },
            },
          },
          tooltip: {
            showRule: "always",
            showType: "standard",
          },
        },
        xAxis: {
          show: true,
          axisLine: { show: true, color: "#3f3f46", size: 1 },
          tickLine: { show: true, color: "#3f3f46", size: 1 },
          tickText: { show: true, color: "#a1a1aa", size: 10 },
        },
        yAxis: {
          show: true,
          axisLine: { show: true, color: "#3f3f46", size: 1 },
          tickLine: { show: true, color: "#3f3f46", size: 1 },
          tickText: { show: true, color: "#a1a1aa", size: 10 },
        },
        separator: { size: 1, color: "#3f3f46", fill: true },
        crosshair: {
          show: true,
          horizontal: {
            line: { color: "#52525b", size: 1 },
            text: { show: true, color: "#a1a1aa", size: 10 },
          },
          vertical: {
            line: { color: "#52525b", size: 1 },
            text: { show: true, color: "#a1a1aa", size: 10 },
          },
        },
      },
    });
    if (!chart) return;

    chartRef.current = chart;

    // ── Symbol metadata ────────────────────────────────────────
    chart.setSymbol({
      ticker: "",
      pricePrecision: precision.price,
      volumePrecision: precision.volume,
    });

    // ── Period from data ───────────────────────────────────────
    chart.setPeriod(guessPeriod(candles));

    // ── MA overlay on candle pane ──────────────────────────────
    // isStack: false → overlay on the existing candle pane
    chart.createIndicator(
      { name: "MA", calcParams: [20, 50, 200] },
      { isStack: false },
    );

    // ── Volume pane below ──────────────────────────────────────
    // isStack: true → create a new separate pane
    chart.createIndicator("VOLUME", { isStack: true });

    // ── DataLoader (v10 replaces applyNewData / updateData) ────
    const dataLoader: DataLoader = {
      getBars({ type, callback }) {
        // 'init' → provide all data we have
        // 'forward' / 'backward' / 'update' → no additional data available
        if (type === "init") {
          callback(dataRef.current, { forward: false, backward: false });
        } else {
          callback([], { forward: false, backward: false });
        }
      },
    };
    chart.setDataLoader(dataLoader);

    // ── Auto-resize ────────────────────────────────────────────
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(container);

    return () => {
      observer.disconnect();
      dispose(container);
      chartRef.current = null;
    };
    // Run once on mount — data reactivity is handled by resetData below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Reactively replace data when candles prop changes ─────────
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    // resetData triggers a re-init via the DataLoader getBars('init'),
    // which picks up the latest dataRef.current.
    chart.resetData();
  }, [klineData]);

  return (
    <div
      ref={containerRef}
      className="bg-zinc-950 rounded-lg"
      style={{ height: `${height}px`, width: "100%" }}
    />
  );
}
