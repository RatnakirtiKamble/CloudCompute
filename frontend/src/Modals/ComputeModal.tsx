import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Cpu, Play, Terminal, X } from "lucide-react";
import ModalWrapper from "../Components/ModalWrapper";
import axios from "axios";

type ComputeTask = {
  id: number;
  task_type: string;
  status: "running" | "completed" | "stopped";
  created_at?: string;
  logs?: string;
};

type StartComputeForm = {
  image: string;
  command: string;
  cpu_cores: number;
  gpu: boolean;
};


export default function ComputeModal({
  setActiveModal,
}: {
  setActiveModal: (modal: string) => void;
}) {
  const [tasks, setTasks] = useState<ComputeTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [showStartModal, setShowStartModal] = useState(false);
  const [currentLogsTask, setCurrentLogsTask] = useState<ComputeTask | null>(null);
  const [form, setForm] = useState<StartComputeForm>({
    image: "",
    command: "",
    cpu_cores: 2,
    gpu: false,
  });
  const [currentLogsTaskId, setCurrentLogsTaskId] = useState<number | null>(
    null
  );
  const [logs, setLogs] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
    },
  });

  // Fetch tasks
  useEffect(() => {
    api
      .get("/status/tasks/compute")
      .then((res) => {
        if (Array.isArray(res.data)) setTasks(res.data.reverse());
        else setTasks([]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // WebSocket for logs
  useEffect(() => {
    if (!currentLogsTaskId) return;
  
    setLogs([]);
    wsRef.current?.close();
  
    // Construct full WS URL
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsHost = "localhost:8080"; // your backend host + port
    const ws = new WebSocket(`${wsProtocol}://${wsHost}/compute/logs/${currentLogsTaskId}`);
    wsRef.current = ws;
  
    ws.onmessage = (ev) => setLogs((prev) => [...prev, ev.data]);
    ws.onclose = () => console.log("WS closed");
    ws.onerror = console.error;
  
    return () => ws.close();
  }, [currentLogsTaskId]);
  
  const startCompute = () => {
    api
      .post("/compute/start", form)
      .then((res) => {
        setTasks((prev) => [res.data, ...prev]);
        setShowStartModal(false);
        setCurrentLogsTaskId(res.data.id);
      })
      .catch(console.error);
  };

  const viewLogs = (task: ComputeTask) => {
    setLogs([]);
    setCurrentLogsTask(task);

    if (task.status === "running") {
      const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
      const wsHost = "localhost:8000"; // backend host
      const ws = new WebSocket(`${wsProtocol}://${wsHost}/compute/logs/${task.id}`);
      wsRef.current = ws;

      ws.onmessage = (ev) => setLogs((prev) => [...prev, ev.data]);
      ws.onclose = () => console.log("WS closed");
      ws.onerror = console.error;
    } else {
      api
        .get(`status/logs/${task.id}`, { responseType: "text" })
        .then((res) => {
          setLogs(res.data);
        })
        .catch(console.error);
        console.log(logs);
    }
  };

  return (
    <ModalWrapper>
      <motion.div
        key="dashboard"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -30 }}
        transition={{ duration: 0.3 }}
        className="bg-white rounded-2xl shadow-2xl w-full h-full p-8 flex flex-col"
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center space-x-3">
            <Cpu className="w-8 h-8 text-blue-600" />
            <span>Compute Dashboard</span>
          </h1>
          <button
            onClick={() => setActiveModal("Dashboard")}
            className="p-2 rounded-full hover:bg-gray-200"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Top Section: Graph + Stats */}
        {/* Top Section: Graph + Stats */}
        <div className="flex gap-6 mb-4 h-64"> {/* Increased height from h-48 to h-64 */}
          {/* Left: Graph placeholder */}
          <div className="flex-1 bg-gray-100 rounded-2xl shadow-lg flex items-center justify-center">
            <span className="text-gray-400">Graph Placeholder</span>
          </div>

          {/* Right: Stats */}
          <div className="w-60 bg-gray-50 rounded-2xl shadow-lg divide-y divide-gray-200 flex flex-col justify-evenly p-4">
            <div className="py-2">
              <span className="text-sm text-gray-500">Last Compute</span>
              <p className="font-medium">
                {tasks[0] ? `Task #${tasks[0].id} - ${tasks[0].status}` : "None"}
              </p>
            </div>
            <div className="py-2">
              <span className="text-sm text-gray-500">Available CPU Cores</span>
              <p className="font-medium">12</p>
            </div>
            <div className="py-2">
              <span className="text-sm text-gray-500">Available GPU VRAM</span>
              <p className="font-medium">8 GB</p>
            </div>
          </div>
        </div>



        {/* Start New Compute button */}
        <div className="mb-4 flex justify-start">
          <button
            onClick={() => setShowStartModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-full shadow-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Play className="w-5 h-5" />
            <span>Start New Compute</span>
          </button>
        </div>

        {/* Task Table */}
        <div className="flex-1 overflow-y-auto border rounded-2xl p-2">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                  Task ID
                </th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                  Type
                </th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                  Status
                </th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                  Logs
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : tasks.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                    No computes
                  </td>
                </tr>
              ) : (
                tasks.map((task) => (
                  <tr key={task.id}>
                    <td className="px-4 py-3 text-sm">{task.id}</td>
                    <td className="px-4 py-3 text-sm">{task.task_type}</td>
                    <td
                      className={`px-4 py-3 text-sm capitalize ${
                        task.status === "running"
                          ? "text-green-600"
                          : task.status === "completed"
                          ? "text-blue-600"
                          : "text-red-600"
                      }`}
                    >
                      {task.status}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={() => viewLogs(task)}
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                      >
                        <Terminal className="w-4 h-4" />
                        View Logs
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Start Compute Modal */}
        {showStartModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-2xl w-96 p-6 relative">
              <button
                onClick={() => setShowStartModal(false)}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-200"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
              <h2 className="text-xl font-bold mb-4">Start New Compute</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Docker Image
                  </label>
                  <input
                    type="text"
                    value={form.image}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, image: e.target.value }))
                    }
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    placeholder="e.g., ubuntu:latest"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Command
                  </label>
                  <input
                    type="text"
                    value={form.command}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, command: e.target.value }))
                    }
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    placeholder="e.g., python app.py"
                  />
                </div>
                <div className="flex gap-4 items-center">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      CPU Cores
                    </label>
                    <input
                      type="number"
                      min={1}
                      max={16}
                      value={form.cpu_cores}
                      onChange={(e) =>
                        setForm((prev) => ({
                          ...prev,
                          cpu_cores: Number(e.target.value),
                        }))
                      }
                      className="mt-1 w-20 border border-gray-300 rounded-md p-2"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={form.gpu}
                      onChange={(e) =>
                        setForm((prev) => ({ ...prev, gpu: e.target.checked }))
                      }
                    />
                    <label className="text-sm text-gray-700">GPU</label>
                  </div>
                </div>
                <div className="flex justify-end gap-2 mt-4">
                  <button
                    onClick={startCompute}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Start
                  </button>
                  <button
                    onClick={() => setShowStartModal(false)}
                    className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Logs Viewer */}
        {currentLogsTask && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-black rounded-2xl w-3/4 p-6 relative">
              <button
                onClick={() => setCurrentLogsTask(null)}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-800"
              >
                <X className="w-5 h-5 text-white" />
              </button>
              <h2 className="text-xl font-bold mb-4 text-white">
                Logs - Task #{currentLogsTask.id}
              </h2>
              <div className="bg-black text-green-400 p-4 rounded h-96 overflow-y-auto font-mono text-sm border border-green-500">
              <pre className="whitespace-pre-wrap">
                {logs}
              </pre>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </ModalWrapper>
  );
}
