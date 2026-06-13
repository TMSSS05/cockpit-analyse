"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import KLineChart from "@/components/chart/KLineChart";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatPrice, scoreColor, scoreBg } from "@/lib/utils";
import {
  getCandles,
  getAnalysis,
  getLevels,
  type CandlesResponse,
  type AnalysisResponse,
  type LevelsResponse,
} from "@/lib/api";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
} from "lucide-react";

export default function AssetDetail() {
  const params = useParams();
  const symbol = params.symbol as string;

  const [candles, setCandles] = useState<CandlesResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [levels, setLevels] = useState<LevelsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState("1h");
  const [error, setError] = useState<string | null>(null);

  async function load(tf: string) {
    setLoading(true);
    setError(null);
    try {
      const [c, a, l] = await Promise.all([
        getCandles(symbol, tf, 200),
        getAnalysis(symbol, tf),
        getLevels(symbol, "4h"),
      ]);
      setCandles(c);
      setAnalysis(a);
      setLevels(l);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(timeframe);
  }, [symbol, timeframe]);

  const tfOptions = ["1h", "4h", "1d", "1w"];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Link
          href="/"
          className="flex items-center gap-1 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-300 transition-colors hover:bg-zinc-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">{symbol}</h1>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <div className="flex rounded-lg border border-zinc-700 overflow-hidden">
            {tfOptions.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                  timeframe === tf
                    ? "bg-zinc-700 text-zinc-100"
                    : "bg-zinc-800 text-zinc-500 hover:bg-zinc-700"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
          <button
            onClick={() => load(timeframe)}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 transition-colors hover:bg-zinc-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {error && (
        <Card className="border-red-500/30 bg-red-500/10">
          <CardContent className="pt-5">
            <p className="text-sm text-red-400">⚠ {error}</p>
          </CardContent>
        </Card>
      )}

      {analysis && (
        <div className="flex items-center gap-6">
          <div>
            <p className="text-xs text-zinc-500 uppercase tracking-wider">
              Prix
            </p>
            <p className="text-3xl font-mono font-bold text-zinc-100">
              ${formatPrice(analysis.price)}
            </p>
          </div>
          <div>
            <p className="text-xs text-zinc-500 uppercase tracking-wider">
              Score
            </p>
            <div className="flex items-center gap-2 mt-1">
              <span
                className={`text-2xl font-bold ${scoreColor(analysis.score.value)}`}
              >
                {analysis.score.value}
              </span>
              <Badge
                variant={
                  analysis.score.action_bias === "buy"
                    ? analysis.score.value >= 70
                      ? "strong_buy"
                      : "buy"
                    : analysis.score.action_bias === "sell"
                    ? analysis.score.value <= -70
                      ? "strong_sell"
                      : "sell"
                    : "neutral"
                }
              >
                {analysis.score.label}
              </Badge>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {analysis.score.action_bias === "buy" ? (
              <TrendingUp className="h-5 w-5 text-emerald-400" />
            ) : analysis.score.action_bias === "sell" ? (
              <TrendingDown className="h-5 w-5 text-red-400" />
            ) : (
              <Minus className="h-5 w-5 text-yellow-400" />
            )}
            <span className="text-sm text-zinc-400">
              {analysis.score.action_bias.toUpperCase()}
            </span>
          </div>
        </div>
      )}

      {candles && (
        <KLineChart candles={candles.candles} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {analysis && (
          <Card>
            <CardHeader>
              <CardTitle>Indicateurs</CardTitle>
            </CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <tbody>
                  {[
                    { label: "RSI", value: analysis.indicators.rsi.toFixed(1) },
                    { label: "ADX", value: analysis.indicators.adx.toFixed(1) },
                    { label: "ATR", value: analysis.indicators.atr.toFixed(2) },
                    {
                      label: "MACD",
                      value: analysis.indicators.macd_line.toFixed(2),
                    },
                    {
                      label: "Signal",
                      value: analysis.indicators.macd_signal.toFixed(2),
                    },
                    {
                      label: "EMA 20",
                      value: analysis.indicators.ema_20.toFixed(2),
                    },
                    {
                      label: "EMA 50",
                      value: analysis.indicators.ema_50.toFixed(2),
                    },
                    {
                      label: "EMA 200",
                      value: analysis.indicators.ema_200.toFixed(2),
                    },
                  ].map(({ label, value }) => (
                    <tr key={label} className="border-b border-zinc-800 last:border-0">
                      <td className="py-2 text-zinc-400">{label}</td>
                      <td className="py-2 text-right font-mono text-zinc-200">
                        {value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        )}

        {analysis && (
          <Card>
            <CardHeader>
              <CardTitle>Structure</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { label: "Tendance", value: analysis.structure.trend },
                  { label: "Momentum", value: analysis.structure.momentum },
                  {
                    label: "Volatilité",
                    value: analysis.structure.volatility,
                  },
                  {
                    label: "Consolidation",
                    value: analysis.structure.consolidation
                      ? "Oui"
                      : "Non",
                  },
                  {
                    label: "Breakout",
                    value: analysis.structure.breakout ? "Oui" : "Non",
                  },
                  {
                    label: "Sweep",
                    value: analysis.structure.sweep ? "Oui" : "Non",
                  },
                ].map(({ label, value }) => (
                  <div
                    key={label}
                    className="flex items-center justify-between border-b border-zinc-800 pb-2 last:border-0"
                  >
                    <span className="text-sm text-zinc-400">{label}</span>
                    <span className="text-sm font-medium text-zinc-200">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {analysis && (
          <Card>
            <CardHeader>
              <CardTitle>Scénarios</CardTitle>
            </CardHeader>
            <CardContent>
              {analysis.scenarios.length > 0 ? (
                <div className="space-y-3">
                  {analysis.scenarios.map((s, i) => (
                    <div
                      key={i}
                      className={`rounded-lg border p-3 ${
                        s.direction === "up"
                          ? "border-emerald-500/20 bg-emerald-500/5"
                          : s.direction === "down"
                          ? "border-red-500/20 bg-red-500/5"
                          : "border-zinc-700 bg-zinc-800/50"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold text-zinc-200">
                          {s.title}
                        </span>
                        <Badge
                          variant={
                            s.direction === "up"
                              ? "buy"
                              : s.direction === "down"
                              ? "sell"
                              : "neutral"
                          }
                        >
                          {s.probability}%
                        </Badge>
                      </div>
                      <p className="text-xs text-zinc-400">{s.description}</p>
                      {s.target && (
                        <p className="text-xs text-zinc-500 mt-1">
                          Cible: ${formatPrice(s.target)}
                          {s.invalidation &&
                            ` · Invalidation: $${formatPrice(s.invalidation)}`}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-zinc-500">Aucun scénario</p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {levels && levels.levels.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Niveaux ({levels.timeframe})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
              {levels.levels.map((l, i) => (
                <div
                  key={i}
                  className={`rounded-lg border p-2 text-center ${
                    l.type === "resistance"
                      ? "border-red-500/20 bg-red-500/5"
                      : l.type === "support"
                      ? "border-emerald-500/20 bg-emerald-500/5"
                      : "border-zinc-700 bg-zinc-800/50"
                  }`}
                >
                  <p className="text-xs text-zinc-500 uppercase mb-1">
                    {l.type}
                  </p>
                  <p className="text-sm font-mono font-semibold text-zinc-200">
                    ${formatPrice(l.price)}
                  </p>
                  {l.importance && (
                    <Badge variant="info" className="mt-1">
                      {l.importance}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
