// Shared helper: turns a backend result into a status bucket + display info.
// Exported so Home.jsx (recent scans) and History.jsx can reuse the same logic.
export const getScanStatus = (item) => {
    const isPhishing = item.prediction === "PHISHING";

    if (!isPhishing) {
        return {
            key: "safe",
            label: "CLEAR",
            badgeClass: "badge-safe",
            dotClass: "dot-safe",
            title: "CLEAR",
            icon: "✓",
        };
    }

    // Treat lower-confidence phishing calls as "suspicious" rather than a full threat
    if (item.confidence < 85) {
        return {
            key: "suspicious",
            label: "SUSPICIOUS",
            badgeClass: "badge-suspicious",
            dotClass: "dot-suspicious",
            title: "SUSPICIOUS",
            icon: "?",
        };
    }

    return {
        key: "danger",
        label: "THREAT DETECTED",
        badgeClass: "badge-danger",
        dotClass: "dot-danger",
        title: "THREAT DETECTED",
        icon: "⚠",
    };
};

const buildIndicators = (item, status) => {
    const indicators = [];

    if (status.key === "safe") {
        indicators.push("No known threat associations");
        indicators.push("Clean reputation across all threat databases");
    } else {
        indicators.push(item.note || "Matched known-fraud signal patterns");
        indicators.push("Flagged during automated threat analysis");
    }

    return indicators;
};

const ResultCard = ({ result }) => {
    if (!result) return null;

    const status = getScanStatus(result);
    const indicators = buildIndicators(result, status);

    return (
        <div className={`panel result-card result-${status.key}`}>
            <div className="result-head">
                <div className="result-icon-title">
                    <div className="icon-circle">{status.icon}</div>
                    <div className="result-title">
                        <p className="eyebrow">Scan Complete</p>
                        <h2>{status.title}</h2>
                    </div>
                </div>
                <span className={`badge ${status.badgeClass}`}>{status.label}</span>
            </div>

            <div className="target-url-box">
                <p className="label">Target URL</p>
                <p className="value">{result.url}</p>
            </div>

            {result.confidence !== undefined && (
                <div className="confidence-block">
                    <div className="confidence-label-row">
                        <span>Confidence Score</span>
                        <strong>{result.confidence}%</strong>
                    </div>
                    <div className="confidence-track">
                        <div className="confidence-fill" style={{ width: `${result.confidence}%` }} />
                    </div>
                </div>
            )}

            <div className="signal-block">
                <p className="label">Primary Signal</p>
                <p className="value">{result.note || (status.key === "safe" ? "Clean reputation across all threat databases" : "Matched known-fraud signal patterns")}</p>
            </div>

            <div className="indicators-block">
                <p className="label">Indicators</p>
                <ul>
                    {indicators.map((point, i) => (
                        <li key={i}>› {point}</li>
                    ))}
                </ul>
            </div>

            {result.createdAt && (
                <p className="scan-timestamp">
                    Scan Timestamp: {new Date(result.createdAt).toLocaleString()}
                </p>
            )}
        </div>
    );
};

export default ResultCard;
