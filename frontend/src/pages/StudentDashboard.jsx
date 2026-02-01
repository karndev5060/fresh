import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const StudentDashboard = () => {
    const { user, logout } = useAuth();
    const [resume, setResume] = useState('');
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');

    const [applyingIds, setApplyingIds] = useState(new Set());
    const [appliedIds, setAppliedIds] = useState(new Set());
    const [wsStatus, setWsStatus] = useState('');

    useEffect(() => {
        fetch('http://localhost:8000/jobs')
            .then(res => res.json())
            .then(data => {
                setJobs(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const handleApply = () => {
        if (!resume.trim()) {
            setMessage('Please paste your resume text first.');
            return;
        }

        const token = localStorage.getItem('token');
        const ws = new WebSocket(`ws://localhost:8000/ws/match`);

        setLoading(true);
        setApplyingIds(new Set());
        setAppliedIds(new Set());
        setJobs([]);

        ws.onopen = () => {
            ws.send(JSON.stringify({ token, resume_text: resume }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.status === 'thinking') {
                setWsStatus('Thinking...');
                setMessage(data.message);
            } else if (data.status === 'ranked') {
                setWsStatus('Ranked');
                setJobs(data.jobs);
                setMessage('AI has ranked the best matches!');
            } else if (data.status === 'applying') {
                setWsStatus('Applying...');
                setApplyingIds(prev => new Set(prev).add(data.job_id));
                setMessage(`Auto-applying to: ${data.job_title}`);
            } else if (data.status === 'applied') {
                setApplyingIds(prev => {
                    const next = new Set(prev);
                    next.delete(data.job_id);
                    return next;
                });
                setAppliedIds(prev => new Set(prev).add(data.job_id));
            } else if (data.status === 'complete') {
                setWsStatus('Complete');
                setLoading(false);
                setMessage(data.message);
                ws.close();
            } else if (data.status === 'error') {
                setMessage('Error: ' + data.message);
                setLoading(false);
                ws.close();
            }
        };

        ws.onerror = (err) => {
            console.error('WebSocket Error:', err);
            setMessage('WebSocket connection failed.');
            setLoading(false);
        };
    };

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h2>Student Dashboard</h2>
                <div className="user-info">
                    <span>Welcome, {user?.username}</span>
                    <button onClick={logout} className="secondary-btn">Logout</button>
                </div>
            </header>

            <section className="resume-section">
                <h3>Find & Apply with Gemini 1.5 Pro</h3>
                <textarea
                    placeholder="Paste your resume text here..."
                    value={resume}
                    onChange={(e) => setResume(e.target.value)}
                    rows={10}
                />
                <button onClick={handleApply} className="primary-btn" disabled={loading}>
                    {loading ? 'Analyzing...' : 'Find & Apply'}
                </button>
                {message && <p className="status-message">{message}</p>}
            </section>

            <section className="jobs-section">
                <h3>{jobs[0]?.match_score !== undefined ? 'AI Ranked Job Matches' : 'Available Jobs'}</h3>
                {loading && !jobs.length ? (
                    <p>Loading jobs...</p>
                ) : (
                    <div className="job-grid">
                        {jobs.map((job, index) => {
                            const isApplying = applyingIds.has(job.id);
                            const isApplied = appliedIds.has(job.id);

                            return (
                                <div key={job.id} className={`job-card ${isApplying ? 'is-applying' : ''} ${isApplied ? 'is-applied' : ''}`}>
                                    <div className="job-header-row">
                                        <h4>{job.title}</h4>
                                        <div className="badge-group">
                                            {job.match_score !== undefined && (
                                                <span className="match-badge">
                                                    {job.match_score}% Match
                                                </span>
                                            )}
                                            {isApplying && <span className="status-badge applying">Applying...</span>}
                                            {isApplied && <span className="status-badge applied">Applied ✅</span>}
                                        </div>
                                    </div>
                                    <p className="company">{job.company}</p>
                                    <p className="description">{job.description.substring(0, 150)}...</p>
                                    {job.reasoning && (
                                        <div className="ai-reasoning">
                                            <strong>AI Reasoning:</strong> {job.reasoning}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </section>
        </div>
    );
};

export default StudentDashboard;
