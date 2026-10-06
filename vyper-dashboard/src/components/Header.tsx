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

export default function Header() {
    return (
        <header
            className="
                bg-aurora
                sticky
                top-0
                z-50
                flex
                items-center
                justify-between
                border-b
                border-vyper-line
                px-8
                py-6
            "
        >
            <div>
                <h1 className="text-[2.6rem] leading-none text-white">
                    Dashboard
                </h1>

                <p className="mt-1 font-display text-xs uppercase tracking-widest text-cyan-400">
                    Postura de segurança, sob controle
                </p>
            </div>
        </header>
    );
}
