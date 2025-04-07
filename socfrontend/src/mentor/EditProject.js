import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Form.css'; // Same styling as the original Form

const EditProject = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = location.state || {};

  const [formData, setFormData] = useState({
    title: '',
    general_category: '',
    specific_category: '',
    mentee_max: '',
    mentor: '',
    co_mentor_info: '',
    description: '',
    weekly_meets: '',
    timeline: '',
    checkpoints: '',
    prereuisites: '',
    banner_image_link: '',
  });

  const token = localStorage.getItem('authToken');
  const axiosConfig = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  };

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const response = await axios.get(
          `https://socb.tech-iitb.org/api/projects/${projectId}/`,
          axiosConfig
        );
        const projectData = response.data;
  
        console.log("Fetched full project:", projectData);
  
        setFormData({
          title: projectData.title || '',
          general_category: projectData.general_category || '',
          specific_category: projectData.specific_category || '',
          mentee_max: projectData.mentee_max || '',
          mentor: projectData.mentor || '',
          co_mentor_info: projectData.co_mentor_info || '',
          description: projectData.description || '',
          weekly_meets: projectData.weekly_meets || '',
          timeline: projectData.timeline || '',
          checkpoints: projectData.checkpoints || '',
          prerequisites: projectData.prerequisites || '',
          banner_image_link: projectData.banner_image_link || '',
        });
      } catch (error) {
        console.error("Error fetching project details:", error);
        alert("Failed to load full project details.");
      }
    };
  
    if (projectId) {
      fetchProjectDetails();
    }
  }, [projectId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.description.length < 50) {
      alert('Description must be at least 50 characters long.');
      return;
    }

    try {
      const response = await axios.put(
        `https://socb.tech-iitb.org/api/projects/mentor/profile/${projectId}/`,
        formData,
        axiosConfig
      );
      console.log('Project updated:', response.data);
      alert('Project updated successfully!');
      navigate('/mentor/home');
    } catch (error) {
      console.error('Error updating project:', error);
      alert('Failed to update the project.');
    }
  };

  return (
    <div className="lp-container">
      <div className="lp-box">
        <h1 className="lp-title">Edit SOC Project</h1>
        <form className="lp-form" onSubmit={handleSubmit}>
          {/* Same exact form fields as in your add-project form */}
          <div className="lp-form-group">
            <label className="lp-label">Project Title *</label>
            <input type="text" name="title" className="lp-input" value={formData.title} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Project Category *</label>
            <div className="lp-radio-group">
              {['Machine Learning', 'Development', 'Competitive Programming', 'Blockchain', 'Others'].map((category) => (
                <label key={category}>
                  <input
                    type="radio"
                    name="general_category"
                    value={category}
                    checked={formData.general_category === category}
                    onChange={handleChange}
                    required
                  />
                  {category}
                </label>
              ))}
            </div>
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Specific Category</label>
            <input type="text" name="specific_category" className="lp-input" value={formData.specific_category} onChange={handleChange} />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Number of mentees *</label>
            <input type="number" name="mentee_max" className="lp-input" value={formData.mentee_max} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Co-mentor(s)</label>
            <input type="text" name="co_mentor_info" className="lp-input" value={formData.co_mentor_info} onChange={handleChange} />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Description *</label>
            <textarea name="description" className="lp-textarea" rows="4" value={formData.description} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Proposed Timeline *</label>
            <textarea name="timeline" className="lp-textarea" rows="4" value={formData.timeline} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Project Checkpoints *</label>
            <textarea name="checkpoints" className="lp-textarea" rows="4" value={formData.checkpoints} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Prerequisites *</label>
            <textarea name="prereuisites" className="lp-textarea" rows="4" value={formData.prereuisites} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Weekly Meets *</label>
            <input type="number" name="weekly_meets" className="lp-input" value={formData.weekly_meets} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Banner Image Link *</label>
            <input type="url" name="banner_image_link" className="lp-input" value={formData.banner_image_link} onChange={handleChange} required />
          </div>

          <button type="submit" className="lp-submit-button">Update Project</button>
        </form>
      </div>
    </div>
  );
};

export default EditProject;
