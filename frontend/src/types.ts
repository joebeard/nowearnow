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
