import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { Link, useParams } from 'react-router-dom';

export default function ProjectCard(props) {
  const [Added, setAdded] = useState(props.isInWishlist);
  const { domain } = useParams();
  const currentDomain = props.domain || domain;

  // Update state when isInWishlist prop changes
  useEffect(() => {
    setAdded(props.isInWishlist);
  }, [props.isInWishlist]);

  const details = {
    project_id: props.ProjectId,
    title: props.title,
    banner_image: props.link,
    general_category: props.general_category,
  };

  const WishlistAdd = () => {
    if (props.isPreferenceFilled) return;
    const token = localStorage.getItem('authToken');

    if (!token) {
      console.log('No authentication token found. Please log in.');
      return;
    }
    
    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    };
    
    if (!Added) {
      // Add to wishlist
      const payload = { ...details };
      if (currentDomain) {
        payload.domain = currentDomain;
      }
      
      api
        .post(`${process.env.REACT_APP_BACKEND_URL}/projects/wishlist/`, payload, axiosConfig)
        .then((res) => {
          setAdded(true);
        })
        .catch((err) => {
          if (err.response && err.response.status === 401) {
            console.log('Unauthorized request. Please log in.');
          } else {
            console.log('Error adding to wishlist:', err);
          }
        });
    } else {
      // Remove from wishlist
      const deleteUrl = currentDomain
        ? `${process.env.REACT_APP_BACKEND_URL}/projects/wishlist/?project_id=${props.ProjectId}&domain=${currentDomain}`
        : `${process.env.REACT_APP_BACKEND_URL}/projects/wishlist?project_id=${props.ProjectId}`;
      
      api
        .delete(deleteUrl, axiosConfig)
        .then((res) => {
          setAdded(false);
          if (props.onWishlistChange) {
            props.onWishlistChange();
          }
        })
        .catch((err) => {
          if (err.response && err.response.status === 401) {
            console.log('Unauthorized request. Please log in.');
          } else {
            console.log('Error removing from wishlist:', err);
          }
        });
    }
  };

  const projectDetailLink = currentDomain 
    ? `/${currentDomain}/current_projects/${props.ProjectId}`
    : `/current_projects/${props.ProjectId}`;

  return (
    <div>
      <article className="overflow-hidden rounded-lg shadow transition hover:shadow-lg">
        {props.link && (
          <Link to={projectDetailLink}>
            <img
              alt={props.title}
              src={props.link}
              className="h-56 w-full object-contain"
            />
          </Link>
        )}
        {!props.link && (
          <Link to={projectDetailLink}>
            <div className="h-32 w-full bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-gray-700 dark:to-gray-800 flex items-center justify-center border-b-2 border-indigo-100 dark:border-gray-600">
              <div className="text-center px-4">
                <div className="text-indigo-400 dark:text-indigo-300 mb-2">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-12 h-12 mx-auto">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
                  </svg>
                </div>
              </div>
            </div>
          </Link>
        )}
        <Link to={projectDetailLink}>
          <div className="bg-rgb(17, 24, 39) p-4 sm:p-6">
            <h3 className="mt-0.5 text-lg line-clamp-1 text-gray-900 dark:text-white">
              Project ID: {props.ProjectId}
            </h3>
            <h3 className="mt-0.5 text-lg line-clamp-1 text-gray-900 dark:text-white">
              {props.title}
            </h3>
          </div>
        </Link>
        <div className="p-4 sm:p-6">
          {props.isPreferenceFilled ? (
            <button className="text-white font-bold bg-green-500 py-2 px-4 rounded inline-flex items-center cursor-default">
              <p>Preference Filled</p>
            </button>
          ) : (
            <button
              onClick={WishlistAdd}
              className={`text-white font-bold ${Added ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'} py-2 px-4 rounded inline-flex items-center`}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6 mr-2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25Z"
                />
              </svg>
              <p>{Added ? 'Remove From Wishlist' : 'Add To Wishlist'}</p>
            </button>
          )}
        </div>
      </article>
    </div>
  );
}
