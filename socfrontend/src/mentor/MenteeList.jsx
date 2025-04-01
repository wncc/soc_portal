import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import "./MenteeList.css";
import axios from "axios";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

const MenteeList = ({ project }) => {
  const token = localStorage.getItem("authToken");
  const [mentees, setMentees] = useState([]);
  const [rankList, setRankList] = useState([]);
  const [preferenceRankList, setPreferenceRankList] = useState([]);
  const [loadingRankList, setLoadingRankList] = useState(true);
  const [selectedSOP, setSelectedSOP] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [showRankList, setShowRankList] = useState(false);

  const axiosConfig = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  };

  // Fetch mentor data
  useEffect(() => {
    axios
      .get(
        process.env.REACT_APP_BACKEND_URL +
          `/projects/mentor/profile/${project}`,
        axiosConfig
      )
      .then((response) => {
        setMentees(response.data.mentees);
      })
      .catch((error) => console.error("Error fetching mentor data:", error));
  }, []);

  // Fetch saved rank list
  useEffect(() => {
    if (project !== null) {
      setLoadingRankList(true);
      axios
        .get(
          `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/ranklist/${project}`,
          axiosConfig
        )
        .then((response) => {
          const savedRankList = response.data.rank_list || [];
          setRankList(savedRankList);
          setLoadingRankList(false);
        })
        .catch((error) => {
          console.error("Error fetching rank list:", error);
          setLoadingRankList(false);
        });
    }
  }, [project]);

  useEffect(() => {
    if (mentees.length > 0) {
      const savedMenteeIds = new Set(
        rankList
          .filter((entry) => entry?.mentee?.user_profile?.roll_number)
          .map((entry) => entry.mentee.user_profile.roll_number)
      );

      const sortedPreferenceList = mentees
        .filter(
          (mentee) =>
            mentee?.user_profile?.roll_number &&
            !savedMenteeIds.has(mentee.user_profile.roll_number)
        )
        .sort((a, b) => {
          const aPref = a.preferences?.preference ?? Infinity;
          const bPref = b.preferences?.preference ?? Infinity;
          return aPref - bPref;
        });

      setPreferenceRankList(sortedPreferenceList);
    }
  }, [mentees, rankList]);

  const selectMentee = (index) => {
    const selectedMentee = preferenceRankList[index];

    const newRankEntry = {
      mentee: {
        user_profile: selectedMentee.user_profile,
        season: selectedMentee.season,
        preferences: selectedMentee.preferences,
      },
      rank: rankList.length + 1,
      preference: selectedMentee.preferences?.preference ?? Infinity,
    };

    setRankList((prev) => [...prev, newRankEntry]);
    setPreferenceRankList((prev) => prev.filter((_, idx) => idx !== index));

    setShowRankList(true);
  };

  const openSOP = (sop) => setSelectedSOP(sop);
  const closeSOP = () => setSelectedSOP(null);

  const moveUp = (index) => {
    if (index === 0) return;
    setRankList((prev) => {
      const updated = [...prev];
      [updated[index - 1], updated[index]] = [
        updated[index],
        updated[index - 1],
      ];
      updated[index - 1].rank = index;
      updated[index].rank = index + 1;
      return updated;
    });
  };

  const moveDown = (index) => {
    if (index === rankList.length - 1) return;
    setRankList((prev) => {
      const updated = [...prev];
      [updated[index + 1], updated[index]] = [
        updated[index],
        updated[index + 1],
      ];
      updated[index + 1].rank = index + 2;
      updated[index].rank = index + 1;
      return updated;
    });
  };

  const removeMenteeFromRankList = (index) => {
    const removedMentee = rankList[index].mentee;

    setRankList((prev) => prev.filter((_, idx) => idx !== index));

    setPreferenceRankList((prev) => [...prev, removedMentee]);
    setShowRankList(true);
  };

  const saveRankList = () => {
    const rankListData = rankList.map((mentee) => ({
      mentee_id: mentee.mentee.user_profile.roll_number,
      rank: mentee.rank,
      preference: mentee.mentee.preferences.preference,
    }));

    axios
      .post(
        `${process.env.REACT_APP_BACKEND_URL}/projects/mentor/ranklist/${project}/`,
        { rank_list: rankListData },
        axiosConfig
      )
      .then(() => {
        setSuccessMessage("Rank List saved successfully!");
        setTimeout(() => setSuccessMessage(""), 2000);
      })
      .catch((error) => console.error("Error saving rank list:", error));
  };

  const onDragEnd = (result) => {
    const { source, destination } = result;

    if (!destination) {
      return; // Dropped outside the list
    }

    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return; // No change in position
    }

    const reorderedRankList = Array.from(rankList);
    const [movedItem] = reorderedRankList.splice(source.index, 1);
    reorderedRankList.splice(destination.index, 0, movedItem);

    const updatedRankList = reorderedRankList.map((mentee, index) => ({
      ...mentee,
      rank: index + 1, // Update rank based on new order
    }));

    setRankList(updatedRankList); // Update state immediately
  };

  useEffect(() => {
    const interval = setInterval(() => {
      saveRankList(); // This will be your save function
    }, 20000); // 20000 milliseconds = 20 seconds

    return () => clearInterval(interval); // Cleanup when the component unmounts
  }, [rankList]);

  return (
    <motion.div
      className="mentee-container"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {successMessage && (
        <motion.div
          className="success-popup"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {successMessage}
        </motion.div>
      )}

      {/* SOP Modal */}
      {selectedSOP && (
        <div className="sop-modal-overlay" onClick={closeSOP}>
          <motion.div
            className="sop-modal"
            onClick={(e) => e.stopPropagation()}
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

      {/* Saved Rank List */}
      <div className="rank-list-container">
        <h2 className="section-title"> Rank List</h2>
        {loadingRankList ? (
          <p>Loading rank list...</p>
        ) : rankList.length === 0 ? (
          <p className="empty-message">No mentees in the rank list yet.</p>
        ) : (
          <DragDropContext
            onDragEnd={onDragEnd}
            dragEndTransition={{ duration: 0.2 }}
          >
            <Droppable droppableId="rankList" direction="vertical">
              {(provided) => (
                <div
                  className="rank-list"
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                >
                  {rankList.map((mentee, index) => (
                    <Draggable
                      key={mentee.mentee.preferences.id}
                      draggableId={String(mentee.mentee.preferences.id)}
                      index={index}
                    >
                      {(provided) => (
                        <div
                          className="rank-card"
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          <div className="rank-info">
                            <p>
                              Rank: {index + 1}{" "}
                              {mentee.mentee.user_profile?.name}{" "}
                              {mentee.user_profile?.roll_number} Preference:
                              {mentee.mentee.preferences?.preference}
                            </p>
                          </div>
                          <div className="rank-actions-row">
                            <button
                              className="action-button sop-button"
                              onClick={() =>
                                openSOP(mentee.mentee.preferences?.sop)
                              }
                            >
                              SOP
                            </button>
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
                            <button
                              onClick={() => removeMenteeFromRankList(index)}
                            >
                              <svg
                                width="38px"
                                height="38px"
                                viewBox="0 0 24 24"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                              >
                                <path
                                  d="M10 12V17"
                                  stroke="#000000"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                ></path>
                                <path
                                  d="M14 12V17"
                                  stroke="#000000"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                ></path>
                                <path
                                  d="M4 7H20"
                                  stroke="#000000"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                ></path>
                                <path
                                  d="M6 10V18C6 19.6569 7.34315 21 9 21H15C16.6569 21 18 19.6569 18 18V10"
                                  stroke="#000000"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                ></path>
                                <path
                                  d="M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5V7H9V5Z"
                                  stroke="#000000"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                ></path>
                              </svg>
                            </button>
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        )}
        <motion.div className="save-modal">
          <button className="save-button" onClick={saveRankList} style={{ width: '100%', height: '100%' }}>
            Save Rank List
          </button>
        </motion.div>
      </div>

      {/* Preference-Based Rank List */}
      <div className="mentee-list-container">
        <h2 className="section-title"> Applied Mentee List</h2>
        {preferenceRankList.length === 0 ? (
          <p>No mentees available for selection.</p>
        ) : (
          preferenceRankList.map((mentee, index) => (
            <div className="mentee-card" key={mentee.id}>
              <div className="mentee-info">
                <p>
                  {mentee.user_profile?.name} {mentee.user_profile?.roll_number}{" "}
                  Preference: {mentee.preferences?.preference}
                </p>
              </div>
              <div className="mentee-actions">
                <button
                  className="action-button sop-button"
                  onClick={() => openSOP(mentee.preferences?.sop)}
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
          ))
        )}
      </div>
    </motion.div>
  );
};

export default MenteeList;
