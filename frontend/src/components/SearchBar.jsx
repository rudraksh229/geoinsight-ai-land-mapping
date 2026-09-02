import React from "react";

const SearchBar = ({
  placeholder = "Search villages, reports, coordinates...",
  value,
  onChange,
  onSearch,
  className = "",
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();

    if (onSearch) {
      onSearch(value);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`w-full max-w-md ${className}`}
    >
      <div className="relative flex items-center w-full">
        {/* Search icon */}
        <div
          className="absolute left-3.5 pointer-events-none"
          style={{ color: "#94a3b8" }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2.2}
            stroke="currentColor"
            className="w-4.5 h-4.5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.637 10.637z"
            />
          </svg>
        </div>

        {/* Search input */}
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="
            w-full
            pl-11
            pr-10
            py-2.5
            rounded-xl
            text-xs
            font-bold
            outline-none
            transition-all
            duration-200
            bg-slate-900/80
            border
            border-slate-800
            focus:border-green-500/70
            focus:bg-slate-900
            tech-mono
          "
          style={{
            color: "#f1f5f9",
            caretColor: "#4ade80",
          }}
        />

        {/* Clear button */}
        {value && (
          <button
            type="button"
            onClick={() => onChange("")}
            className="
              absolute
              right-3
              p-1
              rounded-full
              hover:bg-slate-800
              transition-colors
              cursor-pointer
            "
            style={{ color: "#94a3b8" }}
            aria-label="Clear search"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
              stroke="currentColor"
              className="w-3.5 h-3.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Placeholder styling */}
      <style>
        {`
          input::placeholder {
            color: #64748b;
            opacity: 1;
          }

          input:focus::placeholder {
            color: #475569;
          }
        `}
      </style>
    </form>
  );
};

export default SearchBar;
