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

import { useEffect, useState } from "react";

import {
    connectScanWebSocket,
    getScans,
    startScan,
    getScheduledScans,
    createScheduledScan,
    updateScheduledScan,
    deleteScheduledScan,
    ScheduledScan,
} from "@/services/api";

interface Scan {
    id: number;
    repository_url: string;
    status: string;
    finished_at?: string | null;
    created_at?: string | null;
}

export default function ScansPage() {
    /*
     * ============================
     * SCANS MANUAIS
     * ============================
     */

    const [repoUrl, setRepoUrl] = useState("");

    const [scans, setScans] = useState<Scan[]>([]);

    const [loading, setLoading] = useState(false);

    const [taskId, setTaskId] = useState<string | null>(null);

    const [progress, setProgress] = useState(0);

    const [progressMessage, setProgressMessage] = useState("");

    /*
     * ============================
     * SCANS AUTOMÁTICOS
     * ============================
     */

    const [scheduledScans, setScheduledScans] = useState<
        ScheduledScan[]
    >([]);

    const [scheduledRepoUrl, setScheduledRepoUrl] =
        useState("");

    const [scheduledInterval, setScheduledInterval] =
        useState("60");

    const [creatingSchedule, setCreatingSchedule] =
        useState(false);

    /*
     * ID do agendamento que está sendo salvo.
     */
    const [savingScheduleId, setSavingScheduleId] =
        useState<number | null>(null);

    /*
     * Valores editáveis de cada agendamento.
     *
     * Exemplo:
     * {
     *   2: 30,
     *   3: 60
     * }
     */
    const [editedIntervals, setEditedIntervals] =
        useState<Record<number, string>>({});

    /*
     * ============================
     * CARREGAR DADOS
     * ============================
     */

    async function loadScans() {
        try {
            const data = await getScans();

            setScans(data);
        } catch (error) {
            console.error(
                "Erro ao carregar scans:",
                error
            );
        }
    }

    async function loadScheduledScans() {
        try {
            const data = await getScheduledScans();

            setScheduledScans(data);

            /*
             * Inicializa os campos editáveis
             * usando os intervalos atuais.
             */
            const intervals: Record<number, string> = {};

            data.forEach((schedule) => {
                intervals[schedule.id] =
                    String(schedule.interval_minutes);
            });

            setEditedIntervals(intervals);
        } catch (error) {
            console.error(
                "Erro ao carregar scans automáticos:",
                error
            );
        }
    }

    useEffect(() => {
        loadScans();
        loadScheduledScans();
    }, []);

    /*
     * ============================
     * SCAN MANUAL
     * ============================
     */

    async function handleStartScan() {
        if (!repoUrl.trim()) {
            alert(
                "Informe a URL do repositório."
            );

            return;
        }

        try {
            setLoading(true);

            setProgress(0);

            setProgressMessage(
                "Iniciando scan..."
            );

            const result = await startScan(
                repoUrl.trim()
            );

            setTaskId(result.task_id);

            /*
             * O WebSocket acompanha o progresso
             * do scan executado pelo Celery.
             */
            const socket =
                connectScanWebSocket(
                    result.task_id,
                    (
                        currentProgress,
                        message
                    ) => {
                        setProgress(
                            currentProgress
                        );

                        setProgressMessage(
                            message
                        );

                        if (
                            currentProgress >=
                            100
                        ) {
                            setLoading(false);

                            loadScans();
                        }
                    }
                );

            /*
             * Cleanup do WebSocket quando
             * necessário.
             */
            return () => {
                socket.close();
            };
        } catch (error) {
            console.error(
                "Erro ao iniciar scan:",
                error
            );

            alert(
                "Não foi possível iniciar o scan."
            );

            setLoading(false);
        }
    }

    /*
     * ============================
     * CRIAR SCAN AUTOMÁTICO
     * ============================
     */

    async function handleCreateScheduledScan() {
        const interval = Number(
            scheduledInterval
        );

        if (!scheduledRepoUrl.trim()) {
            alert(
                "Informe a URL do repositório."
            );

            return;
        }

        if (
            !Number.isInteger(interval) ||
            interval < 10
        ) {
            alert(
                "O intervalo mínimo é de 10 minutos."
            );

            return;
        }

        try {
            setCreatingSchedule(true);

            const created =
                await createScheduledScan(
                    scheduledRepoUrl.trim(),
                    interval
                );

            setScheduledScans((current) => [
                created,
                ...current,
            ]);

            setEditedIntervals(
                (current) => ({
                    ...current,
                    [created.id]: String(
                        created.interval_minutes
                    ),
                })
            );

            setScheduledRepoUrl("");

            setScheduledInterval("60");

            alert(
                "Scan automático criado com sucesso."
            );
        } catch (error) {
            console.error(
                "Erro ao criar scan automático:",
                error
            );

            alert(
                "Não foi possível criar o scan automático."
            );
        } finally {
            setCreatingSchedule(false);
        }
    }

    /*
     * ============================
     * ALTERAR INTERVALO
     * ============================
     */

    function handleIntervalChange(
        scheduleId: number,
        value: string
    ) {
        setEditedIntervals(
            (current) => ({
                ...current,
                [scheduleId]: value,
            })
        );
    }

    /*
     * ============================
     * SALVAR CONFIGURAÇÃO
     * ============================
     */

    async function handleSaveScheduledScan(
        schedule: ScheduledScan
    ) {
        const intervalText =
            editedIntervals[schedule.id] ??
            String(schedule.interval_minutes);

        const interval = Number(
            intervalText
        );

        if (
            !Number.isInteger(interval) ||
            interval < 10
        ) {
            alert(
                "O intervalo mínimo é de 10 minutos."
            );

            return;
        }

        try {
            setSavingScheduleId(
                schedule.id
            );

            const updated =
                await updateScheduledScan(
                    schedule.id,
                    undefined,
                    interval
                );

            setScheduledScans(
                (current) =>
                    current.map(
                        (item) =>
                            item.id ===
                            schedule.id
                                ? updated
                                : item
                    )
            );

            setEditedIntervals(
                (current) => ({
                    ...current,
                    [schedule.id]: String(
                        updated.interval_minutes
                    ),
                })
            );

            alert(
                "Configuração atualizada com sucesso."
            );
        } catch (error) {
            console.error(
                "Erro ao atualizar intervalo:",
                error
            );

            alert(
                "Não foi possível atualizar o intervalo."
            );
        } finally {
            setSavingScheduleId(null);
        }
    }

    /*
     * ============================
     * ATIVAR / DESATIVAR
     * ============================
     */

    async function handleToggleScheduledScan(
        schedule: ScheduledScan
    ) {
        try {
            setSavingScheduleId(
                schedule.id
            );

            const updated =
                await updateScheduledScan(
                    schedule.id,
                    !schedule.enabled
                );

            setScheduledScans(
                (current) =>
                    current.map(
                        (item) =>
                            item.id ===
                            schedule.id
                                ? updated
                                : item
                    )
            );
        } catch (error) {
            console.error(
                "Erro ao alterar status do agendamento:",
                error
            );

            alert(
                "Não foi possível alterar o status do agendamento."
            );
        } finally {
            setSavingScheduleId(null);
        }
    }

    /*
     * ============================
     * EXCLUIR
     * ============================
     */

    async function handleDeleteScheduledScan(
        scheduleId: number
    ) {
        const confirmed = window.confirm(
            "Tem certeza que deseja excluir este scan automático?"
        );

        if (!confirmed) {
            return;
        }

        try {
            setSavingScheduleId(
                scheduleId
            );

            await deleteScheduledScan(
                scheduleId
            );

            setScheduledScans(
                (current) =>
                    current.filter(
                        (item) =>
                            item.id !==
                            scheduleId
                    )
            );

            setEditedIntervals(
                (current) => {
                    const copy = {
                        ...current,
                    };

                    delete copy[
                        scheduleId
                    ];

                    return copy;
                }
            );
        } catch (error) {
            console.error(
                "Erro ao excluir scan automático:",
                error
            );

            alert(
                "Não foi possível excluir o scan automático."
            );
        } finally {
            setSavingScheduleId(null);
        }
    }

    /*
     * ============================
     * FORMATAÇÃO DE DATA
     * ============================
     */

    function formatScheduleDate(
        value?: string | null
    ) {
        if (!value) {
            return "—";
        }

        /*
         * O backend grava os timestamps em UTC.
        *
        * Alguns valores históricos podem chegar sem
         * o sufixo "Z", por exemplo:
        *
        * 2026-09-27T23:27:03.051830
         *
         * Nesse caso, informamos explicitamente ao
        * JavaScript que o valor é UTC.
        */
        const normalizedValue =
            /Z$|[+-]\d{2}:\d{2}$/.test(value)
                ? value
                : `${value}Z`;

        const date =
            new Date(normalizedValue);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return "—";
        }

        return new Intl.DateTimeFormat(
            "pt-BR",
            {
            timeZone: "America/Sao_Paulo",
            dateStyle: "short",
            timeStyle: "medium",
            }
        ).format(date);
    }

    /*
     * ============================
     * RENDER
     * ============================
     */

    return (
        <main className="min-h-screen bg-[#121521] text-white">
            <div className="mx-auto w-full max-w-[1800px] px-6 py-8 lg:px-10">

                {/* ============================ */}
                {/* TÍTULO */}
                {/* ============================ */}

                <div className="mb-8">
                    <h1 className="text-[2.6rem] leading-none font-bold">
                        Scans
                    </h1>

                    <p className="mt-2 text-base text-slate-400">
                        Execute análises de segurança
                        e configure scans automáticos.
                    </p>
                </div>

                {/* ============================ */}
                {/* SCANS AUTOMÁTICOS */}
                {/* ============================ */}

                <section className="mb-8 rounded-[14px] border border-[#0f3a46] bg-[#121521] p-6">

                    <div className="mb-6">
                        <h2 className="text-xl font-semibold">
                            Scans Automáticos
                        </h2>

                        <p className="mt-1 text-sm text-slate-400">
                            Configure análises automáticas
                            executadas pelo backend.
                            O intervalo mínimo é de 10 minutos.
                        </p>
                    </div>

                    {/* ============================ */}
                    {/* NOVO AGENDAMENTO */}
                    {/* ============================ */}

                    <div className="rounded-xl border border-[#0f3a46] bg-[#121521] p-5">

                        <h3 className="mb-4 text-base font-semibold">
                            Novo scan automático
                        </h3>

                        <div className="grid gap-4 lg:grid-cols-[1fr_180px_auto]">

                            <div>
                                <label className="mb-2 block text-sm font-medium text-slate-300">
                                    Repositório
                                </label>

                                <input
                                    type="url"
                                    value={
                                        scheduledRepoUrl
                                    }
                                    onChange={(event) =>
                                        setScheduledRepoUrl(
                                            event.target.value
                                        )
                                    }
                                    placeholder="https://github.com/empresa/repositorio.git"
                                    className="w-full rounded-lg border border-[#0f3a46] bg-[#001017] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400"
                                />
                            </div>

                            <div>
                                <label className="mb-2 block text-sm font-medium text-slate-300">
                                    Intervalo
                                </label>

                                <div className="flex items-center gap-2">
                                    <input
                                        type="number"
                                        min={10}
                                        step={1}
                                        value={
                                            scheduledInterval
                                        }
                                        onChange={(event) =>
                                            setScheduledInterval(
                                                event.target.value
                                            )
                                        }
                                        className="w-full rounded-lg border border-[#0f3a46] bg-[#001017] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400"
                                    />

                                    <span className="text-sm text-slate-400">
                                        min
                                    </span>
                                </div>
                            </div>

                            <div className="flex items-end">
                                <button
                                    onClick={
                                        handleCreateScheduledScan
                                    }
                                    disabled={
                                        creatingSchedule
                                    }
                                    className="w-full rounded-lg bg-[#26e238] px-5 py-3 text-sm font-semibold text-[#001017] transition hover:bg-[#4aeb59] disabled:cursor-not-allowed disabled:opacity-50 lg:w-auto"
                                >
                                    {creatingSchedule
                                        ? "Criando..."
                                        : "Agendar"}
                                </button>
                            </div>

                        </div>
                    </div>

                    {/* ============================ */}
                    {/* LISTA DE AGENDAMENTOS */}
                    {/* ============================ */}

                    <div className="mt-6 space-y-4">

                        {scheduledScans.length === 0 ? (
                            <div className="rounded-xl border border-dashed border-[#0f3a46] px-6 py-10 text-center">
                                <p className="text-sm text-slate-400">
                                    Nenhum scan automático
                                    configurado.
                                </p>
                            </div>
                        ) : (
                            scheduledScans.map(
                                (schedule) => {
                                    const currentInterval =
                                        editedIntervals[
                                            schedule.id
                                        ] ??
                                        String(
                                            schedule.interval_minutes
                                        );

                                    const isSaving =
                                        savingScheduleId ===
                                        schedule.id;

                                    return (
                                        <div
                                            key={
                                                schedule.id
                                            }
                                            className="rounded-xl border border-[#0f3a46] bg-[#121521] p-5"
                                        >

                                            {/* ============================ */}
                                            {/* CABEÇALHO */}
                                            {/* ============================ */}

                                            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

                                                <div className="min-w-0">
                                                    <div className="flex flex-wrap items-center gap-3">

                                                        <h3 className="break-all text-base font-semibold text-white">
                                                            {
                                                                schedule.repository_url
                                                            }
                                                        </h3>

                                                        <span
                                                            className={
                                                                schedule.enabled
                                                                    ? "rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400"
                                                                    : "rounded-full bg-slate-500/10 px-3 py-1 text-xs font-semibold text-slate-400"
                                                            }
                                                        >
                                                            {schedule.enabled
                                                                ? "Ativo"
                                                                : "Desativado"}
                                                        </span>

                                                    </div>
                                                </div>

                                            </div>

                                            {/* ============================ */}
                                            {/* CONFIGURAÇÃO */}
                                            {/* ============================ */}

                                            <div className="mt-5 grid gap-4 lg:grid-cols-[180px_1fr_1fr]">

                                                {/* INTERVALO */}

                                                <div className="rounded-lg border border-[#0f3a46] bg-[#121521] p-4">

                                                    <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
                                                        Intervalo
                                                    </label>

                                                    <div className="flex items-center gap-2">

                                                        <input
                                                            type="number"
                                                            min={10}
                                                            step={1}
                                                            value={
                                                                currentInterval
                                                            }
                                                            onChange={(
                                                                event
                                                            ) =>
                                                                handleIntervalChange(
                                                                    schedule.id,
                                                                    event
                                                                        .target
                                                                        .value
                                                                )
                                                            }
                                                            className="w-full rounded-lg border border-[#0f3a46] bg-[#001017] px-3 py-2 text-sm font-semibold text-white outline-none transition focus:border-cyan-400"
                                                        />

                                                        <span className="text-sm text-slate-400">
                                                            min
                                                        </span>

                                                    </div>

                                                    <p className="mt-2 text-xs text-slate-500">
                                                        Mínimo: 10 minutos
                                                    </p>

                                                </div>

                                                {/* ÚLTIMA EXECUÇÃO */}

                                                <div className="rounded-lg border border-[#0f3a46] bg-[#121521] p-4">

                                                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                                                        Última execução
                                                    </p>

                                                    <p className="mt-2 text-sm font-medium text-slate-200">
                                                        {
                                                            formatScheduleDate(
                                                                schedule.last_finished_at
                                                            )
                                                        }
                                                    </p>

                                                </div>

                                                {/* PRÓXIMA EXECUÇÃO */}

                                                <div className="rounded-lg border border-[#0f3a46] bg-[#121521] p-4">

                                                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                                                        Próxima execução
                                                    </p>

                                                    <p className="mt-2 text-sm font-medium text-slate-200">
                                                        {
                                                            schedule.enabled
                                                                ? formatScheduleDate(
                                                                      schedule.next_run_at
                                                                  )
                                                                : "Desativado"
                                                        }
                                                    </p>

                                                </div>

                                            </div>

                                            {/* ============================ */}
                                            {/* AÇÕES */}
                                            {/* ============================ */}

                                            <div className="mt-5 flex flex-col gap-3 border-t border-[#0f3a46] pt-5 sm:flex-row sm:flex-wrap">

                                                {/* ATIVAR / DESATIVAR */}

                                                <button
                                                    onClick={() =>
                                                        handleToggleScheduledScan(
                                                            schedule
                                                        )
                                                    }
                                                    disabled={
                                                        isSaving
                                                    }
                                                    className={
                                                        schedule.enabled
                                                            ? "rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-semibold text-amber-400 transition hover:bg-amber-500/20 disabled:cursor-not-allowed disabled:opacity-50"
                                                            : "rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-400 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-50"
                                                    }
                                                >
                                                    {isSaving
                                                        ? "Salvando..."
                                                        : schedule.enabled
                                                        ? "Desativar"
                                                        : "Ativar"}
                                                </button>

                                                {/* SALVAR INTERVALO */}

                                                <button
                                                    onClick={() =>
                                                        handleSaveScheduledScan(
                                                            schedule
                                                        )
                                                    }
                                                    disabled={
                                                        isSaving
                                                    }
                                                    className="rounded-lg bg-[#26e238] px-4 py-2 text-sm font-semibold text-[#001017] transition hover:bg-[#4aeb59] disabled:cursor-not-allowed disabled:opacity-50"
                                                >
                                                    {isSaving
                                                        ? "Salvando..."
                                                        : "Salvar intervalo"}
                                                </button>

                                                {/* EXCLUIR */}

                                                <button
                                                    onClick={() =>
                                                        handleDeleteScheduledScan(
                                                            schedule.id
                                                        )
                                                    }
                                                    disabled={
                                                        isSaving
                                                    }
                                                    className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-400 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-50"
                                                >
                                                    Excluir
                                                </button>

                                            </div>

                                        </div>
                                    );
                                }
                            )
                        )}

                    </div>

                </section>

                {/* ============================ */}
                {/* NOVO SCAN MANUAL */}
                {/* ============================ */}

                <section className="mb-8 rounded-[14px] border border-[#0f3a46] bg-[#121521] p-6">

                    <div className="mb-5">
                        <h2 className="text-xl font-semibold">
                            Novo Scan
                        </h2>

                        <p className="mt-1 text-sm text-slate-400">
                            Execute uma análise manualmente.
                        </p>
                    </div>

                    <div className="flex flex-col gap-3 lg:flex-row">

                        <input
                            type="url"
                            value={repoUrl}
                            onChange={(event) =>
                                setRepoUrl(
                                    event.target.value
                                )
                            }
                            placeholder="https://github.com/empresa/repositorio.git"
                            disabled={loading}
                            className="flex-1 rounded-lg border border-[#0f3a46] bg-[#001017] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400 disabled:opacity-50"
                        />

                        <button
                            onClick={
                                handleStartScan
                            }
                            disabled={loading}
                            className="rounded-lg bg-[#26e238] px-6 py-3 text-sm font-semibold text-[#001017] transition hover:bg-[#4aeb59] disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {loading
                                ? "Executando..."
                                : "Iniciar Scan"}
                        </button>

                    </div>

                </section>

                {/* ============================ */}
                {/* PROGRESSO */}
                {/* ============================ */}

                {taskId && (
                    <section className="mb-8 rounded-[14px] border border-[#0f3a46] bg-[#121521] p-6">

                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-semibold">
                                Progresso do Scan
                            </h2>

                            <span className="text-lg font-bold text-cyan-400">
                                {progress}%
                            </span>
                        </div>

                        <div className="mt-4 h-3 overflow-hidden rounded-full bg-[#0f3a46]">
                            <div
                                className="h-full rounded-full bg-cyan-500 transition-all duration-500"
                                style={{
                                    width: `${Math.min(
                                        Math.max(
                                            progress,
                                            0
                                        ),
                                        100
                                    )}%`,
                                }}
                            />
                        </div>

                        <p className="mt-3 text-sm text-slate-400">
                            {progressMessage ||
                                "Aguardando atualização..."}
                        </p>

                    </section>
                )}

                {/* ============================ */}
                {/* HISTÓRICO */}
                {/* ============================ */}

                <section className="rounded-[14px] border border-[#0f3a46] bg-[#121521] p-6">

                    <div className="mb-5">
                        <h2 className="text-xl font-semibold">
                            Histórico de Scans
                        </h2>

                        <p className="mt-1 text-sm text-slate-400">
                            Últimas análises executadas.
                        </p>
                    </div>

                    {scans.length === 0 ? (
                        <div className="rounded-xl border border-dashed border-[#0f3a46] px-6 py-10 text-center">
                            <p className="text-sm text-slate-400">
                                Nenhum scan encontrado.
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto rounded-xl border border-[#0f3a46]">

                            <table className="w-full min-w-[700px] text-left">

                                <thead className="bg-[#121521]">
                                    <tr>
                                        <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                            ID
                                        </th>

                                        <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                            Repositório
                                        </th>

                                        <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                            Status
                                        </th>

                                        <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                            Finalizado em
                                        </th>
                                    </tr>
                                </thead>

                                <tbody className="divide-y divide-[#0f3a46]">

                                    {scans.map(
                                        (scan) => (
                                            <tr
                                                key={
                                                    scan.id
                                                }
                                                className="transition hover:bg-[#1a1f31]"
                                            >

                                                <td className="px-5 py-4 text-sm font-semibold text-slate-200">
                                                    {
                                                        scan.id
                                                    }
                                                </td>

                                                <td className="max-w-[500px] px-5 py-4 text-sm text-slate-300">
                                                    <div className="truncate">
                                                        {
                                                            scan.repository_url
                                                        }
                                                    </div>
                                                </td>

                                                <td className="px-5 py-4">

                                                    <span
                                                        className={
                                                            scan.status ===
                                                            "completed"
                                                                ? "rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400"
                                                                : scan.status ===
                                                                  "failed"
                                                                ? "rounded-full bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-400"
                                                                : "rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-400"
                                                        }
                                                    >
                                                        {
                                                            scan.status
                                                        }
                                                    </span>

                                                </td>

                                                <td className="px-5 py-4 text-sm text-slate-400">
                                                    {
                                                        formatScheduleDate(
                                                            scan.finished_at
                                                        )
                                                    }
                                                </td>

                                            </tr>
                                        )
                                    )}

                                </tbody>

                            </table>

                        </div>
                    )}

                </section>

            </div>
        </main>
    );
}