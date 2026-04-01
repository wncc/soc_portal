import { useState,useEffect } from 'react';
import api from '../../utils/api';
import { useNavigate } from 'react-router-dom';
import LoginButton from '../components/SSOButton';

export default function Login() {
  const navigate=useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessid = params.get('accessid');
  
    if (accessid) {
      localStorage.setItem('accessid', accessid);
      navigate(`/loading?accessid=${encodeURIComponent(accessid)}`);
    }
  }, [navigate]);

  return (
    <div className="form h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
      <div className="mx-auto max-w-screen-xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-lg">
          <h1 className="text-center text-2xl font-bold text-indigo-600 sm:text-3xl">
            Summer of Tech
          </h1>

          <p className="text-center text-gray-600 dark:text-gray-300 mt-4 mb-8">
            Login to access all domains. After login, you can apply as mentor or mentee in any domain.
          </p>

          <div className="mb-0 mt-6 space-y-4 rounded-lg p-4 shadow-lg sm:p-6 lg:p-8 dark:bg-slate-700">
            <LoginButton />
          </div>
        </div>
      </div>
    </div>
  );
}
