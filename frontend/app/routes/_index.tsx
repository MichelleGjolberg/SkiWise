import type { MetaFunction } from '@remix-run/node';
import UserInput from '~/components/UserInput';
import NavBar from '~/components/NavBar';
import Prediction from '~/components/Prediction';

//This is the main page (all .tsx files under routes are singular pages)
export const meta: MetaFunction = () => {
  return [
    { title: 'New Remix App' },
    { name: 'description', content: 'Welcome to Remix!' },
  ];
};

export default function Index() {
  return (
    <div className="flex flex-col h-screen">
      <div
        className="absolute h-screen w-full bg-fixed bg-cover bg-top overflow-hidden shadow-lg z-0"
        style={{ backgroundImage: "url('/mountain_range.avif')" }}
      >
        <div className="flex flex-col items-center justify-center h-2/3 ">
          <NavBar />
          <h1 className="text-2xl font-bold text-gray-200 dark:text-gray-800 flex justify-center items-center text-center h-100">
            Welcome to Skiwise - Find your mountain
          </h1>
        </div>
      </div>
      <div className="flex flex-grow items-center h-full justify-center flex-col bg-slate-10 my-5 z-10">
        <div className="flex flex-row">
          <UserInput />

          <Prediction />
        </div>
      </div>
    </div>
  );
}
