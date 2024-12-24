import ProjectCard from "../components/ProjectCard";
import api from "../utils/api";
import "../components/Filter.css";
import { useEffect, useState, useMemo } from "react";
import "../components/ProjectCard.css";

export default function Projects() {
  const [details, setDetails] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    api
      .get(process.env.REACT_APP_BACKEND_URL + "/projects/")
      .then((response) => {
        setDetails(response.data);
      })
      .catch((error) => {
        console.error("Error fetching card image:", error);
      });
  }, []);

  useEffect(() => {
    api
      .get(process.env.REACT_APP_BACKEND_URL + "/projects/wishlist/")
      .then((response) => {
        setWishlist(response.data);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching card image:", error);
        setIsLoading(false);
      });
  }, []);

  const [filterValue, setFilterValue] = useState("All");
  const [active, setActive] = useState("b1");

  // Filter + search
  const filteredProjects = useMemo(() => {
    return details.filter((project) => {
      const matchesCategory =
        filterValue === "All" || project.general_category.includes(filterValue);
      const matchesSearch =
        !searchQuery ||
        project.title?.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [details, filterValue, searchQuery]);

  const handleFilterChange = (value) => {
    setFilterValue(value);
  };

  return (
    <section className="project-card min-h-[calc(100vh-72px)] dark:bg-gray-800 dark:text-white">
      <div className="pt-8 flex flex-wrap items-center justify-center gap-4">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          <button
            onClick={() => {
              handleFilterChange("All");
              setActive("b1");
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === "b1" ? "text-white" : "text-gray-900"
            } ${
              active === "b1" ? "bg-indigo-600" : "bg-white dark:bg-slate-400"
            } border border-gray-500 rounded-s-lg hover:bg-indigo-600 hover:text-white`}
          >
            ALL
          </button>
          <button
            onClick={() => {
              handleFilterChange("ML");
              setActive("b2");
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === "b2" ? "text-white" : "text-gray-900"
            } ${
              active === "b2" ? "bg-indigo-600" : "bg-white dark:bg-slate-400"
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            ML
          </button>
          <button
            onClick={() => {
              handleFilterChange("Development");
              setActive("b3");
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === "b3" ? "text-white" : "text-gray-900"
            } ${
              active === "b3" ? "bg-indigo-600" : "bg-white dark:bg-slate-400"
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            Development
          </button>
          <button
            onClick={() => {
              handleFilterChange("Blockchain");
              setActive("b4");
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === "b4" ? "text-white" : "text-gray-900"
            } ${
              active === "b4" ? "bg-indigo-600" : "bg-white dark:bg-slate-400"
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            Blockchain
          </button>
          <button
            onClick={() => {
              handleFilterChange("CP");
              setActive("b5");
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === "b5" ? "text-white" : "text-gray-900"
            } ${
              active === "b5" ? "bg-indigo-600" : "bg-white dark:bg-slate-400"
            } border border-gray-500 hover:bg-indigo-600 hover:text-white`}
          >
            CP
          </button>
          <button
            onClick={() => {
              handleFilterChange("Others");
              setActive("b6");
            }}
            className={`w-40 px-4 py-2 text-sm font-medium ${
              active === "b6" ? "text-white" : "text-gray-900"
            } ${
              active === "b6" ? "bg-indigo-600" : "bg-white dark:bg-slate-400"
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
            <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600"></div>
            <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600"></div>
            <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600"></div>
          </div>
        </div>
      ) : (
        <div className="px-24 grid grid-cols-1 gap-4 lg:grid-cols-3 lg:gap-8 py-20">
          {filteredProjects.map((project, index) => (
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
    </section>
  );
}
