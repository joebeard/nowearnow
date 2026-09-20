let csrf = "";
export async function api<T>(
  path: string,
  method = "GET",
  data?: unknown,
): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, {
    method,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(method === "GET" ? {} : { "X-CSRFToken": csrf }),
    },
    ...(data === undefined ? {} : { body: JSON.stringify(data) }),
  });
  if (
    response.status !== 204 &&
    !response.headers.get("content-type")?.includes("application/json")
  ) {
    throw new Error(
      response.status === 403
        ? "Your session could not be verified. Refresh and try again."
        : "The service is unavailable. Please try again.",
    );
  }
  const result = response.status === 204 ? {} : await response.json();
  if (!response.ok)
    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : Object.entries(result)
            .map(([key, value]) => `${key}: ${String(value)}`)
            .join(" · "),
    );
  if (result.csrf) csrf = result.csrf;
  return result as T;
}
