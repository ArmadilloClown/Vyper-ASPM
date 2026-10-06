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
import { getFindings } from "@/services/api";
import {
    AlertTriangle,
    Bug,
    Search,
    ShieldAlert,
} from "lucide-react";

interface Finding {
    id: number;
    scan_id: number;

    source?: string;
    severity?: string;
    type?: string;

    title?: string;
    description?: string;

    file?: string;
    line?: number;

    package_name?: string;
    installed_version?: string;
    fixed_version?: string;

    risk_score?: number;
    status?: string;

    cve?: string | null;
    cvss?: number | null;
    cwe?: string | null;
    owasp?: string | null;
    category?: string | null;
    rule_id?: string | null;
}

const severityOrder = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "WARNING",
    "LOW",
    "INFO",
];

function severityLabel(severity?: string) {
    const labels: Record<string, string> = {
        CRITICAL: "Critical",
        HIGH: "High",
        MEDIUM: "Medium",
        WARNING: "Warning",
        LOW: "Low",
        INFO: "Info",
    };

    return labels[severity || ""] || severity || "Unknown";
}

function severityClass(severity?: string) {
    switch (severity) {
        case "CRITICAL":
            return "border-red-500/30 bg-red-500/10 text-red-400";

        case "HIGH":
            return "border-orange-500/30 bg-orange-500/10 text-orange-400";

        case "MEDIUM":
            return "border-yellow-500/30 bg-yellow-500/10 text-yellow-400";

        case "WARNING":
            return "border-amber-500/30 bg-amber-500/10 text-amber-400";

        case "LOW":
            return "border-cyan-500/30 bg-cyan-500/10 text-cyan-400";

        default:
            return "border-slate-500/30 bg-slate-500/10 text-slate-400";
    }
}

function statusClass(status?: string) {
    switch (status) {
        case "fixed":
            return "border-green-500/30 bg-green-500/10 text-green-400";

        case "active":
            return "border-red-500/30 bg-red-500/10 text-red-400";

        case "new":
            return "border-cyan-500/30 bg-cyan-500/10 text-cyan-400";

        default:
            return "border-slate-500/30 bg-slate-500/10 text-slate-400";
    }
}

function statusLabel(status?: string) {
    const labels: Record<string, string> = {
        new: "New",
        active: "Active",
        fixed: "Fixed",
    };

    return labels[status || ""] || status || "Unknown";
}

