// import React from "react";
// import api from "../../utils/api";
// import { useState, useEffect } from "react";
// import PreferenceFormFilled from "../pages/PreferenceFormFilled";
// import { Navigate } from "react-router-dom";

// export default function PreferenceForm() {
//   //to get titles of projects for the dropdown
//   const [details, setDetails] = useState([]);
//   const [userPreference, setUserPreference] = useState([]);
//   const [page, setPage] = useState(1);
//   const [submitted, setSubmitted] = useState(false);
//   const [error, setError] = useState(false);
//   const [error1, setError1] = useState(false);

//   useEffect(() => {
//     // Make an HTTP request to fetch the card image from the backend
//     api
//       .get(process.env.REACT_APP_BACKEND_URL + "/projects/wishlist/")
//       .then((response) => {
//         // Assuming the response contains the image URL
//         console.log(response.data);
//         setDetails(response.data);
//         setSubmitted(false);
//       })
//       .catch((error) => {
//         console.error("Error fetching card image:", error);
//       });
//   }, []);

//   useEffect(() => {
//     // Make an HTTP request to fetch the card image from the backend
//     api
//       .get(process.env.REACT_APP_BACKEND_URL + "/projects/preference")
//       .then((response) => {
//         // Assuming the response contains the image URL
//         console.log(response.data);
//         setUserPreference(response.data);
//       })
//       .catch((error) => {
//         console.error("Error fetching card image:", error);
//       });
//   }, []);

//   const [data1, setData1] = useState({
//     project: "",
//     sop: "",
//     preference: 1,
//   });
//   const [data2, setData2] = useState({
//     project: "",
//     sop: "",
//     preference: 2,
//   });
//   const [data3, setData3] = useState({
//     project: "",
//     sop: "",
//     preference: 3,
//   });

//   if (userPreference.length > 0) {
//     return <Navigate to="/PreferenceFormFilled" />;
//   }
//   const dataChange1 = (e) => {
//     const { id, value } = e.target;
//     setData1({
//       ...data1,
//       [id]: value,
//       // console.log(projectlist)
//     });
//     setSubmitted(false);
//     console.log("id:", id);
//     console.log("value:", value);
//     console.log(data1);
//   };
//   const dataChange2 = (e) => {
//     const { id, value } = e.target;
//     setData2({
//       ...data2,
//       [id]: value,
//       // console.log(projectlist)
//     });
//     setSubmitted(false);
//     console.log("id:", id);
//     console.log("value:", value);
//     console.log(data2);
//   };
//   const dataChange3 = (e) => {
//     const { id, value } = e.target;
//     setData3({
//       ...data3,
//       [id]: value,
//       // console.log(projectlist)
//     });
//     setSubmitted(false);
//     console.log("id:", id);
//     console.log("value:", value);
//     console.log(data3);
//   };

//   const handleSubmit = (e) => {
//     console.log(data1);
//     console.log(data2);
//     console.log(data3);
//     e.preventDefault();
//     if (
//       data1.project === "" ||
//       data1.sop === "" ||
//       data2.project === "" ||
//       data2.sop === "" ||
//       data3.project === "" ||
//       data3.sop === ""
//     ) {
//       setError(true);
//     } else if (
//       data1.project === data2.project ||
//       data1.project === data3.project ||
//       data3.project === data2.project
//     ) {
//       setError1(true);
//     } else {
//       setSubmitted(true);
//       setError(false);

//       const formData1 = new FormData();
//       Object.keys(data1).forEach((key) => {
//         formData1.append(key, data1[key]);
//       });
//       const formData2 = new FormData();
//       Object.keys(data2).forEach((key) => {
//         formData2.append(key, data2[key]);
//       });
//       const formData3 = new FormData();
//       Object.keys(data3).forEach((key) => {
//         formData3.append(key, data3[key]);
//       });

//       api
//         .post(
//           process.env.REACT_APP_BACKEND_URL + "/projects/preference/",
//           formData1
//         )
//         .then((res) => {
//           console.log(res);
//         })
//         .catch((err) => {
//           console.log(err);
//           setError(true);
//         });
//       api
//         .post(
//           process.env.REACT_APP_BACKEND_URL + "/projects/preference/",
//           formData2
//         )
//         .then((res) => {
//           console.log(res);
//         })
//         .catch((err) => {
//           console.log(err);
//           setError(true);
//         });
//       api
//         .post(
//           process.env.REACT_APP_BACKEND_URL + "/projects/preference/",
//           formData3
//         )
//         .then((res) => {
//           console.log(res);
//           setSubmitted(true);
//         })
//         .catch((err) => {
//           console.log(err);
//           setError(true);
//         });
//     }
//   };

