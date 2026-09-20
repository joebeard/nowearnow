import { useState, useEffect, type FormEvent } from "react";
import { api } from "../api";
import { submissionId } from "../id";
export function Finder({ token }: { token: string }) {
  const [info, setInfo] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [website, setWebsite] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [submission] = useState(submissionId);
  useEffect(() => {
    api<{ public_text: string }>(`scan/${token}/`)
      .then((x) => setInfo(x.public_text))
      .catch(() => setError("This label is unavailable."));
  }, [token]);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api(`scan/${token}/`, "POST", {
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
