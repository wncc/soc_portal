import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom'; 
import axios from 'axios';
import './Form.css';

const Form = () => {
  const navigate = useNavigate();
  const { domain } = useParams();
  const [domainData, setDomainData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Form State
  const [formData, setFormData] = useState({
    title: '',
    general_category: 'Others',
    specific_category: 'NA',
    mentee_max: '',
    mentor: 'NA',
    co_mentor_info: 'NA',
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
        
        if (!response.data.project_creation_open) {
          alert('Project creation is currently closed for this domain.');
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
    const fetchMentorData = async () => {
      try {
        const endpoint = domain
          ? `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/?domain=${domain}`
          : `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/`;
        
        const response = await axios.get(endpoint, axiosConfig);
        const mentorName = response.data.mentor.user_profile.name;

        setFormData((prevData) => ({
          ...prevData,
          mentor: mentorName,
        }));
      } catch (error) {
        console.error('Error fetching mentor data:', error);
      }
    };

    fetchMentorData();
  }, [domain]);

  // Handle Input Change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle Form Submit
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.description.length < 50) {
      alert('Description must be at least 50 characters long.');
      return;
    }  

    try {
      const endpoint = domain
        ? `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/?domain=${domain}`
        : `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/`;
      
      const dataToSubmit = domain ? { ...formData, domain } : formData;
      
      const profileResponse = await axios.post(endpoint, dataToSubmit, axiosConfig);
      console.log('Project added:', profileResponse.data);
  
      alert('Project submitted successfully!');
      navigate(domain ? `/${domain}/mentor/home` : '/mentor/home');
  
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Failed to submit the project. Please try again.');
    }
  };

  // console.log(formData);

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
        <h1 className="lp-title">{domainData?.name || 'SOC'} Project Submission Form</h1>
        <p className="lp-description">
          {domainData?.name || 'SOC'} is a great way to convert your ideas into reality and guide mentees in the process of building an awesome end product.
        </p>
        <form className="lp-form" onSubmit={handleSubmit}>
          
          {/* Title */}
          <div className="lp-form-group">
            <label className="lp-label">Project Title *</label>
            <p className="lp-help-text">We are looking for your hobby projects and ideas on your to-do list.</p>
            <input
              type="text"
              name="title"
              className="lp-input"
              placeholder="Enter project title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          {/* General Category */}
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

          {/* Specific Category */}
          <div className="lp-form-group">
            <label className="lp-label">Specific Category</label>
            <input
              type="text"
              name="specific_category"
              className="lp-input"
              placeholder="Enter specific category"
              value={formData.specific_category}
              onChange={handleChange}
            />
          </div>

          {/* Mentee Max */}
          <div className="lp-form-group">
            <label className="lp-label">Number of mentees *</label>
            <input
              type="number"
              name="mentee_max"
              className="lp-input"
              placeholder="Enter number of mentees"
              value={formData.mentee_max}
              onChange={handleChange}
              required
              min="1"
            />
          </div>

          {/* Co-Mentor Info */}
          <div className="lp-form-group">
            <label className="lp-label">Co-mentor(s)</label>
            <p className="lp-help-text">
              If there are multiple co-mentors, add their names in this format: Name (roll No) separated by commas.
            </p>
            <input
              type="text"
              name="co_mentor_info"
              className="lp-input"
              placeholder="Enter co-mentors"
              value={formData.co_mentor_info}
              onChange={handleChange}
            />
          </div>

          {/* Description */}
          <div className="lp-form-group">
            <label className="lp-label">Description *</label>
            <p className="lp-help-text">
              Elaborate on the work and learning involved in the project. Suggest resources for mentees to gain context.
            </p>
            <textarea
              name="description"
              className="lp-textarea"
              placeholder="Enter project description"
              rows="4"
              value={formData.description}
              onChange={handleChange}
              required
            />
          </div>

          {/* Timeline */}
          <div className="lp-form-group">
            <label className="lp-label">Proposed Timeline *</label>
            <textarea
              name="timeline"
              className="lp-textarea"
              placeholder="Enter week-wise timeline"
              rows="4"
              value={formData.timeline}
              onChange={handleChange}
              required
            />
          </div>

          {/* Checkpoints */}
          <div className="lp-form-group">
            <label className="lp-label">Project Checkpoints *</label>
            <textarea
              name="checkpoints"
              className="lp-textarea"
              placeholder="Enter 5 major milestones"
              rows="4"
              value={formData.checkpoints}
              onChange={handleChange}
              required
            />
          </div>

          {/* Prerequisites */}
          <div className="lp-form-group">
            <label className="lp-label">Prerequisites *</label>
            <textarea
              name="prereuisites"
              className="lp-textarea"
              placeholder="Describe prerequisites"
              rows="4"
              value={formData.prereuisites}
              onChange={handleChange}
              required
            />
          </div>

          {/* Weekly Meets */}
          <div className="lp-form-group">
            <label className="lp-label">How many weekly meets are you planning to conduct ? *</label>
            <input
              type="number"
              name="weekly_meets"
              className="lp-input"
              placeholder="Write the approximate number per week"
              value={formData.weekly_meets}
              onChange={handleChange}
              required
              min="0"
            />
          </div>

          {/* Banner Image Link */}
          <div className="lp-form-group">
            <label className="lp-label">Banner Image Link (upload to Drive and share link with view access) *</label>
            <input
              type="url"
              name="banner_image_link"
              className="lp-input"
              placeholder="Paste banner image link"
              value={formData.banner_image_link}
              onChange={handleChange}
              required
            />
          </div>

          {/* Submit Button */}
          <button type="submit" className="lp-submit-button">Submit</button>
        </form>
      </div>
    </div>
  );
};

export default Form;
