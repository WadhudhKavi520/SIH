import React from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from "./Landing";


function App() {
 
  return (
  
     <div>
      <Router>
      
        <Routes>
          <Route path="/" element={<Landing/>}></Route>
    
        </Routes>
      
      </Router>
    </div>
  );
}

export default App;
