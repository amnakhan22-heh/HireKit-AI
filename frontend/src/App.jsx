import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import HomePage from './pages/HomePage';
import KitsPage from './pages/KitsPage';
import KitDetailPage from './pages/KitDetailPage';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            borderRadius: '8px',
            fontFamily: 'inherit',
            fontSize: '14px',
          },
        }}
      />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/kits" element={<KitsPage />} />
        <Route path="/kits/:id" element={<KitDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
