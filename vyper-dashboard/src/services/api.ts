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

import {DashboardData} from "@/types";

const API_URL = "http://127.0.0.1:8000";


async function request<T>(
    url: string,
    options?: RequestInit
): Promise<T> {

    const response = await fetch(
        `${API_URL}${url}`,
        options
    );

    if (!response.ok) {

        throw new Error(
            `Erro HTTP ${response.status}`
        );

    }

    return response.json();

}


export async function getScans(): Promise<any[]> {

    return request<any[]>("/scans");

}


export async function getRisks(): Promise<any[]> {

    return request<any[]>("/risks");

}


export async function getDashboard(): Promise<DashboardData> {

    return request<DashboardData>("/dashboard");

}


export async function getSeverity(): Promise<any[]> {

    return request<any>("/dashboard/severity");

}


export async function getScansHistory(): Promise<any[]>{

    return request<any[]>("/dashboard/scans-history");

}


export async function getTopRisks(): Promise<any[]> {

    return request<any[]>("/dashboard/top-risks");

}


export async function getTopPackages(): Promise<any[]> {

    return request<any[]>("/dashboard/top-packages");

}


export async function getAssets(): Promise<any[]>{

    return request<any[]>("/dashboard/assets");

}


export async function getSecurityScore(): Promise<any[]> {

    return request<any[]>("/dashboard/security-score");

}


export async function getFindings(): Promise<any[]> {

    return request<any[]>("/findings");

}


export function connectScanWebSocket(
    taskId: string,
    onProgress: (
        progress: number,
        message: string
    ) => void
) {

    const socket = new WebSocket(
        `ws://127.0.0.1:8000/ws/${taskId}`
    );

    socket.onmessage = (event) => {

        try {

            const data = JSON.parse(
                event.data
            );

            onProgress(
                data.progress ?? 0,
                data.message ?? ""
            );

        } catch (error) {

            console.error(
                "Erro ao processar mensagem do WebSocket:",
                error
            );

        }

    };

    socket.onerror = (error) => {

        console.error(
            "Erro no WebSocket:",
            error
        );

    };

    return socket;
}


export async function startScan(
    repoUrl: string
): Promise<{
    message: string;
    task_id: string;
}> {

    return request<{
        message: string;
        task_id: string;
    }>(
        `/?repo_url=${encodeURIComponent(repoUrl)}`,
        {
            method: "POST",
        }
    );

}


export async function getRiskAnalysis(
    riskId: number
): Promise<{
    id: number;
    risk_id: number;
    summary: string;
    impact: string;
    remediation: string;
    created_at?: string;
} | {
    analysis: null;
}> {

    return request(
        `/risk/${riskId}/analysis`
    );

}


export async function analyzeRisk(
    riskId: number
): Promise<{
    id: number;
    risk_id: number;
    summary: string;
    impact: string;
    remediation: string;
    created_at?: string;
}> {

    return request<{
        id: number;
        risk_id: number;
        summary: string;
        impact: string;
        remediation: string;
        created_at?: string;
    }>(
        `/risk/${riskId}/analyze`,
        {
            method: "POST",
        }
    );

}

export interface ScheduledScan {
    id: number;
    repository_url: string;
    enabled: boolean;
    interval_minutes: number;
    last_started_at?: string | null;
    last_finished_at?: string | null;
    next_run_at?: string | null;
    created_at?: string;
    updated_at?: string;
}

export async function getScheduledScans(): Promise<ScheduledScan[]> {
    return request<ScheduledScan[]>("/scheduled-scans");
}

export async function createScheduledScan(
    repositoryUrl: string,
    intervalMinutes: number
): Promise<ScheduledScan> {
    return request<ScheduledScan>(
        `/scheduled-scans?repository_url=${encodeURIComponent(
            repositoryUrl
        )}&interval_minutes=${intervalMinutes}`,
        {
            method: "POST",
        }
    );
}

export async function updateScheduledScan(
    scheduledScanId: number,
    enabled?: boolean,
    intervalMinutes?: number
): Promise<ScheduledScan> {
    const params = new URLSearchParams();

    if (enabled !== undefined) {
        params.set("enabled", String(enabled));
    }

    if (intervalMinutes !== undefined) {
        params.set(
            "interval_minutes",
            String(intervalMinutes)
        );
    }

    return request<ScheduledScan>(
        `/scheduled-scans/${scheduledScanId}?${params.toString()}`,
        {
            method: "PATCH",
        }
    );
}

export async function deleteScheduledScan(
    scheduledScanId: number
): Promise<any> {
    return request(
        `/scheduled-scans/${scheduledScanId}`,
        {
            method: "DELETE",
        }
    );
}