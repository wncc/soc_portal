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
        <Link to={projectDetailLink}>
          <img
            alt={props.title}
            src={props.link}
            className="h-56 w-full object-contain"
          />
        </Link>
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
