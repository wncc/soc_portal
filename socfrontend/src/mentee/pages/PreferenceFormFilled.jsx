import { useEffect } from 'react';
import { useState } from 'react';
import { useCallback } from 'react';
import { Link } from 'react-router-dom';
import ProjectCard from '../components/ProjectCard';
import api from '../../utils/api';

function PreferenceFormFilled() {
  const [details, setDetails] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const fetchPreferenceList = useCallback(() => {
    setIsLoading(true);
    api
      .get('https://socb.tech-iitb.org/api/projects/preference/')
      .then((response) => {
        setDetails(response.data);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching Preference:', error);
        if (error.response && error.response.status === 401) {
          window.location.href = '/';
        }
        setIsLoading(false);
      });
  }, []);
  useEffect(() => {
    fetchPreferenceList(); // Call the memoized fetch function
  }, [fetchPreferenceList]);

  return (
    <>
      <div className="pt-16 grid place-content-center bg-white dark:bg-gray-800 dark:text-white">
        <div className="text-center ">
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
            Your response has been recorded.
          </p>

          {/* <p className="mt-4 text-gray-500">Thank you.</p> */}
        </div>
      </div>
      <section className="project-card dark:bg-gray-800 dark:text-white">
        {details.length === 0 ? (
          <>
            <p className="text-2xl font-bold tracking-tight text-gray-900 sm:text-4xl" />
          </>
        ) : (
          <>
            <div className="flex items-center justify-center ">
              {isLoading ? (
                <p>Loading...</p>
              ) : (
                <div className="px-24 grid grid-cols-1 gap-4 lg:grid-cols-3 lg:gap-8 pt-16">
                  {details.map((project, index) => {
                    // if (!project.project.banner_image.includes(':8000')) {
                    //   project.project.banner_image = `http://127.0.0.1:8000${project.project.banner_image}`;
                    // }
                    if (project.project.banner_image && !project.project.banner_image.includes('socb.tech-iitb.org')) {
                      project.project.banner_image = `https://socb.tech-iitb.org${project.project.banner_image}`;
                    }
                    return (
                      <div key={index}>
                        <ProjectCard
                          ProjectId={project.project.id}
                          link={project.project.banner_image}
                          title={project.project.title}
                          general_category={project.project.general_category}
                          isPreferenceFilled={true}
                        />
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </section>
      <div className="text-center py-2">
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
