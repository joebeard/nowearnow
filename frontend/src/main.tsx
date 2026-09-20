import { StrictMode, useEffect, useState, type MouseEvent } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import { Auth } from "./pages/Auth";
import { Finder } from "./pages/Finder";
import { ManageFamily } from "./pages/ManageFamily";
import { Objects } from "./pages/Objects";
import { Messages } from "./pages/Messages";
import { SheetBuilder } from "./SheetBuilder";
import type { User, Profile, Belonging, Report, RunAction } from "./types";
import "./style.css";

const initialAction = {path:window.location.pathname,token:window.location.hash.slice(1)};
if(initialAction.token) history.replaceState(null,'',window.location.pathname);
const sections = [{path:'/dashboard',label:'Overview',symbol:'⌂'}, {path:'/family',label:'Manage family',symbol:'♡'}, {path:'/objects',label:'Objects',symbol:'◇'}, {path:'/labels',label:'Print labels',symbol:'▦'}, {path:'/messages',label:'Messages',symbol:'✉'}, {path:'/account',label:'Account',symbol:'○'}];
function Brand(){return <a className="brand" href="/" aria-label="nowearnow home"><img src="/branding/nowearnow-return-tag.svg" alt="nowearnow" width="240" height="56" /></a>;}
function Workspace({user,setUser,path,navigate}:{user:User;setUser:(u:User|null)=>void;path:string;navigate:(path:string)=>void}) {
  const [profiles,setProfiles]=useState<Profile[]>([]);const [objects,setObjects]=useState<Belonging[]>([]);const [reports,setReports]=useState<Report[]>([]);
  const [quantities,setQuantities]=useState<Record<string,number>>({});const [selected,setSelected]=useState('all');
  const [busy,setBusy]=useState(false);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const [notice,setNotice]=useState('');
  const [actionDone,setActionDone]=useState(false);
  const active=profiles.filter(p=>!p.archived);
  const page=path==='/'?'/dashboard':['/verify','/invite'].includes(path)?'/account':path;
  async function refresh(){const [p,o,m]=await Promise.all([api<Profile[]>('profiles/'),api<Belonging[]>('objects/'),api<Report[]>('inbox/')]);setProfiles(p);setObjects(o);setReports(m);setSelected(old=>old==='all'||p.some(x=>x.id===old&&!x.archived)?old:'all');}
  useEffect(()=>{refresh().catch(e=>setError(e.message)).finally(()=>setLoading(false));},[]);
  useEffect(()=>{document.title=`${sections.find(s=>s.path===page)?.label||'nowearnow'} · nowearnow`;},[page]);
  const run:RunAction=async(fn,message='')=>{setBusy(true);setError('');setNotice('');try{await fn();await refresh();setNotice(message);return true;}catch(e){setError((e as Error).message);return false;}finally{setBusy(false);}};
  function go(destination:string){setError('');setNotice('');navigate(destination);window.scrollTo({top:0});}
  function nav(event:MouseEvent<HTMLAnchorElement>,destination:string){if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();go(destination);}
  async function sample(){const success=await run(async()=>{let profile=active.find(p=>p.kind==='family')||active[0];let id=profile?.id;if(!id){id=(await api<{id:string}>('profiles/','POST',{name:'Sample family',kind:'family'})).id;}const object=await api<Belonging>('objects/','POST',{profile:id,name:'Sample belongings',kind:'group'});setQuantities(old=>({...old,[object.id]:1}));},'Sample object created. Preview your sheet to see its QR.');if(success)navigate('/labels');}
  return <><header className="app-header no-print"><Brand/><span className="header-note">a little peace of mind</span></header>
    <div className="app-frame"><aside className="app-sidebar no-print"><nav aria-label="Main navigation">{sections.map(s=><a key={s.path} href={s.path} aria-current={page===s.path?'page':undefined} onClick={e=>nav(e,s.path)}><span aria-hidden="true">{s.symbol}</span>{s.label}{s.path==='/labels'&&Object.values(quantities).reduce((a,b)=>a+b,0)>0&&<small>{objects.filter(o=>o.label.active).reduce((n,o)=>n+(quantities[o.id]||0),0)}</small>}</a>)}</nav><div className="sidebar-account"><span className="avatar" aria-hidden="true">{user.username.slice(0,1).toUpperCase()}</span><span><strong>{user.username}</strong><small>Your private space</small></span></div></aside>
    <div className="page-content"><div className="no-print">{error&&<p role="alert" className="error">{error}</p>}{notice&&<p role="status" className="notice">{notice}</p>}{loading&&<p role="status">Loading your family and objects…</p>}</div>
      {!loading&&<>
        {page==='/dashboard'&&<><div className="page-heading"><div><p className="eyebrow">Your little lost-and-found</p><h1>Hello, {user.username}.</h1><p>A home for your family’s belongings. Where would you like to start?</p></div></div>
          <div className="overview-stats"><button onClick={()=>go('/family')}><strong>{active.filter(p=>p.kind==='child').length}</strong><span>Children</span></button><button onClick={()=>go('/objects')}><strong>{objects.length}</strong><span>Objects</span></button><button onClick={()=>go('/messages')}><strong>{reports.length}</strong><span>Recent messages</span></button></div>
          <div className="quick-actions"><article className="panel"><span className="eyebrow">01 · People first</span><h2>Your family, your way</h2><p>Add children and adults, organize family groups and decide who can help manage each profile.</p><button onClick={()=>go('/family')}>Manage family</button></article><article className="panel"><span className="eyebrow">02 · A way back home</span><h2>Make it theirs</h2><p>Add a laptop, a lunch bag or a clothing group. Each object keeps its own QR code.</p><button className="secondary" onClick={()=>go('/objects')}>Manage objects</button></article><article className="panel"><span className="eyebrow">03 · Mix & match</span><h2>A sheet for everyone</h2><p>Choose quantities across your objects and print a mixed sheet of labels.</p><button className="secondary" onClick={()=>go('/labels')}>Build a label sheet</button></article></div>
          <div className="panel getting-started"><div><h2>Just trying things out?</h2><p>Make a sample object with a private QR and preview a label.</p></div><button className="secondary" disabled={busy} onClick={sample}>Make a sample QR</button></div>
        </>}
        {page==='/family'&&<ManageFamily profiles={profiles} objects={objects} user={user} run={run} busy={busy} viewObjects={id=>{setSelected(id);go('/objects');}}/>}
        {page==='/objects'&&<Objects profiles={profiles} objects={objects} selected={selected} setSelected={setSelected} run={run} busy={busy} manageFamily={()=>go('/family')} addToSheet={id=>{setQuantities(old=>({...old,[id]:Math.min(180,(old[id]||0)+1)}));go('/labels');}}/>}
        {page==='/labels'&&<><div className="page-heading no-print"><div><p className="eyebrow">Ready, set, stick</p><h1>Print labels</h1><p>One sheet can include objects from different children, adults and families.</p></div><button className="secondary" onClick={()=>go('/objects')}>Manage objects</button></div><SheetBuilder objects={objects} quantities={quantities} setQuantities={setQuantities}/></>}
        {page==='/messages'&&<Messages reports={reports} busy={busy} refresh={()=>run(async()=>{},'Messages refreshed.')}/>}
        {page==='/account'&&<><div className="page-heading"><div><p className="eyebrow">Your own little corner</p><h1>Account</h1><p>Manage your sign-in session and verify your email for guardian invitations and alerts.</p></div></div>
          <section className="panel account-panel"><h2>{user.username}</h2><p className="tag">{user.email_verified?'Email verified':'Email not verified'}</p>{!user.email_verified&&<><p>Verify your email, then choose which profiles should send you found-item alerts.</p><button disabled={busy} onClick={()=>run(()=>api('auth/verify/','POST'),'Verification email sent. Follow its link to confirm your address.')}>Send verification email</button></>}
            <div className="management-section"><h3>Notification preferences</h3><p>Each guardian chooses their own alerts for each profile.</p><button className="secondary" onClick={()=>go('/family')}>Manage family notifications</button></div>
            {user.is_staff&&<div className="management-section"><h3>Site administration</h3><a className="button secondary" href="/admin/" target="_blank" rel="noreferrer">Open Django admin</a></div>}
            <div className="management-section"><button className="secondary" disabled={busy} onClick={async()=>{setBusy(true);try{await api('auth/logout/','POST');setUser(null);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}}>Log out</button></div>
          </section>
          {initialAction.token&&!actionDone&&['/verify','/invite'].includes(initialAction.path)&&<section className="panel action-panel"><h2>{initialAction.path==='/verify'?'Confirm your email':'Accept guardian access'}</h2><p>Confirm using the account this invitation or verification link was sent to.</p><button disabled={busy} onClick={()=>run(async()=>{if(initialAction.path==='/verify'){const result=await api<{user:User}>('auth/verify/confirm/','POST',{token:initialAction.token});setUser(result.user);}else{await api(`invitations/${initialAction.token}/accept/`,'POST');}setActionDone(true);navigate('/account');},'Confirmed.')}>Confirm</button></section>}
        </>}
        {!sections.some(s=>s.path===page)&&<section className="panel empty-state"><h1>Page not found</h1><button onClick={()=>go('/dashboard')}>Go to overview</button></section>}
      </>}
    </div></div><footer className="no-print">Little labels. Less worry. <span>nowearnow.com</span></footer>
  </>;
}
function App(){const[user,setUser]=useState<User|null>(null);const[ready,setReady]=useState(false);const[error,setError]=useState('');const[path,setPath]=useState(window.location.pathname);
  useEffect(()=>{api<{user:User|null}>('auth/session/').then(x=>{setUser(x.user);setReady(true);}).catch(()=>setError('Unable to connect. Start the backend and refresh this page.'));},[]);
  useEffect(()=>{const update=()=>setPath(window.location.pathname);window.addEventListener('popstate',update);return()=>window.removeEventListener('popstate',update);},[]);
  function navigate(destination:string){if(window.location.pathname!==destination)history.pushState(null,'',destination);setPath(destination);}
  const token=path.match(/^\/s\/([a-f0-9-]+)\/?$/i)?.[1];
  return <main>{!ready?<><header><Brand/></header><p role="status">{error||'Getting things ready…'}</p></>:token?<><header><Brand/></header><Finder token={token}/></>:user?<Workspace user={user} setUser={setUser} path={path} navigate={navigate}/>:<><header><Brand/><span className="header-note">a way back home</span></header><Auth onUser={setUser}/></>}</main>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><App/></StrictMode>);
