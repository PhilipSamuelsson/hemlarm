"use client";

import React, { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL; // Load the API URL from .env.local

const Dashboard = () => {
  const [devices, setDevices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 10;

  console.log("API_URL:", API_URL); // Debugging API URL

  // 🔹 Fetch devices
  useEffect(() => {
    const fetchDevices = async () => {
      try {
        console.log("Fetching devices from:", `${API_URL}/devices`);
        const res = await fetch(`${API_URL}/devices`);

        if (!res.ok) {
          throw new Error(`Failed to fetch devices: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        console.log("API Devices Response:", data); // Debugging log

        if (Array.isArray(data)) {
          setDevices(data);
        } else if (typeof data === "object") {
          setDevices(
            Object.entries(data).map(([id, details]) => ({
              id,
              ...details,
            }))
          );
        } else {
          setDevices([]); // Default to an empty array
        }
      } catch (err) {
        console.error("Error fetching devices:", err);
      }
    };

    fetchDevices();
  }, []);

  // 🔹 Fetch logs with pagination
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        console.log("Fetching logs from:", `${API_URL}/logs?_page=${currentPage}&_limit=${logsPerPage}&_sort=timestamp&_order=desc`);
        const res = await fetch(`${API_URL}/logs?_page=${currentPage}&_limit=${logsPerPage}&_sort=timestamp&_order=desc`);

        if (!res.ok) {
          throw new Error(`Failed to fetch logs: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        console.log("Fetched logs:", data); // Debugging log

        if (Array.isArray(data)) {
          setLogs(data);
        } else {
          console.error("Unexpected API response for logs:", data);
          setLogs([]);
        }
      } catch (err) {
        console.error("Error fetching logs:", err);
      } finally {
        setLoadingLogs(false);
      }
    };

    fetchLogs();
  }, [currentPage]);

  // 🔹 Toggle Alarm
  const toggleAlarm = async (id) => {
    try {
      console.log(`Toggling alarm for device: ${id}`);
      const res = await fetch(`${API_URL}/toggle_alarm/${id}`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error(`Failed to toggle alarm: ${res.status} ${res.statusText}`);
      }

      const updatedDevice = await res.json();
      console.log("Updated device:", updatedDevice);

      setDevices((prevDevices) =>
        prevDevices.map((device) =>
          device.id === updatedDevice.id ? { ...device, isActive: updatedDevice.isActive } : device
        )
      );

      const newLog = {
        timestamp: new Date().toISOString().slice(0, 16).replace("T", " "),
        message: `${updatedDevice.name} alarm ${updatedDevice.isActive ? "activated" : "deactivated"}`,
      };
      setLogs((prevLogs) => [newLog, ...prevLogs]);
    } catch (err) {
      console.error("Error toggling alarm:", err);
    }
  };
  //new online status and button for later use. 
  <div className="p-8 bg-gray-900 min-h-screen text-white">
      <h1 className="text-2xl mb-4">IoT Alarm Dashboard</h1>

      <div className="p-4 border rounded-md bg-gray-800 text-white shadow-lg">
        <h2 className="text-xl mb-2">Connected Devices</h2>
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
                <span className="text-sm text-gray-400">{device.status === "online" ? "Online" : "Offline"}</span>
                {/* You can optionally keep the button for manual alarm control */}
                <button
                  className={`ml-4 px-4 py-2 rounded-md ${
                    device.isActive ? "bg-red-500" : "bg-green-500"
                  }`}
                  onClick={() => toggleAlarm(device.id)}
                >
                  {device.isActive ? "Turn Off Alarm" : "Turn On Alarm"}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
  return (
    <div className="p-8 bg-gray-900 min-h-screen text-white">
      <h1 className="text-2xl mb-4">IoT Alarm Dashboard</h1>

      <div className="p-4 border rounded-md bg-gray-800 text-white shadow-lg">
        <h2 className="text-xl mb-2">Connected Devices</h2>
        {devices.length === 0 ? (
          <p className="text-gray-400">No devices connected</p>
        ) : (
          devices.map((device) => (
            <div key={device.id} className="flex justify-between items-center p-2 border-b">
              <span>{device.name}</span>
              <button
                className={`px-4 py-2 rounded-md ${
                  device.isActive ? "bg-red-500" : "bg-green-500"
                }`}
                onClick={() => toggleAlarm(device.id)}
              >
                {device.isActive ? "Turn Off" : "Turn On"}
              </button>
            </div>
          ))
        )}
      </div>

     <div className="p-4 border rounded-md bg-gray-800 text-white shadow-lg mt-4">
        <h2 className="text-xl mb-2">Activity Log</h2>
        {loadingLogs ? (
          <p className="text-gray-400">Loading logs...</p>
        ) : logs.length === 0 ? (
          <p className="text-gray-400">No activity recorded</p>
        ) : (
          <>
            <ul>
              {logs.map((log, index) => (
                <li key={index} className="border-b p-2">
                  {log.timestamp || "No timestamp"} - {log.device_id || "Unknown Device"} - {log.message || "No message"}
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
