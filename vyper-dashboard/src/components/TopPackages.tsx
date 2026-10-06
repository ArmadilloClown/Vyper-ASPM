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


export default function TopPackages({data}:Props){


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

Top Vulnerable Packages

</h2>


<div className="space-y-4">


{
data.map((pkg,index)=>(


<div

key={index}

className="
flex
justify-between
bg-[#121521]
rounded-xl
p-4
"

>


<span className="text-white">

{pkg.package}

</span>


<span className="text-cyan-400 font-bold">

{pkg.total}

</span>


</div>


))

}


</div>


</div>


)


}