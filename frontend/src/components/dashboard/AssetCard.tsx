"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatPrice, formatPercent, scoreBg } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus, ChevronRight } from "lucide-react";
import Link from "next/link";
import type { BriefAsset } from "@/lib/api";

const assetName: Record<string, string> = {
  XAUUSD: "Or / USD",
  EURUSD: "Euro / USD",
  BTCUSD: "Bitcoin / USD",
  AAPL: "Apple Inc.",
  SPY: "S&P 500 ETF",
  "CL=F": "Pétrole Brut",
};

function DirectionIcon({ bias }: { bias: string }) {
  if (bias === "buy") return <TrendingUp className="h-4 w-4 text-emerald-400" />;
  if (bias === "sell") return <TrendingDown className="h-4 w-4 text-red-400" />;
  return <Minus className="h-4 w-4 text-yellow-400" />;
}

export default function AssetCard({ asset }: { asset: BriefAsset }) {
  const { value: score, label, action_bias } = asset.score;

  return (
    <Link href={`/assets/${asset.symbol}`}>
      <Card className="transition-colors hover:border-zinc-700 cursor-pointer">
        <CardContent className="pt-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-lg font-bold text-zinc-100">{asset.symbol}</p>
              <p className="text-xs text-zinc-500">
                {assetName[asset.symbol] || asset.symbol}
              </p>
            </div>
            <DirectionIcon bias={action_bias} />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xl font-mono font-semibold text-zinc-100">
              ${formatPrice(asset.price)}
            </span>
            <div className="flex items-center gap-2">
              <span
                className={`inline-flex items-center rounded-md border px-2 py-0.5 text-sm font-bold ${scoreBg(
                  score
                )}`}
              >
                {score}
              </span>
              <Badge
                variant={
                  action_bias === "buy"
                    ? "buy"
                    : action_bias === "sell"
                    ? "sell"
                    : "neutral"
                }
              >
                {label}
              </Badge>
            </div>
          </div>
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-800">
            <span className="text-xs text-zinc-500">
              {asset.scenario_count > 0
                ? `${asset.scenario_count} scénario${asset.scenario_count > 1 ? "s" : ""}`
                : "Aucun scénario"}
            </span>
            <ChevronRight className="h-4 w-4 text-zinc-600" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
