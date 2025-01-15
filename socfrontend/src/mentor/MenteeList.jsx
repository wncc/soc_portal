import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import "./MenteeList.css";
import axios from "axios";

const MenteeList = () => {
  const token = localStorage.getItem("authToken");
  const [mentees, setMentees] = useState([]);

  const axiosConfig = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  };
  // Fetch mentor data from the backend
  useEffect(() => {
    // You can replace this URL with the correct endpoint to fetch the current mentor's data
    axios
      .get(
        process.env.REACT_APP_BACKEND_URL + "/projects/mentor/profile",
        axiosConfig
      )
      .then((response) => {
        const sortedMentees = response.data.mentees.sort((a, b) => {
          const aPreference = a.preferences.preference || Infinity;
          const bPreference = b.preferences.preference || Infinity;
          return aPreference - bPreference;
        });
        setMentees(sortedMentees);
      })
      .catch((error) => {
        console.error("Error fetching mentor data:", error);
      });
  }, []);

  const [rankList, setRankList] = useState([]);
  const [selectedSOP, setSelectedSOP] = useState(null); // For SOP modal

  const selectMentee = (index) => {
    const selectedMentee = mentees[index];
    setRankList((prev) => [
      ...prev,
      { ...selectedMentee, rank: prev.length + 1 },
    ]);
    setMentees((prev) => prev.filter((_, idx) => idx !== index));
  };

  const openSOP = (sop) => {
    setSelectedSOP(sop);
  };

  const closeSOP = () => {
    setSelectedSOP(null);
  };

  const moveUp = (index) => {
    if (index === 0) return;
    setRankList((prev) => {
      const updated = [...prev];
      [updated[index - 1], updated[index]] = [
        updated[index],
        updated[index - 1],
      ]; // Swap with the previous item
      updated[index - 1].rank = index;
      updated[index].rank = index + 1;
      return updated;
    });
  };
  console.log(rankList)
  const moveDown = (index) => {
    if (index === rankList.length - 1) return;
    setRankList((prev) => {
      const updated = [...prev];
      [updated[index + 1], updated[index]] = [
        updated[index],
        updated[index + 1],
      ]; // Swap with the next item
      updated[index + 1].rank = index + 2;
      updated[index].rank = index + 1;
      return updated;
    });
  };
  
  const saveRankList = () => {
    const token = localStorage.getItem("authToken");
    
    if (!token) {
      console.error("No auth token found.");
      return;
    }

    const axiosConfig = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };

    // Prepare data to be sent to the backend
    const rankListData = rankList.map((mentee) => ({
      mentee_id: mentee.user_profile.roll_number,
      rank: mentee.rank,
    }));

    console.log(rankListData)

    axios
      .post(
        process.env.REACT_APP_BACKEND_URL + "/projects/mentor/ranklist/", // Ensure this URL matches the backend URL
        { rank_list: rankListData },
        axiosConfig
      )
      .then((response) => {
        console.log("Rank List saved:", response.data);
        // Optionally, you can show a success message here
      })
      .catch((error) => {
        console.error("Error saving rank list:", error);
        // Optionally, you can show an error message here
      });
  };

  return (
    <motion.div
      className="mentee-container"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* SOP Modal */}
      {selectedSOP && (
        <div className="sop-modal-overlay" onClick={closeSOP}>
          <motion.div
            className="sop-modal"
            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h3 className="sop-title">SOP</h3>
            <p className="sop-content">{selectedSOP}</p>
          </motion.div>
        </div>
      )}

      {/* Rank List */}
      <div className="rank-list-container">
        <h2 className="section-title">Rank List</h2>
        {rankList.length === 0 ? (
          <p className="empty-message">No mentees in the rank list yet.</p>
        ) : (
          <div className="rank-list">
            {rankList.map((mentee, index) => (
              <div className="rank-card" key={mentee.id}>
                <div className="rank-info">
                  <p>
                    Rank:{index + 1} {mentee.user_profile.name}{" "}
                    {mentee.user_profile.roll_number}{" "}
                    Preference:{mentee.preferences.preference}
                  </p>
                </div>
                <div className="rank-actions-row">
                  <button
                    className="action-button move-up"
                    onClick={() => moveUp(index)}
                  >
                    Move Up
                  </button>
                  <button
                    className="action-button move-down"
                    onClick={() => moveDown(index)}
                  >
                    Move Down
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        <motion.div className="save-modal">
          <button className="save-button" onClick={saveRankList}>
            Save Rank List
          </button>
        </motion.div>
      </div>

      {/* Mentee List */}
      <div className="mentee-list-container">
        <h2 className="section-title">Applied Mentees</h2>
        {mentees
          .map((mentee, index) => (
            <div className="mentee-card" key={mentee.id}>
              <div className="mentee-info">
                <p>
                  {mentee.user_profile.name} {mentee.user_profile.roll_number}{" "}
                  Preference:{mentee.preferences.preference}
                </p>
              </div>
              <div className="mentee-actions">
                <button
                  className="action-button sop-button"
                  onClick={() => openSOP(mentee.preferences.sop)}
                >
                  SOP
                </button>
                <button
                  className="action-button select-button"
                  onClick={() => selectMentee(index)}
                >
                  Select
                </button>
              </div>
            </div>
          ))}
      </div>
    </motion.div>
  );
};

export default MenteeList;
