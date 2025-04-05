// import { useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import api from "../../utils/api";

// const Loading = () => {
//   const navigate = useNavigate();

//   const departmentMap = {
//     AE: "Aerospace Engineering",
//     BS: "Biosciences and Bioengineering",
//     CH: "Chemical Engineering",
//     CY: "Chemistry",
//     CE: "Civil Engineering",
//     CSE: "Computer Science and Engineering",
//     ES: "Earth Sciences",
//     ECON: "Economics",
//     EE: "Electrical Engineering",
//     EN: "Energy Science and Engineering",
//     EP: "Engineering Physics",
//     EV: "Environmental Science and Engineering",
//     HSS: "Humanities and Social Sciences",
//     IDC: "Industrial Design Centre",
//     MA: "Mathematics",
//     ME: "Mechanical Engineering",
//     MM: "Metallurgical Engineering and Materials Science",
//     PH: "Physics",
//     IEOR: "Industrial Engineering and Operations Research",
//     OTHER: "Other",
//   };

//   function getYearChoice(degree, passingYear) {
//     const currentYear = new Date().getFullYear();
//     const yearsLeft = passingYear - currentYear;

//     if (degree === "B.Tech") {
//       if (yearsLeft === 4) return "First Year";
//       if (yearsLeft === 3) return "Second Year";
//       if (yearsLeft === 2) return "Third Year";
//       if (yearsLeft === 1) return "Fourth Year";
//       if (yearsLeft === 0) return "Fifth Year"; // for dual degrees
//     } else if (degree === "M.Tech") {
//       return "M.Tech";
//     } else if (degree === "Ph.D.") {
//       return "Ph.D.";
//     }
//     return "Other";
//   }

//   useEffect(() => {
//     const accessid = localStorage.getItem("accessid");
//     const role = "mentor";

//     const isMentor = true;

//     const doSSOLogin = async () => {
//       if (!accessid) {
//         alert("No access ID found");
//         navigate("/login");
//         return;
//       }

//       try {
//         const ssoRes = await api.post(
//           `${process.env.REACT_APP_BACKEND_URL}/accounts/get-sso-user/`,
//           { accessid }
//         );

//         const user = ssoRes.data;
//         console.log("SSO User Data:", user);

//         const department = departmentMap[user.department] || "Other";
//         const year = getYearChoice(user.degree, user.passing_year);

//         // Step 2: Try registering the user
//         try {
//           const formData = new FormData();
//           formData.append("role", role);
//           formData.append("name", user.name);
//           formData.append("roll_number", user.roll);
//           formData.append("phone_number", "0000000000"); // placeholder
//           formData.append("password", user.roll); // dummy
//           formData.append("year", year);
//           formData.append("department", department);

//           await api.post(
//             `${process.env.REACT_APP_BACKEND_URL}/accounts/register_sso/`,
//             formData
//           );
//           console.log("User registered successfully via SSO");

//           localStorage.setItem("authtoken", accessid);
//           localStorage.removeItem('accessid');
//           localStorage.setItem("role", role);

//           if (isMentor) {
//             navigate("/mentor/home");
//           } else {
//             window.location.reload();
//           }
//         } catch (err) {
//           if (err.response?.data?.error === "User already exists") {
//             console.log("User already registered, continuing login...");
//             localStorage.setItem("authToken", accessid);
//             const authtoken = localStorage.getItem("authtoken");
//             localStorage.setItem("role", role);
//             console.log(isMentor,authtoken,role);
//             localStorage.removeItem('accessid');
//             if (isMentor) {
//               navigate("/mentor/home");
//             } else {
//               window.location.reload();
//             }
//           } else {
//             console.error("Registration failed", err);
//             localStorage.removeItem("authtoken");
//             localStorage.removeItem('accessid');
//             alert("Failed to register. Please try again.");
//             navigate("/login");
//             return;
//           }
//         }
//       } catch (err) {
//         console.error("SSO Login Failed:", err);
//         localStorage.removeItem('accessid');
//         alert("SSO Login failed. Please try again.");
//         navigate("/login");
//       }
//     };

//     doSSOLogin();
//   }, [navigate]);

//   return (
//     <div className="flex items-center justify-center h-screen flex-col">
//       <p className="text-lg text-gray-700">Logging you in via SSO...</p>
//       ;;;;;;;
//     </div>
//   );
// };

