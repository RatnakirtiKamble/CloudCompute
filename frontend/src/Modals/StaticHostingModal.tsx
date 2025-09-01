import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Globe, Upload, X, Trash } from "lucide-react";
import ModalWrapper from "../Components/ModalWrapper";
import axios from "axios";
import { format } from "date-fns";

export default function StaticHostingModal({ setActiveModal }: { setActiveModal: (modal: string) => void }) {
  const [mode, setMode] = useState<"archive" | "github">("archive");
  const [file, setFile] = useState<File | null>(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [subdir, setSubdir] = useState<string | null>(null); // restored subdir
  const [buildCommand, setBuildCommand] = useState("npm run build");
  const [envVars, setEnvVars] = useState<{ key: string; value: string }[]>([{ key: "", value: "" }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [url, setUrl] = useState<string | null>(null);

  const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: { Authorization: `Bearer ${localStorage.getItem("token") || ""}` },
  });

  const fetchTasks = async () => {
    try {
      const { data } = await api.get("/status/tasks/static");
      setTasks(data);
    } catch (err) {
      console.error("Failed to fetch tasks:", err);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    setLoading(true);
    setError(null);
    setUrl(null);

    try {
      if (mode === "archive") {
        if (!file || !(file.name.endsWith(".zip") || file.name.endsWith(".tar.gz"))) {
          setError("Please select a valid .zip or .tar.gz archive.");
          setLoading(false);
          return;
        }

        const formData = new FormData();
        formData.append("file", file);

        const { data } = await api.post("/static_pages/static", formData);
        setUrl(data.url);
      } else {
        if (!repoUrl) {
          setError("Please enter a GitHub repository URL.");
          setLoading(false);
          return;
        }

        const envObj: Record<string, string> = {};
        envVars.forEach((e) => {
          if (e.key && e.value) envObj[e.key] = e.value;
        });

        const body = { repo_url: repoUrl, build_command: buildCommand, subdir, env_vars: envObj };
        const { data } = await api.post("/static_pages/github", body);
        setUrl(`Deployed! Task ID: ${data.id}`);
      }

      fetchTasks();
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (taskId: number) => {
    try {
      await api.delete(`/static_pages/delete/${taskId}`);
      fetchTasks();
    } catch (err) {
      console.error("Failed to delete deployment:", err);
    }
  };

  const updateEnvVar = (index: number, keyOrValue: "key" | "value", value: string) => {
    const newVars = [...envVars];
    newVars[index][keyOrValue] = value;
    setEnvVars(newVars);
  };

  const addEnvVar = () => setEnvVars([...envVars, { key: "", value: "" }]);
  const removeEnvVar = (index: number) => setEnvVars(envVars.filter((_, i) => i !== index));

  return (
    <ModalWrapper>
      <motion.div
        key="static-hosting"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -30 }}
        transition={{ duration: 0.3 }}
        className="bg-white rounded-2xl shadow-2xl w-full h-full p-8 flex flex-col"
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center space-x-3">
            <Globe className="w-8 h-8 text-blue-600" />
            <span>Static Hosting Dashboard</span>
          </h1>
          <button
            onClick={() => setActiveModal("Dashboard")}
            className="p-2 rounded-full hover:bg-gray-200"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Toggle Buttons */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setMode("archive")}
            className={`px-4 py-2 rounded-lg ${mode === "archive" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            Zip/Tar Hosting
          </button>
          <button
            onClick={() => setMode("github")}
            className={`px-4 py-2 rounded-lg ${mode === "github" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            GitHub Hosting
          </button>
        </div>

        {/* Upload / GitHub Form */}
        <div className="flex-1 flex flex-col items-center justify-center space-y-6">
          {mode === "archive" && (
            <>
              <label className="block w-full">
                <span className="block text-sm font-medium text-gray-700 mb-2">
                  Upload a .zip or .tar.gz containing your static site (HTML/CSS/JS)
                </span>
                <input type="file" onChange={handleFileChange} className="hidden" id="file-upload" />
                <label htmlFor="file-upload" className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700 transition">
                  Choose File
                </label>
                {file && <p className="text-gray-600 text-sm mt-2">Selected: <span className="font-medium">{file.name}</span></p>}
              </label>
            </>
          )}
          {mode === "github" && (
            <>
              <label className="block w-full">
                <span className="block text-sm font-medium text-gray-700 mb-2">
                  Enter GitHub repository URL (React-based projects)
                </span>
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/user/repo"
                  className="block w-full border rounded p-2 mb-2"
                />
                <span className="block text-sm text-gray-500 mb-1">
                  Optional subfolder inside repo
                </span>
                <input
                  type="text"
                  value={subdir || ""}
                  onChange={(e) => setSubdir(e.target.value || null)}
                  placeholder="e.g., frontend"
                  className="block w-full border rounded p-2 mb-2"
                />
                <span className="block text-sm text-gray-500">
                  Build command (default: npm run build)
                </span>
                <input
                  type="text"
                  value={buildCommand}
                  onChange={(e) => setBuildCommand(e.target.value)}
                  className="block w-full border rounded p-2 mb-2"
                />

                {/* Environment Variables Input */}
                <span className="block text-sm text-gray-700 mt-2">Environment Variables (optional)</span>
                {envVars.map((env, idx) => (
                  <div key={idx} className="flex space-x-2 mb-2">
                    <input type="text" placeholder="KEY" value={env.key} onChange={(e) => updateEnvVar(idx, "key", e.target.value)} className="flex-1 border rounded p-1" />
                    <input type="text" placeholder="VALUE" value={env.value} onChange={(e) => updateEnvVar(idx, "value", e.target.value)} className="flex-1 border rounded p-1" />
                    <button onClick={() => removeEnvVar(idx)} className="px-2 bg-red-500 text-white rounded">X</button>
                  </div>
                ))}
                <button onClick={addEnvVar} className="px-3 py-1 bg-blue-500 text-white rounded text-sm mb-2">+ Add Variable</button>
              </label>
            </>
          )}

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            onClick={handleUpload}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-full shadow-lg hover:bg-blue-700 flex items-center space-x-2 disabled:opacity-50"
          >
            <Upload className="w-5 h-5" />
            <span>{loading ? "Deploying..." : "Deploy"}</span>
          </button>

          {url && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg w-full text-center">
              <p className="text-green-700 font-medium">
                ✅ {mode === "archive" ? "Deployed at:" : url}
                {mode === "archive" && <a href={url} target="_blank" className="text-blue-600 underline ml-1">{url}</a>}
              </p>
            </div>
          )}
        </div>

        {/* Existing Tasks Table */}
        <div className="mt-8 overflow-y-auto flex-1">
          <h2 className="text-lg font-semibold mb-2">Your Static Tasks</h2>
          <table className="w-full text-left border border-gray-200 rounded-lg">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-3 py-2 border-b">Task ID</th>
                <th className="px-3 py-2 border-b">Status</th>
                <th className="px-3 py-2 border-b">Logs / URL</th>
                <th className="px-3 py-2 border-b">Created At</th>
                <th className="px-3 py-2 border-b">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-3 py-2 border-b">{t.id}</td>
                  <td className="px-3 py-2 border-b">{t.status}</td>
                  <td className="px-3 py-2 border-b break-words">{t.logs}</td>
                  <td className="px-3 py-2 border-b">{t.created_at ? format(new Date(t.created_at), "dd/MM/yyyy HH:mm") : "-"}</td>
                  <td className="px-3 py-2 border-b">
                    <button
                      onClick={() => handleDelete(t.id)}
                      className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      <Trash className="w-4 h-4" />
                      <span className="text-sm">Delete</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </ModalWrapper>
  );
}
