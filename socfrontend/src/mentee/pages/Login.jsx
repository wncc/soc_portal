// import { useState } from "react";
// import api from "../../utils/api";
// import { Link, useNavigate } from "react-router-dom";

// export default function Login() {
//   // States for user profile
//   const [profile, setProfile] = useState({
//     username: "",
//     password: "",
//   });

//   // States for checking the errors
//   const [error, setError] = useState(false);
//   const [isMentor, setIsMentor] = useState(true);

//   const navigate = useNavigate();

//   // Handling input change
//   const handleProfile = (e) => {
//     const { id, value } = e.target;
//     setProfile((prevProfile) => ({
//       ...prevProfile,
//       [id]: id === "username" ? value.toLowerCase() : value,
//     }));
//     setError(false);
//   };

//   // Handling form submission
//   const handleSubmit = (e) => {
//     e.preventDefault();
//     const baseUrl = process.env.REACT_APP_BACKEND_URL + `/accounts`;
//     const formData = new FormData();
//     Object.keys(profile).forEach((key) => {
//       formData.append(key, profile[key]);
//     });
//     formData.append('role', isMentor ? 'mentor' : 'mentee');
//     api
//       .post(`${baseUrl}/token/`, formData)
//       .then(function (response) {
//         const token = response.data.access; // Extract token
//         const role = response.data.role;
//         console.log("Login successful, token:", token);
//         console.log("Login successful, role:", role);

//         // Store the token in localStorage
//         localStorage.setItem("role", role);
//         localStorage.setItem("authToken", token);
//         // Redirect to Dashboard and reload the page
//         if (isMentor) {
//           console.log("Hello Mentor")
//           navigate('/mentor/home')
//         } else {
//           window.location.reload();
//         }
        
//       })
//       .catch((err) => {
//         console.log("Login failed:", err);
//         setError(true);
//         localStorage.removeItem("authToken");
//       });
//   };

//   const [passwordVisible, setPasswordVisible] = useState(false);

//   const togglePasswordVisibility = () => {
//     setPasswordVisible(!passwordVisible);
//   };

//   // Error message display
//   function ErrorPopup({ onClose }) {

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
//             Wrong Username or Password
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
//     <div className="form h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
//       <div className="messages">{error && <ErrorPopup onClose={() => setError(false)} />}</div>

//       <div className="mx-auto max-w-screen-xl px-4 py-16 sm:px-6 lg:px-8">
//         <div className="mx-auto max-w-lg">
//           <h1 className="text-center text-2xl font-bold text-indigo-600 sm:text-3xl flex items-center justify-center">
//             <svg
//               xmlns="http://www.w3.org/2000/svg"
//               fill="none"
//               viewBox="0 0 24 24"
//               strokeWidth={1.5}
//               stroke="currentColor"
//               className="w-10 h-10"
//             >
//               <path
//                 strokeLinecap="round"
//                 strokeLinejoin="round"
//                 d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
//               />
//             </svg>
//             <span className="mx-3">Seasons of Code</span>
//             <svg
//               xmlns="http://www.w3.org/2000/svg"
//               fill="none"
//               viewBox="0 0 24 24"
//               strokeWidth={1.5}
//               stroke="currentColor"
//               className="w-10 h-10"
//             >
//               <path
//                 strokeLinecap="round"
//                 strokeLinejoin="round"
//                 d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
//               />
//             </svg>
//           </h1>

//           <div className="flex justify-center gap-4 my-4">
//             <button
//               className={`px-4 py-2 font-medium ${
//                 isMentor ? "bg-indigo-600 text-white dark:bg-indigo-600 dark:text-white" : "bg-gray-200 dark:bg-gray-700 dark:text-white"
//               } rounded`}
//               onClick={() => {setIsMentor(true);console.log(isMentor);}}
//             >
//               Mentor
//             </button>
//             <button
//               className={`px-4 py-2 font-medium ${
//                 !isMentor ? "bg-indigo-600 text-white dark:bg-indigo-600 dark:text-white" : "bg-gray-200 dark:bg-gray-700 dark:text-white"
//               } rounded`}
//               onClick={() => {setIsMentor(false);console.log(isMentor);}}
//             >
//               Mentee
//             </button>
            
//           </div>

