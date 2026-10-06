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

import {
    analyzeRisk,
    getRisks,
    getRiskAnalysis,
    getSecurityScore,
} from "@/services/api";

import SecurityScore from "@/components/SecurityScore";

interface Risk {
    id: number;
    title: string;
    severity: string;
    score: number;
    priority: string;
    status: string;
    evidence_count: number;
}

interface AIAnalysis {
    id: number;
    risk_id: number;
    summary: string;
    impact: string;
    remediation: string;
    created_at?: string;
}

const severityLevels = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "WARNING",
    "LOW",
    "INFO",
];

function severityLabel(severity: string) {
    const labels: Record<string, string> = {
        CRITICAL: "Critical",
        HIGH: "High",
        MEDIUM: "Medium",
        WARNING: "Warning",
        LOW: "Low",
        INFO: "Info",
        ERROR: "Critical",
    };

    return labels[severity] || severity;
}

function severityRank(severity: string) {
    const normalized =
        severity === "ERROR" ? "CRITICAL" : severity;

    const ranks: Record<string, number> = {
        INFO: 1,
        LOW: 2,
        WARNING: 3,
        MEDIUM: 4,
        HIGH: 5,
        CRITICAL: 6,
    };

    return ranks[normalized] || 0;
}

function cellClass(
    severity: string,
    evidence: number
) {
    const rank = severityRank(severity);

    if (rank >= 5 && evidence >= 10) {
        return "border-red-500/40 bg-red-500/20";
    }

    if (rank >= 5) {
        return "border-red-500/25 bg-red-500/10";
    }

    if (rank >= 4 && evidence >= 10) {
        return "border-orange-500/40 bg-orange-500/15";
    }

    if (rank >= 3 && evidence >= 5) {
        return "border-yellow-500/30 bg-yellow-500/10";
    }

    if (rank >= 2) {
        return "border-emerald-500/20 bg-emerald-500/5";
    }

    return "border-white/5 bg-white/[0.02]";
}

