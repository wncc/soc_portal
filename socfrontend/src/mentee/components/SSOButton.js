const LoginButton = () => {
  const handleLoginRedirect = () => {
    const redirect = encodeURIComponent(`${process.env.REACT_APP_FRONTEND_URL}/loading`);
    const projectId = '38dd0ef6-28a1-4a14-980e-b294bd987636';
    window.location.href = `https://sso.tech-iitb.org/project/${projectId}/ssocall/?redirect=${redirect}`;
  };
  
  return (
    <>
      <button
        type="button"
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 w-full"
        onClick={handleLoginRedirect}
      >
          Login with ITC SSO
      </button>
      <span className="text-sm text-gray-600 dark:text-gray-400 px-6 py-2 flex justify-center">
          After login, choose your role in each domain
      </span>
    </>
  );
};
  
export default LoginButton;
  
