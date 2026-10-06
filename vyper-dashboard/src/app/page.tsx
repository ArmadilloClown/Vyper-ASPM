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

import Header from "@/components/Header";

import { useEffect, useState } from "react";

import {
    getDashboard,
    getSeverity,
    getScansHistory,
    getTopRisks,
    getTopPackages,
    getAssets,
    getSecurityScore,
} from "@/services/api";

import { DashboardData } from "@/types";

import SecurityScore from "@/components/SecurityScore";

import MetricsSection from "@/components/dashboard/MetricsSection";
import ChartsSection from "@/components/dashboard/ChartsSection";
import RisksSection from "@/components/dashboard/RisksSection";
import PackagesSection from "@/components/dashboard/PackagesSection";
import AssetsSection from "@/components/dashboard/AssetsSection";

export default function Home() {
    const [dashboard, setDashboard] =
        useState<DashboardData | null>(null);

    const [severityData, setSeverityData] =
        useState<any[]>([]);

    const [historyData, setHistoryData] =
        useState<any[]>([]);

    const [topRisks, setTopRisks] =
        useState<any[]>([]);

    const [topPackages, setTopPackages] =
        useState<any[]>([]);

    const [assets, setAssets] =
        useState<any[]>([]);

    const [securityScore, setSecurityScore] =
        useState<any>(null);

    useEffect(() => {
        async function loadDashboard() {
            try {
                const [
                    dashboardData,
                    severity,
                    history,
                    risks,
                    packages,
                    assetsData,
                    score,
                ] = await Promise.all([
                    getDashboard(),
                    getSeverity(),
                    getScansHistory(),
                    getTopRisks(),
                    getTopPackages(),
                    getAssets(),
                    getSecurityScore(),
                ]);

                setDashboard(dashboardData);

                setSeverityData(
                    severity.map((item: any) => ({
                        severity: item.severity,
                        total: item.count,
                    }))
                );

                setHistoryData(history);
                setTopRisks(risks);
                setTopPackages(packages);
                setAssets(assetsData);
                setSecurityScore(score);
            } catch (error) {
                console.error(
                    "Erro ao carregar dashboard:",
                    error
                );
            }
        }

        loadDashboard();
    }, []);

    if (!dashboard) {
        return (
            <main className="min-h-screen bg-[#121521] px-6 py-8 lg:px-10">
                <div className="flex min-h-[60vh] items-center justify-center">
                    <div className="rounded-[14px] border border-[#0f3a46] bg-[#1a1f31] px-8 py-6 ">
                        <p className="text-base font-medium text-slate-300">
                            Carregando dashboard...
                        </p>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-[#121521] text-white">
            <div className="mx-auto w-full max-w-[1800px] px-6 py-6 lg:px-10">

                <Header />

                <div className="mt-6 space-y-6">

                    {securityScore && (
                        <section>
                            <SecurityScore
                                data={securityScore}
                            />
                        </section>
                    )}

                    <section>
                        <MetricsSection
                            totalScans={
                                dashboard.total_scans
                            }
                            totalFindings={
                                dashboard.total_findings
                            }
                            totalAssets={
                                dashboard.total_assets
                            }
                            totalRisks={
                                dashboard.total_risks
                            }
                        />
                    </section>

                    <section>
                        <ChartsSection
                            severityData={
                                severityData
                            }
                            historyData={
                                historyData
                            }
                        />
                    </section>

                    <section>
                        <RisksSection
                            data={topRisks}
                        />
                    </section>

                    <section>
                        <PackagesSection
                            data={topPackages}
                        />
                    </section>

                    <section>
                        <AssetsSection
                            data={assets}
                        />
                    </section>

                </div>
            </div>
        </main>
    );
}