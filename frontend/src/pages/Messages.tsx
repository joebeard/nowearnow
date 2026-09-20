import { useState } from "react";
import type { Report } from "../types";
export function Messages({reports,refresh,busy}:{reports:Report[];refresh:()=>void;busy:boolean}) {
 const [search,setSearch]=useState('');const filtered=reports.filter(r=>`${r.profile} ${r.item_name} ${r.message}`.toLowerCase().includes(search.toLowerCase()));
 return <><div className="page-heading"><div><p className="eyebrow">Good news finds its way here</p><h1>Messages</h1><p>Found-item reports shared with you. Showing up to 100 recent messages.</p></div><button className="secondary" disabled={busy} onClick={refresh}>Refresh messages</button></div><div className="panel filter-bar"><label>Search messages<input type="search" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Person, object or message"/></label></div>
 {!filtered.length?<div className="panel empty-state"><h2>{search?'No matching messages':'Nothing found yet'}</h2><p>{search?'Try another search.':'When someone scans a label and sends a message, it will appear here.'}</p></div>:<section className="message-list">{filtered.map(m=><article className="panel" key={m.id}><span className="tag">Found-item report</span><h2>{m.profile}{m.item_name&&` · ${m.item_name}`}</h2><time dateTime={m.created_at}>{new Date(m.created_at).toLocaleString()}</time><p className="message">{m.message}</p></article>)}</section>}</>;
}