//           <form
//             onSubmit={handleSubmit}
//             className="mb-0 mt-6 space-y-4 rounded-lg p-4 shadow-lg sm:p-6 lg:p-8 dark:bg-slate-700 "
//           >
//             <p className="text-center text-lg font-medium">
//               Login to your account
//             </p>

//             <div>
//               <label htmlFor="username">Roll No.</label>
//               <div className="relative">
//                 <input
//                   type="text"
//                   id="username"
//                   className="w-full rounded-lg border-gray-200 p-4 pe-12 text-sm shadow-sm dark:bg-gray-800"
//                   placeholder="Enter Roll No."
//                   onChange={handleProfile}
//                   required
//                 />
//               </div>
//             </div>

//             <div>
//               <label htmlFor="password">Password</label>
//               <div className="relative">
//                 <input
//                   type={passwordVisible ? "text" : "password"}
//                   id="password"
//                   className="w-full rounded-lg border-gray-200 p-4 pe-12 text-sm shadow-sm dark:bg-gray-800"
//                   placeholder="Enter Password"
//                   onChange={handleProfile}
//                   required
//                 />
//                 <span
//                   className="absolute inset-y-0 right-4 flex items-center cursor-pointer"
//                   onClick={togglePasswordVisibility}
//                 >
//                   {passwordVisible ? (
//                     <svg
//                       width="24"
//                       height="24"
//                       stroke-width="1.5"
//                       viewBox="0 0 24 24"
//                       fill="none"
//                       xmlns="http://www.w3.org/2000/svg"
//                     >
//                       <path
//                         d="M3 3L21 21"
//                         stroke="currentColor"
//                         stroke-linecap="round"
//                         stroke-linejoin="round"
//                       />
//                       <path
//                         d="M10.5 10.6771C10.1888 11.0296 10 11.4928 10 12C10 13.1045 10.8954 14 12 14C12.5072 14 12.9703 13.8112 13.3229 13.5"
//                         stroke="currentColor"
//                         stroke-linecap="round"
//                         stroke-linejoin="round"
//                       />
//                       <path
//                         d="M7.36185 7.5611C5.68002 8.73968 4.27894 10.4188 3 12C4.88856 14.991 8.2817 18 12 18C13.5499 18 15.0434 17.4772 16.3949 16.6508"
//                         stroke="currentColor"
//                         stroke-linecap="round"
//                         stroke-linejoin="round"
//                       />
//                       <path
//                         d="M12 6C16.0084 6 18.7015 9.1582 21 12C20.6815 12.5043 20.3203 13.0092 19.922 13.5"
//                         stroke="currentColor"
//                         stroke-linecap="round"
//                         stroke-linejoin="round"
//                       />
//                     </svg>
//                   ) : (
//                     <svg
//                       width="24"
//                       height="24"
//                       stroke-width="1.5"
//                       viewBox="0 0 24 24"
//                       fill="none"
//                       xmlns="http://www.w3.org/2000/svg"
//                     >
//                       <path
//                         d="M12 14C13.1046 14 14 13.1046 14 12C14 10.8954 13.1046 10 12 10C10.8954 10 10 10.8954 10 12C10 13.1046 10.8954 14 12 14Z"
//                         stroke="currentColor"
//                         stroke-linecap="round"
//                         stroke-linejoin="round"
//                       />
//                       <path
//                         d="M21 12C19.1114 14.991 15.7183 18 12 18C8.2817 18 4.88856 14.991 3 12C5.29855 9.15825 7.99163 6 12 6C16.0084 6 18.7015 9.1582 21 12Z"
//                         stroke="currentColor"
//                         stroke-linecap="round"
//                         stroke-linejoin="round"
//                       />
//                     </svg>
//                   )}
//                 </span>
//                 <style jsx>{`
//                   input::-ms-reveal,
//                   input::-ms-clear {
//                     display: none;
//                   }
//                   input::-webkit-clear-button,
//                   input::-webkit-password-toggle {
//                     display: none;
//                     -webkit-appearance: none;
//                   }
//                 `}</style>
//               </div>
//             </div>
//             <button
//               type="submit"
//               className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white"
//             >
//               Login
//             </button>

//             {/* <p className="text-center text-sm text-gray-500">
//                             <Link className="underline" to="/forget">Forget Password</Link>
//                         </p>
//                         <p className="text-center text-sm text-gray-500">
//                             <Link className="underline" to="/forget">Forget Username</Link>
//                         </p> */}
//             <p className="text-center text-sm text-gray-500 dark:text-white">
//               No account?{" "}
//               <Link className="underline" to="/register">
//                 Register Now
//               </Link>
//             </p>
//           </form>
//         </div>
//       </div>
//     </div>
//   );
// }

