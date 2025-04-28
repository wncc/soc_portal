// // components/SSOButton.jsx
import React from 'react';

// const LoginButton = () => {
//   const handleLoginRedirect = () => {
//     const redirect = encodeURIComponent(`https://wncc-soc.tech-iitb.org/loading`);
//     const projectId = '38dd0ef6-28a1-4a14-980e-b294bd987636';
//     window.location.href = `https://sso.tech-iitb.org/project/${projectId}/ssocall/?redirect=${redirect}`;
//   };
  
//   return (
//     <>
//       <button
//         className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 w-full"
//         onClick={handleLoginRedirect}
//       >
//           Login with ITC SSO
//       </button>
//       {/* <span className="text-sm text-gray-600 px-6 py-2 flex justify-center">
//           No need to register if logging in with SSO
//         </span> */}
//     </>
//   );
// };
  
// export default LoginButton;

const LoginButton = ({role}) => {
  const handleLoginRedirect = () => {
    const redirect = encodeURIComponent(`https://wncc-soc.tech-iitb.org/loading`);
    const projectId = '38dd0ef6-28a1-4a14-980e-b294bd987636';
    localStorage.setItem('role', role);
    window.location.href = `https://sso.tech-iitb.org/project/${projectId}/ssocall/?redirect=${redirect}`;
  };
  
  return (
    <>
      <button
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 w-full"
        onClick={handleLoginRedirect}
      >
          Login with ITC SSO
      </button>
      {/* <span className="text-sm text-gray-600 px-6 py-2 flex justify-center">
          No need to register if logging in with SSO
        </span> */}
    </>
  );
};
  
export default LoginButton;
  
