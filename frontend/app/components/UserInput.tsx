import React, { useState, useEffect } from 'react';
import Prediction from '~/components/Prediction';
import Default from './default/Default';

//Need to fetch data for default list when page load
//When submit boutton is clicked => new predicted data should show

const UserInput: React.FC = () => {
  const [userName, setUserName] = useState('');
  const [distance, setDistance] = useState('');
  const [people, setPeople] = useState('');
  const [budget, setBudget] = useState('');
  const [drivingExperience, setDrivingExperience] = useState('beginner');
  const [freshPowder, setFreshPowder] = useState('');
  const [passType, setPassType] = useState('none');
  const [isPayOptionSelected, setIsPayOptionSelected] = useState(false);
  const [costImportance, setCostImportance] = useState(5);
  const [timeImportance, setTimeImportance] = useState(5);
  const [error, setError] = useState<string | null>(null);
  const [predictionData, setPredictionData] = useState<any[] | null>(null);
  const [isDefault, setIsDefault] = useState(true);
  const [defaultData, setDefaultData] = useState<any[] | null>(null);
  const [startpoint, setStartpoint] = useState([40.0189728, -105.2747406]); //startingpoint is denver as a default
  const [distanceError, setDistanceError] = useState('');
  const [peopleError, setPeopleError] = useState('');
  const [budgetError, setBudgetError] = useState('');
  const [freshPowderError, setfreshPowderError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const cityOptions = [
    { name: 'Boulder, CO', coords: [40.01499, -105.27055] },
    { name: 'Denver, CO', coords: [39.7392, -104.9903] },
    { name: 'Fort Collins, CO', coords: [40.5853, -105.0844] },
    { name: 'Colorado springs, CO', coords: [38.8339, -104.8214] },
    { name: 'Durango, CO', coords: [37.2753, -107.8801] },
  ];

  const [selectedCity, setSelectedCity] = useState(cityOptions[0]);
  // This function allows for "value=none" for "Both Passes" and "Willing to pay"
  const handleNoneChange = (value: string) => {
    setPassType('none');
    setIsPayOptionSelected(value === 'pay');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    let hasError = false;

    if (!userName || !distance) {
      setError('Please fill in all required fields.');
      return;
    }

    setDistanceError('');
    setPeopleError('');
    setBudgetError('');
    setError(null);

    if (Number(distance) <= 0) {
      setDistanceError('Driving time should be > 0 minutes');
      hasError = true;
    }
    if (Number(people) <= 0) {
      setPeopleError('Number of people should be > 0');
      hasError = true;
    }
    if (Number(budget) <= 0) {
      setBudgetError('Budget should be > 0 dollars');
      hasError = true;
    }
    if (Number(freshPowder) <= 0) {
      setfreshPowderError('Fresh pow should be > 0" (What were you thinking?)');
      hasError = true;
    }

    if (hasError) return;

    setIsLoading(true);

    const [latitude, longitude] = selectedCity?.coords || [
      40.0189728, -105.2747406,
    ];
    setStartpoint([latitude, longitude]);

    //Only one call needed
    await sendFormData(latitude, longitude);

    setError(null);
  };

  const sendFormData = async (latitude: number, longitude: number) => {
    const formData = {
      userName,
      distance: Number(distance),
      people: Number(people),
      budget: Number(budget),
      drivingExperience,
      freshPowder: Number(freshPowder),
      passType,
      costImportance,
      timeImportance,
      location: { latitude, longitude },
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

      if (!data.resorts || data.resorts.length === 0) {
        setError(
          'Sorry, no resorts match your search. Showing all resorts instead.'
        );
        setIsDefault(true);
        await get_all_resorts(); // fallback
        return;
      }

      setPredictionData(data.resorts);
      setIsDefault(false);
      setError(null);
    } catch (error) {
      console.error('Error:', error);
      setError('Something went wrong. Showing default resorts.');
      setIsDefault(true);
      await get_all_resorts(); // fallback
    }
    setIsLoading(false);
  };

  useEffect(() => {
    get_all_resorts();
  }, []);

  const get_all_resorts = async () => {
    try {
      const response = await fetch('http://localhost:8000/get_all_resorts', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch all mountain data');
      }

      const data = await response.json();
      setDefaultData(data.resorts);
      setIsDefault(true);
    } catch (error) {
      console.error('Error fetching all resorts:', error);
    }
  };

  return (
    <div className="flex flex-grow justify-center flex-col md:flex-row w-full h-full bg-lightblue  py-5 mt-[-400px] ">
      {isLoading && (
        <div className="fixed inset-0 bg-white bg-opacity-70 z-[9999] flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-14 w-14 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
            <p className="text-lg font-semibold text-blue-600">
              Finding your mountain...
            </p>
          </div>
        </div>
      )}
      <form
        onSubmit={handleSubmit}
        className="flex flex-col space-y-4 p-6 mx-4 bg-white shadow-md rounded-lg min-w-[250px] max-w-[400px] max-h-[500px] overflow-y-auto"
      >
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
          <span className="font-semibold">Starting Location:</span>
          <select
            value={selectedCity.name}
            onChange={(e) => {
              const city = cityOptions.find((c) => c.name === e.target.value);
              if (city) setSelectedCity(city);
            }}
            className="border rounded p-2"
          >
            {cityOptions.map((city) => (
              <option key={city.name} value={city.name}>
                {city.name}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col">
          <span className="font-semibold">Driving Time (minutes):</span>
          <input
            type="number"
            placeholder="Enter driving time"
            value={distance}
            onChange={(e) => setDistance(e.target.value)}
            className="border rounded p-2"
            required
          />
          {distanceError && (
            <p className="text-red-500 text-sm">{distanceError}</p>
          )}
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
          {peopleError && <p className="text-red-500 text-sm">{peopleError}</p>}
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
          {budgetError && <p className="text-red-500 text-sm">{budgetError}</p>}
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
          <span className="font-semibold">
            Minimum fresh powder in 24 hours (inches):
          </span>
          <input
            type="number"
            placeholder="Enter inches of fresh snow"
            value={freshPowder}
            onChange={(e) => setFreshPowder(e.target.value)}
            className="border rounded p-2"
          />
          {freshPowderError && (
            <p className="text-red-500 text-sm">{freshPowderError}</p>
          )}
        </label>
        {/* Type of pass */}
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
              checked={passType === 'none' && !isPayOptionSelected}
              onChange={() => handleNoneChange('both')}
            />
            <span>Both Passes</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="none"
              checked={passType === 'none' && isPayOptionSelected}
              onChange={() => handleNoneChange('pay')}
            />
            <span>Willing to pay for a pass</span>
          </label>
        </fieldset>

        <label className="flex flex-col">
          <span className="font-semibold">How important is cost? (1-10)</span>
          <input
            type="range"
            min="1"
            max="10"
            value={costImportance}
            onChange={(e) => setCostImportance(Number(e.target.value))}
            className="cursor-pointer"
          />
          <span className="text-center">{costImportance}</span>
        </label>

        <label className="flex flex-col">
          <span className="font-semibold">
            How important is driving time? (1-10)
          </span>
          <input
            type="range"
            min="1"
            max="10"
            value={timeImportance}
            onChange={(e) => setTimeImportance(Number(e.target.value))}
            className="cursor-pointer"
          />
          <span className="text-center">{timeImportance}</span>
        </label>
        {error && <p className="text-red-500 font-semibold">{error}</p>}
        <button
          type="submit"
          className="bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
        >
          Search for resort
        </button>
      </form>
      {isDefault ? (
        <Default defaultData={defaultData} />
      ) : (
        <Prediction predictionData={predictionData} startpoint={startpoint} />
      )}
    </div>
  );
};

export default UserInput;
