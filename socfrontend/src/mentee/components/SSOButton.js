// // components/SSOButton.jsx
import React from 'react';

// const LoginButton = () => {
//   const handleLogin = () => {
//     const redirect = encodeURIComponent(`${window.location.origin}/login`);
//     const projectId = "38dd0ef6-28a1-4a14-980e-b294bd987636";

//     // Redirect to SSO
//     window.location.href = `https://sso.tech-iitb.org/project/${projectId}/ssocall/?redirect=${redirect}`;
//   };

//   return (
//     <>
//       <button
//         className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 w-full"
//         onClick={handleLogin}
//       >
//         Login with IITB SSO
//       </button>
//       <span className="text-sm text-gray-600 px-6 py-2 flex justify-center text-center">
//         You’ll be redirected back here after login
//       </span>
//     </>
//   );
// };

// export default LoginButton;

const LoginButton = () => {
  const handleLoginRedirect = () => {
    const redirect = encodeURIComponent(`${window.location.origin}/loading`);
    const projectId = '38dd0ef6-28a1-4a14-980e-b294bd987636';
    window.location.href = `https://sso.tech-iitb.org/project/${projectId}/ssocall/?redirect=${redirect}`;
  };
  
  return (
    <>
      <button
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 w-full"
        onClick={handleLoginRedirect}
      >
          Login with IITB SSO
      </button>
      {/* <span className="text-sm text-gray-600 px-6 py-2 flex justify-center">
          No need to register if logging in with SSO
        </span> */}
    </>
  );
};
  
export default LoginButton;
  
