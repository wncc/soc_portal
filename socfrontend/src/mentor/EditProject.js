import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import './Form.css'; // Same styling as the original Form

const EditProject = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { domain } = useParams();
  const { projectId } = location.state || {};
  const [domainData, setDomainData] = useState(null);
  const [loading, setLoading] = useState(true);

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

  // Fetch domain data to check permissions
  useEffect(() => {
    const fetchDomainData = async () => {
      if (!domain) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/domains/${domain}/`,
          axiosConfig
        );
        setDomainData(response.data);
        
        if (!response.data.project_editing_open) {
          alert('Project editing is currently closed for this domain.');
          navigate(domain ? `/${domain}/mentor/home` : '/mentor/home');
        }
      } catch (error) {
        console.error('Error fetching domain data:', error);
      }
      setLoading(false);
    };
    
    fetchDomainData();
  }, [domain]);

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/projects/${projectId}/`,
          axiosConfig
        );
        const projectData = response.data;
  
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
          prereuisites: projectData.prereuisites || '',
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
      const endpoint = domain
        ? `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/${projectId}/?domain=${domain}`
        : `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/${projectId}/`;
      
      const response = await axios.put(endpoint, formData, axiosConfig);
      console.log('Project updated:', response.data);
      alert('Project updated successfully!');
      navigate(domain ? `/${domain}/mentor/home` : '/mentor/home');
    } catch (error) {
      console.error('Error updating project:', error);
      alert('Failed to update the project.');
    }
  };

  if (loading) {
    return (
      <div className="h-screen flex justify-center items-center">
        <div className="flex gap-2">
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="lp-container">
      <div className="lp-box">
        <h1 className="lp-title">Edit {domainData?.name || 'SOC'} Project</h1>
        <p className="lp-description">
          Update your project details below.
        </p>
        <form className="lp-form" onSubmit={handleSubmit}>
          <div className="lp-form-group">
            <label className="lp-label">Project Title *</label>
            <p className="lp-help-text">We are looking for your hobby projects and ideas on your to-do list.</p>
            <input type="text" name="title" className="lp-input" placeholder="Enter project title" value={formData.title} onChange={handleChange} required />
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
            <input type="text" name="specific_category" className="lp-input" placeholder="Enter specific category" value={formData.specific_category} onChange={handleChange} />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Number of mentees *</label>
            <input type="number" name="mentee_max" className="lp-input" placeholder="Enter number of mentees" value={formData.mentee_max} onChange={handleChange} required min="1" />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Co-mentor(s)</label>
            <p className="lp-help-text">
              If there are multiple co-mentors, add their names in this format: Name (roll No) separated by commas. Eg: John Doe (21b1111), Alice (22b2222), Bob (23b3333)
            </p>
            <input type="text" name="co_mentor_info" className="lp-input" placeholder="Enter co-mentors" value={formData.co_mentor_info} onChange={handleChange} />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Description *</label>
            <p className="lp-help-text">
              Elaborate on the work and learning involved in the project. Suggest resources for mentees to gain context.
            </p>
            <textarea name="description" className="lp-textarea" placeholder="Enter project description" rows="4" value={formData.description} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Proposed Timeline *</label>
            <textarea name="timeline" className="lp-textarea" placeholder="Enter week-wise timeline" rows="4" value={formData.timeline} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Project Checkpoints *</label>
            <textarea name="checkpoints" className="lp-textarea" placeholder="Enter 5 major milestones" rows="4" value={formData.checkpoints} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Prerequisites *</label>
            <textarea name="prereuisites" className="lp-textarea" placeholder="Describe prerequisites" rows="4" value={formData.prereuisites} onChange={handleChange} required />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">How many weekly meets are you planning to conduct ? *</label>
            <input type="number" name="weekly_meets" className="lp-input" placeholder="Write the approximate number per week" value={formData.weekly_meets} onChange={handleChange} required min="0" />
          </div>

          <div className="lp-form-group">
            <label className="lp-label">Banner Image Link (upload to Drive and share link with view access) *</label>
            <input type="url" name="banner_image_link" className="lp-input" placeholder="Paste banner image link" value={formData.banner_image_link} onChange={handleChange} required />
          </div>

          <button type="submit" className="lp-submit-button">Update Project</button>
        </form>
      </div>
    </div>
  );
};

export default EditProject;
