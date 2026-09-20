import { useEffect, useState } from "react";
import type { Label } from "../types";
export function LabelEditor({
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
