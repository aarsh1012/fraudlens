import { useContext, useEffect } from 'react';
import { AuthContext } from '../context/auth.context';
import { register, Login, logout, getMe } from '../services/auth.api';

export const useAuth = () => {
    const context = useContext(AuthContext);
    const { user, setUser, loading, setLoading } = context;

    const handlelogin = async (email, password) => {
        setLoading(true);
        try {
            const data = await Login({ email, password });
            setUser(data.user);
            return true;
        } catch (err) {
            console.error("login failed", err);
            return false;
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async ({ fullName, email, password }) => {
        setLoading(true);
        try {
            const data = await register({ fullName, email, password });
            setUser(data.user);
        } catch (err) {
            console.error("register failed", err);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = async () => {
        setLoading(true);
        try {
            await logout();
            setUser(null);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const getAndSetUser = async () => {
            try {
                const data = await getMe();
                setUser(data?.user ?? null);
            } catch (err) {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };
        getAndSetUser();
    }, []);

    return { user, loading, handlelogin, handleRegister, handleLogout };
};