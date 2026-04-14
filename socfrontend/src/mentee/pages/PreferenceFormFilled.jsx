import { useEffect, useState, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import ProjectCard from '../components/ProjectCard';
import api from '../../utils/api';

function PreferenceFormFilled() {
  const [details, setDetails] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { domain } = useParams();
  const navigate = useNavigate();

  const fetchPreferenceList = useCallback(() => {
    setIsLoading(true);
    const endpoint = domain
      ? `${process.env.REACT_APP_BACKEND_URL}/projects/preference/?domain=${domain}`
      : `${process.env.REACT_APP_BACKEND_URL}/projects/preference/`;
    
    api
      .get(endpoint)
      .then((response) => {
        // Sort by preference order (1, 2, 3)
        const sorted = response.data.sort((a, b) => a.preference - b.preference);
        setDetails(sorted);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching Preference:', error);
        if (error.response && error.response.status === 401) {
          window.location.href = '/';
        }
        setIsLoading(false);
      });
  }, [domain]);

  useEffect(() => {
    fetchPreferenceList();
  }, [fetchPreferenceList]);

  return (
    <>
      {/* Quick Navigation Bar */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 py-3 px-6">
        <div className="max-w-screen-xl mx-auto flex gap-4">
          <button
            onClick={() => navigate(domain ? `/${domain}/current_projects` : '/current_projects')}
            className="px-4 py-2 text-sm font-medium bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Projects
          </button>
          <button
            onClick={() => navigate(domain ? `/${domain}/wishlist` : '/wishlist')}
            className="px-4 py-2 text-sm font-medium bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Wishlist
          </button>
          <button
            onClick={() => navigate(domain ? `/${domain}/PreferenceForm` : '/PreferenceForm')}
            className="px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Preferences
          </button>
        </div>
      </div>

      <div className="pt-16 grid place-content-center bg-white dark:bg-gray-800 dark:text-white">
        <div className="text-center">
          <span className="text-green-600 flex justify-center items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
              className="h-40 w-40"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </span>

          <p className="text-2xl font-bold tracking-tight text-gray-900 sm:text-4xl dark:text-white">
            Your preferences have been recorded.
          </p>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Showing your preferences in order of priority
          </p>
        </div>
      </div>

      <section className="project-card dark:bg-gray-800 dark:text-white pb-16">
        {details.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">No preferences submitted yet.</p>
          </div>
        ) : (
          <div className="flex items-center justify-center">
            {isLoading ? (
              <p>Loading...</p>
            ) : (
              <div className="px-24 grid grid-cols-1 gap-4 lg:grid-cols-3 lg:gap-8 pt-16">
                {details.map((pref, index) => {
                  const project = pref.project;
                  let bannerImage = project.banner_image;
                  
                  if (bannerImage && !bannerImage.includes('http')) {
                    bannerImage = `${process.env.REACT_APP_API_URL}${bannerImage}`;
                  }
                  
                  return (
                    <div key={index} className="relative">
                      <div className="absolute -top-3 -left-3 bg-indigo-600 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg shadow-lg z-10">
                        {pref.preference}
                      </div>
                      <ProjectCard
                        ProjectId={project.id}
                        link={bannerImage}
                        title={project.title}
                        general_category={project.general_category}
                        isPreferenceFilled={true}
                      />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </section>

      <div className="text-center py-2 dark:bg-gray-800 dark:text-white">
        <Link
          to="/"
          className="mt-6 inline-block rounded bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring"
        >
          Home
        </Link>
      </div>
    </>
  );
}

export default PreferenceFormFilled;
