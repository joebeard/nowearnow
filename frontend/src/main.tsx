import { StrictMode, useEffect, useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import "./style.css";

type User = { username: string; email_verified: boolean };
type Profile = {
  id: string;
  name: string;
  kind: string;
  controller: boolean;
  email_alerts: boolean;
};
type Label = {
  id: string;
  profile: string;
  item_name: string;
  print_text: string;
  public_text: string;
  share_text: boolean;
  active: boolean;
  scan_url: string;
  qr_url: string;
};
type Report = {
  id: string;
  message: string;
  profile: string;
  item_name: string;
  created_at: string;
};
type Access = { id: number; username: string; controller: boolean };
const scanToken = window.location.pathname.match(
  /^\/s\/([a-f0-9-]+)\/?$/i,
)?.[1];
const landingAction = window.location.pathname;
const actionToken = window.location.hash.slice(1);
if (actionToken) history.replaceState(null, "", window.location.pathname);

function Brand() {
  return (
    <a className="brand" href="/">
      nowearnow
      <span className="brand-flower" aria-hidden="true">
        ✿
      </span>
    </a>
  );
}
function Sticker({ label, onLoad }: { label: Label; onLoad?: () => void }) {
  return (
    <div className="sticker">
      <div className="sticker-brand">
        nowearnow<span aria-hidden="true">✿</span>
      </div>
      <img
        src={label.qr_url}
        alt="Scan to help return this item"
        onLoad={onLoad}
      />
      {label.print_text && (
        <div className="sticker-name">{label.print_text}</div>
      )}
      <div className="sticker-footer">
        found me? scan me! <span aria-hidden="true">↗</span>
      </div>
    </div>
  );
}
function Finder() {
  const [info, setInfo] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [website, setWebsite] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [submission] = useState(() => crypto.randomUUID());
  useEffect(() => {
    api<{ public_text: string }>(`scan/${scanToken}/`)
      .then((x) => setInfo(x.public_text))
      .catch(() => setError("This label is unavailable."));
  }, []);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api(`scan/${scanToken}/`, "POST", {
        message,
        website,
        submission_id: submission,
      });
      setSent(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="finder panel">
      <span className="eyebrow">A little kindness goes a long way</span>
      <h1>Found something?</h1>
      <p>Help this item find its way home.</p>
      {info === null ? (
        <p role="status">{error || "Looking up this label…"}</p>
      ) : (
        <>
          {info && <div className="public-info">{info}</div>}
          {sent ? (
            <div className="notice" role="status">
              Thank you! Your message has been received.
            </div>
          ) : (
            <form onSubmit={submit}>
              <label>
                Your message
                <textarea
                  required
                  maxLength={1500}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Where can the item be collected?"
                />
              </label>
              <p className="hint">
                Your message will be shared with the authorized guardians. Avoid
                including sensitive information.
              </p>
              <div className="honeypot" aria-hidden="true">
                <label>
                  Website
                  <input
                    tabIndex={-1}
                    autoComplete="off"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                  />
                </label>
              </div>
              <button disabled={busy}>
                {busy ? "Sending…" : "Send a message"}
              </button>
              {error && (
                <p role="alert" className="error">
                  {error}
                </p>
              )}
            </form>
          )}
        </>
      )}
    </section>
  );
}
function Auth({ onUser }: { onUser: (u: User) => void }) {
  const [register, setRegister] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const fields = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const result = await api<{ user: User }>(
        `auth/${register ? "register" : "login"}/`,
        "POST",
        fields,
      );
      onUser(result.user);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="welcome">
      <section>
        <p className="eyebrow">Little labels. Happy reunions.</p>
        <h1>
          Out exploring.
          <br />
          Back belonging.
        </h1>
        <p className="intro">
          Make a little label for the things you love. Keep personal details
          private, and give lost things a way home.
        </p>
        <div className="fun-shapes" aria-hidden="true">
          <span>✿</span>
          <span>↗</span>
          <span>☺</span>
        </div>
      </section>
      <section className="panel">
        <h2>{register ? "Create your account" : "Welcome back"}</h2>
        <p>For parents and guardians.</p>
        <form onSubmit={submit}>
          <label>
            Username
            <input
              name="username"
              required
              maxLength={150}
              autoComplete="username"
            />
          </label>
          {register && (
            <label>
              Email
              <input name="email" type="email" required autoComplete="email" />
            </label>
          )}
          <label>
            Password
            <input
              name="password"
              type="password"
              required
              maxLength={128}
              autoComplete={register ? "new-password" : "current-password"}
            />
          </label>
          {register && (
            <p className="hint">
              Use a long, unique password, not a name or common phrase.
            </p>
          )}
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          <button disabled={busy}>
            {busy ? "Please wait…" : register ? "Create account" : "Log in"}
          </button>
        </form>
        <button
          className="text-button"
          onClick={() => {
            setRegister(!register);
            setError("");
          }}
        >
          {register
            ? "Already registered? Log in"
            : "New here? Create an account"}
        </button>
      </section>
    </div>
  );
}
function LabelEditor({
  label,
  controller,
  busy,
  save,
}: {
  label: Label;
  controller: boolean;
  busy: boolean;
  save: (changes: {
    print_text: string;
    public_text?: string;
    share_text?: boolean;
  }) => void;
}) {
  const [printText, setPrintText] = useState(label.print_text);
  const [publicText, setPublicText] = useState(label.public_text);
  const [share, setShare] = useState(label.share_text);
  useEffect(() => {
    setPrintText(label.print_text);
    setPublicText(label.public_text);
    setShare(label.share_text);
  }, [label.print_text, label.public_text, label.share_text]);
  return (
    <details>
      <summary>Edit label text</summary>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          save({
            print_text: printText,
            ...(controller
              ? { public_text: publicText, share_text: share }
              : {}),
          });
        }}
      >
        <label>
          Printed text
          <input
            maxLength={80}
            value={printText}
            onChange={(e) => setPrintText(e.target.value)}
          />
        </label>
        <p className="hint">
          Visible on the sticker. Reprint to apply changes to physical labels.
        </p>
        {controller && (
          <>
            <label>
              Scan-page text
              <textarea
                maxLength={200}
                value={publicText}
                onChange={(e) => setPublicText(e.target.value)}
              />
            </label>
            <label className="check">
              <input
                type="checkbox"
                checked={share}
                onChange={(e) => setShare(e.target.checked)}
              />
              Show scan-page text publicly
            </label>
            <p className="hint">
              Scanner sees:{" "}
              {share && publicText
                ? publicText
                : "Generic guidance and a message form only."}
            </p>
          </>
        )}
        <button disabled={busy}>Save label text</button>
      </form>
    </details>
  );
}
function Dashboard({
  user,
  setUser,
}: {
  user: User;
  setUser: (u: User | null) => void;
}) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [labels, setLabels] = useState<Label[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [selected, setSelected] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [printing, setPrinting] = useState<Label | null>(null);
  const [copies, setCopies] = useState(18);
  const [loaded, setLoaded] = useState(0);
  const [paper, setPaper] = useState("A4");
  const [members, setMembers] = useState<Access[]>([]);
  const [itemName, setItemName] = useState("");
  const [printText, setPrintText] = useState("");
  const [publicText, setPublicText] = useState("");
  const [shareText, setShareText] = useState(false);
  const profile = profiles.find((p) => p.id === selected);
  async function refresh() {
    const [p, l, m] = await Promise.all([
      api<Profile[]>("profiles/"),
      api<Label[]>("labels/"),
      api<Report[]>("inbox/"),
    ]);
    setProfiles(p);
    setLabels(l);
    setReports(m);
    setSelected((old) => (p.some((x) => x.id === old) ? old : p[0]?.id || ""));
  }
  useEffect(() => {
    refresh().catch((e) => setError(e.message));
  }, []);
  useEffect(() => {
    setMembers([]);
    setShareText(false);
    if (profile?.controller)
      api<Access[]>(`profiles/${selected}/access/`)
        .then(setMembers)
        .catch((e) => setError(e.message));
  }, [selected, profile?.controller]);
  async function act(fn: () => Promise<unknown>, success = "") {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
      await refresh();
      setNotice(success);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function createProfile(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const fields = Object.fromEntries(new FormData(form));
    await act(async () => {
      const p = await api<{ id: string }>("profiles/", "POST", fields);
      setSelected(p.id);
      form.reset();
    }, "Profile added. Its name stays private.");
  }
  async function sample() {
    await act(async () => {
      let id = selected;
      if (!id) {
        const p = await api<{ id: string }>("profiles/", "POST", {
          name: "Sample family",
          kind: "family",
        });
        id = p.id;
        setSelected(id);
      }
      const l = await api<Label>("labels/", "POST", {
        profile: id,
        item_name: "",
        print_text: "",
        public_text: "",
        share_text: false,
      });
      setLoaded(0);
      setPrinting(l);
    }, "Sample label ready. No personal information is public.");
  }
  function printLabel(l: Label) {
    setLoaded(0);
    setPrinting(l);
  }
  const localQR =
    printing && /^http:\/\/(127\.0\.0\.1|localhost)/.test(printing.scan_url);
  return (
    <>
      <div className="dashboard-heading no-print">
        <div>
          <p className="eyebrow">Your little lost-and-found</p>
          <h1>Hello, {user.username}.</h1>
        </div>
        <button className="secondary" disabled={busy} onClick={sample}>
          Make a sample QR
        </button>
      </div>
      {error && (
        <p role="alert" className="error no-print">
          {error}
        </p>
      )}
      {notice && (
        <p role="status" className="notice no-print">
          {notice}
        </p>
      )}
      <div className="no-print account-bar">
        <span>
          {user.email_verified
            ? "Email verified"
            : "Verify your email to enable found-item alerts."}
        </span>
        {!user.email_verified && (
          <button
            className="text-button"
            disabled={busy}
            onClick={() =>
              act(
                () => api("auth/verify/", "POST"),
                "Verification email sent. Follow the link to confirm your address.",
              )
            }
          >
            Send verification email
          </button>
        )}
        <button
          className="text-button"
          onClick={() =>
            act(async () => {
              await api("auth/logout/", "POST");
              setUser(null);
            })
          }
        >
          Log out
        </button>
      </div>
      {(landingAction === "/verify" || landingAction === "/invite") &&
        actionToken && (
          <div className="panel no-print">
            <h2>
              {landingAction === "/verify"
                ? "Confirm your email"
                : "Accept shared access"}
            </h2>
            <button
              disabled={busy}
              onClick={() =>
                act(async () => {
                  if (landingAction === "/verify") {
                    const x = await api<{ user: User }>(
                      "auth/verify/confirm/",
                      "POST",
                      { token: actionToken },
                    );
                    setUser(x.user);
                  } else {
                    await api(`invitations/${actionToken}/accept/`, "POST");
                  }
                  history.replaceState(null, "", "/");
                }, "Confirmed.")
              }
            >
              Confirm
            </button>
          </div>
        )}
      <div className="workspace no-print">
        <aside className="panel">
          <h2>Who do things belong to?</h2>
          {profiles.length > 0 && (
            <label>
              Selected profile
              <select
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} · {p.kind}
                  </option>
                ))}
              </select>
            </label>
          )}
          <details open={!profiles.length}>
            <summary>Add a child, adult or family</summary>
            <form onSubmit={createProfile}>
              <label>
                Private name
                <input
                  name="name"
                  required
                  maxLength={80}
                  placeholder="e.g. a nickname or family name"
                />
              </label>
              <label>
                Profile type
                <select name="kind">
                  <option value="child">Child</option>
                  <option value="adult">Adult / parent</option>
                  <option value="family">Family</option>
                </select>
              </label>
              <button disabled={busy}>Add profile</button>
            </form>
          </details>
          {profile && (
            <>
              <hr />
              <label className="check">
                <input
                  type="checkbox"
                  checked={profile.email_alerts}
                  disabled={busy || !user.email_verified}
                  onChange={(e) =>
                    act(() =>
                      api(`profiles/${selected}/preferences/`, "PATCH", {
                        email_alerts: e.target.checked,
                      }),
                    )
                  }
                />
                Email me when something is found
              </label>
              <p className="hint">
                Applies only to {profile.name}. Each guardian chooses their own
                alerts.
              </p>
              {profile.controller && (
                <details>
                  <summary>Share with another guardian</summary>
                  <p className="hint">
                    They can manage labels and see new messages for this
                    profile. Only you can enable public text. They do not gain
                    access to your other profiles.
                  </p>
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      const form = e.currentTarget;
                      const email = new FormData(form).get("email");
                      act(
                        () =>
                          api(`profiles/${selected}/invitations/`, "POST", {
                            email,
                          }),
                        "Invitation sent.",
                      );
                    }}
                  >
                    <label>
                      Their email
                      <input name="email" type="email" required />
                    </label>
                    <button disabled={busy || !user.email_verified}>
                      Send invitation
                    </button>
                  </form>
                  {members
                    .filter((m) => !m.controller)
                    .map((m) => (
                      <p key={m.id}>
                        {m.username}{" "}
                        <button
                          className="text-button"
                          onClick={() =>
                            act(async () => {
                              await api(
                                `profiles/${selected}/access/${m.id}/`,
                                "DELETE",
                              );
                              setMembers(
                                await api<Access[]>(
                                  `profiles/${selected}/access/`,
                                ),
                              );
                            }, "Access removed.")
                          }
                        >
                          Remove access
                        </button>
                      </p>
                    ))}
                </details>
              )}
            </>
          )}
        </aside>
        <section className="panel">
          <h2>A label with a little personality</h2>
          <p>Make a general label, or give one particular thing its own QR.</p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              act(async () => {
                const l = await api<Label>("labels/", "POST", {
                  profile: selected,
                  item_name: itemName,
                  print_text: printText,
                  public_text: publicText,
                  share_text: shareText,
                });
                printLabel(l);
              }, "Label created.");
            }}
          >
            <label>
              Specific item <span className="hint">optional</span>
              <input
                maxLength={100}
                value={itemName}
                onChange={(e) => setItemName(e.target.value)}
                placeholder="Laptop, jumper… Leave blank for a general label"
              />
            </label>
            <label>
              Text printed under the QR <span className="hint">optional</span>
              <input
                maxLength={80}
                value={printText}
                onChange={(e) => setPrintText(e.target.value)}
                placeholder="Austin’s laptop · This belongs to the Smith family"
              />
            </label>
            <p className="hint">
              Printed names are visible to anyone holding the item. They will
              not appear on the scan page automatically.
            </p>
            <label>
              Text for the scan page <span className="hint">optional</span>
              <textarea
                maxLength={200}
                value={publicText}
                onChange={(e) => setPublicText(e.target.value)}
                placeholder="A message you are comfortable making public"
              />
            </label>
            <label className="check">
              <input
                type="checkbox"
                checked={shareText}
                disabled={!profile?.controller}
                onChange={(e) => setShareText(e.target.checked)}
              />
              Show this text to anyone scanning the QR
            </label>
            <div className="privacy-preview">
              <strong>Scanner will see</strong>
              <p>
                {shareText && publicText
                  ? publicText
                  : "Generic return instructions. No personal information."}
              </p>
              <small>Plus a private message form.</small>
            </div>
            <button disabled={busy || !selected}>Create label & preview</button>
          </form>
        </section>
      </div>
      <section className="no-print">
        <h2>Your labels</h2>
        {!labels.length && (
          <p>No labels yet. Start with a sample or create your own above.</p>
        )}
        <div className="label-grid">
          {labels
            .filter((l) => l.profile === selected)
            .map((l) => (
              <article key={l.id} className="panel label-card">
                <span className="tag">{l.active ? "Active" : "Disabled"}</span>
                <h3>{l.item_name || "General label"}</h3>
                <p>{l.print_text || "No printed name"}</p>
                <p className="hint">
                  Scan text:{" "}
                  {l.share_text ? l.public_text || "(empty)" : "hidden"}
                </p>
                <div className="button-row">
                  <button disabled={!l.active} onClick={() => printLabel(l)}>
                    Print sheet
                  </button>
                  <a
                    className="button secondary"
                    href={l.scan_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Preview scan
                  </a>
                </div>
                <button
                  className="text-button"
                  disabled={busy || (!l.active && !profile?.controller)}
                  onClick={() =>
                    act(
                      () =>
                        api(`labels/${l.id}/`, "PATCH", { active: !l.active }),
                      l.active ? "Label disabled." : "Label enabled.",
                    )
                  }
                >
                  {l.active ? "Disable QR" : "Enable QR"}
                </button>
                {l.share_text && (
                  <button
                    className="text-button"
                    disabled={busy}
                    onClick={() =>
                      act(
                        () =>
                          api(`labels/${l.id}/`, "PATCH", {
                            share_text: false,
                          }),
                        "Public text hidden.",
                      )
                    }
                  >
                    Hide scan text
                  </button>
                )}
                <LabelEditor
                  label={l}
                  controller={!!profile?.controller}
                  busy={busy}
                  save={(changes) =>
                    act(async () => {
                      const updated = await api<Label>(
                        `labels/${l.id}/`,
                        "PATCH",
                        changes,
                      );
                      if (printing?.id === l.id) {
                        setPrinting(updated);
                      }
                    }, "Label text saved.")
                  }
                />
              </article>
            ))}
        </div>
      </section>
      <section className="panel no-print inbox">
        <div className="button-row">
          <h2>Found-item messages</h2>
          <button className="text-button" onClick={() => act(async () => {})}>
            Refresh
          </button>
        </div>
        {!reports.length && (
          <p>
            No messages yet. They will appear here when someone reports an item.
          </p>
        )}
        {reports.map((m) => (
          <article key={m.id}>
            <h3>
              {m.profile}
              {m.item_name && ` · ${m.item_name}`}
            </h3>
            <time>{new Date(m.created_at).toLocaleString()}</time>
            <p className="message">{m.message}</p>
          </article>
        ))}
      </section>
      {printing && (
        <section className="print-preview">
          <div className="panel no-print">
            <div className="button-row">
              <h2>Your happy little labels</h2>
              <button className="text-button" onClick={() => setPrinting(null)}>
                Close preview
              </button>
            </div>
            <p>
              {printing.print_text
                ? "Your chosen text will be printed under each QR."
                : "No name or personal information will be printed."}
            </p>
            {localQR && (
              <p className="notice">
                Local sample: this QR opens this computer’s loopback address. To
                scan from a phone, configure PUBLIC_BASE_URL to an address the
                phone can reach before printing.
              </p>
            )}
            <div className="print-controls">
              <label>
                Copies
                <select
                  value={copies}
                  onChange={(e) => {
                    setCopies(Number(e.target.value));
                    setLoaded(0);
                  }}
                >
                  {[1, 6, 12, 18].map((n) => (
                    <option key={n}>{n}</option>
                  ))}
                </select>
              </label>
              <label>
                Paper
                <select
                  value={paper}
                  onChange={(e) => setPaper(e.target.value)}
                >
                  <option>A4</option>
                  <option>Letter</option>
                </select>
              </label>
              <button disabled={loaded < copies} onClick={() => window.print()}>
                {loaded < copies ? "Loading QR codes…" : "Print / save PDF"}
              </button>
            </div>
            <p className="hint">
              18-up cut-out layout: 3 × 6 labels, each 60 × 40 mm. Print at 100%
              / actual size, with browser headers and footers off. Use
              full-sheet adhesive paper and cut out; this is not a preset for
              pre-cut label stock.
            </p>
          </div>
          <style>{`@media print { @page { size: ${paper}; margin: 10mm; } }`}</style>
          <div className="sheet" key={`${printing.id}-${copies}`}>
            {Array.from({ length: copies }, (_, i) => (
              <Sticker
                key={i}
                label={printing}
                onLoad={() => setLoaded((n) => n + 1)}
              />
            ))}
          </div>
        </section>
      )}
    </>
  );
}
function App() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    api<{ user: User | null }>("auth/session/")
      .then((x) => {
        setUser(x.user);
        setReady(true);
      })
      .catch(() =>
        setError("Unable to connect. Start the backend and refresh this page."),
      );
  }, []);
  return (
    <main>
      <header className="no-print">
        <Brand />
        <span className="header-note">a way back home</span>
      </header>
      {!ready ? (
        <p role="status">{error || "Getting things ready…"}</p>
      ) : scanToken ? (
        <Finder />
      ) : user ? (
        <Dashboard user={user} setUser={setUser} />
      ) : (
        <Auth onUser={setUser} />
      )}
      <footer className="no-print">
        Little labels. Less worry. <span>nowearnow.com</span>
      </footer>
    </main>
  );
}
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
