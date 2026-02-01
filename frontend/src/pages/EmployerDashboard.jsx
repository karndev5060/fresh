import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const EmployerDashboard = () => {
    const { user, logout } = useAuth();
    const [title, setTitle] = useState('');
    const [company, setCompany] = useState('');
    const [description, setDescription] = useState('');
    const [requirements, setRequirements] = useState('');
    const [message, setMessage] = useState('');

    const handlePostJob = async (e) => {
        e.preventDefault();
        setMessage('');
        const token = localStorage.getItem('token');
        try {
            const res = await fetch('http://localhost:8000/jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ title, company, description, requirements })
            });

            if (!res.ok) throw new Error('Failed to post job');

            setMessage('Job posted successfully!');
            setTitle('');
            setCompany('');
            setDescription('');
            setRequirements('');
        } catch (err) {
            setMessage(err.message);
        }
    };

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h2>Employer Dashboard</h2>
                <div className="user-info">
                    <span>Welcome, {user?.username}</span>
                    <button onClick={logout} className="secondary-btn">Logout</button>
                </div>
            </header>

            <section className="post-job-section">
                <h3>Post a New Job</h3>
                {message && <p className="status-message">{message}</p>}
                <form onSubmit={handlePostJob}>
                    <div className="form-group">
                        <label>Job Title</label>
                        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label>Company</label>
                        <input type="text" value={company} onChange={(e) => setCompany(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea value={description} onChange={(e) => setDescription(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label>Requirements</label>
                        <textarea value={requirements} onChange={(e) => setRequirements(e.target.value)} required />
                    </div>
                    <button type="submit" className="primary-btn">Post Job</button>
                </form>
            </section>
        </div>
    );
};

export default EmployerDashboard;
