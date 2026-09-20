import { useState, type FormEvent } from "react";
import { api } from "../api";
import type { User } from "../types";
export function Auth({ onUser }: { onUser: (u: User) => void }) {
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
        <div className="return-promise"><img src="/branding/nowearnow-return-tag-icon.svg" alt="" width="44" height="49" /><span>A small tag.<br /><strong>A way back home.</strong></span></div>
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
