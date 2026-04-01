import React, { useEffect, useState } from "react";
import "./LandingPage.scss";
import { useNavigate, useParams } from "react-router-dom";
import { IoMailOutline } from "react-icons/io5";
import { IconContext } from "react-icons";
import { motion } from "framer-motion";
import axios from "axios";
import MentorPortal from "./MentorPortal"; // Import MentorPortal component
import PhoneUpdateModal from "../mentee/components/PhoneUpdateModal";

const easing = [0.6, -0.05, 0.01, 0.99];

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
  initial: { y: -60, opacity: 0, transition: { duration: 0.6, ease: easing } },
  animate: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.6, delay: 0.5, ease: easing },
  },
};

function LandingPage() {
  const navigate = useNavigate();
  const { domain } = useParams();
  const [mentorName, setMentorName] = useState("");
  const [mentorEmail, setMentorEmail] = useState("");
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showInfo, setShowInfo] = useState(false);
  const [domainData, setDomainData] = useState(null);

  const token = localStorage.getItem("authToken");
  const axiosConfig = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  };

  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const fetchDomainData = async () => {
      if (!domain) return;
      
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/domains/${domain}/`,
          axiosConfig
        );
        setDomainData(response.data);
      } catch (error) {
        console.error('Error fetching domain data:', error);
      }
    };
    
    fetchDomainData();
  }, [domain]);

  useEffect(() => {
    const checkPhoneNumber = async () => {
      const role = localStorage.getItem("role");
      if (role === "mentor") {
        try {
          const endpoint = domain
            ? `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/?domain=${domain}`
            : `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/`;
          
          const res = await axios.get(endpoint, axiosConfig);
          const phone = res.data.mentor.user_profile.phone_number;

          if (phone === "0000000000") {
            setShowModal(true); // Show the modal if phone number is '0000000000'
          }
        } catch (err) {
          console.error("Error fetching mentor profile:", err);
        }
      }
    };

    checkPhoneNumber();
  }, [domain]);

  useEffect(() => {
    const fetchMentorData = async () => {
      try {
        const endpoint = domain
          ? `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/?domain=${domain}`
          : `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/profile/`;
        
        const response = await axios.get(endpoint, axiosConfig);
        setMentorName(response.data.mentor.user_profile.name);
        setMentorEmail(
          response.data.mentor.user_profile.roll_number + "@iitb.ac.in"
        );
        setProjects(response.data.mentor.projects); // Expecting an array of projects
      } catch (error) {
        console.error("Error fetching mentor data:", error);
      }
      setLoading(false);
    };

    fetchMentorData();
  }, [domain]);

  return (
    <motion.div initial="initial" animate="animate">
      <motion.header variants={stagger}>
        <motion.div className="logo_wrapper" variants={fadeInUp}>
          {mentorName ? (
            <>
              {mentorName.split(" ")[0]} <span>{mentorName.split(" ")[1]}</span>
            </>
          ) : (
            "Loading..."
          )}
        </motion.div>
        <motion.div className="menu_container" variants={stagger}>
          <motion.span variants={fadeInUp} />
          <motion.span variants={fadeInUp}>
            <IconContext.Provider value={{ color: "#000", size: "18px" }}>
              <div className="icon">
                <IoMailOutline />
              </div>
              {mentorEmail || "Loading..."}
            </IconContext.Provider>
          </motion.span>
        </motion.div>
      </motion.header>

      <div className="dropdown_wrapper">
        <section className="mentor_info_container">
          <div
            className="mentor_info_header"
            onClick={() => setShowInfo(!showInfo)}
          >
            <h2>📘 Read Me !!</h2>
            <h3> All Mentors are requested to read the procedure before selecting mentees.</h3>
            <span className={`arrow ${showInfo ? "up" : "down"}`}>
              {showInfo ? "▲" : "▼"}
            </span>
          </div>

          {showInfo && (
            <div className="mentor_info_content">
              <h3>Basic Duties of an SOC Mentor:</h3>
              <ol>
                <li>Staying in touch with your mentees regularly.</li>
                <li>
                  Providing them with resources and a learning pathway for the
                  project.
                </li>
                <li>
                  Encouraging active participation and involvement of each
                  mentee.
                </li>
                <li>
                  Conducting review meetings to track updates and progress.
                </li>
                <li>Timely resolution of doubts and queries.</li>
              </ol>

              <h3>How to Select Mentees:</h3>
              <ul>
                <li>
                  <strong>Read All SOPs Carefully:</strong>
                  <br />
                  Go through the Statements of Purpose (SOPs) submitted by all
                  applicants to your project. Try to understand their
                  motivation, background, and expectations from the project.
                </li>
                <li>
                  <strong>Ignore the Mentee Limit for Now:</strong>
                  <br />
                  Don’t worry about the number of mentees you said you'd take
                  up—just focus on evaluating everyone fairly. You'll submit
                  your ranked list, and we’ll handle the cutoff based on
                  preferences and availability.
                </li>
                <li>
                  <strong>Prepare a Ranked List:</strong>
                  <br />
                  Rank the mentees in order of preference based on the quality
                  of their SOP, relevant skills, past experience (if any), and
                  enthusiasm.
                </li>
              </ul>
            </div>
          )}
        </section>
      </div>

      {/* If a project is selected, show MentorPortal */}
      {selectedProject ? (
        <MentorPortal
          project={selectedProject}
          onBack={() => setSelectedProject(null)}
        />
      ) : (
        <motion.div className="cards_container" variants={stagger}>
          {loading ? (
            <motion.div className="loading" variants={fadeInUp}>
              Loading projects...
            </motion.div>
          ) : (
            <>
              {projects.map((project) => (
                <motion.div
                  key={project.id}
                  className="project_card"
                  variants={fadeInUp}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div onClick={() => setSelectedProject(project)}>
                    <h3>{project.title}</h3>
                    <p>{project.general_category}</p>
                  </div>
                  {domainData?.project_editing_open && (
                    <button
                      className="edit_project_btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(domain ? `/${domain}/mentor/edit-project` : '/mentor/edit-project', {
                          state: { projectId: project.id }
                        });
                      }}
                      title="Edit Project"
                    >
                      ✏️ Edit
                    </button>
                  )}
                </motion.div>
              ))}
              
              {/* Add Project Card */}
              {domainData?.project_creation_open && (
                <motion.div
                  className="add_project_card"
                  variants={fadeInUp}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate(domain ? `/${domain}/mentor/add-project` : '/mentor/add-project')}
                >
                  <div className="add_project_content">
                    <motion.div
                      className="add_icon"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.5, ease: easing }}
                    >
                      +
                    </motion.div>
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.6, ease: easing }}
                    >
                      Add Project
                    </motion.p>
                  </div>
                </motion.div>
              )}
            </>
          )}
        </motion.div>
      )}
      {showModal && <PhoneUpdateModal onClose={() => setShowModal(false)} />}
    </motion.div>
  );
}

export default LandingPage;
