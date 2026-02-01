import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            // Validate token and fetch user info
            fetch('http://localhost:8000/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
                .then(res => {
                    if (res.ok) return res.json();
                    throw new Error('Invalid token');
                })
                .then(data => setUser(data))
                .catch(() => {
                    localStorage.removeItem('token');
                    setUser(null);
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch('http://localhost:8000/login', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await res.json();
        localStorage.setItem('token', data.access_token);

        // Fetch user data after login
        const userRes = await fetch('http://localhost:8000/me', {
            headers: {
                'Authorization': `Bearer ${data.access_token}`
            }
        });
        const userData = await userRes.json();
        setUser(userData);
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    const register = async (username, email, password, role) => {
        const res = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password, role })
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return res.json();
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
