import { useEffect, useState } from "react";
import { api } from "./api";
import type { Belonging, Label, SheetPreview } from "./types";

function Sticker({
  label,
  loaded,
  failed,
}: {
  label: Label;
  loaded: () => void;
  failed: () => void;
}) {
  return (
    <div className="sticker">
      <div className="sticker-brand">
        nowearnow<span aria-hidden="true">✿</span>
      </div>
      <img
        src={label.qr_url}
        alt="Scan to help return this object"
        onLoad={loaded}
        onError={failed}
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
export function SheetBuilder({
  objects,
  quantities,
  setQuantities,
}: {
  objects: Belonging[];
  quantities: Record<string, number>;
  setQuantities: (value: Record<string, number>) => void;
}) {
  const [paper, setPaper] = useState<"A4" | "Letter">("A4");
  const [preview, setPreview] = useState<SheetPreview | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loaded, setLoaded] = useState(0);
  const [failed, setFailed] = useState(false);
  const active = objects.filter((o) => o.label.active);
  const entries = active
    .filter((o) => (quantities[o.id] || 0) > 0)
    .map((o) => ({ object_id: o.id, quantity: quantities[o.id] }));
  const total = entries.reduce((n, e) => n + e.quantity, 0);
  const fingerprint = JSON.stringify({ objects, quantities, paper });
  useEffect(() => {
    setPreview(null);
    setLoaded(0);
    setFailed(false);
  }, [fingerprint]);
  async function build() {
    setBusy(true);
    setError("");
    setPreview(null);
    setLoaded(0);
    setFailed(false);
    try {
      setPreview(
        await api<SheetPreview>("sheets/preview/", "POST", { entries, paper }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="sheet-builder" id="sheet-builder">
      <div className="panel no-print">
        <p className="eyebrow">Mix, match, stick</p>
        <h2>Build your label sheets</h2>
        <p>
          Choose how many labels you want for each object. Mix different
          children, adults and families on the same sheet.
        </p>
        {!objects.length && <p>Add an object above to get started.</p>}
        <div className="quantity-list">
          {objects.map((o) => (
            <div className="quantity-row" key={o.id}>
              <div>
                <strong>{o.name}</strong>
                <span>
                  {o.profile_name} ·{" "}
                  {o.kind === "group" ? "Reusable group" : "Specific item"}
                  {!o.label.active && " · QR disabled"}
                </span>
              </div>
              <label>
                Labels for {o.name} — {o.profile_name}
                <input
                  type="number"
                  min={0}
                  max={180}
                  step={1}
                  disabled={!o.label.active || busy}
                  value={o.label.active ? quantities[o.id] || 0 : 0}
                  onChange={(e) => {
                    const n = Number(e.target.value);
                    setQuantities({
                      ...quantities,
                      [o.id]: Number.isFinite(n)
                        ? Math.max(0, Math.min(180, Math.floor(n)))
                        : 0,
                    });
                  }}
                />
              </label>
            </div>
          ))}
        </div>
        <div className="print-controls">
          <label>
            Paper
            <select
              value={paper}
              onChange={(e) => setPaper(e.target.value as "A4" | "Letter")}
            >
              <option>A4</option>
              <option>Letter</option>
            </select>
          </label>
          <button disabled={busy || total === 0 || total > 180} onClick={build}>
            {busy ? "Preparing…" : "Preview sheets"}
          </button>
          <button
            className="text-button"
            disabled={!total || busy}
            onClick={() => setQuantities({})}
          >
            Clear quantities
          </button>
        </div>
        <p className="sheet-summary" aria-live="polite">
          {total} labels · {Math.ceil(total / 18)}{" "}
          {Math.ceil(total / 18) === 1 ? "sheet" : "sheets"} · 18 labels per
          sheet
        </p>
        {total > 180 && (
          <p role="alert" className="error">
            Choose at most 180 labels per print run.
          </p>
        )}
        <p className="hint">
          Copies of an object use the same QR. Quantities are for this print run
          and are not saved between page reloads.
        </p>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
      </div>
      {preview && (
        <div className="print-preview">
          <div className="panel no-print">
            <h2>Your happy little labels</h2>
            <p>
              {preview.total} labels across {preview.sheets.length}{" "}
              {preview.sheets.length === 1 ? "sheet" : "sheets"}. Only your
              chosen printed text appears under each QR.
            </p>
            {preview.sheets
              .flat()
              .some((l) =>
                /^http:\/\/(127\.0\.0\.1|localhost)/.test(l.scan_url),
              ) && (
              <p className="notice">
                Local test codes only open on this computer. Configure a
                phone-accessible site address before printing labels for real
                use.
              </p>
            )}
            <button
              disabled={failed || loaded < preview.total}
              onClick={() => window.print()}
            >
              {failed
                ? "QR loading failed — rebuild the preview"
                : loaded < preview.total
                  ? "Loading QR codes…"
                  : "Print / save PDF"}
            </button>
            <p className="hint">
              18-up cut-out layout: 3 × 6, 60 × 40 mm. Print at 100% / actual
              size; turn off browser headers and footers. Use full-sheet
              adhesive paper and cut out. This is not a preset for pre-cut label
              stock.
            </p>
          </div>
          <style>{`@media print { @page { size: ${preview.paper}; margin: 10mm; } }`}</style>
          {preview.sheets.map((sheet, page) => (
            <div className="sheet-page" key={page}>
              <p className="no-print sheet-caption">
                Sheet {page + 1} of {preview.sheets.length}
              </p>
              <div className="sheet">
                {sheet.map((label, cell) => (
                  <Sticker
                    key={`${label.id}-${cell}`}
                    label={label}
                    loaded={() => setLoaded((n) => n + 1)}
                    failed={() => setFailed(true)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
