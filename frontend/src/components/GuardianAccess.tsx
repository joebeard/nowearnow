import { useEffect, useState } from "react";
import { api } from "../api";
import type { Profile, RunAction, User } from "../types";
type Grant = { id: number; username: string; controller: boolean };
type Invitation = { id: string; email: string; expires_at: string };
export function GuardianAccess({profile, user, run, busy}: {profile:Profile; user:User; run:RunAction; busy:boolean}) {
  const [grants, setGrants] = useState<Grant[]>([]); const [invites, setInvites] = useState<Invitation[]>([]);
  const [error, setError] = useState(''); const [removing, setRemoving] = useState<number|null>(null);
  async function refresh() { const [g,i] = await Promise.all([api<Grant[]>(`profiles/${profile.id}/access/`), api<Invitation[]>(`profiles/${profile.id}/invitations/`)]); setGrants(g); setInvites(i); }
  useEffect(() => {let live=true; Promise.all([api<Grant[]>(`profiles/${profile.id}/access/`), api<Invitation[]>(`profiles/${profile.id}/invitations/`)]).then(([g,i]) => {if(live){setGrants(g);setInvites(i);}}).catch(e=>{if(live)setError(e.message);}); return()=>{live=false;};},[profile.id]);
  return <section className="management-section"><h3>Guardian access for {profile.name}</h3>
    <p className="hint">Invitations apply only to this profile. Sharing a family group does not share its children. Guardians can manage objects and see new messages; only the profile manager can change public information or manage access.</p>
    {error && <p role="alert" className="error">{error}</p>}
    <ul className="people-list">{grants.map(g=><li key={g.id}><span><strong>{g.username}</strong><small>{g.controller?'Profile manager':'Guardian'}</small></span>{!g.controller && <button className="text-button" disabled={busy} onClick={()=>setRemoving(g.id)}>Remove access for {g.username}</button>}
      {removing===g.id && <div className="inline-confirm"><p>Remove {g.username}’s access to {profile.name}? Their other profiles are unaffected. They will lose access and stop receiving future alerts for this profile.</p><button disabled={busy} onClick={()=>run(async()=>{await api(`profiles/${profile.id}/access/${g.id}/`,'DELETE');await refresh();setRemoving(null);},'Guardian access removed.')}>Confirm removal</button><button className="text-button" onClick={()=>setRemoving(null)}>Cancel</button></div>}
    </li>)}</ul>
    <form onSubmit={async e=>{e.preventDefault();const form=e.currentTarget;const email=new FormData(form).get('email');if(await run(async()=>{await api(`profiles/${profile.id}/invitations/`,'POST',{email});await refresh();},'Invitation sent. Access begins only after the recipient accepts.'))form.reset();}}>
      <label>Guardian email<input name="email" type="email" required autoComplete="off"/></label><button disabled={busy||!user.email_verified}>Invite guardian to {profile.name}</button>
      {!user.email_verified&&<p className="hint">Verify your email on the Account page before inviting someone.</p>}
    </form>
    {invites.length>0&&<><h4>Pending invitations</h4><ul className="people-list">{invites.map(i=><li key={i.id}><span>{i.email}<small>Expires {new Date(i.expires_at).toLocaleString()}</small></span><button className="text-button" disabled={busy} onClick={()=>run(async()=>{await api(`profiles/${profile.id}/invitations/${i.id}/`,'DELETE');await refresh();},'Invitation cancelled.')}>Cancel invitation to {i.email}</button></li>)}</ul></>}
  </section>;
}
