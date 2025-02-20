import type { MetaFunction } from '@remix-run/node';
import UserInput from '~/components/UserInput';
import NavBar from '~/components/NavBar';
import Map from '~/components/Map';

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
      <NavBar />
      <div className="flex flex-grow items-center justify-center flex-col">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-800">
          Welcome to Skiwise
        </h1>
        <div className="flex flex-row">
          <UserInput />
          <Map />
        </div>
      </div>
    </div>
  );
}
