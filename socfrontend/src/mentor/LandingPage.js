import React, { useEffect, useState } from "react";
import "./LandingPage.scss";
import { useNavigate } from "react-router-dom";
import { IoMailOutline } from "react-icons/io5";
import { IconContext } from "react-icons";
import { motion } from "framer-motion";
import axios from "axios";
import MentorPortal from "./MentorPortal"; // Import MentorPortal component

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
  const [mentorName, setMentorName] = useState("");
  const [mentorEmail, setMentorEmail] = useState("");
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState(null); // Store selected project

  const token = localStorage.getItem("authToken");
  const axiosConfig = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  };

  useEffect(() => {
    const fetchMentorData = async () => {
      try {
        const response = await axios.get(
          `https://socb.tech-iitb.org/api/projects/mentor/profile`,
          axiosConfig
        );
        console.log(response.data);
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
  }, []);

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
        <motion.div>
          <h2>Basic Duties of an SOC Mentor:</h2>
          <ol>
            <li>Staying in touch with your mentees regularly.</li>
            <li>
              Providing them with resources and a learning pathway for the
              project.
            </li>
            <li>
              Encouraging active participation and involvement of each mentee.
            </li>
            <li>Conducting review meetings to track updates and progress.</li>
            <li>Timely resolution of doubts and queries.</li>
          </ol>

          <h2>Selection Procedure:</h2>
          <ol>
            <li>
              Project proposals will be thoroughly reviewed. Mentors might be
              contacted for clarification.
            </li>
            <li>
              Mentees will submit a written proposal along with their project
              preferences.
            </li>
            <li>
              Mentors will decide the selection procedure and finalize the
              number of mentees.
            </li>
          </ol>

          <h2>Important Notes:</h2>
          <ul>
            <li>
              Since SOC has a long timeline, project ideas should be meaningful
              with a decent learning curve.
            </li>
            <li>
              Mentoring multiple projects is allowed, but equal time commitment
              is expected.
            </li>
            <li>
              Staying in the institute during the project is not mandatory.
            </li>
            <li>
              Mentors are encouraged to consider deployment and final
              presentation of the project. WnCC can assist with special
              requirements.
            </li>
          </ul>
        </motion.div>
      </motion.header>

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
            projects.map((project) => (
              <motion.div
                key={project.id}
                className="project_card"
                variants={fadeInUp}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedProject(project)} // Set selected project
              >
                <h3>{project.title}</h3>
                <p>{project.general_category}</p>
              </motion.div>
            ))
          )}

          {/* Add Project Button */}
          <motion.div
            className="add_project_card"
            variants={fadeInUp}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/mentor/add-project")}
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
        </motion.div>
      )}
    </motion.div>
  );
}

export default LandingPage;
