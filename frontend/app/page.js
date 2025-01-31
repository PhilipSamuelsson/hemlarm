"use client"

import React, { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL; // Load the API URL from .env.local

const Dashboard = () => {
  const [devices, setDevices] = useState([]);
  const [logs, setLogs] = useState([]);

  // Fetch devices
  useEffect(() => {
    fetch(`${API_URL}/devices`)
      .then((res) => res.json())
      .then((data) => setDevices(data))
      .catch((err) => console.error("Error fetching devices:", err));

    fetch(`${API_URL}/logs`)
      .then((res) => res.json())
      .then((data) => setLogs(data))
      .catch((err) => console.error("Error fetching logs:", err));
  }, []);

  // Toggle Alarm
  const toggleAlarm = (id) => {
    fetch(`${API_URL}/toggle_alarm/${id}`, { method: "POST" })
      .then((res) => res.json())
      .then((updatedDevice) => {
        setDevices((prevDevices) =>
          prevDevices.map((device) =>
            device.id === updatedDevice.id ? { ...device, isActive: updatedDevice.isActive } : device
          )
        );
  
        const newLog = {
          timestamp: new Date().toISOString().slice(0, 16).replace("T", " "),
          message: `${updatedDevice.name} alarm ${
            updatedDevice.isActive ? "activated" : "deactivated"
          }`,
        };
        setLogs((prevLogs) => [newLog, ...prevLogs]);
      })
      .catch((err) => console.error("Error toggling alarm:", err));
  };

  return (
    <div className="p-8 bg-gray-900 min-h-screen text-white">
      <h1 className="text-2xl mb-4">IoT Alarm Dashboard</h1>

      <div className="p-4 border rounded-md bg-gray-800 text-white shadow-lg">
        <h2 className="text-xl mb-2">Connected Devices</h2>
        {devices.length === 0 ? (
          <p className="text-gray-400">No devices connected</p>
        ) : (
          devices.map((device) => (
            <div
              key={device.id}
              className="flex justify-between items-center p-2 border-b"
            >
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
        <ul>
          {logs.length === 0 ? (
            <p className="text-gray-400">No activity recorded</p>
          ) : (
            logs.map((log, index) => (
              <li key={index} className="border-b p-2">
                {log.timestamp} - {log.message}
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;