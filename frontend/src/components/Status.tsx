interface StatusProps {
  error?: string | null;
  success?: string | null;
}

export function Status({ error, success }: StatusProps) {
  if (!error && !success) return null;
  return <div className={error ? "status status-error" : "status status-success"}>{error || success}</div>;
}
