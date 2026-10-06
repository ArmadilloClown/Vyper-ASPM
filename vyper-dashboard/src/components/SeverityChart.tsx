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
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Cell
} from "recharts";

interface Props {

    data:{
        severity:string;
        total:number;
    }[];

}

const colors:any={

    CRITICAL:"#FF4D5E",
    HIGH:"#FF9F43",
    MEDIUM:"#F5D142",
    WARNING:"#4FD6E4",
    LOW:"#00B9CA",
    INFO:"#8B96AB"

};

export default function SeverityChart({

    data

}:Props){

    return(

        <div
            className="
                rounded-[14px]
                bg-[#1a1f31]
                border
                border-[#0f3a46]
                p-8
                shadow-xl
            "
        >

            <h2 className="text-xl font-semibold text-white mb-6">

                Severity Distribution

            </h2>

            <ResponsiveContainer
                width="100%"
                height={330}
            >

                <BarChart
                    data={data}
                >

                    <CartesianGrid
                        stroke="#0f3a46"
                        vertical={false}
                    />

                    <XAxis
                        dataKey="severity"
                        stroke="#8b96ab"
                    />

                    <YAxis
                        stroke="#8b96ab"
                    />

                    <Tooltip
                        contentStyle={{
                            background:"#1a1f31",
                            border:"1px solid #0f3a46",
                            borderRadius:12,
                            color:"white"
                        }}
                    />

                    <Bar
                        dataKey="total"
                        radius={[8,8,0,0]}
                    >

                        {

                            data.map((entry,index)=>(

                                <Cell

                                    key={index}

                                    fill={
                                        colors[entry.severity]
                                    }

                                />

                            ))

                        }

                    </Bar>

                </BarChart>

            </ResponsiveContainer>

        </div>

    );

}