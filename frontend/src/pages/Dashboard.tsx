import { useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart3,
  Cpu,
  User,
  Layers,
  Menu,
  LayoutDashboard,
} from "lucide-react";

import DashboardModal from "../Modals/DashboardModal";
import AnalyticsModal from "../Modals/AnalyticsModal";
import ComputeModal from "../Modals/ComputeModal";
import StaticModal from "../Modals/StaticHostingModal";
import UserModal from "../Modals/UserProfileModal";

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeModal, setActiveModal] = useState("Dashboard");

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <motion.div
        initial={{ width: "4rem" }}
        animate={{ width: sidebarOpen ? "16rem" : "4rem" }}
        transition={{ duration: 0.3 }}
        className="bg-gradient-to-b from-blue-700 to-indigo-800 text-white shadow-xl flex flex-col"
        onMouseEnter={() => setSidebarOpen(true)}
        onMouseLeave={() => setSidebarOpen(false)}
      >
        <div className="flex items-center justify-start h-16 px-3">
          <Menu className="w-6 h-6" />
        </div>

        <nav className="flex-1 space-y-4 mt-4 px-2">
          <SidebarItem
            icon={<LayoutDashboard />}
            text="Dashboard"
            open={sidebarOpen}
            onClick={() => setActiveModal("Dashboard")}
          />
          <SidebarItem
            icon={<BarChart3 />}
            text="Analytics"
            open={sidebarOpen}
            onClick={() => setActiveModal("Analytics")}
          />
          <SidebarItem
            icon={<Cpu />}
            text="Compute"
            open={sidebarOpen}
            onClick={() => setActiveModal("Compute")}
          />
          <SidebarItem
            icon={<Layers />}
            text="Static Hosting"
            open={sidebarOpen}
            onClick={() => setActiveModal("Static")}
          />
          <SidebarItem
            icon={<User />}
            text="User Profile"
            open={sidebarOpen}
            onClick={() => setActiveModal("User")}
          />
        </nav>
      </motion.div>

      {/* Main Content Modal */}
      <div className="flex-1 flex items-start justify-center p-6">
      {activeModal === "Dashboard" && (
         <DashboardModal setActiveModal={setActiveModal} />
      )}

      {activeModal === "Compute" && (
        <ComputeModal setActiveModal={setActiveModal} />
      )}


      {activeModal === "Static" && (
        <StaticModal setActiveModal={setActiveModal} />
      )}

      {/* {activeModal === "Analytics" && (
        <AnalyticsModal setActiveModal={setActiveModal} />
      )}

      {activeModal === "User" && (
        <UserModal setActiveModal={setActiveModal} />
)} */}

      </div>
    </div>
  );
}

function SidebarItem({
  icon,
  text,
  open,
  onClick,
}: {
  icon: any;
  text: string;
  open: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="flex space-x-3 p-2 hover:bg-blue-600 rounded-lg cursor-pointer transition"
    >
      <div className="w-6 h-6">{icon}</div>
      {open && <span className="text-sm font-medium">{text}</span>}
    </div>
  );
}
