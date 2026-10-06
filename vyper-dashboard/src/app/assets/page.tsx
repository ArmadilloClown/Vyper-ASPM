/*
 * Vyper ASPM
 *
 * Copyright (C) 2026 Pedro
 *
 * This file is part of Vyper ASPM.
 *
 * Vyper ASPM is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Vyper ASPM is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Vyper ASPM. If not, see <https://www.gnu.org/licenses/>.
 */

"use client";

import { useEffect, useMemo, useState } from "react";
import { getAssets } from "@/services/api";
import {
    Boxes,
    Globe,
    Container,
    GitBranch,
    KeyRound,
    ShieldAlert,
} from "lucide-react";

interface Asset {
    type: string;
    total: number;
}

const assetInfo: Record<
    string,
    {
        label: string;
        description: string;
        icon: React.ElementType;
    }
> = {
    url: {
        label: "Web URLs",
        description:
            "URLs descobertas durante a análise dos repositórios.",
        icon: Globe,
    },
    docker: {
        label: "Docker",
        description:
            "Imagens e configurações Docker identificadas.",
        icon: Container,
    },
    pipeline: {
        label: "CI/CD Pipelines",
        description:
            "Pipelines de integração e entrega contínua.",
        icon: GitBranch,
    },
    secret: {
        label: "Secrets",
        description:
            "Possíveis secrets encontrados durante a descoberta.",
        icon: KeyRound,
    },
};

function getAssetInfo(type: string) {
    return (
        assetInfo[type.toLowerCase()] || {
            label: type,
            description: "Asset descoberto pelo Vyper.",
            icon: Boxes,
        }
    );
}

function formatNumber(value: number) {
    return new Intl.NumberFormat("pt-BR").format(value);
}

