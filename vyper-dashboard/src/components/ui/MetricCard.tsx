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

import { LucideIcon, TrendingUp } from "lucide-react";

interface MetricCardProps {

    title: string;

    value: number;

    subtitle: string;

    color: string;

    Icon: LucideIcon;

}

export default function MetricCard({

    title,

    value,

    subtitle,

    color,

    Icon

}: MetricCardProps) {

    return (

        <div
            className="
            relative
            overflow-hidden
            rounded-[14px]
            bg-vyper-surface
            border
            border-vyper-line
            border-l-2
            border-l-cyan-400
            p-7
            transition-colors
            duration-200
            hover:border-cyan-400
            
            "
        >

            <div className="relative flex justify-between items-start">

                <div>

                    <p className="text-gray-400 text-sm">

                        {title}

                    </p>

                    <h2 className="font-title text-6xl leading-none text-white mt-3">

                        {value}

                    </h2>

                    <div className="flex items-center gap-2 mt-4">

                        <TrendingUp
                            size={15}
                            className="text-green-400"
                        />

                        <span className="text-green-400 text-sm font-semibold">

                            +12%

                        </span>

                    </div>

                    <p className="text-gray-500 text-sm mt-3">

                        {subtitle}

                    </p>

                </div>

                <div
                    className="w-16 h-16 rounded-[14px] flex items-center justify-center border"
                    style={{ borderColor: color, background: `${color}1a` }}
                >

                    <Icon
                        size={30}
                        color={color}
                    />

                </div>

            </div>

        </div>

    );

}