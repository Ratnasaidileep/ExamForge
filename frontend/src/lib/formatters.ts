export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
}

export function formatDuration(minutes?: number | null): string {
  if (!minutes) return '0 mins';
  if (minutes < 60) return `${minutes} mins`;
  const hrs = Math.floor(minutes / 60);
  const rem = minutes % 60;
  return rem > 0 ? `${hrs}h ${rem}m` : `${hrs} hr${hrs > 1 ? 's' : ''}`;
}

export function formatMarks(marks?: number | null): string {
  if (marks === null || marks === undefined) return '—';
  return Number(marks).toString();
}

export function formatPercentage(val?: number | null): string {
  if (val === null || val === undefined) return '0%';
  return `${Math.round(val)}%`;
}

export function formatFileSize(bytes?: number): string {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return `${size.toFixed(1)} ${units[i]}`;
}
