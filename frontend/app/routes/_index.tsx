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
    <div className="relative flex flex-col ">
      <div
        className="absolute h-screen w-full bg-fixed bg-cover bg-top  shadow-lg z-0"
        style={{ backgroundImage: "url('/mountain_range.avif')" }}
      >
        <div className="flex flex-col items-center justify-center h-1/3">
          <NavBar />
          <h1 className="text-2xl font-bold text-gray-100  flex justify-center items-center text-center h-100">
            Welcome to Skiwise - Find your perfect mountain!
          </h1>
        </div>
        <div className="flex relative flex-grow items-center w-full h-fit justify-center flex-col bg-slate-50 my-5  py-8">
          <div className="flex flex-row">
            <UserInput />

            <Prediction />
          </div>
        </div>
      </div>
    </div>
  );
}
