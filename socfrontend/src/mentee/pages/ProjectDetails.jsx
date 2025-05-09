import React from 'react';
//import ProjectTimeline from '../components/ProjectTimeline';
import { useState , useEffect } from 'react';
import api from '../../utils/api';
import ProjectTitle from '../components/ProjectTitle';
import { useParams } from 'react-router-dom';

export default function ProjectDetails(props) {

  const [details, setDetails] = useState({
    'id': 0,
    'created': '',
    'title': '',
    'general_category': '',
    'specific_category': '',
    'mentee_max': '',
    'mentor': '',
    'description': '',
    'weekly_meets':'',
    'timeline': '',
    'checkpoints': '',
    'prerequisites': '',
    'co_mentor_info': '',
    'banner_image': null,
    'banner_image_link':null,
    'code': '',
    'season': 1,
  });
  let { ProjectId } = useParams();
  ProjectId = parseInt(ProjectId);
  const [wishlist, setWishlist] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.get(`https://socb.tech-iitb.org/api/projects/${ProjectId}/`)
      .then((response) => {
        // Assuming the response contains the image URL
        // console.log(response.data);

        if (response.data.banner_image) {
          response.data.banner_image = `https://socb.tech-iitb.org${response.data.banner_image}`;
        }

        response.data.description = response.data.description.split('\\r\\n').join('<br>');
        response.data.description = response.data.description.replace(
          /(https?:\/\/[^\s]+)/g,
          '<Link to="$1" class="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">$1</Link>',
        );
        setDetails(response.data);
      })
      .catch((error) => {
        console.error('Error fetching card image:', error);
      });
  }, []);

  const [Added, setAdded] = useState();
  useEffect(() => {
    api.get('https://socb.tech-iitb.org/api/projects/wishlist/')
      .then((response) => {
        // console.log(response.data);
        setWishlist(response.data);
        setIsLoading(false);
        // const isAdded = wishlist.some((item) => item.id === details.id);
        const isAdded = response.data.some((item) => item.id === ProjectId);
        setAdded(isAdded);
        // console.log(isAdded);
            
      })
      .catch((error) => {
        console.error('Error fetching card image:', error);
        setIsLoading(false);
      });
  }, [Added]);

  const wishDetails = {
    project_id: details.id,
    title: details.title,
    banner_image: details.banner_image,
    general_category: details.general_category,
  };
        
  const formData = new FormData();
        
  Object.keys(wishDetails).forEach(key => {
    formData.append(key, wishDetails[key]);
  });
        
  const WishlistAdd = (e) => {
    if (!Added) {
      // console.log(formData);
          
      api
        .post('https://socb.tech-iitb.org/api/projects/wishlist/', formData)
        .then((res) => {
          // console.log('hi',res);
          setAdded(true);
        })
        .catch((err) => console.log(err));
    } 
    else {
            
      api.delete(`https://socb.tech-iitb.org/api/projects/wishlist?project_id=${details.id}`)
        .then((res) => {
          // console.log(res);
          setAdded(false);
        })
        .catch((err) => console.log(err));
    }
  };
    
  const buttonMessage = Added ? 'Remove From Wishlist' : 'Add To Wishlist';

  return (  
    <>
      {isLoading ? <div className="h-screen flex justify-center items-center">
        <div className="flex gap-2">
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
        </div>
      </div> : 
        <div className="px-10 py-10 sm:px-2 md:px-10 lg:px-24">
                
          <div className='pb-10 flex items-center justify-center'>
            <div className="relative inline-flex justify-start overflow-hidden transition-all bg-white rounded hover:bg-white group">
              <span className="w-0 h-0 rounded bg-indigo-600 absolute top-0 left-0 ease-out duration-500 transition-all group-hover:w-full group-hover:h-full -z-1" />
              <ProjectTitle text={`Project ID: ${details.id} ${details.title} `}/>
            </div>
          </div>
          <div className="grid grid-cols-1 pb-10 gap-4 lg:grid-cols-3 lg:gap-8">
            <div className="h-56 rounded-lg">
              {/* <img alt="" src="https://itc.gymkhana.iitb.ac.in/wncc/assets/images/soc/2023/item221.jpg" className="h-75 w-full object-cover"/> */}
              <img alt="" src={details.banner_image} className="h-56 w-full object-contain"/>
            </div>
            <div className="rounded-lg lg:col-span-2 h-75">
                        
              <div className="grid grid-cols-1 gap-1 lg:grid-cols-2 lg:gap-8">
                <div className="h-12 rounded-lg">
                  <h4 className=" pt-5 text-2xl text-indigo-400 sm:text-3xl">Mentors:</h4>
                  <ul className="pl-8 sm:pl-2 md:pl-8 lg:pl-20">
                    <p>{details.mentor}</p>
                  </ul>
                </div>
                <div className="h-28 rounded-lg">
                  <h4 className=" pt-5 text-2xl text-indigo-400 sm:text-3xl">Co-Mentors:</h4>
                  <ul className="pl-8 sm:pl-2 md:pl-8 lg:pl-20">
                    <li>
                      <p dangerouslySetInnerHTML={{ __html: details.co_mentor_info.replace(/\\r\\n/g, '<br>') }} />
                    </li>
                  </ul>
                </div>
              </div>
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-8">
                <div className="h-10 rounded-lg ">
                  <h4 className=" pt-5 text-2xl text-indigo-400 sm:text-3xl">Mentees:</h4>
                  <ul className="pl-8 sm:pl-2 md:pl-8 lg:pl-20">
                    <li>
                      {/* <p>20+</p> */}
                      <p>{details.mentee_max}</p>
                    </li>
                  </ul>
                </div>
                <div className="h-28 rounded-lg">
                  <h4 className=" pt-5 text-2xl text-indigo-400 sm:text-3xl">Category:</h4>
                  <ul className="pl-8 sm:pl-2 md:pl-8 lg:pl-20">
                    <li>
                      {/* <p>20+</p> */}
                      <p>{details.general_category}</p>
                    </li>
                  </ul>
                </div>
              </div>
              {/* <WishlistButton str={str} WishlistAdd={WishlistAdd}/> */}
              {!props.isPreferenceFilled && (
                <button
                  onClick={WishlistAdd}
                  className={`text-white font-bold ${
                    buttonMessage === 'Remove From Wishlist' ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'
                  } text-white font-bold py-2 px-4 rounded inline-flex items-center`}
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
                      d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0 0 21 18V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v12a2.25 2.25 0 0 0 2.25 2.25Z"
                    />
                  </svg>
                  <p>{buttonMessage}</p>
                </button>
              )}
            </div>
          </div>

          <div className="flow-root">
            <dl className="-my-3 divide-y divide-gray-100 text-sm">
              <div className="grid grid-cols-1 gap-1 py-3 even:bg-gray-50 sm:grid-cols-3 sm:gap-4">
                <dt className="text-2xl text-indigo-600 sm:text-3xl">Description</dt>
                <dd className="text-gray-700 sm:col-span-2"><p dangerouslySetInnerHTML={{ __html: details.description }} /></dd>
              </div>

              <div className="grid grid-cols-1 gap-1 py-3 even:bg-gray-50 sm:grid-cols-3 sm:gap-4">
                <dt className="text-2xl text-indigo-600 sm:text-3xl">Prerequisites</dt>
                <dd className="text-gray-700 sm:col-span-2">{details.prereuisites}</dd>
              </div>

              <div className="grid grid-cols-1 gap-1 py-3 even:bg-gray-50 sm:grid-cols-3 sm:gap-4">
                <dt className="text-2xl text-indigo-600 sm:text-3xl">Timeline</dt>
                <dd className="text-gray-700 sm:col-span-2"><p dangerouslySetInnerHTML={{ __html: details.timeline.replace(/\\r\\n/g, '<br>') }} /></dd>
              </div>

              <div className="grid grid-cols-1 gap-1 py-3 even:bg-gray-50 sm:grid-cols-3 sm:gap-4">
                <dt className="text-2xl text-indigo-600 sm:text-3xl">Checkpoints</dt>
                <dd className="text-gray-700 sm:col-span-2"><p dangerouslySetInnerHTML={{ __html: details.checkpoints.replace(/\\r\\n/g, '<br>') }} /></dd>
              </div>

              <div className="grid grid-cols-1 gap-1 py-3 even:bg-gray-50 sm:grid-cols-3 sm:gap-4">
                <dt className="text-2xl text-indigo-600 sm:text-3xl">Number of Weekly Meets Approximately</dt>
                <dd className="text-gray-700 sm:col-span-2"><p dangerouslySetInnerHTML={{ __html: details.weekly_meets.replace(/\\r\\n/g, '<br>') }} /></dd>
              </div>
            </dl>
          </div>
        </div>}
    </>
  );
}
