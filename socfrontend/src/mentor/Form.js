import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; 
import axios from 'axios';
import './Form.css';

const Form = () => {
  const navigate = useNavigate();
  
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

  useEffect(() => {
    const fetchMentorData = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile`,
          axiosConfig,
        );
        console.log('Mentor Data:', response.data);

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
  }, []);

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
      // First request
      const profileResponse = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/`,
        formData,
        axiosConfig,
      );
      console.log('Project added:', profileResponse.data);
  
      alert('Project submitted successfully!');
      navigate('/mentor/home');
  
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Failed to submit the project. Please try again.');
    }
  };

  console.log(formData);

  return (
    <div className="lp-container">
      <div className="lp-box">
        <h1 className="lp-title">SOC Project Submission Form</h1>
        <p className="lp-description">
          SOC is a great way to convert your ideas into reality and guide mentees in the process of building an awesome end product.
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
              {['ML', 'Development', 'CP', 'Blockchain', 'Others'].map((category) => (
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
