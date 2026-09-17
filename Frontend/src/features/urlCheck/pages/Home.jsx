import { useState, useEffect } from 'react';
import { Link } from 'react-router';
import "../urlcheck.style.scss";
import { useUrlCheck } from '../../../hooks/useUrlCheck';
import { useAuth } from '../../../hooks/useAuth';
import ResultCard, { getScanStatus } from '../components/ResultCards';

const Home = () => {
    const [url, setUrl] = useState('');
    const { result, loading, error, checkUrl, clearResult, history, fetchHistory } = useUrlCheck();
    const { user, handleLogout } = useAuth();

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!url.trim()) return;
        await checkUrl(url.trim());
    };

    const handleNewCheck = () => {
        setUrl('');
        clearResult();
    };

    const recentScans = history.slice(0, 3);

    return (
        <main className="home-main">
            <div className="topbar">
                <div className="system-status">
                    <span className="dot" />
                    System Online
                </div>
                <div className="topbar-right">
                    <div className="operator">
                        <p className="label">Operator</p>
                        <p className="name">{user?.fullName || user?.email}</p>
                    </div>
                    <Link to="/history" className="history-link">
                        ◈ History <span className="count">{history.length}</span>
                    </Link>
                    <button className="button ghost-button" onClick={handleLogout}>Logout</button>
                </div>
            </div>

            <section className="hero">
                <h1 className="brand-title">FRAUDLENS</h1>
                <p className="tagline">
                    "In a world where deception is engineered, intelligence is your shield."
                </p>
                <span className="welcome-pill">Welcome back, {user?.fullName || user?.email}</span>
            </section>

            <div className="panel scanner-panel">
                <p className="eyebrow">○ Threat Analysis Module</p>
                <h2 className="panel-title">URL Scanner</h2>
                <p className="panel-description">Submit any URL for deep threat intelligence analysis.</p>

                <form onSubmit={handleSubmit}>
                    <label htmlFor="url">Target URL</label>
                    <input
                        id="url"
                        type="text"
                        placeholder="https://example.com"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                    <button className="button primary-button" disabled={loading}>
                        {loading ? "Scanning..." : "Initiate Scan"}
                    </button>
                </form>

                {error && <p className="error-text">{error}</p>}
            </div>

            {result ? (
                <>
                    <ResultCard result={result} />
                    <div className="result-actions" style={{ maxWidth: "650px", margin: "1rem auto 0", display: "flex", gap: "0.75rem" }}>
                        <button className="button ghost-button" style={{ flex: 1 }} onClick={handleNewCheck}>← Check Other URL</button>
                        <Link to="/history" className="button" style={{ flex: 1, textAlign: "center" }}>View History →</Link>
                    </div>
                </>
            ) : (
                recentScans.length > 0 && (
                    <div className="recent-scans">
                        <div className="recent-header">
                            <h3>Recent Scans</h3>
                            <Link to="/history" className="view-all">View All →</Link>
                        </div>
                        {recentScans.map((item) => {
                            const status = getScanStatus(item);
                            return (
                                <div className="scan-row" key={item._id}>
                                    <div className="scan-row-left">
                                        <span className={`status-dot ${status.dotClass}`} />
                                        <span className="scan-url">{item.url}</span>
                                    </div>
                                    <span className={`badge ${status.badgeClass}`}>{status.label}</span>
                                </div>
                            );
                        })}
                    </div>
                )
            )}
        </main>
    );
};

export default Home;