export default function FindingsPage() {
    const [findings, setFindings] = useState<Finding[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [search, setSearch] = useState("");
    const [severity, setSeverity] = useState("ALL");
    const [status, setStatus] = useState("ALL");
    const [source, setSource] = useState("ALL");

    const [selectedFinding, setSelectedFinding] =
        useState<Finding | null>(null);

    useEffect(() => {
        async function loadFindings() {
            try {
                setLoading(true);
                setError("");

                const data = await getFindings();

                setFindings(data);
            } catch (err) {
                console.error(
                    "Erro ao carregar findings:",
                    err
                );

                setError(
                    "Não foi possível carregar os findings."
                );
            } finally {
                setLoading(false);
            }
        }

        loadFindings();
    }, []);

    const sources = useMemo(() => {
        return Array.from(
            new Set(
                findings
                    .map((finding) => finding.source)
                    .filter(Boolean)
            )
        ) as string[];
    }, [findings]);

    const filteredFindings = useMemo(() => {
        const searchValue =
            search.toLowerCase().trim();

        return findings
            .filter((finding) => {
                if (
                    severity !== "ALL" &&
                    finding.severity !== severity
                ) {
                    return false;
                }

                if (
                    status !== "ALL" &&
                    finding.status !== status
                ) {
                    return false;
                }

                if (
                    source !== "ALL" &&
                    finding.source !== source
                ) {
                    return false;
                }

                if (!searchValue) {
                    return true;
                }

                const searchable = [
                    finding.title,
                    finding.description,
                    finding.source,
                    finding.type,
                    finding.file,
                    finding.package_name,
                    finding.cve,
                    finding.cwe,
                    finding.rule_id,
                ]
                    .filter(Boolean)
                    .join(" ")
                    .toLowerCase();

                return searchable.includes(
                    searchValue
                );
            })
            .sort((a, b) => {
                const severityA =
                    severityOrder.indexOf(
                        a.severity || "INFO"
                    );

                const severityB =
                    severityOrder.indexOf(
                        b.severity || "INFO"
                    );

                return severityA - severityB;
            });
    }, [
        findings,
        search,
        severity,
        status,
        source,
    ]);

    const total = findings.length;

    const critical = findings.filter(
        (finding) =>
            finding.severity === "CRITICAL"
    ).length;

    const high = findings.filter(
        (finding) =>
            finding.severity === "HIGH"
    ).length;

    const active = findings.filter(
        (finding) =>
            finding.status === "active" ||
            finding.status === "new"
    ).length;

    return (
        <main className="min-h-screen bg-[#121521] text-white">
            <div className="mx-auto w-full max-w-[1800px] px-6 py-5 lg:px-8">

                {/* HEADER */}

                <header className="mb-6">
                    <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                        Security findings
                    </p>

                    <div className="mt-2 flex items-center gap-3">
                        <Bug
                            size={28}
                            className="text-cyan-400"
                        />

                        <h1 className="text-[2.6rem] leading-none font-semibold">
                            Findings
                        </h1>
                    </div>

                    <p className="mt-2 max-w-2xl text-base text-slate-400">
                        Vulnerabilidades e problemas
                        identificados pelos scanners do
                        Vyper.
                    </p>
                </header>

                {/* ERROR */}

                {error && (
                    <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                        {error}
                    </div>
                )}

                {/* SUMMARY */}

                <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

                    <SummaryCard
                        label="Total findings"
                        value={total}
                        icon={
                            <Bug
                                size={24}
                                className="text-cyan-400"
                            />
                        }
                    />

                    <SummaryCard
                        label="Critical"
                        value={critical}
                        valueClass="text-red-400"
                        borderClass="border-red-500/20"
                        icon={
                            <ShieldAlert
                                size={24}
                                className="text-red-400"
                            />
                        }
                    />

                    <SummaryCard
                        label="High"
                        value={high}
                        valueClass="text-orange-400"
                        borderClass="border-orange-500/20"
                        icon={
                            <AlertTriangle
                                size={24}
                                className="text-orange-400"
                            />
                        }
                    />

                    <SummaryCard
                        label="Active"
                        value={active}
                        valueClass="text-cyan-400"
                        borderClass="border-cyan-500/20"
                        icon={
                            <Search
                                size={24}
                                className="text-cyan-400"
                            />
                        }
                    />

                </section>

                {/* FILTERS */}

                <section className="mb-6 rounded-[14px] border border-white/10 bg-white/[0.03] p-5">

                    <div className="mb-4">
                        <h2 className="text-base font-semibold">
                            Filter findings
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Pesquise e filtre os resultados
                            encontrados pelos scanners.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-4">

                        <div className="relative xl:col-span-2">
                            <Search
                                size={18}
                                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                            />

                            <input
                                value={search}
                                onChange={(event) =>
                                    setSearch(
                                        event.target.value
                                    )
                                }
                                placeholder="Search findings..."
                                className="w-full rounded-lg border border-white/10 bg-[#121521] py-3 pl-10 pr-4 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/50"
                            />
                        </div>

                        <select
                            value={severity}
                            onChange={(event) =>
                                setSeverity(
                                    event.target.value
                                )
                            }
                            className="rounded-lg border border-white/10 bg-[#121521] px-3 py-3 text-sm text-white outline-none"
                        >
                            <option value="ALL">
                                All severities
                            </option>

                            {severityOrder.map(
                                (level) => (
                                    <option
                                        key={level}
                                        value={level}
                                    >
                                        {severityLabel(
                                            level
                                        )}
                                    </option>
                                )
                            )}
                        </select>

                        <select
                            value={status}
                            onChange={(event) =>
                                setStatus(
                                    event.target.value
                                )
                            }
                            className="rounded-lg border border-white/10 bg-[#121521] px-3 py-3 text-sm text-white outline-none"
                        >
                            <option value="ALL">
                                All statuses
                            </option>

                            <option value="new">
                                New
                            </option>

                            <option value="active">
                                Active
                            </option>

                            <option value="fixed">
                                Fixed
                            </option>
                        </select>

                        <select
                            value={source}
                            onChange={(event) =>
                                setSource(
                                    event.target.value
                                )
                            }
                            className="rounded-lg border border-white/10 bg-[#121521] px-3 py-3 text-sm text-white outline-none lg:col-span-2 xl:col-span-1"
                        >
                            <option value="ALL">
                                All sources
                            </option>

                            {sources.map(
                                (item) => (
                                    <option
                                        key={item}
                                        value={item}
                                    >
                                        {item}
                                    </option>
                                )
                            )}
                        </select>

                    </div>

                </section>

                {/* FINDINGS LIST */}

                <section className="overflow-hidden rounded-[14px] border border-white/10 bg-white/[0.03]">

                    <div className="border-b border-white/10 px-5 py-4">
                        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">

                            <div>
                                <h2 className="text-lg font-semibold">
                                    Findings
                                </h2>

                                <p className="text-sm text-slate-500">
                                    Resultados dos scanners
                                </p>
                            </div>

                            <span className="text-sm text-slate-500">
                                {filteredFindings.length}{" "}
                                resultado
                                {filteredFindings.length !==
                                1
                                    ? "s"
                                    : ""}
                            </span>

                        </div>
                    </div>

                    {loading ? (
                        <div className="py-16 text-center text-sm text-slate-500">
                            Carregando findings...
                        </div>
                    ) : filteredFindings.length === 0 ? (
                        <div className="px-6 py-16 text-center">

                            <Bug
                                size={36}
                                className="mx-auto mb-3 text-slate-600"
                            />

                            <p className="text-base font-medium text-slate-300">
                                No findings found.
                            </p>

                            <p className="mt-1 text-sm text-slate-500">
                                Tente alterar os filtros ou
                                execute um novo scan.
                            </p>

                        </div>
                    ) : (
                        <div className="divide-y divide-white/5">

                            {filteredFindings.map(
                                (finding) => (
                                    <button
                                        key={finding.id}
                                        onClick={() =>
                                            setSelectedFinding(
                                                finding
                                            )
                                        }
                                        className="block w-full px-5 py-5 text-left transition hover:bg-white/[0.02]"
                                    >

                                        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">

                                            <div className="min-w-0 flex-1">

                                                <div className="flex flex-wrap items-center gap-2">

                                                    <h3 className="text-base font-semibold text-white">
                                                        {finding.title ||
                                                            finding.type ||
                                                            "Untitled finding"}
                                                    </h3>

                                                    <span
                                                        className={`rounded-md border px-2 py-1 text-xs font-semibold ${severityClass(
                                                            finding.severity
                                                        )}`}
                                                    >
                                                        {severityLabel(
                                                            finding.severity
                                                        )}
                                                    </span>

                                                    <span
                                                        className={`rounded-md border px-2 py-1 text-xs font-semibold ${statusClass(
                                                            finding.status
                                                        )}`}
                                                    >
                                                        {statusLabel(
                                                            finding.status
                                                        )}
                                                    </span>

                                                </div>

                                                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-400">

                                                    <span>
                                                        Source:{" "}
                                                        {finding.source ||
                                                            "Unknown"}
                                                    </span>

                                                    {finding.file && (
                                                        <span className="break-all">
                                                            {finding.file}
                                                            {finding.line
                                                                ? `:${finding.line}`
                                                                : ""}
                                                        </span>
                                                    )}

                                                    {finding.package_name && (
                                                        <span>
                                                            Package:{" "}
                                                            {
                                                                finding.package_name
                                                            }
                                                        </span>
                                                    )}

                                                </div>

                                            </div>

                                            <div className="shrink-0 xl:text-right">

                                                <p className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                                                    Risk score
                                                </p>

                                                <p className="mt-1 text-xl font-semibold text-cyan-400">
                                                    {finding.risk_score ??
                                                        "—"}
                                                </p>

                                            </div>

                                        </div>

                                    </button>
                                )
                            )}

                        </div>
                    )}

                </section>

            </div>

            {/* DETAIL MODAL */}

            {selectedFinding && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
                    onClick={() =>
                        setSelectedFinding(null)
                    }
                >

                    <div
                        className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[14px] border border-white/10 bg-[#121521] p-6 shadow-2xl sm:p-7"
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                    >

                        <div className="mb-6 flex items-start justify-between gap-4">

                            <div className="min-w-0">

                                <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                                    Finding details
                                </p>

                                <h2 className="mt-2 break-words text-2xl font-semibold text-white">
                                    {selectedFinding.title ||
                                        selectedFinding.type ||
                                        "Finding"}
                                </h2>

                                <div className="mt-3 flex flex-wrap gap-2">

                                    <span
                                        className={`rounded-md border px-2 py-1 text-xs font-semibold ${severityClass(
                                            selectedFinding.severity
                                        )}`}
                                    >
                                        {severityLabel(
                                            selectedFinding.severity
                                        )}
                                    </span>

                                    <span
                                        className={`rounded-md border px-2 py-1 text-xs font-semibold ${statusClass(
                                            selectedFinding.status
                                        )}`}
                                    >
                                        {statusLabel(
                                            selectedFinding.status
                                        )}
                                    </span>

                                </div>

                            </div>

                            <button
                                onClick={() =>
                                    setSelectedFinding(null)
                                }
                                aria-label="Close details"
                                className="shrink-0 rounded-lg px-3 py-2 text-lg text-slate-400 transition hover:bg-white/5 hover:text-white"
                            >
                                ✕
                            </button>

                        </div>

                        <div className="space-y-6">

                            <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">

                                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    Description
                                </p>

                                <p className="text-sm leading-6 text-slate-300">
                                    {selectedFinding.description ||
                                        "No description available."}
                                </p>

                            </div>

                            <div>
                                <p className="mb-3 text-sm font-semibold text-white">
                                    Technical details
                                </p>

                                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">

                                    <Detail
                                        label="Source"
                                        value={
                                            selectedFinding.source
                                        }
                                    />

                                    <Detail
                                        label="Type"
                                        value={
                                            selectedFinding.type
                                        }
                                    />

                                    <Detail
                                        label="File"
                                        value={
                                            selectedFinding.file
                                        }
                                    />

                                    <Detail
                                        label="Line"
                                        value={
                                            selectedFinding.line
                                        }
                                    />

                                    <Detail
                                        label="Package"
                                        value={
                                            selectedFinding.package_name
                                        }
                                    />

                                    <Detail
                                        label="Installed version"
                                        value={
                                            selectedFinding.installed_version
                                        }
                                    />

                                    <Detail
                                        label="Fixed version"
                                        value={
                                            selectedFinding.fixed_version
                                        }
                                    />

                                    <Detail
                                        label="Risk score"
                                        value={
                                            selectedFinding.risk_score
                                        }
                                    />

                                    <Detail
                                        label="CVE"
                                        value={
                                            selectedFinding.cve
                                        }
                                    />

                                    <Detail
                                        label="CVSS"
                                        value={
                                            selectedFinding.cvss
                                        }
                                    />

                                    <Detail
                                        label="CWE"
                                        value={
                                            selectedFinding.cwe
                                        }
                                    />

                                    <Detail
                                        label="OWASP"
                                        value={
                                            selectedFinding.owasp
                                        }
                                    />

                                    <Detail
                                        label="Category"
                                        value={
                                            selectedFinding.category
                                        }
                                    />

                                    <Detail
                                        label="Rule ID"
                                        value={
                                            selectedFinding.rule_id
                                        }
                                    />

                                    <Detail
                                        label="Scan ID"
                                        value={
                                            selectedFinding.scan_id
                                        }
                                    />

                                </div>
                            </div>

                        </div>

                    </div>
                </div>
            )}
        </main>
    );
}

function SummaryCard({
    label,
    value,
    icon,
    valueClass = "text-white",
    borderClass = "border-white/10",
}: {
    label: string;
    value: number;
    icon: React.ReactNode;
    valueClass?: string;
    borderClass?: string;
}) {
    return (
        <div
            className={`rounded-[14px] border bg-white/[0.03] p-5 ${borderClass}`}
        >
            <div className="flex items-start justify-between gap-4">

                <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                        {label}
                    </p>

                    <p
                        className={`mt-3 text-3xl font-semibold ${valueClass}`}
                    >
                        {value}
                    </p>
                </div>

                <div className="rounded-lg border border-white/5 bg-white/[0.03] p-2">
                    {icon}
                </div>

            </div>
        </div>
    );
}

function Detail({
    label,
    value,
}: {
    label: string;
    value?: string | number | null;
}) {
    return (
        <div className="rounded-xl border border-white/5 bg-[#121521] p-4">

            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                {label}
            </p>

            <p className="mt-1 break-words text-sm text-slate-200">
                {value !== null &&
                value !== undefined &&
                value !== ""
                    ? String(value)
                    : "—"}
            </p>

        </div>
    );
}