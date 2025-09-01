import { motion } from "framer-motion";

export default function AnalyticsModal() {
  const tasks = [
    { id: 1, name: "Training Model", status: "Running" },
    { id: 2, name: "Data Sync", status: "Pending" },
  ];

  const history = [
    { id: 1, name: "Deployment #327", log: "View Logs" },
    { id: 2, name: "Backup Job", log: "View Logs" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-2xl shadow-xl p-8 w-[600px]"
    >
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Analytics</h2>

      {/* Current Tasks */}
      <h3 className="text-lg font-semibold text-gray-700 mb-2">Current Tasks</h3>
      <ul className="mb-6 space-y-2">
        {tasks.map((task) => (
          <li
            key={task.id}
            className="flex justify-between bg-gray-100 p-3 rounded-lg"
          >
            <span>{task.name}</span>
            <span className="text-sm text-blue-600">{task.status}</span>
          </li>
        ))}
      </ul>

      {/* History */}
      <h3 className="text-lg font-semibold text-gray-700 mb-2">Past History</h3>
      <ul className="space-y-2">
        {history.map((item) => (
          <li
            key={item.id}
            className="flex justify-between bg-gray-100 p-3 rounded-lg"
          >
            <span>{item.name}</span>
            <button className="text-sm text-indigo-600 hover:underline">
              {item.log}
            </button>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}