import { useState,useEffect } from 'react';
import api from '../../utils/api';
import { Link, useNavigate } from 'react-router-dom';
import LoginButton from '../components/SSOButton';

export default function Login() {
  const [profile, setProfile] = useState({
    username: '',
    password: '',
  });

  const [error, setError] = useState(false);
  const [isMentor, setIsMentor] = useState(true);

  const navigate=useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessid = params.get('accessid');
  
    if (accessid) {
      localStorage.setItem('accessid', accessid);
      navigate(`/loading?accessid=${encodeURIComponent(accessid)}`);
    }
  }, [navigate]);

  const handleProfile = (e) => {
    const { id, value } = e.target;
    setProfile((prevProfile) => ({
      ...prevProfile,
      [id]: id === 'username' ? value.toLowerCase() : value,
    }));
    setError(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // if (!isMentor) return; // Prevent login attempt for mentees

    const baseUrl = 'https://socb.tech-iitb.org/api/accounts';
    const formData = new FormData();
    Object.keys(profile).forEach((key) => {
      formData.append(key, profile[key]);
    });
    formData.append('role', isMentor ? 'mentor' : 'mentee');

    api
      .post(`${baseUrl}/token/`, formData)
      .then((response) => {
        const token = response.data.access;
        const role = response.data.role;
        // console.log('Login successful, token:', token);
        // console.log('Login successful, role:', role);

        localStorage.setItem('role', role);
        localStorage.setItem('authToken', token);

        if (isMentor) {
          navigate('/mentor/home');
        } else {
          window.location.reload();
        }
      })
      .catch((err) => {
        console.log('Login failed:', err);
        setError(true);
        localStorage.removeItem('authToken');
      });
  };


  return (
    <div className="form h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
      <div className="mx-auto max-w-screen-xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-lg">
          <h1 className="text-center text-2xl font-bold text-indigo-600 sm:text-3xl">
            Seasons of Code
          </h1>

          <div className="flex justify-center gap-4 my-4">
            <button
              className={`px-4 py-2 font-medium ${
                isMentor
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 dark:text-white'
              } rounded`}
              onClick={() => setIsMentor(true)}
            >
              Mentor
            </button>
            <button
              className={`px-4 py-2 font-medium ${
                !isMentor
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 dark:text-white'
              } rounded`}
              onClick={() => setIsMentor(false)}
            >
              Mentee
            </button>
          </div>

          {/* {!isMentor ? (
            <form
            onSubmit={handleSubmit}
            className="mb-0 mt-6 space-y-4 rounded-lg p-4 shadow-lg sm:p-6 lg:p-8 dark:bg-slate-700"
          >
            <div className="text-center text-xl font-semibold text-gray-600 dark:text-white">
              Registrations Closed
            </div>
          </form>
          ) : ( */}
            <form
              onSubmit={handleSubmit}
              className="mb-0 mt-6 space-y-4 rounded-lg p-4 shadow-lg sm:p-6 lg:p-8 dark:bg-slate-700"
            >
              {/* <div className="text-center text-xl font-semibold text-gray-600 dark:text-white">
                Registrations Closed
              </div> */}

              {/* <div>
                <label htmlFor="username">Roll No.</label>
                <input
                  type="text"
                  id="username"
                  className="w-full rounded-lg border-gray-200 p-4 text-sm shadow-sm dark:bg-gray-800"
                  placeholder="Enter Roll No."
                  onChange={handleProfile}
                  required
                />
              </div>

              <div>
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  className="w-full rounded-lg border-gray-200 p-4 text-sm shadow-sm dark:bg-gray-800"
                  placeholder="Enter Password"
                  onChange={handleProfile}
                  required
                />
              </div>

              <button
                type="submit"
                className="block w-full rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white"
              >
                Login
              </button> */}

<LoginButton role={isMentor ? 'mentor' : 'mentee'}/>
            
              {/* <p className="text-center text-sm text-gray-500 dark:text-white">
                No account?{" "}
                <Link className="underline" to="/register">
                  Register Now
                </Link>
              </p> */}
            </form>
           {/* )}  */}
        </div>
      </div>
    </div>
  );
}