// export default Loading;


import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../utils/api";

const Loading = () => {
  const navigate = useNavigate();

  const departmentMap = {
    AE: "Aerospace Engineering",
    BS: "Biosciences and Bioengineering",
    CH: "Chemical Engineering",
    CY: "Chemistry",
    CE: "Civil Engineering",
    CSE: "Computer Science and Engineering",
    ES: "Earth Sciences",
    ECON: "Economics",
    EE: "Electrical Engineering",
    EN: "Energy Science and Engineering",
    EP: "Engineering Physics",
    EV: "Environmental Science and Engineering",
    HSS: "Humanities and Social Sciences",
    IDC: "Industrial Design Centre",
    MA: "Mathematics",
    ME: "Mechanical Engineering",
    MM: "Metallurgical Engineering and Materials Science",
    PH: "Physics",
    IEOR: "Industrial Engineering and Operations Research",
    OTHER: "Other",
  };

  function getYearChoice(degree, passingYear) {
    const currentYear = new Date().getFullYear();
    const yearsLeft = passingYear - currentYear;

    if (degree === "B.Tech") {
      if (yearsLeft === 4) return "First Year";
      if (yearsLeft === 3) return "Second Year";
      if (yearsLeft === 2) return "Third Year";
      if (yearsLeft === 1) return "Fourth Year";
      if (yearsLeft === 0) return "Fifth Year";
    } else if (degree === "M.Tech") return "M.Tech";
    else if (degree === "Ph.D.") return "Ph.D.";
    return "Other";
  }

  useEffect(() => {
    const accessid = localStorage.getItem("accessid");
    const role = localStorage.getItem("role") || "mentor";
    const isMentor = role === "mentor";

    if (!accessid) {
      alert("No access ID found");
      navigate("/login");
      return;
    }

    const doSSOLogin = async () => {
      try {
        const ssoRes = await api.post(
          `${process.env.REACT_APP_BACKEND_URL}/accounts/get-sso-user/`,
          { accessid }
        );

        const user = ssoRes.data;
        const department = departmentMap[user.department] || "Other";
        const year = getYearChoice(user.degree, user.passing_year);

        const formData = new FormData();
        formData.append("role", role);
        formData.append("name", user.name);
        formData.append("roll_number", user.roll);
        formData.append("phone_number", "0000000000"); // placeholder
        formData.append("password", user.roll.toLowerCase()); // dummy
        formData.append("year", year);
        formData.append("department", department);

        try {
          // Attempt to register
          await api.post(`${process.env.REACT_APP_BACKEND_URL}/accounts/register_sso/`, formData);
          console.log("Registered successfully");

          // Now try logging in
          await loginUser(user.roll, role);
        } catch (err) {
          if (err.response?.data?.error === "User already exists") {
            console.log("Already registered. Logging in...");
            await loginUser(user.roll, role);
          } else {
            console.error("Registration failed:", err);
            alert("Registration failed. Try again.");
            localStorage.removeItem("accessid");
            navigate("/login");
          }
        }
      } catch (err) {
        console.error("SSO Login Failed:", err);
        localStorage.removeItem("accessid");
        alert("SSO Login failed. Try again.");
        navigate("/login");
      }
    };

    const loginUser = async (roll_number, role) => {
      try {
        const loginForm = new FormData();
        loginForm.append("username", roll_number);
        loginForm.append("password", roll_number); // since dummy password = roll
        loginForm.append("role", role);

        const loginRes = await api.post(
          `${process.env.REACT_APP_BACKEND_URL}/accounts/token_sso/`,
          loginForm
        );

        const token = loginRes.data.access;
        const userRole = loginRes.data.role;

        localStorage.setItem("authToken", token);
        localStorage.setItem("role", userRole);
        localStorage.removeItem("accessid");

        if (userRole === "mentor") {
          navigate("/mentor/home");
        } else {
          window.location.reload();
        }
      } catch (loginErr) {
        console.log("Login failed:", loginErr);
        alert("Login failed. Please try again.");
        localStorage.removeItem("authToken");
        localStorage.removeItem("accessid");
        navigate("/login");
      }
    };

    doSSOLogin();
  }, [navigate]);

  return (
    <div className="flex items-center justify-center h-screen flex-col">
      <p className="text-lg text-gray-700">Logging you in via SSO...</p>
    </div>
  );
};

export default Loading;
