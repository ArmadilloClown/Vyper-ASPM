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
    ShieldCheck,
} from "lucide-react";

interface Props {
    data: {
        score: number;
        status: string;
        critical: number;
        high: number;
        medium: number;
        low: number;
        warning: number;
    };
}

export default function SecurityScore({
    data,
}: Props) {
    if (!data) {
        return null;
    }

    const {
        score,
        status,
        critical,
        high,
        medium,
        low,
        warning,
    } = data;

    const color =
        score >= 90
            ? "#26E238"
            : score >= 70
            ? "#00B9CA"
            : score >= 50
            ? "#FF9F43"
            : "#FF4D5E";

    return (
        <div className="rounded-[14px] border border-[#0f3a46] bg-[#1a1f31] p-6 ">

            <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">

                {/* SCORE */}

                <div className="flex items-center gap-5">

                    <div
                        className="
                            flex
                            h-28
                            w-28
                            shrink-0
                            items-center
                            justify-center
                            rounded-full
                            border-[8px]
                        "
                        style={{
                            borderColor: color,
                        }}
                    >
                        <div className="text-center">
                            <p className="font-title text-5xl leading-none text-white">
                                {score}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                                /100
                            </p>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center gap-2.5">
                            <ShieldCheck
                                size={22}
                                style={{
                                    color,
                                }}
                            />

                            <h2 className="text-lg font-semibold text-white">
                                Overall Security Score
                            </h2>
                        </div>

                        <p
                            className="mt-2 text-2xl font-bold"
                            style={{
                                color,
                            }}
                        >
                            {status}
                        </p>

                        <p className="mt-1 text-sm text-slate-400">
                            Security posture score
                        </p>
                    </div>

                </div>

                {/* SEVERIDADES */}

                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">

                    <Card
                        title="Critical"
                        value={critical}
                        color="text-red-400"
                    />

                    <Card
                        title="High"
                        value={high}
                        color="text-orange-400"
                    />

                    <Card
                        title="Medium"
                        value={medium}
                        color="text-yellow-400"
                    />

                    <Card
                        title="Low"
                        value={low}
                        color="text-cyan-400"
                    />

                    <Card
                        title="Warning"
                        value={warning}
                        color="text-amber-400"
                    />

                </div>

            </div>
        </div>
    );
}

function Card({
    title,
    value,
    color,
}: {
    title: string;
    value: number;
    color: string;
}) {
    return (
        <div className="min-w-[100px] rounded-xl border border-[#0f3a46] bg-[#121521] px-4 py-3 text-center">

            <p className="text-xs font-medium text-slate-500">
                {title}
            </p>

            <p
                className={`font-title mt-1 text-4xl leading-none ${color}`}
            >
                {value}
            </p>

        </div>
    );
}