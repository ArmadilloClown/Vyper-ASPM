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

import "./globals.css";
import { Orbitron, Oxanium, VT323 } from "next/font/google";
import Sidebar from "@/components/Sidebar";

const vt323 = VT323({
    subsets: ["latin"],
    weight: "400",
    variable: "--font-vt323",
    display: "swap",
});

const orbitron = Orbitron({
    subsets: ["latin"],
    weight: "400",
    variable: "--font-orbitron",
    display: "swap",
});

const oxanium = Oxanium({
    subsets: ["latin"],
    weight: ["200", "300", "400", "500", "600", "700"],
    variable: "--font-oxanium",
    display: "swap",
});

export const metadata = {
    title: "Vyper ASPM",
    description: "Postura de segurança, sob controle.",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html
            lang="pt-BR"
            className={`${vt323.variable} ${orbitron.variable} ${oxanium.variable}`}
        >
            <body className="bg-vyper-base text-white">
                <div className="flex min-h-screen">
                    <Sidebar />

                    <main className="flex-1 overflow-auto bg-vyper-base">
                        {children}
                    </main>
                </div>
            </body>
        </html>
    );
}
