import React, { useState } from 'react';

const UserInput: React.FC = () => {
  const [userName, setUserName] = useState('');
  const [distance, setDistance] = useState('');
  const [passType, setPassType] = useState('none');
  const [difficulty, setDifficulty] = useState('beginner');
  const [avalancheRisk, setAvalancheRisk] = useState('1');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!userName || !distance) {
      setError('Please fill in all required fields.');
      return;
    }
    setError(null);
    console.log({ userName, distance, passType, difficulty, avalancheRisk });
    const formData = {
      userName,
      distance,
      passType,
      difficulty,
      avalancheRisk,
    };

    try {
      const response = await fetch('http://localhost:8000/get_mountain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch mountain data');
      }

      const data = await response.json();
      console.log('Response:', data);
      alert('Form Submitted Successfully');
    } catch (error) {
      console.error('Error:', error);
      alert('Error submitting the form');
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col space-y-4 p-6 mx-4 bg-white shadow-md rounded-lg max-w-md"
    >
      {error && <p className="text-red-500 font-semibold">{error}</p>}
      <label className="flex flex-col">
        <span className="font-semibold">Your Name:</span>
        <input
          type="text"
          placeholder="Enter your name"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          className="border rounded p-2"
          required
        />
      </label>

      <label className="flex flex-col">
        <span className="font-semibold">Driving Distance (minutes):</span>
        <input
          type="number"
          placeholder="Enter driving time"
          value={distance}
          onChange={(e) => setDistance(e.target.value)}
          className="border rounded p-2"
          required
        />
      </label>

      <fieldset className="flex flex-col">
        <legend className="font-semibold">
          Do you have an Ikon/Epic pass?
        </legend>
        <label className="flex items-center space-x-2">
          <input
            type="radio"
            value="ikon"
            checked={passType === 'ikon'}
            onChange={() => setPassType('ikon')}
          />
          <span>Ikon Pass</span>
        </label>
        <label className="flex items-center space-x-2">
          <input
            type="radio"
            value="epic"
            checked={passType === 'epic'}
            onChange={() => setPassType('epic')}
          />
          <span>Epic Pass</span>
        </label>
        <label className="flex items-center space-x-2">
          <input
            type="radio"
            value="none"
            checked={passType === 'none'}
            onChange={() => setPassType('none')}
          />
          <span>No Pass</span>
        </label>
      </fieldset>

      <label className="flex flex-col">
        <span className="font-semibold">Skiing Difficulty:</span>
        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          className="border rounded p-2"
        >
          <option value="beginner">Beginner (10-20° slopes)</option>
          <option value="intermediate">Intermediate (20-35° slopes)</option>
          <option value="advanced">Advanced (35+° slopes)</option>
        </select>
      </label>

      <label className="flex flex-col">
        <span className="font-semibold">Avalanche risk:</span>
        <select
          value={avalancheRisk}
          onChange={(e) => setAvalancheRisk(e.target.value)}
          className="border rounded p-2"
        >
          <option value="1">1 - Low</option>
          <option value="2">2 - Moderate</option>
          <option value="3">3 - Considerable</option>
          <option value="4">4 - High</option>
          <option value="5">5 - Extreme (Please, avoid)</option>
        </select>
      </label>
      <button
        type="submit"
        className="bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
      >
        Find your mountain
      </button>
    </form>
  );
};

export default UserInput;
