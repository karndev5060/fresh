import React from 'react';

const StudentArtifactCard = ({ data }) => {
    if (!data) return null;

    const { tags, achievements } = data;

    return (
        <div className="artifact-card modern-horizontal">
            <div className="artifact-section tags-section">
                <div className="artifact-tag-row">
                    {tags.map((tag, index) => (
                        <span key={index} className={`artifact-tag ${tag.category}`}>
                            {tag.name}
                        </span>
                    ))}
                </div>
            </div>
            <div className="artifact-section accomplishments-section">
                <h4>Top 5 Achievements</h4>
                <ul className="achievement-list">
                    {achievements.slice(0, 5).map((point, index) => (
                        <li key={index}>{point}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default StudentArtifactCard;
