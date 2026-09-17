import { useEffect } from 'react';
import { Link } from 'react-router';
import "../urlcheck.style.scss";
import { useUrlCheck } from '../../../hooks/useUrlCheck';
import { getScanStatus } from '../components/ResultCards';

const History = () => {
    const { history, loading, error, fetchHistory } = useUrlCheck();

    useEffect(() => {
        fetchHistory();
    }, []);

    const threatCount = history.filter((item) => getScanStatus(item).key === "danger").length;
    const cleanCount = history.filter((item) => getScanStatus(item).key === "safe").length;
    const suspiciousCount = history.filter((item) => getScanStatus(item).key === "suspicious").length;

    return (
        <main className="home-main">
            <div className="history-topbar">
                <Link to="/" className="back-link">← Back to Scanner</Link>
                <span className="brand-mini">FRAUDLENS</span>
                <span className="archive-label">Scan Archive</span>
            </div>

            <div className="history-main">
                <h1>Intelligence History</h1>
                <p className="history-subtitle">Complete audit log of all URL scans conducted in this session.</p>

                <div className="stat-row">
                    <div className="stat-card stat-danger">
                        <p className="stat-number">{threatCount}</p>
                        <p className="stat-label">Threats Detected</p>
                    </div>
                    <div className="stat-card stat-safe">
                        <p className="stat-number">{cleanCount}</p>
                        <p className="stat-label">Clean URLs</p>
                    </div>
                    <div className="stat-card stat-suspicious">
                        <p className="stat-number">{suspiciousCount}</p>
                        <p className="stat-label">Suspicious</p>
                    </div>
                </div>

                {loading && <p className="empty-state">Loading...</p>}
                {error && <p className="error-text">{error}</p>}
                {!loading && history.length === 0 && <p className="empty-state">No checks yet.</p>}

                {history.map((item) => {
                    const status = getScanStatus(item);
                    return (
                        <div key={item._id} className={`history-row row-${status.key}`}>
                            <div className="row-icon">{status.icon}</div>
                            <div className="row-body">
                                <div className="row-top">
                                    <span className={`badge ${status.badgeClass}`}>{status.label}</span>
                                    <span className="row-confidence">{item.confidence}% confidence</span>
                                    <span className="row-date">{new Date(item.createdAt).toLocaleString()}</span>
                                </div>
                                <p className="row-url">{item.url}</p>
                                {item.note && <p className="row-note">{item.note}</p>}
                            </div>
                            <div className="row-underline" />
                        </div>
                    );
                })}
            </div>
        </main>
    );
};

export default History;
