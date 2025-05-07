import { useState,useEffect } from 'react';
import api from '../../utils/api';
import { Link, useNavigate } from 'react-router-dom';
import LoginButton from '../components/SSOButton';

export default function Admin() {
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
        console.log('Login successful, token:', token);
        console.log('Login successful, role:', role);

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
        </div>
      </div>
    </div>
  );
}