//   if (submitted) {
//     return <Navigate to="/PreferenceFormFilled" />;
//   }

//   const successMessage = () => {
//     return (
//       <>
//         <div
//           className="success dark:bg-gray-800 dark:text-white"
//           style={{
//             display: submitted ? "" : "none",
//           }}
//         >
//           <div
//             role="alert"
//             className="rounded-xl border border-gray-100 bg-white p-4"
//           >
//             <div className="flex items-start gap-4">
//               <span className="text-green-600">
//                 <svg
//                   xmlns="http://www.w3.org/2000/svg"
//                   fill="none"
//                   viewBox="0 0 24 24"
//                   strokeWidth="1.5"
//                   stroke="currentColor"
//                   className="h-6 w-6"
//                 >
//                   <path
//                     strokeLinecap="round"
//                     strokeLinejoin="round"
//                     d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
//                   />
//                 </svg>
//               </span>

//               <div className="flex-1">
//                 <strong className="block font-medium text-gray-900">
//                   {" "}
//                   Thank You{" "}
//                 </strong>

//                 <p className="mt-1 text-sm text-gray-700">
//                   You have successfully filled the form.
//                 </p>
//               </div>

//               <button className="text-gray-500 transition hover:text-gray-600">
//                 <span className="sr-only">Dismiss popup</span>

//                 <svg
//                   xmlns="http://www.w3.org/2000/svg"
//                   fill="none"
//                   viewBox="0 0 24 24"
//                   strokeWidth="1.5"
//                   stroke="currentColor"
//                   className="h-6 w-6"
//                 >
//                   <path
//                     strokeLinecap="round"
//                     strokeLinejoin="round"
//                     d="M6 18L18 6M6 6l12 12"
//                   />
//                 </svg>
//               </button>
//             </div>
//           </div>
//         </div>
//       </>
//     );
//   };

//   function ErrorPopup({ message, onClose }) {
//     if (!message) return null;

//     return (
//       <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg max-w-sm text-center">
//           <div className="text-red-600 dark:text-red-400 mb-2">
//             <svg
//               xmlns="http://www.w3.org/2000/svg"
//               viewBox="0 0 24 24"
//               fill="currentColor"
//               className="w-12 h-12 mx-auto"
//             >
//               <path
//                 fillRule="evenodd"
//                 d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z"
//                 clipRule="evenodd"
//               />
//             </svg>
//           </div>
//           <p className="text-lg font-semibold text-gray-800 dark:text-white">
//             {message}
//           </p>
//           <button
//             onClick={onClose}
//             className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg"
//           >
//             OK
//           </button>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <>
//       <div className="form h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
//         {/* Calling to the methods */}
//         <div className="messages">
//         {error && <ErrorPopup message={"All fields are Required"} onClose={() => setError(false)} />}
//         {error1 && (
//           <ErrorPopup message={"Cannot Repeat Preferences."} onClose={() => setError1(false)} />
//         )}
//           {successMessage()}
//         </div>

//         <div className="mx-auto max-w-screen-xl px-4 py-16 sm:px-6 lg:px-8">
//           <div className="mx-auto max-w-lg">
//             <h1 className="text-center text-2xl font-bold text-indigo-600 sm:text-3xl flex items-center justify-center">
//               <svg
//                 xmlns="http://www.w3.org/2000/svg"
//                 fill="none"
//                 viewBox="0 0 24 24"
//                 strokeWidth={1.5}
//                 stroke="currentColor"
//                 className="w-10 h-10"
//               >
//                 <path
//                   strokeLinecap="round"
//                   strokeLinejoin="round"
//                   d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
//                 />
//               </svg>
//               <span className="mx-3">Seasons of Code</span>
//               <svg
//                 xmlns="http://www.w3.org/2000/svg"
//                 fill="none"
//                 viewBox="0 0 24 24"
//                 strokeWidth={1.5}
//                 stroke="currentColor"
//                 className="w-10 h-10"
//               >
//                 <path
//                   strokeLinecap="round"
//                   strokeLinejoin="round"
//                   d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
//                 />
//               </svg>
//             </h1>

