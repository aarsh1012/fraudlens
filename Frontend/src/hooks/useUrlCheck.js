import { useContext } from 'react';
import { UrlCheckContext } from '../context/urlCheck.context';
import { checkUrlRequest, getHistoryRequest } from '../services/urlCheck.api';

export const useUrlCheck = () => {
    const context = useContext(UrlCheckContext);
    const { result, setResult, history, setHistory, loading, setLoading, error, setError } = context;

    const checkUrl = async (url) => {
        setLoading(true);
        setError(null);
        try {
            const data = await checkUrlRequest(url);
            setResult(data);
            return data;
        } catch (err) {
            console.error("URL check failed", err);
            setError(err?.response?.data?.message || "Something went wrong while checking the URL.");
            return null;
        } finally {
            setLoading(false);
        }
    };

    const fetchHistory = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getHistoryRequest();
            setHistory(data?.history ?? []);
        } catch (err) {
            console.error("Failed to fetch history", err);
            setError("Could not load history.");
        } finally {
            setLoading(false);
        }
    };

    const clearResult = () => setResult(null);

    return { result, history, loading, error, checkUrl, fetchHistory, clearResult };
};