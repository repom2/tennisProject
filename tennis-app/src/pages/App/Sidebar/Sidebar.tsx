import React from 'react';
import './Sidebar.css';
import { Link } from 'react-router-dom';


const Sidebar: React.FC = () => {
  return (
    <div className="sidebar">
      <h2>Menu</h2>
      <ul>
        <li><Link to="/elo">Home</Link></li>
        <li><Link to="/tips">Tips</Link></li>
      </ul>
    </div>
  );
};

export default Sidebar;