//             <form className="mb-0 mt-6 space-y-4 rounded-lg p-4 shadow-2xl sm:p-6 lg:p-8">
//               <p className="text-center text-lg font-medium">Preference Form</p>
//               {page === 1 && (
//                 <Page2
//                   project={data1.project}
//                   sop={data1.sop}
//                   dataChange={dataChange1}
//                   setPage={setPage}
//                   details={details}
//                 />
//               )}
//               {page === 2 && (
//                 <Page3
//                   project={data2.project}
//                   sop={data2.sop}
//                   dataChange={dataChange2}
//                   setPage={setPage}
//                   details={details}
//                 />
//               )}
//               {page === 3 && (
//                 <Page4
//                   project={data3.project}
//                   sop={data3.sop}
//                   dataChange={dataChange3}
//                   setPage={setPage}
//                   details={details}
//                   handleSubmit={handleSubmit}
//                 />
//               )}
//             </form>
//           </div>
//         </div>
//       </div>
//     </>
//   );
// }

// const Page2 = ({ project, sop, dataChange, setPage, details }) => {
//   return (
//     <>
//       <div className="inline-block relative w-full">
//         <label htmlFor="project" className="block text-sm font-medium">
//           {" "}
//           Project 1{" "}
//         </label>

//         <select
//           id="project"
//           name="project"
//           className="w-full rounded-lg border-gray-200 p-4 pe-12 text-sm shadow-sm  dark:bg-gray-800 "
//           onChange={dataChange}
//           value={project}
//           required
//         >
//           <option value="">Please select</option>
//           {details.map((details, index) => (
//             <option key={index} value={details.id}>
//               {`Project ID: ${details.id} ${details.title}`}
//             </option>
//           ))}
//         </select>
//       </div>

//       <div>
//         <label htmlFor="sop" className="block text-sm font-medium">
//           Statement of Purpose
//         </label>

//         <textarea
//           id="sop"
//           className="mt-2 w-full rounded-lg border-gray-200 p-4 pe-12 align-top shadow-sm sm:text-sm  dark:bg-gray-800 "
//           rows="4"
//           placeholder="Write your SOP here..."
//           required
//           value={sop}
//           onChange={dataChange}
//           aria-required
//         ></textarea>
//       </div>
//       <button
//         type="submit"
//         className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white flex items-center justify-center"
//         onClick={() => setPage(2)}
//       >
//         Next
//         <svg
//           xmlns="http://www.w3.org/2000/svg"
//           fill="none"
//           viewBox="0 0 24 24"
//           strokeWidth={1.5}
//           stroke="currentColor"
//           className="w-6 h-6"
//         >
//           <path
//             strokeLinecap="round"
//             strokeLinejoin="round"
//             d="m8.25 4.5 7.5 7.5-7.5 7.5"
//           />
//         </svg>
//       </button>
//     </>
//   );
// };
// const Page3 = ({ project, sop, dataChange, setPage, details }) => {
//   return (
//     <>
//       <div className="inline-block relative w-full">
//         <label htmlFor="project" className="block text-sm font-medium">
//           {" "}
//           Project 2{" "}
//         </label>

//         <select
//           id="project"
//           name="project"
//           className="w-full rounded-lg border-gray-200 p-4 pe-12 text-sm shadow-sm  dark:bg-gray-800 "
//           onChange={dataChange}
//           value={project}
//           required
//         >
//           <option value="">Please select</option>
//           {details.map((details, index) => (
//             <option key={index} value={details.id}>
//               {`Project ID: ${details.id} ${details.title}`}
//             </option>
//           ))}
//         </select>
//       </div>

//       <div>
//         <label htmlFor="sop" className="block text-sm font-medium">
//           Statement of Purpose
//         </label>

//         <textarea
//           id="sop"
//           className="mt-2 w-full rounded-lg border-gray-200 p-4 pe-12 align-top shadow-sm sm:text-sm  dark:bg-gray-800 "
//           rows="4"
//           placeholder="Write your SOP here..."
//           required
//           value={sop}
//           onChange={dataChange}
//         ></textarea>
//       </div>

//       <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-8">
//         <button
//           type="submit"
//           className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white flex items-center justify-center"
//           onClick={() => setPage(1)}
//         >
//           <svg
//             xmlns="http://www.w3.org/2000/svg"
//             fill="none"
//             viewBox="0 0 24 24"
//             strokeWidth={1.5}
//             stroke="currentColor"
//             className="w-6 h-6"
//           >
//             <path
//               strokeLinecap="round"
//               strokeLinejoin="round"
//               d="M15.75 19.5 8.25 12l7.5-7.5"
//             />
//           </svg>
//           Prev
//         </button>
//         <button
//           type="submit"
//           className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white flex items-center justify-center"
//           onClick={() => setPage(3)}
//         >
//           Next
//           <svg
//             xmlns="http://www.w3.org/2000/svg"
//             fill="none"
//             viewBox="0 0 24 24"
//             strokeWidth={1.5}
//             stroke="currentColor"
//             className="w-6 h-6"
//           >
//             <path
//               strokeLinecap="round"
//               strokeLinejoin="round"
//               d="m8.25 4.5 7.5 7.5-7.5 7.5"
//             />
//           </svg>
//         </button>
//       </div>
//     </>
//   );
// };
// const Page4 = ({
//   project,
//   sop,
//   dataChange,
//   setPage,
//   details,
//   handleSubmit,
// }) => {
//   return (
//     <>
//       <div className="inline-block relative w-full">
//         <label htmlFor="project" className="block text-sm font-medium">
//           {" "}
//           Project 3{" "}
//         </label>

