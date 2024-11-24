import React, { useState } from 'react';
import axios from 'axios';

const CustomGameForm: React.FC = () => {
  const [seedWords, setSeedWords] = useState<string[]>(['', '']);
  const API_URL = process.env.REACT_APP_API_URL;

  const createCustomGame = async () => {
    try {
      const response = await axios.post(`${API_URL}/games`, { seedWords });
      console.log('Custom game created:', response.data);
    } catch (error) {
      console.error('Error creating custom game:', error);
    }
  };

  return (
    <div>
      <h2>Create Custom Game</h2>
      <input
        type="text"
        placeholder="Seed Word 1"
        value={seedWords[0]}
        onChange={(e) => setSeedWords([e.target.value, seedWords[1]])}
      />
      <input
        type="text"
        placeholder="Seed Word 2"
        value={seedWords[1]}
        onChange={(e) => setSeedWords([seedWords[0], e.target.value])}
      />
      <button onClick={createCustomGame}>Create Game</button>
    </div>
  );
};

export default CustomGameForm;
