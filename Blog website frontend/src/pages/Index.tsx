
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Index = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to blog list page
    navigate('/blogs');
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to Vacation BNA Blog</h1>
        <p className="text-xl text-muted-foreground">Redirecting to blogs...</p>
      </div>
    </div>
  );
};

export default Index;
