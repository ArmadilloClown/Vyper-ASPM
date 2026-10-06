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


interface Props{

data:any[];

}


export default function AssetsTable({data}:Props){


return(

<div

className="
bg-[#1a1f31]
border
border-[#0f3a46]
rounded-[14px]
p-6
"

>


<h2 className="text-xl font-semibold text-white mb-6">

Assets Discovery

</h2>



<table className="w-full">


<thead>

<tr className="text-gray-400 border-b border-gray-700">


<th className="text-left p-3">

Type

</th>


<th className="text-left p-3">

Asset

</th>


</tr>

</thead>



<tbody>


{
data.slice(0,10).map((asset,index)=>(


<tr

key={index}

className="
border-b
border-gray-800
hover:bg-[#121521]
"

>


<td className="p-3 text-cyan-400">

{asset.asset_type}

</td>


<td className="p-3 text-white">

{asset.value}

</td>


</tr>


))

}


</tbody>


</table>


</div>


)


}