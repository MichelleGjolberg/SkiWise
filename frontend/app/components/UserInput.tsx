import React, { useState } from 'react';

const UserInput: React.FC = () => {
  const [userName, setUserName] = useState('');
  const [distance, setDistance] = useState('');
  const [people, setPeople] = useState("");
  const [budget, setBudget] = useState("");
  const [drivingExperience, setDrivingExperience] = useState("beginner");
  const [freshPowder, setFreshPowder] = useState("");
  const [passType, setPassType] = useState('none');
  const [difficulty, setDifficulty] = useState('beginner');
  const [avalancheRisk, setAvalancheRisk] = useState('1');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!userName || !distance) {
      setError('Please fill in all required fields.');
      return;
    }
    setError(null);
    console.log({ userName, distance, passType, difficulty, avalancheRisk });
    alert('Form Submitted');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col space-y-4 p-6 bg-white shadow-md rounded-lg max-w-md"
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

      {/* Number of People */}
      <label className="flex flex-col">
        <span className="font-semibold">People on the trip:</span>
        <input
          type="number"
          placeholder="Enter number of people"
          value={people}
          onChange={(e) => setPeople(e.target.value)}
          className="border rounded p-2"
          required
        />
      </label>

      {/* Max Budget */}
      <label className="flex flex-col">
        <span className="font-semibold">Max Budget ($):</span>
        <input
          type="number"
          placeholder="Enter your budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          className="border rounded p-2"
          required
        />
      </label>

      {/* Driving Experience */}
      <label className="flex flex-col">
        <span className="font-semibold">Driving Experience:</span>
        <select
          value={drivingExperience}
          onChange={(e) => setDrivingExperience(e.target.value)}
          className="border rounded p-2"
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="expert">Expert</option>
        </select>
      </label>

      {/* Minimum Fresh Powder */}
      <label className="flex flex-col">
        <span className="font-semibold">Minimum fresh powder in 24 hours (inches):</span>
        <input
          type="number"
          placeholder="Enter inches of fresh snow"
          value={freshPowder}
          onChange={(e) => setFreshPowder(e.target.value)}
          className="border rounded p-2"
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
