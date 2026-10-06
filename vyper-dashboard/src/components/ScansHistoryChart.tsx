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
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";


interface Props {

    data:{
        date:string;
        total:number;
    }[];

}


export default function ScansHistoryChart({data}:Props){


return(

<div
className="
rounded-[14px]
bg-[#1a1f31]
border
border-[#0f3a46]
p-6

"
>

<h2 className="text-xl font-semibold text-white mb-6">

Scan History

</h2>


<ResponsiveContainer
width="100%"
height={320}
>


<LineChart data={data}>


<CartesianGrid
strokeDasharray="3 3"
stroke="#0f3a46"
/>


<XAxis
dataKey="date"
stroke="#8b96ab"
/>


<YAxis
stroke="#8b96ab"
/>


<Tooltip
contentStyle={{
background:"#1a1f31",
border:"1px solid #0f3a46",
borderRadius:10,
color:"#ffffff"
}}
labelStyle={{color:"#00b9ca"}}
/>


<Line

type="monotone"

dataKey="total"

stroke="#00b9ca"

strokeWidth={3}

dot={{r:5}}

 />



</LineChart>


</ResponsiveContainer>


</div>


)


}