export default function AssetsPage() {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadAssets() {
            try {
                setLoading(true);
                setError("");

                const data = await getAssets();

                setAssets(Array.isArray(data) ? data : []);
            } catch (err) {
                console.error(err);
                setError(
                    "Não foi possível carregar a superfície de ataque."
                );
            } finally {
                setLoading(false);
            }
        }

        loadAssets();
    }, []);

    const totalAssets = useMemo(
        () =>
            assets.reduce(
                (total, asset) =>
                    total + (asset.total || 0),
                0
            ),
        [assets]
    );

    const largestAsset = useMemo(() => {
        if (!assets.length) return null;

        return [...assets].sort(
            (a, b) => b.total - a.total
        )[0];
    }, [assets]);

    return (
        <main className="min-h-screen bg-[#001017] px-6 py-8 text-white md:px-8">
            <div className="mx-auto max-w-[1800px] space-y-6">

                {/* HEADER */}

                <header>
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10">
                            <ShieldAlert
                                size={20}
                                className="text-cyan-300"
                            />
                        </div>

                        <div>
                            <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                                External attack surface
                            </p>

                            <h1 className="mt-1 text-[2.6rem] leading-none font-semibold">
                                Attack Surface
                            </h1>
                        </div>
                    </div>

                    <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
                        Visibilidade dos ativos descobertos pelo
                        Vyper durante as análises de segurança.
                    </p>
                </header>

                {/* ERROR */}

                {error && (
                    <div className="rounded-[14px] border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-300">
                        {error}
                    </div>
                )}

                {/* SUMMARY */}

                <section className="grid grid-cols-1 gap-4 md:grid-cols-3">

                    <SummaryCard
                        label="Total assets"
                        value={
                            loading
                                ? "—"
                                : formatNumber(totalAssets)
                        }
                        description="Assets descobertos"
                    />

                    <SummaryCard
                        label="Asset types"
                        value={
                            loading
                                ? "—"
                                : formatNumber(assets.length)
                        }
                        description="Categorias identificadas"
                    />

                    <SummaryCard
                        label="Largest surface"
                        value={
                            loading
                                ? "—"
                                : largestAsset
                                    ? formatNumber(
                                          largestAsset.total
                                      )
                                    : "0"
                        }
                        description={
                            largestAsset
                                ? getAssetInfo(
                                      largestAsset.type
                                  ).label
                                : "Nenhum asset encontrado"
                        }
                    />

                </section>

                {/* ASSETS */}

                <section className="rounded-[14px] border border-white/10 bg-white/[0.03] p-5 md:p-6">

                    <div className="mb-6 flex items-start justify-between gap-4">
                        <div>
                            <h2 className="text-lg font-semibold">
                                Discovered Assets
                            </h2>

                            <p className="mt-1 text-sm leading-6 text-slate-400">
                                Inventário da superfície de ataque
                                identificada pelo Vyper.
                            </p>
                        </div>

                        <div className="hidden rounded-xl border border-white/10 bg-white/[0.03] p-2.5 sm:block">
                            <Boxes
                                size={20}
                                className="text-slate-400"
                            />
                        </div>
                    </div>

                    {loading ? (
                        <div className="flex min-h-[220px] items-center justify-center">
                            <div className="text-center">
                                <div className="mx-auto mb-3 h-6 w-6 animate-spin rounded-full border-2 border-white/10 border-t-cyan-400" />

                                <p className="text-sm text-slate-500">
                                    Carregando assets...
                                </p>
                            </div>
                        </div>
                    ) : assets.length === 0 ? (
                        <div className="flex min-h-[220px] flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-black/10 px-6 text-center">
                            <Boxes
                                size={30}
                                className="mb-3 text-slate-600"
                            />

                            <p className="text-sm font-medium text-slate-400">
                                Nenhum asset encontrado
                            </p>

                            <p className="mt-1 max-w-md text-xs leading-5 text-slate-600">
                                Execute uma análise para que o
                                Vyper possa descobrir ativos e
                                ampliar a visibilidade da superfície
                                de ataque.
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">

                            {assets.map((asset) => {
                                const info = getAssetInfo(
                                    asset.type
                                );

                                const Icon = info.icon;

                                const percentage =
                                    totalAssets > 0
                                        ? (asset.total /
                                              totalAssets) *
                                          100
                                        : 0;

                                return (
                                    <div
                                        key={asset.type}
                                        className="rounded-[14px] border border-white/10 bg-black/10 p-5 transition-colors hover:border-white/20 hover:bg-white/[0.025]"
                                    >
                                        <div className="flex items-start justify-between gap-5">

                                            <div className="flex min-w-0 items-start gap-4">

                                                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-cyan-400/15 bg-cyan-400/10">
                                                    <Icon
                                                        size={19}
                                                        className="text-cyan-300"
                                                    />
                                                </div>

                                                <div className="min-w-0">
                                                    <p className="text-sm font-semibold text-white">
                                                        {info.label}
                                                    </p>

                                                    <p className="mt-1 text-xs leading-5 text-slate-500">
                                                        {info.description}
                                                    </p>
                                                </div>

                                            </div>

                                            <div className="shrink-0 text-right">
                                                <p className="text-2xl font-semibold tracking-tight">
                                                    {formatNumber(
                                                        asset.total
                                                    )}
                                                </p>

                                                <p className="mt-1 text-[11px] text-slate-500">
                                                    {percentage.toFixed(
                                                        1
                                                    )}
                                                    %
                                                </p>
                                            </div>

                                        </div>

                                        <div className="mt-5">
                                            <div className="mb-2 flex items-center justify-between">
                                                <span className="text-[11px] uppercase tracking-wider text-slate-600">
                                                    Surface share
                                                </span>

                                                <span className="text-[11px] text-slate-500">
                                                    {percentage.toFixed(
                                                        1
                                                    )}
                                                    %
                                                </span>
                                            </div>

                                            <div className="h-2 overflow-hidden rounded-full bg-white/5">
                                                <div
                                                    className="h-full rounded-full bg-cyan-400/70 transition-all"
                                                    style={{
                                                        width: `${Math.min(
                                                            percentage,
                                                            100
                                                        )}%`,
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}

                        </div>
                    )}

                </section>

                {/* VISIBILITY */}

                <section className="rounded-[14px] border border-white/10 bg-white/[0.02] p-5">
                    <div className="flex items-start gap-3">
                        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-400/10">
                            <ShieldAlert
                                size={16}
                                className="text-cyan-300"
                            />
                        </div>

                        <div>
                            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                                Visibility
                            </p>

                            <p className="mt-2 text-sm leading-6 text-slate-400">
                                A superfície de ataque representa os
                                ativos que podem ampliar a exposição
                                de uma aplicação. O Vyper utiliza
                                esses dados como contexto adicional
                                para priorização de riscos e análise
                                de segurança.
                            </p>
                        </div>
                    </div>
                </section>

            </div>
        </main>
    );
}

function SummaryCard({
    label,
    value,
    description,
}: {
    label: string;
    value: string;
    description: string;
}) {
    return (
        <div className="rounded-[14px] border border-white/10 bg-white/[0.03] p-5">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                {label}
            </p>

            <p className="mt-3 text-3xl font-semibold tracking-tight">
                {value}
            </p>

            <p className="mt-1 text-xs text-slate-500">
                {description}
            </p>
        </div>
    );
}