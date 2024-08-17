export default function Logout() {
  return (
    <div className="ms-5 me-4 py-10">
      <div className="flex flex-row flex-wrap font-semibold justify-end items-center">
        <button className="flex flex-row flex-wrap text-white hover:text-magenta">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="1.5em"
            height="1.5em"
            viewBox="0 0 24 24"
          >
            <path
              fill="currentColor"
              d="m17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5M4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4z"
            />
          </svg>
          <p className="px-2 text-xl">Log Out</p>
        </button>
      </div>
    </div>
  );
}
