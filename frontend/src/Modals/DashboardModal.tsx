import { motion } from "framer-motion";
import { Cpu, User, Layers, FileText } from "lucide-react";
import ModalWrapper from "../Components/ModalWrapper";

export default function DashboardModal({
  setActiveModal,
}: {
  setActiveModal: (modal: string) => void;
}) {
  const currentTasks = [
    { id: 1, name: "Deploy frontend service", status: "In Progress" },
    { id: 2, name: "Database migration", status: "Queued" },
    { id: 3, name: "AI model training", status: "Running" },
  ];

  const taskHistory = [
    { id: 1, name: "Backup completed", date: "Aug 23, 2025" },
    { id: 2, name: "Static hosting updated", date: "Aug 22, 2025" },
    { id: 3, name: "Compute autoscaling event", date: "Aug 20, 2025" },
  ];

  return (
    <ModalWrapper>
      <motion.div
        key="dashboard"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -30 }}
        transition={{ duration: 0.3 }}
        className="bg-white rounded-2xl shadow-2xl w-full p-8"
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">Hello, User</span>
            <img
              src="https://i.pravatar.cc/40"
              alt="profile"
              className="w-10 h-10 rounded-full border"
            />
          </div>
        </div>

        {/* Analytics Section */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <AnalyticsCard title="Active Users" value="1,245" change="+12%" />
          <AnalyticsCard title="Deployments" value="327" change="+8%" />
          <AnalyticsCard title="CPU Usage" value="68%" change="-5%" />
        </div>

        {/* Feature Tiles */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <FeatureCard
            icon={<Cpu className="w-8 h-8 text-blue-600" />}
            title="Compute"
            desc="Manage and monitor compute workloads with scaling support."
            onClick={() => setActiveModal("compute")}
          />
          <FeatureCard
            icon={<Layers className="w-8 h-8 text-indigo-600" />}
            title="Static Hosting"
            desc="Deploy and serve static sites globally with ease."
            onClick={() => setActiveModal("static")}
          />
          <FeatureCard
            icon={<User className="w-8 h-8 text-green-600" />}
            title="User Profile"
            desc="Update account settings, security, and personal info."
            onClick={() => setActiveModal("profile")}
          />
        </div>

        {/* Current Tasks */}
        <div className="mb-12">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Current Tasks</h2>
          <div className="bg-gray-50 rounded-2xl shadow-inner p-6 space-y-4">
            {currentTasks.map((task) => (
              <div
                key={task.id}
                className="flex justify-between items-center border-b pb-3 last:border-0"
              >
                <span className="text-gray-700 font-medium">{task.name}</span>
                <span
                  className={`px-3 py-1 text-xs rounded-full ${
                    task.status === "Running"
                      ? "bg-green-100 text-green-600"
                      : task.status === "Queued"
                      ? "bg-yellow-100 text-yellow-600"
                      : "bg-blue-100 text-blue-600"
                  }`}
                >
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Task History */}
        <div>
          <h2 className="text-xl font-bold text-gray-800 mb-4">Task History</h2>
          <div className="bg-gray-50 rounded-2xl shadow-inner p-6 space-y-4">
            {taskHistory.map((task) => (
              <div
                key={task.id}
                className="flex justify-between items-center border-b pb-3 last:border-0"
              >
                <div>
                  <p className="text-gray-700 font-medium">{task.name}</p>
                  <p className="text-sm text-gray-500">{task.date}</p>
                </div>
                <button className="flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium">
                  <FileText className="w-4 h-4 mr-1" /> View Logs
                </button>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </ModalWrapper>
  );
}

function FeatureCard({
  icon,
  title,
  desc,
  onClick,
}: {
  icon: any;
  title: string;
  desc: string;
  onClick?: () => void;
}) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      onClick={onClick}
      className="bg-white rounded-2xl shadow-md p-6 cursor-pointer"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-bold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{desc}</p>
    </motion.div>
  );
}

function AnalyticsCard({
  title,
  value,
  change,
}: {
  title: string;
  value: string;
  change: string;
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-2xl shadow-md p-6"
    >
      <h3 className="text-gray-500 text-sm mb-2">{title}</h3>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <span className="text-sm text-green-600">{change}</span>
    </motion.div>
  );
}
