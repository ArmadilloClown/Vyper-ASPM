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


export default function TopRisks({data}:Props){


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

Top 10 Risks

</h2>



<div className="space-y-4">


{
data.map((risk)=>(
<div

key={risk.id}

className="
flex
justify-between
items-center
bg-[#121521]
rounded-xl
p-4
hover:border-cyan-400
border
border-transparent
transition
"

>


<div>

<p className="text-white font-semibold">

{risk.title}

</p>


<p className="text-gray-400 text-sm">

{risk.priority} • {risk.evidence_count} evidências

</p>


</div>


<div
className="
text-red-400
font-bold
text-xl
"
>

{risk.score}

</div>


</div>


))

}


</div>


</div>


)


}