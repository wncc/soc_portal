import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import wncc_logo from '../assets/itc-logo.png';
import api from '../utils/api';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function UnifiedNavbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [memberships, setMemberships] = useState([]);
  const [isManager, setIsManager] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const authToken = localStorage.getItem('authToken');

  useEffect(() => {
    setIsMenuOpen(false);
    setIsProfileOpen(false);
  }, [location]);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
      setDarkMode(true);
    }
  }, []);

  useEffect(() => {
    if (authToken) {
      api.get(`${BACKEND}/accounts/my-memberships/`)
        .then((res) => {
          setMemberships(res.data.memberships || []);
          setIsManager(res.data.is_manager || false);
        })
        .catch(() => {});
    }
  }, [authToken]);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('role');
    localStorage.removeItem('memberships');
    localStorage.removeItem('is_manager');
    window.location.href = '/';
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (darkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
  };

  const getDomainName = (slug) => {
    const map = {
      soc: 'Seasons of Code',
      soq: 'Summer of Quant',
      sor: 'Summer of Robotics',
    };
    return map[slug] || slug.toUpperCase();
  };

  const getRoleBadgeClass = (role) => {
    const map = {
      manager: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      mentor: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      mentee: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    };
    return map[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <nav className="bg-indigo-600 border-gray-200 dark:bg-gray-900 dark:border-gray-700 shadow-xl opacity-90 relative z-[9999]">
      <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
        <Link to="/" className="flex items-center space-x-3 rtl:space-x-reverse">
          <img src={wncc_logo} className="h-10" alt="WnCC Logo" />
          {/* <span className="self-center text-2xl font-semibold whitespace-nowrap text-white dark:text-white">
            Summer of Tech
          </span> */}
        </Link>

        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:bg-transparent dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
        >
          <span className="sr-only">Open main menu</span>
          <svg className="w-5 h-5" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 1h15M1 7h15M1 13h15" />
          </svg>
        </button>

        <div className={`w-full md:flex md:w-auto ${isMenuOpen ? 'block' : 'hidden'}`}>
          <ul className="flex flex-col md:flex-row font-medium p-4 md:p-0 mt-4 border border-gray-100 rounded-lg md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 dark:border-gray-700">
            
            {/* Dark Mode Toggle */}
            <li className="flex items-center">
              <button onClick={toggleDarkMode} className="text-white px-3 py-2">
                {!darkMode ? (
                  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
                    <path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Z" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
                    <path d="M480-360q50 0 85-35t35-85q0-50-35-85t-85-35q-50 0-85 35t-35 85q0 50 35 85t85 35Zm0 80q-83 0-141.5-58.5T280-480q0-83 58.5-141.5T480-680q83 0 141.5 58.5T680-480q0 83-58.5 141.5T480-280ZM200-440H40v-80h160v80Zm720 0H760v-80h160v80ZM440-760v-160h80v160h-80Zm0 720v-160h80v160h-80Z" />
                  </svg>
                )}
              </button>
            </li>

            {/* Home Link */}
            <li className="flex items-center">
              <Link
                to="/"
                className="block py-2 px-3 text-white rounded hover:bg-gray-100 hover:text-gray-500 md:hover:bg-transparent md:border-0 md:hover:text-gray-200 md:p-0"
              >
                Home
              </Link>
            </li>

            {authToken ? (
              <>
                {/* Profile Dropdown - Only shows memberships */}
                <li className="relative flex items-center z-[9999]">
                  <button
                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                    className="flex items-center py-2 px-3 text-white rounded hover:bg-gray-100 hover:text-gray-500 md:hover:bg-transparent md:border-0 md:hover:text-gray-200 md:p-0"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    My Domains
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {isProfileOpen && (
                    <div className="absolute right-0 top-full mt-2 w-72 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-[9999]">
                      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">Your Memberships</p>
                      </div>
                      
                      <div className="p-2 max-h-96 overflow-y-auto">
                        {isManager && (
                          <button
                            onClick={() => {
                              setIsProfileOpen(false);
                              navigate('/manager');
                            }}
                            className="w-full text-left px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md mb-2"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900 dark:text-white">
                                 Manager Dashboard
                              </span>
                              <span className={`text-xs px-2 py-1 rounded-full ${getRoleBadgeClass('manager')}`}>
                                Manager
                              </span>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Manage all domains</p>
                          </button>
                        )}

                        {memberships.filter(m => m.is_approved).length === 0 && !isManager && (
                          <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                            No active memberships yet. Explore domains on the home page!
                          </div>
                        )}

                        {memberships.filter(m => m.is_approved && m.domain).map((m, idx) => (
                          <button
                            key={idx}
                            onClick={() => {
                              setIsProfileOpen(false);
                              if (m.role === 'mentor') {
                                navigate(`/${m.domain}/mentor/home`);
                              } else if (m.role === 'mentee') {
                                navigate(`/${m.domain}/current_projects`);
                              }
                            }}
                            className="w-full text-left px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {getDomainName(m.domain)}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded-full ${getRoleBadgeClass(m.role)}`}>
                                {m.role}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {m.role === 'mentor' ? 'View your projects' : 'Browse projects'}
                            </p>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </li>

                {/* Logout Button */}
                <li className="flex items-center">
                  <button
                    onClick={handleLogout}
                    className="block py-2 px-3 text-white rounded hover:bg-gray-100 hover:text-gray-500 md:hover:bg-transparent md:border-0 md:hover:text-gray-200 md:p-0"
                  >
                    Logout
                  </button>
                </li>
              </>
            ) : (
              <li className="flex items-center">
                <Link
                  to="/login"
                  className="block py-2 px-3 text-white rounded hover:bg-gray-100 hover:text-gray-500 md:hover:bg-transparent md:border-0 md:hover:text-gray-200 md:p-0"
                >
                  Login
                </Link>
              </li>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}
