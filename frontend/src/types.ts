export type Label = {
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
export type Belonging = {
  id: string;
  name: string;
  kind: "item" | "group";
  profile: string;
  profile_name: string;
  label: Label;
};
export type SheetPreview = {
  paper: "A4" | "Letter";
  total: number;
  sheets: (Label & {
    object_id: string;
    object_name: string;
    profile_name: string;
  })[][];
};

export type User = { username: string; email_verified: boolean; is_staff?: boolean };
export type Profile = {
  id: string; name: string; kind: "child" | "adult" | "family";
  controller: boolean; email_alerts: boolean; archived: boolean;
  families: string[]; members: string[];
};
export type Report = { id: string; message: string; profile: string; item_name: string; created_at: string };
export type RunAction = (action: () => Promise<unknown>, message?: string) => Promise<boolean>;
