import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import FileUpload from './components/FileUpload';
import Navbar from './components/Navbar';

const App = () => {
  const [userID, setUserID] = useState('');

  useEffect(() => {
    if (localStorage.getItem('userID') === null) {
      const id = uuidv4();
      localStorage.setItem('userID', id);
    }
    setUserID(localStorage.getItem('userID'));
  }, []);

  return (
    <>
      <Navbar userID={userID} />
      <div className="container text-center">
        <FileUpload userID={userID} />
      </div>
    </>
  );
};

export default App;
