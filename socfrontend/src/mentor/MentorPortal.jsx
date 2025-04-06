import './MentorPortal.scss';
import React, { useRef, useEffect, useState } from 'react';
import { IoMailOutline, IoChevronForwardCircle, IoStar } from 'react-icons/io5';
import { IconContext } from 'react-icons';
import { motion } from 'framer-motion';
import MenteeList from './MenteeList';
import axios from 'axios';

const easeing = [0.6, -0.05, 0.01, 0.99];

const stagger = {
  animate: {
    transition: {
      delayChildren: 0.4,
      staggerChildren: 0.2,
      staggerDirection: 1,
    },
  },
};

const fadeInUp = {
  initial: {
    y: -60,
    opacity: 0,
    transition: {
      duration: 0.6,
      ease: easeing,
    },
  },
  animate: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6,
      delay: 0.5,
      ease: easeing,
    },
  },
};

const btnGroup = {
  initial: {
    y: -60,
    opacity: 0,
    transition: { duration: 0.6, ease: easeing },
  },
  animate: {
    y: 0,
    opacity: 1,
    animation: {
      duration: 0.6,
      ease: easeing,
    },
  },
};

function MentorPortal({ project, onBack }) {
  // State for storing mentor's data
  const [mentees, setMentees] = useState();
  const [mentorProj, setMentorProj] = useState('');
  const [mentorPath, setMentorPath] = useState('');
  const [bannerImage, setBannerImage] = useState('');
  const menteeListRef = useRef(null);
  const token = localStorage.getItem('authToken');
  const [isLoading, setIsLoading] = useState(true);

  const axiosConfig = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  };

  // Fetch mentor data from the backend
  useEffect(() => {
    // You can replace this URL with the correct endpoint to fetch the current mentor's data
    axios
      .get(
        `https://socb.tech-iitb.org/api/projects/mentor/profile/${project.id}`,
        axiosConfig,
      )
      .then((response) => {
        const matchedProject = response.data.mentor.projects.find((x) => x.id === project.id);
        setMentees(response.data.mentees.length);
        if (matchedProject) {
          console.log(matchedProject);
          setMentorProj(matchedProject.title);
          console.log('you',matchedProject.bannerImage);
          if (matchedProject.banner_image) {
            setMentorPath(matchedProject.banner_image);
          } else {
            // Call download API if the banner is missing
            downloadBannerImage(matchedProject.banner_image_link, project.id);
          }
        } else {
          console.warn('No matching project found for the given ID');
        }
      })
      .catch((error) => {
        console.error('Error fetching mentor data:', error);
      });
  }, [project]);
  
  const downloadBannerImage = async (fileUrl, title) => {
    if (!fileUrl || !title) return;

    try {
      const response = await axios.get(
        `https://socb.tech-iitb.org/api/projects/download-banner/`,
        {
          params: { file_url: fileUrl, id: project.id },
          headers: axiosConfig.headers,
        },
      );
      if (response.data.success) {
        setBannerImage(response.data.file_path);
        setIsLoading(false);
      } else {
        console.error('Error downloading banner:', response.data.error);
      }
    } catch (error) {
      console.error('Failed to download banner:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (mentorPath && mentorProj) {
      setIsLoading(true); // Set loading to true when we start fetching the image
      downloadBannerImage(mentorPath, mentorProj);
    }
  }, [mentorPath, mentorProj]);

  useEffect(() => {
    if (mentorPath && mentorProj) {
      downloadBannerImage(mentorPath, mentorProj);
    }
  }, [mentorPath, mentorProj]);

  console.log('what ',bannerImage);
  const fullImageUrl = `https://socb.tech-iitb.org/media/${bannerImage}`;
  console.log(fullImageUrl);

  // Function to scroll to a section
  const scrollToSection = (ref) => {
    ref.current.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <motion.div initial="initial" animate="animate">

      <motion.header className="logo_wrapper" variants={fadeInUp}>
        <button className="back_button" onClick={onBack}>⬅ Back to Projects</button>
      </motion.header>
      <motion.div
        className="content_wrapper"
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, ease: easeing }}
      >
        <div className="left_content_wrapper">
          <motion.h2>
            <motion.span
              variants={fadeInUp}
              initial="initial"
              animate="animate"
            >
              {mentorProj ? (
                <>
                  <span>{mentorProj}</span>
                </>
              ) : (
                'Loading...'
              )}
            </motion.span>
          </motion.h2>

          <motion.p variants={fadeInUp}>
            "Guiding Minds, Building Expertise: Where Mentors Lead and Mentees
            Excel!" <br />
            CODERS TOGETHER STRONG
          </motion.p>

          <motion.div className="btn_group" variants={stagger}>
            <motion.div
              className="btn btn_primary"
              variants={btnGroup}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => scrollToSection(menteeListRef)} // Scroll to mentee list
            >
              Applied Mentees
              <IconContext.Provider value={{ color: '#0052cc', size: '25px' }}>
                <IoChevronForwardCircle />
              </IconContext.Provider>
            </motion.div>
          </motion.div>

          <motion.div className="review_container" variants={stagger}>
            <motion.p className="total_review" variants={fadeInUp}>
              Choose Your Mentees Wisely :)
            </motion.p>
            <IconContext.Provider value={{ color: '#fff', size: '18px' }}>
              {[...Array(5)].map((_, i) => (
                <motion.span
                  key={i}
                  variants={fadeInUp}
                  whileHover={{
                    scale: 1.2,
                    rotate: 180,
                    borderRadius: '100%',
                    cursor: 'pointer',
                  }}
                >
                  <IoStar />
                </motion.span>
              ))}
            </IconContext.Provider>
            <motion.p className="more_review" variants={fadeInUp}>
              {`${mentees} student${(mentees === 1) || (mentees===0) ? '' : 's'} applied`}
            </motion.p>
          </motion.div>
        </div>
        
        <motion.div className="right_content_wrapper">
          {isLoading ? (
            <h2>Loading the Image. Please wait</h2>
  
          ) : (
            <motion.img
              src={fullImageUrl}
              alt="bg"
              initial={{ x: 200, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.8 }}
            />
          )}
        </motion.div>
      </motion.div>

      {/* Mentee List Section */}
      <div ref={menteeListRef}>
        <MenteeList key={project.id} project={project.id}/>
      </div>
      
    </motion.div>
    
  );
}

export default MentorPortal;
