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

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

import {
    LayoutDashboard,
    ShieldAlert,
    Bug,
    Boxes,
    ScanSearch
} from "lucide-react";

const menu = [
    {
        name: "Dashboard",
        href: "/",
        icon: LayoutDashboard
    },
    {
        name: "Risks",
        href: "/risks",
        icon: ShieldAlert
    },
    {
        name: "Findings",
        href: "/findings",
        icon: Bug
    },
    {
        name: "Assets",
        href: "/assets",
        icon: Boxes
    },
    {
        name: "Scans",
        href: "/scans",
        icon: ScanSearch
    }
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="flex w-64 shrink-0 flex-col border-r border-vyper-line bg-vyper-night">

            {/* Logo (versão principal, com o nome VYPER) */}
            <div className="flex justify-center border-b border-vyper-line px-6 py-7">
                <Image
                    src="/images/vyper-logo.png"
                    alt="Vyper"
                    width={446}
                    height={515}
                    className="h-auto w-28"
                    priority
                />
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-5">

                <div className="space-y-1">

                    {menu.map((item) => {
                        const Icon = item.icon;

                        const active =
                            item.href === "/"
                                ? pathname === "/"
                                : pathname.startsWith(item.href);

                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                aria-current={active ? "page" : undefined}
                                className={`group flex items-center gap-3 rounded-lg border px-3 py-3 font-display text-xs uppercase tracking-wider transition ${
                                    active
                                        ? "border-cyan-400/60 bg-cyan-400/10 text-cyan-400"
                                        : "border-transparent text-slate-300 hover:bg-vyper-surface hover:text-cyan-400"
                                }`}
                            >
                                <Icon
                                    size={18}
                                    className={`shrink-0 transition group-hover:text-cyan-400 ${
                                        active ? "text-cyan-400" : "text-slate-400"
                                    }`}
                                />

                                <span>
                                    {item.name}
                                </span>
                            </Link>
                        );
                    })}

                </div>

            </nav>

            {/* Version */}
            <div className="border-t border-vyper-line p-4">

                <div className="rounded-[14px] border border-vyper-line bg-vyper-surface px-4 py-3">

                    <p className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                        Version
                    </p>

                    <p className="mt-1 font-display text-sm text-cyan-400">
                        Vyper 1.2 Beta
                    </p>

                </div>

            </div>

        </aside>
    );
}
