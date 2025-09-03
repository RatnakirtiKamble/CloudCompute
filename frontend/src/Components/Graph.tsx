import { useEffect, useState, useRef } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type DataPoint = {
  time: string;
  vram: number;
};

export default function GpuUsageGraph() {
  const [gpuHistory, setGpuHistory] = useState<DataPoint[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsBase = "localhost:8000/status/ws";

    wsRef.current?.close();
    const ws = new WebSocket(`${wsProtocol}://${wsBase}/resource_status`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
      
          // Extract CPU, memory, and VRAM
          const cpu = data.cpu;
          const memory = data.memory;
          const vram = data.gpu?.[0]?.vram_used ?? 0;
      
          const now = new Date();
          const timestamp = now.toLocaleTimeString();
      
          setGpuHistory((prev) => {
            const updated = [...prev, { time: timestamp, cpu, memory, vram }];
            return updated.slice(-20); // keep last 20 points
          });
        } catch (err) {
          console.error("Invalid GPU status:", err);
        }
      };
      

    return () => ws.close();
  }, []);

  return (
    <div className="w-full h-full">
      {gpuHistory.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          Waiting for GPU data...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
        <LineChart data={gpuHistory}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="cpu" stroke="#2563eb" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="memory" stroke="#16a34a" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="vram" stroke="#f59e0b" strokeWidth={2} dot={false} />
        </LineChart>

        </ResponsiveContainer>
      )}
    </div>
  );
}
