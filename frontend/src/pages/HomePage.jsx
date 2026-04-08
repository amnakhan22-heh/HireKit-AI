import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import { useAuth } from '../context/AuthContext';

export default function HomePage() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <HeroSection
        getStartedTo={token ? '/manager/roles/new' : '/login'}
        viewKitsTo={token ? '/manager' : '/kits'}
      />
    </div>
  );
}
