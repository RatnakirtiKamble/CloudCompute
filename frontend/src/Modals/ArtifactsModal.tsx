import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface ArtifactsModalProps {
  isOpen: boolean;
  onClose: () => void;
  taskId: number;
  token: string; // Bearer token
}

interface TreeNode {
  name: string;
  path: string;
  children?: TreeNode[];
  isFile: boolean;
}

export default function ArtifactsModal({ isOpen, onClose, taskId, token }: ArtifactsModalProps) {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Convert flat list ["folder1/file1.txt", "folder2/file2.png"] → tree
  function buildTree(paths: string[]): TreeNode[] {
    const root: TreeNode[] = [];

    paths.forEach((path) => {
      const parts = path.split("/");
      let currentLevel = root;

      parts.forEach((part, i) => {
        const existingNode = currentLevel.find((node) => node.name === part);

        if (existingNode) {
          currentLevel = existingNode.children!;
        } else {
          const newNode: TreeNode = {
            name: part,
            path: parts.slice(0, i + 1).join("/"),
            isFile: i === parts.length - 1,
            children: i === parts.length - 1 ? [] : [],
          };
          currentLevel.push(newNode);
          currentLevel = newNode.children!;
        }
      });
    });

    return root;
  }

  useEffect(() => {
    if (!isOpen) return;

    const fetchArtifacts = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`http://localhost:8000/status/artifacts/${taskId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          throw new Error(`Error ${res.status}`);
        }

        const data: string[] = await res.json();
        setTree(buildTree(data));
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchArtifacts();
  }, [isOpen, taskId, token]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        className="relative bg-white rounded-2xl shadow-xl w-[600px] max-h-[80vh] overflow-y-auto p-6"
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
        >
          ✕
        </button>

        <h2 className="text-xl font-semibold mb-4">Artifacts for Task {taskId}</h2>

        {loading && <p className="text-gray-500">Loading artifacts...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}
        {!loading && !error && tree.length === 0 && (
          <p className="text-gray-500">No artifacts found.</p>
        )}

        {!loading && !error && tree.length > 0 && (
          <div className="space-y-2">
            <FileTree nodes={tree} taskId={taskId} token={token} />
          </div>
        )}
      </motion.div>
    </div>
  );
}

// Recursive file tree renderer
function FileTree({ nodes, taskId, token  }: { nodes: TreeNode[], taskId: number, token: string }) {
  const [open, setOpen] = useState<Record<string, boolean>>({});

  const toggle = (path: string) => {
    setOpen((prev) => ({ ...prev, [path]: !prev[path] }));
    };

    const downloadFile = async (filePath: string, fileName: string) => {
        try {
          const res = await fetch(
            `http://localhost:8000/status/artifacts/${taskId}/${encodeURIComponent(filePath)}`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );
    
          if (!res.ok) {
            throw new Error(`Download failed: ${res.status}`);
          }
    
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
    
          const a = document.createElement("a");
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          a.remove();
    
          window.URL.revokeObjectURL(url);
        } catch (err) {
          console.error("Download error:", err);
          alert("Failed to download file");
        }
      };
 

  return (
    <ul className="pl-4">
      {nodes.map((node) => (
        <li key={node.path} className="mb-1">
          {node.isFile ? (
             <button
             onClick={() => downloadFile(node.path, node.name)}
             className="text-blue-600 cursor-pointer hover:underline"
           >
             📄 {node.name}
           </button>
          ) : (
            <div>
              <button
                onClick={() => toggle(node.path)}
                className="flex items-center gap-1 text-left w-full"
              >
                <span>{open[node.path] ? "📂" : "📁"}</span>
                <span>{node.name}</span>
              </button>
              {open[node.path] && node.children && (
                 <FileTree nodes={node.children} taskId={taskId} token={token} />
              )}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
