import React, { useState } from "react";
import { motion } from "framer-motion";
import "./MenteeList.css";

const MenteeList = () => {
  const [mentees, setMentees] = useState([
    { id: 1, name: "Mentee1", Roll: "23b0601", preference: "Preference-1", sop: "This is SOP for Mentee1." },
    { id: 2, name: "Mentee2", Roll: "23b0602", preference: "Preference-1", sop: "This is SOP for Mentee2." },
    { id: 3, name: "Mentee3", Roll: "23b0603", preference: "Preference-3", sop: "This is SOP for Mentee3." },
    { id: 4, name: "Mentee4", Roll: "23b0604", preference: "Preference-2", sop: "This is SOP for Mentee4." },
    { id: 5, name: "Mentee5", Roll: "23b0605", preference: "Preference-2", sop: "This is SOP for Mentee5." },
    { id: 6, name: "Mentee6", Roll: "23b0606", preference: "Preference-1", sop: "This is SOP for Mentee6." },
    { id: 7, name: "Mentee7", Roll: "23b0607", preference: "Preference-1", sop: "This is SOP for Mentee7." },
    { id: 8, name: "Mentee8", Roll: "23b0608", preference: "Preference-1", sop: "This is SOP for Mentee8." },
    { id: 9, name: "Mentee9", Roll: "23b0609", preference: "Preference-1", sop: "This is SOP for Mentee9." },
  ]);

  const [rankList, setRankList] = useState([]);
  const [selectedSOP, setSelectedSOP] = useState(null); // For SOP modal

  const selectMentee = (index) => {
    const selectedMentee = mentees[index];
    setRankList((prev) => [...prev, { ...selectedMentee, rank: prev.length + 1 }]);
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
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]]; // Swap with the previous item
      return updated;
    });
  };

  const moveDown = (index) => {
    if (index === rankList.length - 1) return;
    setRankList((prev) => {
      const updated = [...prev];
      [updated[index + 1], updated[index]] = [updated[index], updated[index + 1]]; // Swap with the next item
      return updated;
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
                  Rank:{index + 1}  {mentee.name} {mentee.Roll}  {mentee.preference}
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
      </div>

      {/* Mentee List */}
      <div className="mentee-list-container">
        <h2 className="section-title">Applied Mentees</h2>
        {mentees.map((mentee, index) => (
          <div className="mentee-card" key={mentee.id}>
            <div className="mentee-info">
              <p>
                ({mentee.id}) {mentee.name} {mentee.Roll} {mentee.preference}
              </p>
            </div>
            <div className="mentee-actions">
              <button
                className="action-button sop-button"
                onClick={() => openSOP(mentee.sop)}
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
