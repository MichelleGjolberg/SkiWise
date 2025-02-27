import type { MetaFunction } from '@remix-run/node';
import UserInput from '~/components/UserInput';
import NavBar from '~/components/NavBar';
import Map from '~/components/Map';
import ResortCard from '~/components/ResortCard';
import ResortMap from '~/components/ResortMap';

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
          Welcome to Skiwise - Find your mountain
        </h1>
        <div className="flex flex-row ">
          <UserInput />
          <ResortMap lat={39.47911297352002} long={-106.16137643069165} />
          <ResortCard place={'Copper Mountain'} distance={40} />
        </div>
      </div>
    </div>
  );
}
