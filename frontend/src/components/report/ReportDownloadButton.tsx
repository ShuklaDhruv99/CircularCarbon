import { reportUrl } from "../../services/report";

interface ReportDownloadButtonProps {
  factoryId: number;
  hasCalculatedEmissions: boolean;
}

// Presentational only: the PDF itself is generated and streamed entirely by
// the backend. This component just points a plain anchor tag at the report
// endpoint so the browser handles the download natively — no fetch/blob
// handling here.
function ReportDownloadButton({ factoryId, hasCalculatedEmissions }: ReportDownloadButtonProps) {
  if (!hasCalculatedEmissions) {
    return (
      <span className="w-fit rounded-md border border-border px-4 py-2 text-sm font-semibold text-muted opacity-60">
        Download Report
      </span>
    );
  }

  return (
    <a
      href={reportUrl(factoryId)}
      download
      className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
    >
      Download Report
    </a>
  );
}

export default ReportDownloadButton;