export default function RisksPage() {
    const [risks, setRisks] = useState<Risk[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [aiLoading, setAiLoading] =
        useState<number | null>(null);

    const [aiAnalysis, setAiAnalysis] =
        useState<AIAnalysis | null>(null);

    const [aiError, setAiError] =
        useState<string | null>(null);

    const [securityScore, setSecurityScore] =
        useState<any>(null);

    async function handleAIAnalysis(
        riskId: number
    ) {
        try {
            setAiLoading(riskId);
            setAiError(null);
            setAiAnalysis(null);

            const existing =
                await getRiskAnalysis(riskId);

            if ("id" in existing) {
                setAiAnalysis(existing);
                return;
            }

            const analysis =
                await analyzeRisk(riskId);

            setAiAnalysis(analysis);
        } catch (err) {
            console.error(
                "Erro na análise da IA:",
                err
            );

            setAiError(
                "Não foi possível gerar a análise da IA."
            );
        } finally {
            setAiLoading(null);
        }
    }

    useEffect(() => {
        async function loadRisks() {
            try {
                setLoading(true);
                setError("");

                const [
                    risksData,
                    scoreData,
                ] = await Promise.all([
                    getRisks(),
                    getSecurityScore(),
                ]);

                setRisks(risksData);
                setSecurityScore(scoreData);
            } catch (err) {
                console.error(err);

                setError(
                    "Não foi possível carregar os riscos."
                );
            } finally {
                setLoading(false);
            }
        }

        loadRisks();
    }, []);

    const activeRisks = useMemo(
        () =>
            risks.filter(
                (risk) =>
                    risk.status !== "fixed"
            ),
        [risks]
    );

    const criticalRisks = useMemo(
        () =>
            activeRisks.filter(
                (risk) =>
                    risk.severity === "CRITICAL" ||
                    risk.severity === "ERROR"
            ).length,
        [activeRisks]
    );

    const highRisks = useMemo(
        () =>
            activeRisks.filter(
                (risk) =>
                    risk.severity === "HIGH"
            ).length,
        [activeRisks]
    );

    const totalEvidence = useMemo(
        () =>
            activeRisks.reduce(
                (total, risk) =>
                    total +
                    (risk.evidence_count || 0),
                0
            ),
        [activeRisks]
    );

    const topRisks = useMemo(
        () =>
            [...activeRisks]
                .sort(
                    (a, b) =>
                        b.score - a.score
                )
                .slice(0, 10),
        [activeRisks]
    );

    return (
        <main className="min-h-screen bg-[#121521] text-white">
            <div className="mx-auto w-full max-w-[1800px] px-6 py-5 lg:px-8">

                {/* SECURITY SCORE */}

                {securityScore && (
                    <section className="mb-6">
                        <SecurityScore
                            data={securityScore}
                        />
                    </section>
                )}

                {/* HEADER */}

                <header className="mb-6">
                    <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                        Security posture
                    </p>

                    <h1 className="mt-2 text-[2.6rem] leading-none font-semibold">
                        Risk Management
                    </h1>

                    <p className="mt-2 max-w-2xl text-base text-slate-400">
                        Visualização e priorização dos
                        principais riscos identificados
                        pelo Vyper.
                    </p>
                </header>

                {/* ERROR */}

                {error && (
                    <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                        {error}
                    </div>
                )}

                {/* METRICS */}

                <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">

                    <div className="rounded-[14px] border border-white/10 bg-white/[0.03] p-5">
                        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                            Active risks
                        </p>

                        <p className="mt-3 text-3xl font-semibold">
                            {loading
                                ? "—"
                                : activeRisks.length}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                            Riscos atualmente ativos
                        </p>
                    </div>

                    <div className="rounded-[14px] border border-red-500/20 bg-red-500/[0.04] p-5">
                        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                            Critical
                        </p>

                        <p className="mt-3 text-3xl font-semibold text-red-400">
                            {loading
                                ? "—"
                                : criticalRisks}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                            Riscos de severidade crítica
                        </p>
                    </div>

                    <div className="rounded-[14px] border border-white/10 bg-white/[0.03] p-5 sm:col-span-2 xl:col-span-1">
                        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                            Evidence
                        </p>

                        <p className="mt-3 text-3xl font-semibold">
                            {loading
                                ? "—"
                                : totalEvidence}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                            {highRisks} high-severity risks
                        </p>
                    </div>

                </section>

                {/* HEATMAP */}

                <section className="rounded-[14px] border border-white/10 bg-white/[0.03] p-5 sm:p-6">

                    <div className="mb-5">
                        <h2 className="text-lg font-semibold">
                            Risk Heatmap
                        </h2>

                        <p className="mt-1 text-sm text-slate-400">
                            Relação entre severidade do
                            risco e volume de evidências.
                        </p>
                    </div>

                    <div className="overflow-x-auto">
                        <div className="min-w-[760px]">

                            {/* AXIS */}

                            <div className="mb-2 grid grid-cols-[140px_repeat(6,minmax(0,1fr))] gap-2">

                                <div />

                                {severityLevels.map(
                                    (severity) => (
                                        <div
                                            key={severity}
                                            className="text-center text-[11px] font-medium uppercase tracking-wider text-slate-500"
                                        >
                                            {severityLabel(
                                                severity
                                            )}
                                        </div>
                                    )
                                )}

                            </div>

                            {/* ROWS */}

                            {[
                                {
                                    label:
                                        "10+ evidências",
                                    min: 10,
                                },
                                {
                                    label:
                                        "5–9 evidências",
                                    min: 5,
                                },
                                {
                                    label:
                                        "2–4 evidências",
                                    min: 2,
                                },
                                {
                                    label:
                                        "1 evidência",
                                    min: 1,
                                },
                            ].map((row) => (

                                <div
                                    key={row.label}
                                    className="mb-2 grid grid-cols-[140px_repeat(6,minmax(0,1fr))] gap-2"
                                >

                                    <div className="flex items-center text-xs text-slate-500">
                                        {row.label}
                                    </div>

                                    {severityLevels.map(
                                        (severity) => {

                                            const normalizedSeverity =
                                                severity ===
                                                "CRITICAL"
                                                    ? [
                                                          "CRITICAL",
                                                          "ERROR",
                                                      ]
                                                    : [
                                                          severity,
                                                      ];

                                            const cellRisks =
                                                activeRisks.filter(
                                                    (
                                                        risk
                                                    ) =>
                                                        normalizedSeverity.includes(
                                                            risk.severity
                                                        ) &&
                                                        (
                                                            row.min ===
                                                            10
                                                                ? risk.evidence_count >=
                                                                  10
                                                                : row.min ===
                                                                  5
                                                                ? risk.evidence_count >=
                                                                      5 &&
                                                                  risk.evidence_count <
                                                                      10
                                                                : row.min ===
                                                                  2
                                                                ? risk.evidence_count >=
                                                                      2 &&
                                                                  risk.evidence_count <
                                                                      5
                                                                : risk.evidence_count ===
                                                                  1
                                                        )
                                                );

                                            const highestScore =
                                                cellRisks.length >
                                                0
                                                    ? Math.max(
                                                          ...cellRisks.map(
                                                              (
                                                                  risk
                                                              ) =>
                                                                  risk.score
                                                          )
                                                      )
                                                    : 0;

                                            return (
                                                <div
                                                    key={
                                                        severity
                                                    }
                                                    className={`min-h-[78px] rounded-xl border p-3 transition hover:scale-[1.01] ${cellClass(
                                                        severity,
                                                        row.min
                                                    )}`}
                                                >
                                                    <div className="flex h-full flex-col justify-between">

                                                        <span className="text-xs text-slate-500">
                                                            {
                                                                cellRisks.length
                                                            }{" "}
                                                            risk
                                                            {cellRisks.length !==
                                                            1
                                                                ? "s"
                                                                : ""}
                                                        </span>

                                                        {cellRisks.length >
                                                            0 && (
                                                            <div>
                                                                <span className="text-lg font-semibold">
                                                                    {
                                                                        highestScore
                                                                    }
                                                                </span>

                                                                <span className="ml-1 text-[10px] text-slate-500">
                                                                    max score
                                                                </span>
                                                            </div>
                                                        )}

                                                    </div>
                                                </div>
                                            );
                                        }
                                    )}

                                </div>

                            ))}

                        </div>
                    </div>

                    {/* LEGEND */}

                    <div className="mt-5 flex flex-wrap gap-x-5 gap-y-3 text-xs text-slate-500">

                        <div className="flex items-center gap-2">
                            <span className="h-3 w-3 rounded border border-emerald-500/20 bg-emerald-500/20" />
                            Lower
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="h-3 w-3 rounded border border-yellow-500/30 bg-yellow-500/10" />
                            Moderate
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="h-3 w-3 rounded border border-orange-500/40 bg-orange-500/15" />
                            Elevated
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="h-3 w-3 rounded border border-red-500/40 bg-red-500/20" />
                            Critical
                        </div>

                    </div>

                </section>

                {/* TOP RISKS */}

                <section className="mt-6 rounded-[14px] border border-white/10 bg-white/[0.03] p-5 sm:p-6">

                    <div className="mb-5">
                        <h2 className="text-lg font-semibold">
                            Top Risks
                        </h2>

                        <p className="mt-1 text-sm text-slate-400">
                            Riscos ordenados pelo score
                            de prioridade.
                        </p>
                    </div>

                    {aiError && (
                        <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                            {aiError}
                        </div>
                    )}

                    <div className="space-y-3">

                        {loading ? (

                            <div className="py-10 text-center text-sm text-slate-500">
                                Carregando riscos...
                            </div>

                        ) : topRisks.length === 0 ? (

                            <div className="rounded-xl border border-white/5 bg-black/10 py-10 text-center text-sm text-slate-500">
                                Nenhum risco ativo encontrado.
                            </div>

                        ) : (

                            topRisks.map((risk) => {

                                const isAnalyzing =
                                    aiLoading ===
                                    risk.id;

                                const hasAnalysis =
                                    aiAnalysis?.risk_id ===
                                    risk.id;

                                return (
                                    <div
                                        key={risk.id}
                                        className="rounded-xl border border-white/5 bg-black/10 p-4 transition hover:border-white/10"
                                    >

                                        {/* RISK HEADER */}

                                        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

                                            <div className="min-w-0">
                                                <p className="text-base font-medium text-white">
                                                    {risk.title}
                                                </p>

                                                <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">

                                                    <span>
                                                        {severityLabel(
                                                            risk.severity
                                                        )}
                                                    </span>

                                                    <span>
                                                        {
                                                            risk.evidence_count
                                                        }{" "}
                                                        evidence
                                                    </span>

                                                    <span>
                                                        {
                                                            risk.priority
                                                        }
                                                    </span>

                                                </div>
                                            </div>

                                            <div className="flex flex-wrap items-center gap-3">

                                                <div className="text-right">
                                                    <p className="text-[10px] uppercase tracking-wider text-slate-500">
                                                        Score
                                                    </p>

                                                    <p className="text-xl font-semibold">
                                                        {
                                                            risk.score
                                                        }
                                                    </p>
                                                </div>

                                                <button
                                                    onClick={() =>
                                                        handleAIAnalysis(
                                                            risk.id
                                                        )
                                                    }
                                                    disabled={
                                                        isAnalyzing
                                                    }
                                                    className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs font-medium text-cyan-300 transition hover:bg-cyan-500/20 disabled:cursor-not-allowed disabled:opacity-50"
                                                >
                                                    {isAnalyzing
                                                        ? "Analisando..."
                                                        : hasAnalysis
                                                        ? "Atualizar IA"
                                                        : "Analisar com IA"}
                                                </button>

                                            </div>

                                        </div>

                                        {/* AI ANALYSIS */}

                                        {hasAnalysis && (
                                            <div className="mt-4 rounded-xl border border-cyan-500/20 bg-cyan-500/[0.05] p-4 sm:p-5">

                                                <div className="mb-5 flex flex-col gap-2 border-b border-white/5 pb-4 sm:flex-row sm:items-center sm:justify-between">

                                                    <div>
                                                        <p className="text-sm font-semibold text-cyan-300">
                                                            AI Recommendations
                                                        </p>

                                                        <p className="mt-1 text-xs text-slate-500">
                                                            Análise gerada para este risco.
                                                        </p>
                                                    </div>

                                                    {aiAnalysis.created_at && (
                                                        <span className="text-[10px] text-slate-600">
                                                            {new Date(
                                                                aiAnalysis.created_at
                                                            ).toLocaleString(
                                                                "pt-BR"
                                                            )}
                                                        </span>
                                                    )}

                                                </div>

                                                <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">

                                                    <div>
                                                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                                                            Resumo
                                                        </p>

                                                        <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-300">
                                                            {aiAnalysis.summary ||
                                                                "Não informado."}
                                                        </p>
                                                    </div>

                                                    <div>
                                                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                                                            Impacto
                                                        </p>

                                                        <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-300">
                                                            {aiAnalysis.impact ||
                                                                "Não informado."}
                                                        </p>
                                                    </div>

                                                    <div>
                                                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                                                            Remediação
                                                        </p>

                                                        <div className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-300">
                                                            {aiAnalysis.remediation ||
                                                                "Não informado."}
                                                        </div>
                                                    </div>

                                                </div>

                                            </div>
                                        )}

                                    </div>
                                );
                            })

                        )}

                    </div>

                </section>

            </div>
        </main>
    );
}