import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import StudentArtifactCard from '../components/StudentArtifactCard';

const EmployerDashboard = () => {
    const { user, logout } = useAuth();
    const [title, setTitle] = useState('');
    const [company, setCompany] = useState('');
    const [description, setDescription] = useState('');
    const [requirements, setRequirements] = useState('');
    const [message, setMessage] = useState('');

    const [applicants] = useState([
        {
            id: 1,
            name: "Alex Johnson",
            job: "Senior Frontend Engineer",
            artifact: {
                tags: [
                    { name: "React", category: "frameworks" },
                    { name: "JavaScript", category: "languages" },
                    { name: "CSS/Tailwind", category: "others" }
                ],
                achievements: [
                    "Redesigned the core fintech dashboard, improving Lighthouse score by 40 points.",
                    "Implemented an internal UI library used by 30+ team members.",
                    "Reduced bundle size by 25% through advanced tree-shaking and lazy loading.",
                    "Led the migration from Class components to Hooks for 200+ files.",
                    "Mentored 3 junior developers who were subsequently promoted."
                ]
            }
        },
        {
            id: 2,
            name: "Sarah Chen",
            job: "ML Infrastructure Engineer",
            artifact: {
                tags: [
                    { name: "Python", category: "languages" },
                    { name: "PyTorch", category: "ml_ai" },
                    { name: "Docker", category: "others" }
                ],
                achievements: [
                    "Built BlackTorchKD from scratch, a knowledge distillation library for LLMs.",
                    "Optimized model inference latency by 3x using TensorRT integration.",
                    "Managed a Kubernetes cluster of 50+ GPU nodes for training pipelines.",
                    "Top 1% contributor to a major open-source deep learning repository.",
                    "Ranked 1500+ on Codeforces (Excellent competitive programmer)."
                ]
            }
        }
    ]);

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

            <section className="applicants-section" style={{ marginTop: '3rem' }}>
                <h3>Review Applicants</h3>
                <div className="applicant-list" style={{ display: 'grid', gap: '2rem' }}>
                    {applicants.map(app => (
                        <div key={app.id} className="applicant-entry">
                            <div className="applicant-info-header" style={{ marginBottom: '0.5rem' }}>
                                <strong style={{ fontSize: '1.2rem', color: 'var(--primary)' }}>{app.name}</strong>
                                <span style={{ marginLeft: '1rem', color: '#94a3b8' }}>Applying for: {app.job}</span>
                            </div>
                            <StudentArtifactCard data={app.artifact} />
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default EmployerDashboard;