//         <select
//           id="project"
//           name="project"
//           className="w-full rounded-lg border-gray-200 p-4 pe-12 text-sm shadow-sm  dark:bg-gray-800 "
//           onChange={dataChange}
//           value={project}
//           required
//         >
//           <option value="">Please select</option>
//           {details.map((details, index) => (
//             <option key={index} value={details.id}>
//               {`Project ID: ${details.id} ${details.title}`}
//             </option>
//           ))}
//         </select>
//       </div>

//       <div>
//         <label htmlFor="sop" className="block text-sm font-medium">
//           Statement of Purpose
//         </label>

//         <textarea
//           id="sop"
//           className="mt-2 w-full rounded-lg border-gray-200 p-4 pe-12 align-top shadow-sm sm:text-sm  dark:bg-gray-800 "
//           rows="4"
//           placeholder="Write your SOP here..."
//           required
//           value={sop}
//           onChange={dataChange}
//         ></textarea>
//       </div>
//       <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-8">
//         <button
//           type="submit"
//           className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white flex items-center justify-center"
//           onClick={() => setPage(2)}
//         >
//           <svg
//             xmlns="http://www.w3.org/2000/svg"
//             fill="none"
//             viewBox="0 0 24 24"
//             strokeWidth={1.5}
//             stroke="currentColor"
//             className="w-6 h-6"
//           >
//             <path
//               strokeLinecap="round"
//               strokeLinejoin="round"
//               d="M15.75 19.5 8.25 12l7.5-7.5"
//             />
//           </svg>
//           Prev
//         </button>
//         <button
//           type="submit"
//           className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white"
//           onClick={handleSubmit}
//         >
//           Submit
//         </button>
//       </div>
//     </>
//   );
// };

import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import api from '../../utils/api';

export default function PreferenceForm() {
  const [details, setDetails] = useState([]);
  const [userPreference, setUserPreference] = useState([]);
  const [page, setPage] = useState(1);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(false);
  const [error1, setError1] = useState(false);

  useEffect(() => {
    api
      .get(process.env.REACT_APP_BACKEND_URL + '/projects/wishlist/')
      .then((response) => setDetails(response.data))
      .catch((error) => console.error('Error fetching projects:', error));
  }, []);

  useEffect(() => {
    api
      .get(process.env.REACT_APP_BACKEND_URL + '/projects/preference')
      .then((response) => setUserPreference(response.data))
      .catch((error) => console.error('Error fetching preferences:', error));
  }, []);

  const [selectedProjects, setSelectedProjects] = useState(['', '', '']);
  const [data, setData] = useState([
    { project: '', sop: '', preference: 1 },
    { project: '', sop: '', preference: 2 },
    { project: '', sop: '', preference: 3 },
  ]);

  if (userPreference.length > 0) {
    return <Navigate to="/PreferenceFormFilled" />;
  }

  if (submitted) {
    return <Navigate to="/PreferenceFormFilled" />;
  }

  return (
    <div className="form h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
      <div className="mx-auto max-w-screen-xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-lg">
          <h1 className="text-center text-2xl font-bold text-indigo-600 sm:text-3xl">
            Preference Form
          </h1>

          {/* Remove onSubmit to prevent form auto-submitting */}
          <form className="mt-6 space-y-4 p-4 shadow-2xl sm:p-6 lg:p-8">
            {page >= 1 && page <= 3 && (
              <Page
                data={data}
                setData={setData}
                details={details}
                page={page}
                setPage={setPage}
                selectedProjects={selectedProjects}
                setSelectedProjects={setSelectedProjects}
                setSubmitted={setSubmitted} // Pass submit handler to third page only
                setError={setError}
                setError1={setError1}
              />
            )}
          </form>

          {error && <p className="text-red-500">Please fill SOPs.</p>}
          {error1 && <p className="text-red-500">Select 3 unique projects.</p>}
        </div>
      </div>
    </div>
  );
}

