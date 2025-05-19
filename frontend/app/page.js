"use client";

import React, { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const Dashboard = () => {
  const [devices, setDevices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 10;

  // 🔹 Fetch devices
  const fetchDevices = async () => {
    try {
      const res = await fetch(`${API_URL}/devices`);
      if (!res.ok) throw new Error(`Failed to fetch devices: ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data)) {
        setDevices(data);
      } else if (typeof data === "object") {
        setDevices(Object.entries(data).map(([id, details]) => ({ id, ...details })));
      }
    } catch (err) {
      console.error("Error fetching devices:", err);
    }
  };

  // 🔹 Fetch logs
  const fetchLogs = async () => {
    setLoadingLogs(true);
    try {
      const res = await fetch(`${API_URL}/logs?_page=${currentPage}&_limit=${logsPerPage}&_sort=timestamp&_order=desc`);
      if (!res.ok) throw new Error(`Failed to fetch logs: ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data)) setLogs(data);
      else setLogs([]);
    } catch (err) {
      console.error("Error fetching logs:", err);
    } finally {
      setLoadingLogs(false);
    }
  };

  // 🔁 Auto-refresh every 5 seconds
  useEffect(() => {
    fetchDevices();
    fetchLogs();
    const interval = setInterval(() => {
      fetchDevices();
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, [currentPage]);

  // 🔹 Clear logs
  const clearLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/clear_logs`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to clear logs");
      fetchLogs(); // Refresh logs
    } catch (err) {
      console.error("Error clearing logs:", err);
    }
  };

  // 🔹 Clear devices
  const clearDevices = async () => {
    try {
      const res = await fetch(`${API_URL}/clear_devices`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to clear devices");
      fetchDevices(); // Refresh devices
    } catch (err) {
      console.error("Error clearing devices:", err);
    }
  };

  return (
    <div className="p-8 bg-gray-900 min-h-screen text-white">
      <h1 className="text-2xl mb-4">IoT Alarm Dashboard</h1>

      <div className="p-4 border rounded-md bg-gray-800 shadow-lg">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl">Connected Devices</h2>
          <button onClick={clearDevices} className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700">
            Rensa enheter
          </button>
        </div>
        {devices.length === 0 ? (
          <p className="text-gray-400">No devices connected</p>
        ) : (
          devices.map((device) => (
            <div key={device.id} className="flex justify-between items-center p-2 border-b">
              <span>{device.name}</span>
              <div className="flex items-center">
                <div
                  className={`w-3 h-3 rounded-full mr-2 ${
                    device.status === "online" ? "bg-green-500" : "bg-red-500"
                  }`}
                />
                <span className="text-sm text-gray-400">
                  {device.status === "online" ? "Online" : "Offline"}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="p-4 border rounded-md bg-gray-800 shadow-lg mt-4">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl">Activity Log</h2>
          <button onClick={clearLogs} className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700">
            Rensa loggar
          </button>
        </div>
        {loadingLogs ? (
          <p className="text-gray-400">Loading logs...</p>
        ) : logs.length === 0 ? (
          <p className="text-gray-400">No activity recorded</p>
        ) : (
          <>
            <ul>
              {logs.map((log, index) => (
                <li key={index} className="border-b p-2">
                  {log.timestamp || "No timestamp"} - {log.device_id || "Unknown Device"} -{" "}
                  {log.message || "No message"}
                </li>
              ))}
            </ul>
            <div className="flex justify-between mt-2">
              <button
                className="px-4 py-2 bg-gray-700 rounded"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              >
                Previous
              </button>
              <button
                className="px-4 py-2 bg-gray-700 rounded"
                onClick={() => setCurrentPage((prev) => prev + 1)}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;