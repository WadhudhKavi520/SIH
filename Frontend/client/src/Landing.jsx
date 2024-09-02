import React, { useState } from "react";
import { PolarArea } from "react-chartjs-2";
import './Landing.css';
import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend);

const Laning = () => {
  const [polarData, setPolarData] = useState([]);
  const [angle, setAngle] = useState("");
  const [radius, setRadius] = useState("");

  const handleAddCoordinate = () => {
    const theta = parseFloat(angle);
    const r = radius ? parseFloat(radius) : 100;
    const timestamp = new Date().toLocaleString();

    if (isNaN(theta)) {
      alert("Please enter a valid angle.");
      return;
    }

    setPolarData([...polarData, { angle: theta, radius: r, time: timestamp }]);
    setAngle("");
    setRadius("");
  };


  const filteredPolarData = polarData.slice(1);

  const data = {
    labels: filteredPolarData.map((_, index) => `Point ${index + 1}`),
    datasets: [
      {
        label: "Polar Coordinates",
        data: filteredPolarData.map((point) => point.radius),
        backgroundColor: filteredPolarData.map(() =>
          "red"
        ), 
      },
    ],
  };

  const options = {
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
      },
    },
    plugins: {
      legend: {
        labels: {
          color: "black",
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const point = filteredPolarData[context.dataIndex];
            return `Angle: ${point.angle}, Radius: ${
              point.radius
            }, Time: ${point.time}`;
          },
        },
      },
    },
    startAngle: 0,
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: 20,
    },
    backgroundColor: "black",
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Polar Coordinate Plotter</h1>
        <div>
          <input
            type="number"
            value={angle}
            onChange={(e) => setAngle(e.target.value)}
            placeholder="Enter Angle (θ)"
          />
          <input
            type="number"
            value={radius}
            onChange={(e) => setRadius(e.target.value)}
            placeholder="Enter Radius (r) - Optional"
          />
          <button onClick={handleAddCoordinate}>Add Coordinate</button>
        </div>
        <div className="chart-container">
          <PolarArea data={data} options={options} />
        </div>
      </div>
    </div>
  );
};

export default Laning;