const Page = ({
  data,
  setData,
  details,
  page,
  setPage,
  selectedProjects,
  setSelectedProjects,
  setSubmitted,
  setError,
  setError1,
}) => {
  const [showConfirmPopup, setShowConfirmPopup] = useState(false); // <-- new
  useEffect(() => {
    setSelectedProjects([...selectedProjects]); // Ensures state persistence
  }, [page]);

  const handleSubmitClick = (e) => {
    e.preventDefault();
    setError(false);
    setError1(false);

    const filteredData = data.filter(({ project, sop }) => project.trim() !== '');

    if (filteredData.length === 0) {
      setError(true);
      return;
    }

    const selectedProjectIDs = filteredData.map((entry) => entry.project);
    if (new Set(selectedProjectIDs).size !== selectedProjectIDs.length) {
      setError1(true);
      return;
    }

    setShowConfirmPopup(true); // <-- show confirmation popup
  };

  const actuallySubmit = () => {
    const filteredData = data.filter(({ project, sop }) => project.trim() !== '');

    const submitData = filteredData.map((entry) => {
      const formData = new FormData();
      Object.keys(entry).forEach((key) => formData.append(key, entry[key]));
      return api.post(`${process.env.REACT_APP_BACKEND_URL}/projects/preference/`, formData);
    });

    Promise.all(submitData)
      .then(() => setSubmitted(true))
      .catch(() => setError(true));
  };

  const handleNextPage = () => setPage(page + 1);
  const handlePrevPage = () => setPage(page - 1);

  const handleProjectChange = (e) => {
    const { value } = e.target;
    const newSelectedProjects = [...selectedProjects];
    newSelectedProjects[page - 1] = value;
    setSelectedProjects(newSelectedProjects);

    const newData = [...data];
    newData[page - 1].project = value;
    setData(newData);
  };

  const handleSOPChange = (e) => {
    const newData = [...data];
    newData[page - 1].sop = e.target.value;
    setData(newData);
  };

  const availableProjects = details.filter(
    (p) => !selectedProjects.includes(p.id.toString()) || p.id.toString() === selectedProjects[page - 1],
  );

  const handleConfirm = () => {
    setShowConfirmPopup(false);
    actuallySubmit();
  };

  const handleCancel = () => {
    setShowConfirmPopup(false);
  };


  return (
    <div>
      <div className="inline-block relative w-full">
        <label htmlFor="project" className="block text-sm font-medium">{`Project ${page}`}</label>
        <select
          id="project"
          name="project"
          className="w-full rounded-lg border-gray-200 p-4 text-sm shadow-sm dark:bg-gray-800"
          onChange={handleProjectChange}
          value={selectedProjects[page - 1]}
          required
        >
          <option value="">Please select</option>
          {availableProjects.map(({ id, title }) => (
            <option key={id} value={id}>{`Project ID: ${id} - ${title}`}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="sop" className="block text-sm font-medium">Statement of Purpose</label>
        <textarea
          id="sop"
          className="mt-2 w-full rounded-lg border-gray-200 p-4 shadow-sm dark:bg-gray-800"
          rows="4"
          placeholder="Write your SOP here..."
          required
          value={data[page - 1].sop}
          onChange={handleSOPChange}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-8">
        {page > 1 && (
          <button
            type="button"
            className="block w-full rounded-lg bg-gray-600 px-5 py-3 text-sm font-medium text-white"
            onClick={handlePrevPage}
          >
            Prev
          </button>
        )}
        {page === 3 ? (
          <button
            type="button" // Changed from submit to button
            className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white"
            onClick={handleSubmitClick} // Only submit when clicked
          >
            Submit
          </button>
        ) : (
          <button
            type="button"
            className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white"
            onClick={handleNextPage}
          >
            Next
          </button>
        )}
      </div>
      {showConfirmPopup && (
        <ConfirmationPopup onConfirm={handleConfirm} onCancel={handleCancel} />
      )}
    </div>
  );
};

function ConfirmationPopup({ onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg max-w-sm text-center">
        <div className="text-indigo-600 dark:text-indigo-400 mb-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-12 h-12 mx-auto"
          >
            <path
              fillRule="evenodd"
              d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 15a1 1 0 110-2 1 1 0 010 2zm.75-4.75a.75.75 0 00-1.5 0V7a.75.75 0 001.5 0v5.25z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <p className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
          Are you sure you want to submit your preferences?
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg"
          >
            Confirm
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-400 text-white rounded-lg"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
