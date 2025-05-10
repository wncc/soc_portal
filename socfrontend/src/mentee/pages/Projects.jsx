import ProjectCard from '../components/ProjectCard';
import api from '../../utils/api';
import '../components/Filter.css';
import { useEffect, useState, useMemo } from 'react';

export default function Projects() {
  const [details, setDetails] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showScroll, setShowScroll] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    api
      .get('https://socb.tech-iitb.org/api/projects/')
      .then((response) => {
        setDetails(response.data);
      })
      .catch((error) => {
        console.error('Error fetching card image:', error);
      });
  }, []);

  useEffect(() => {
    api
      .get('https://socb.tech-iitb.org/api/projects/wishlist/')
      .then((response) => {
        setWishlist(response.data);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching card image:', error);
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 200) {
        setShowScroll(true);
      } else {
        setShowScroll(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const [filterValue, setFilterValue] = useState('All');
  const [active, setActive] = useState('b1');

  // Filter + search
  const filteredProjects = useMemo(() => {
    return details.filter((project) => {
      const matchesCategory =
        filterValue === 'All' || project.general_category.includes(filterValue);
      const matchesSearch =
        !searchQuery ||
        project.title?.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [details, filterValue, searchQuery]);

  const sortedProjects = useMemo(() => {
    return filteredProjects.sort((a, b) => {
      const wishlistCountA = wishlist.filter((item) => item.project === a.id).length;
      const wishlistCountB = wishlist.filter((item) => item.project === b.id).length;
      return wishlistCountB - wishlistCountA; // Descending order
    });
  }, [filteredProjects, wishlist]);

  const handleFilterChange = (value) => {
    setFilterValue(value);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  console.log(sortedProjects)

  return (
    <section className="project-card min-h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
      <div className="pt-8 flex flex-wrap items-center justify-center gap-4">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          <button
            onClick={() => {
              handleFilterChange('All');
              setActive('b1');
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === 'b1' ? 'text-white' : 'text-gray-900'
            } ${
              active === 'b1' ? 'bg-indigo-600' : 'bg-white dark:bg-slate-400'
            } border border-gray-500 rounded-s-lg hover:bg-indigo-600 hover:text-white`}
          >
            ALL
          </button>
          <button
            onClick={() => {
              handleFilterChange('Machine Learning');
              setActive('b2');
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === 'b2' ? 'text-white' : 'text-gray-900'
            } ${
              active === 'b2' ? 'bg-indigo-600' : 'bg-white dark:bg-slate-400'
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            Machine Learning
          </button>
          <button
            onClick={() => {
              handleFilterChange('Development');
              setActive('b3');
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === 'b3' ? 'text-white' : 'text-gray-900'
            } ${
              active === 'b3' ? 'bg-indigo-600' : 'bg-white dark:bg-slate-400'
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            Development
          </button>
          <button
            onClick={() => {
              handleFilterChange('Blockchain');
              setActive('b4');
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === 'b4' ? 'text-white' : 'text-gray-900'
            } ${
              active === 'b4' ? 'bg-indigo-600' : 'bg-white dark:bg-slate-400'
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            Blockchain
          </button>
          <button
            onClick={() => {
              handleFilterChange('Competitive Programming');
              setActive('b5');
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === 'b5' ? 'text-white' : 'text-gray-900'
            } ${
              active === 'b5' ? 'bg-indigo-600' : 'bg-white dark:bg-slate-400'
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            Competitive Programming
          </button>
          <button
            onClick={() => {
              handleFilterChange('Others');
              setActive('b6');
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === 'b6' ? 'text-white' : 'text-gray-900'
            } ${
              active === 'b6' ? 'bg-indigo-600' : 'bg-white dark:bg-slate-400'
            } border border-gray-500 rounded-e-lg hover:bg-indigo-600 hover:text-white`}
          >
            Others
          </button>
        </div>
        <input
          type="text"
          placeholder="Search by title"
          className="px-4 py-2 border border-gray-300 rounded dark:bg-gray-800 dark:text-white"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="h-screen flex justify-center items-center">
          <div className="flex gap-2">
            <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
            <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
            <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          </div>
        </div>
      ) : (
        <div className="px-24 grid grid-cols-1 gap-4 lg:grid-cols-3 lg:gap-8 py-20">
          {sortedProjects.map((project, index) => (
            <div key={index}>
              <ProjectCard
                ProjectId={project.id}
                link={project.banner_image}
                title={project.title}
                general_category={project.general_category}
                isInWishlist={wishlist.some((item) => item.id === project.id)}
              />
            </div>
          ))}
        </div>
      )}

      {showScroll && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-10 right-10 bg-indigo-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-indigo-700 transition-all"
        >
          ↑ Go to Top
        </button>
      )}
    </section>
  );
}
