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

import {
    Search,
    Shield,
    Boxes,
    AlertTriangle,
} from "lucide-react";

import MetricCard from "@/components/ui/MetricCard";

interface Props {
    totalScans: number;
    totalFindings: number;
    totalAssets: number;
    totalRisks: number;
}

export default function MetricsSection({
    totalScans,
    totalFindings,
    totalAssets,
    totalRisks,
}: Props) {
    return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <MetricCard
                title="Total de Scans"
                value={totalScans}
                subtitle="Repositórios analisados"
                color="#00B9CA"
                Icon={Search}
            />

            <MetricCard
                title="Total de Findings"
                value={totalFindings}
                subtitle="Vulnerabilidades encontradas"
                color="#00B9CA"
                Icon={Shield}
            />

            <MetricCard
                title="Total de Assets"
                value={totalAssets}
                subtitle="Assets descobertos"
                color="#00B9CA"
                Icon={Boxes}
            />

            <MetricCard
                title="Total de Risks"
                value={totalRisks}
                subtitle="Riscos priorizados"
                color="#00B9CA"
                Icon={AlertTriangle}
            />

        </div>
    );
}