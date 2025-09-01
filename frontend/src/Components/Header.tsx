import { useNavigate } from "react-router-dom";

export default function Header() {

  const navigate = useNavigate();

  return (
    <header className="bg-white p-5 flex justify-between shadow-xl border-b border-gray-200  z-20 relative">
      <h1 className="text-3xl font-bold"> CloudFlow </h1>

      <div className="flex gap-x-10 text-lg">
          <button className="text-gray-500 hover:text-gray-800 ">
              About
          </button>

          <button 
            className="text-blue-500 hover:text-blue-700"
            onClick={() => navigate("/auth")}>
              Sign in
          </button>
      </div>
    </header>


  );
}
  