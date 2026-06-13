"use client";

import { useEffect, useState } from "react";
import AssetCard from "@/components/dashboard/AssetCard";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { getBrief, type BriefResponse } from "@/lib/api";
import { BarChart3, RefreshCw } from "lucide-react";

export default function Dashboard() {
  const [brief, setBrief] = useState<BriefResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await getBrief("4h");
      setBrief(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">
            Cockpit d&apos;Analyse
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            Vue d&apos;ensemble des marchés
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-300 transition-colors hover:bg-zinc-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Actualiser
        </button>
      </div>

      {error && (
        <Card className="border-red-500/30 bg-red-500/10">
          <CardContent className="pt-5">
            <p className="text-sm text-red-400">
              ⚠ Erreur API : {error}
              <br />
              <span className="text-zinc-500">
                Assurez-vous que le backend tourne sur{" "}
                <code className="text-zinc-300">localhost:8000</code>
              </span>
            </p>
          </CardContent>
        </Card>
      )}

      {loading && !brief ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-5">
                <div className="animate-pulse space-y-3">
                  <div className="h-5 w-24 bg-zinc-800 rounded" />
                  <div className="h-8 w-28 bg-zinc-800 rounded" />
                  <div className="h-4 w-16 bg-zinc-800 rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : brief ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {brief.assets.map((asset) => (
              <AssetCard key={asset.symbol} asset={asset} />
            ))}
          </div>
          <p className="text-xs text-zinc-600 text-center">
            {brief.asset_count} actifs suivis — données en {brief.timeframe}
          </p>
        </>
      ) : null}
    </div>
  );
}
