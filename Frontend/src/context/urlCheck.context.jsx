import { createContext, useState } from "react";

export const UrlCheckContext = createContext();

export const UrlCheckProvider = ({ children }) => {
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    return (
        <UrlCheckContext.Provider
            value={{
                result, setResult,
                history, setHistory,
                loading, setLoading,
                error, setError
            }}
        >
            {children}
        </UrlCheckContext.Provider>
    );
};