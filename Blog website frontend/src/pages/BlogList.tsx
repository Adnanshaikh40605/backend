
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@/components/ui/pagination';
import { Settings } from 'lucide-react';
import ModernFooter from '@/components/ModernFooter';
import AdvancedMode from '@/components/AdvancedMode';

interface BlogPost {
  id: number;
  title: string;
  description: string;
  published_date: string;
  image: string;
  content?: string;
}

const BlogList = () => {
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showAdvancedMode, setShowAdvancedMode] = useState(false);
  const postsPerPage = 6;

  // Mock data for demonstration - replace with actual API call
  useEffect(() => {
    const fetchBlogPosts = async () => {
      try {
        // Simulated API call - replace with actual axios call to your Django backend
        // const response = await axios.get('/api/blogs/');
        // setBlogPosts(response.data);
        
        // Mock data for demonstration
        const mockPosts: BlogPost[] = [
          {
            id: 1,
            title: "Safety First: The Importance of Background Checks for Professional Drivers",
            description: "Understanding the significance of thorough background verification for professional drivers and its impact on passenger safety.",
            published_date: "2024-12-13",
            image: "https://images.unsplash.com/photo-1549972904349-6e44c42644a7?w=500&h=300&fit=crop"
          },
          {
            id: 2,
            title: "Exploring the Nightlife of Your City with a Dedicated Night Driver",
            description: "Discover how professional night drivers can enhance your urban exploration experience safely and conveniently.",
            published_date: "2024-12-13",
            image: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=500&h=300&fit=crop"
          },
          {
            id: 3,
            title: "Top Destinations from Mumbai for a Relaxing Driver-Driven Experience",
            description: "Explore the best scenic routes and destinations accessible from Mumbai with professional driving services.",
            published_date: "2024-12-13",
            image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&h=300&fit=crop"
          },
          {
            id: 4,
            title: "The Technology Behind Modern Transportation Services",
            description: "How digital platforms are revolutionizing the way we book and experience transportation services.",
            published_date: "2024-12-12",
            image: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=500&h=300&fit=crop"
          },
          {
            id: 5,
            title: "Sustainable Transportation: The Future of Urban Mobility",
            description: "Exploring eco-friendly transportation options and their role in creating sustainable cities.",
            published_date: "2024-12-11",
            image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=500&h=300&fit=crop"
          },
          {
            id: 6,
            title: "Building Trust in Transportation: Customer Safety Protocols",
            description: "A comprehensive look at safety measures and protocols that ensure passenger security.",
            published_date: "2024-12-10",
            image: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&h=300&fit=crop"
          }
        ];
        
        setBlogPosts(mockPosts);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching blog posts:', error);
        setLoading(false);
      }
    };

    fetchBlogPosts();
  }, []);

  // Calculate pagination
  const indexOfLastPost = currentPage * postsPerPage;
  const indexOfFirstPost = indexOfLastPost - postsPerPage;
  const currentPosts = blogPosts.slice(indexOfFirstPost, indexOfLastPost);
  const totalPages = Math.ceil(blogPosts.length / postsPerPage);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-inter">
        <div className="text-lg font-medium">Loading blog posts...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-inter font-smooth">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center shadow-md">
                <span className="text-white font-bold text-lg font-playfair">VB</span>
              </div>
              <span className="text-2xl font-bold text-gray-900 font-playfair">Vacation BNA</span>
            </div>
            <nav className="hidden md:flex space-x-8">
              <Link to="/" className="text-gray-700 hover:text-red-500 font-medium transition-colors font-inter">Home</Link>
              <Link to="/blogs" className="text-red-500 font-medium font-inter">Blogs</Link>
              <span className="text-gray-700 hover:text-red-500 font-medium cursor-pointer transition-colors font-inter">About Us</span>
              <span className="text-gray-700 hover:text-red-500 font-medium cursor-pointer transition-colors font-inter">Contact Us</span>
              <span className="text-gray-700 hover:text-red-500 font-medium cursor-pointer transition-colors font-inter">Wishlist ❤️</span>
            </nav>
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowAdvancedMode(true)}
                className="hidden md:flex items-center gap-2 font-inter"
              >
                <Settings size={16} />
                Advanced
              </Button>
              <span className="text-gray-700 hover:text-red-500 font-medium cursor-pointer transition-colors font-inter">Login/Signup</span>
              <Button className="bg-red-500 hover:bg-red-600 text-white transition-colors font-inter font-medium">
                List your property
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <h1 className="heading-xl mb-6">Blog Articles</h1>
          <p className="text-body-lg max-w-3xl mx-auto text-gray-600">
            Discover insights, tips, and stories about travel, safety, and transportation services.
          </p>
          <div className="flex items-center justify-center space-x-4 mb-8 mt-10">
            <input
              type="text"
              placeholder="Search blogs..."
              className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 w-64 transition-all font-inter text-body"
            />
            <select className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 transition-all font-inter text-body">
              <option>All Categories</option>
              <option>Safety</option>
              <option>Technology</option>
              <option>Travel</option>
            </select>
            <select className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 transition-all font-inter text-body">
              <option>Newest First</option>
              <option>Oldest First</option>
              <option>Most Popular</option>
            </select>
          </div>
        </div>

        {/* Blog Posts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {currentPosts.map((post) => (
            <Card key={post.id} className="overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 bg-white border border-gray-200">
              <div className="aspect-video overflow-hidden">
                <img
                  src={post.image}
                  alt={post.title}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                />
              </div>
              <CardHeader className="pb-4">
                <CardTitle className="heading-sm line-clamp-2 hover:text-red-600 transition-colors">
                  {post.title}
                </CardTitle>
                <CardDescription className="text-body line-clamp-3 text-gray-600">
                  {post.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-gray-500 font-medium">
                    {formatDate(post.published_date)}
                  </span>
                  <Link to={`/blogs/${post.id}`}>
                    <Button variant="outline" className="text-red-500 border-red-500 hover:bg-red-50 transition-all font-inter font-medium">
                      Read More →
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Pagination */}
        <Pagination className="mb-8">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious 
                onClick={handlePrevPage} 
                className={currentPage === 1 ? 'opacity-50 cursor-not-allowed font-inter' : 'cursor-pointer hover:bg-red-50 font-inter'}
              />
            </PaginationItem>
            <PaginationItem>
              <PaginationLink isActive className="bg-red-500 text-white font-inter font-medium">
                Page {currentPage}
              </PaginationLink>
            </PaginationItem>
            <PaginationItem>
              <PaginationNext 
                onClick={handleNextPage}
                className={currentPage === totalPages ? 'opacity-50 cursor-not-allowed font-inter' : 'cursor-pointer hover:bg-red-50 font-inter'}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      </main>

      {/* Advanced Mode Modal */}
      <AdvancedMode 
        isOpen={showAdvancedMode} 
        onClose={() => setShowAdvancedMode(false)} 
      />

      {/* Modern Footer */}
      <ModernFooter />
    </div>
  );
};

export default BlogList;
