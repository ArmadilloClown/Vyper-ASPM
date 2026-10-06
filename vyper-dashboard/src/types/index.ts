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

export interface Scan {

    id:number;

    repository_url:string;

    status:string;

    created_at:string;

}


export interface Risk {

    id:number;

    title:string;

    severity:string;

    score:number;

    status:string;

}

export interface DashboardData {

    total_scans: number;

    total_findings: number;

    total_assets: number;

    total_risks: number;

}

export interface SeverityChart {

    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    WARNING: number;
    LOW: number;
    INFO: number;

}