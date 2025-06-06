import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Settings } from 'lucide-react';
import ModernFooter from '@/components/ModernFooter';
import AdvancedMode from '@/components/AdvancedMode';

interface BlogPost {
  id: number;
  title: string;
  description: string;
  published_date: string;
  image: string;
  content: string;
  reading_time: string;
}

interface Comment {
  id: number;
  email: string;
  comment: string;
  created_at: string;
}

const BlogDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [blogPost, setBlogPost] = useState<BlogPost | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState({ email: '', comment: '' });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showAdvancedMode, setShowAdvancedMode] = useState(false);

  useEffect(() => {
    const fetchBlogPost = async () => {
      try {
        // Simulated API call - replace with actual axios call
        // const response = await axios.get(`/api/blogs/${id}/`);
        // setBlogPost(response.data);
        
        // Mock data for demonstration
        const mockPost: BlogPost = {
          id: parseInt(id || '1'),
          title: "Safety First: The Importance of Background Checks for Professional Drivers",
          description: "Understanding the significance of thorough background verification for professional drivers and its impact on passenger safety.",
          published_date: "2024-12-13",
          image: "https://images.unsplash.com/photo-1549972904349-6e44c42644a7?w=800&h=400&fit=crop",
          content: `
            <h2>Introduction</h2>
            <p>In the modern world of ride-sharing and professional transportation services, ensuring passenger safety has become paramount. One of the most critical steps in establishing trust and reliability is conducting thorough background checks for professional drivers.</p>
            
            <h2>The Significance of Background Checks</h2>
            
            <h3>1. Trust and Reliability</h3>
            <p>Background checks help build trust and confidence in passengers, ensuring that they are entrusting their safety to qualified and trustworthy drivers.</p>
            
            <h3>2. Criminal History Screening</h3>
            <p>Conducting criminal background checks helps identify any past criminal convictions that could pose a risk to passenger safety.</p>
            
            <h3>3. Verification of Driving Record</h3>
            <p>A clean driving record is essential for any professional driver. Background checks include verification of driving history, including any traffic violations, accidents, or license suspensions.</p>
            
            <h3>4. Identity Verification</h3>
            <p>Background checks confirm the identity of drivers, ensuring that they are who they claim to be and reducing the risk of fraudulent activity.</p>
            
            <h3>5. Screening for Substance Abuse</h3>
            <p>Drug and alcohol screening are essential components of background checks, preventing employment of drivers who may be under the influence while driving.</p>
            
            <h2>Best Practices for Comprehensive Background Checks</h2>
            
            <h3>1. Multi-Level Verification Process</h3>
            <p>Implement a comprehensive screening process that includes criminal and traffic background checks, offering multiple levels of verification to ensure the highest standards of safety.</p>
            
            <h3>2. Regular Re-screening</h3>
            <p>Conduct periodic re-screening of drivers to ensure ongoing compliance with safety standards and identify any new issues that may arise.</p>
            
            <h3>3. Transparent Communication</h3>
            <p>Maintain open communication with passengers about the background check process and safety measures in place.</p>
            
            <h2>Conclusion</h2>
            <p>Background checks are not just a regulatory requirement; they are a fundamental principle that guides everything we do. By conducting thorough background checks on all drivers, transportation companies can build trust with their customers and ensure the highest level of safety for all passengers.</p>
          `,
          reading_time: "7 min read"
        };
        
        setBlogPost(mockPost);
        
        // Mock comments
        const mockComments: Comment[] = [
          {
            id: 1,
            email: "milan1272@example.com",
            comment: "I appreciate following your blog! I've enjoyed checking these details out immensely and I'm very excited.",
            created_at: "2024-12-13T10:30:00Z"
          },
          {
            id: 2,
            email: "abhishek@example.com",
            comment: "Safety first! Impressive post.",
            created_at: "2024-12-13T11:45:00Z"
          },
          {
            id: 3,
            email: "jamal.t@example.com",
            comment: "Perfect advice for startup 📍",
            created_at: "2024-12-13T14:20:00Z"
          }
        ];
        
        setComments(mockComments);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching blog post:', error);
        setLoading(false);
      }
    };

    if (id) {
      fetchBlogPost();
    }
  }, [id]);

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newComment.email.trim() || !newComment.comment.trim()) {
      alert('Please fill in both email and comment fields.');
      return;
    }

    setSubmitting(true);
    
    try {
      // Simulated API call - replace with actual axios call
      // await axios.post(`/api/blogs/${id}/comments/`, newComment);
      
      // Mock comment addition
      const comment: Comment = {
        id: comments.length + 1,
        email: newComment.email,
        comment: newComment.comment,
        created_at: new Date().toISOString()
      };
      
      setComments([...comments, comment]);
      setNewComment({ email: '', comment: '' });
    } catch (error) {
      console.error('Error submitting comment:', error);
      alert('Failed to submit comment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatCommentDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-inter">
        <div className="text-lg font-medium">Loading blog post...</div>
      </div>
    );
  }

  if (!blogPost) {
    return (
      <div className="min-h-screen flex items-center justify-center font-inter">
        <div className="text-center">
          <h1 className="heading-md mb-4">Blog post not found</h1>
          <Link to="/blogs">
            <Button className="font-inter font-medium">Back to Blogs</Button>
          </Link>
        </div>
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

      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <nav className="text-body-sm text-gray-600 font-inter">
            <Link to="/" className="hover:text-red-500 transition-colors">Home</Link>
            <span className="mx-2">{'>'}</span>
            <Link to="/blogs" className="hover:text-red-500 transition-colors">Blogs</Link>
            <span className="mx-2">{'>'}</span>
            <span className="text-gray-900 font-medium">Safety First: The Importance of Background Checks for Professional Drivers</span>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
          {/* Blog Header */}
          <div className="p-8 pb-0">
            <div className="flex items-center gap-6 text-body-sm text-gray-600 mb-6 font-inter">
              <span className="flex items-center gap-2">
                <span>📅</span>
                <span className="font-medium">Published</span>
              </span>
              <span className="font-medium">{formatDate(blogPost.published_date)}</span>
              <span className="flex items-center gap-2">
                <span>📖</span>
                <span className="font-medium">Reading Time</span>
              </span>
              <span className="font-medium">{blogPost.reading_time}</span>
            </div>
            
            <h1 className="heading-xl mb-8">
              {blogPost.title}
            </h1>
          </div>

          {/* Featured Image */}
          <div className="px-8">
            <img
              src={blogPost.image}
              alt={blogPost.title}
              className="w-full h-64 md:h-96 object-cover rounded-xl shadow-md"
            />
          </div>

          {/* Blog Content */}
          <div className="p-8">
            <div 
              className="prose prose-lg max-w-none"
              dangerouslySetInnerHTML={{ __html: blogPost.content }}
            />
            
            {/* Social Share */}
            <div className="mt-10 pt-8 border-t border-gray-200">
              <div className="flex items-center gap-4">
                <span className="text-body font-medium text-gray-700 font-inter">Share this article:</span>
                <div className="flex gap-3">
                  <Button size="sm" variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-50 font-inter font-medium">
                    Facebook
                  </Button>
                  <Button size="sm" variant="outline" className="text-blue-400 border-blue-400 hover:bg-blue-50 font-inter font-medium">
                    Twitter
                  </Button>
                  <Button size="sm" variant="outline" className="text-blue-700 border-blue-700 hover:bg-blue-50 font-inter font-medium">
                    LinkedIn
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Related Blogs Sidebar */}
        <div className="mt-10">
          <Card className="border border-gray-200 shadow-sm">
            <CardHeader>
              <CardTitle className="heading-sm">Related Articles</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex gap-4">
                <img
                  src="https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=80&h=80&fit=crop"
                  alt="Related blog"
                  className="w-20 h-20 object-cover rounded-lg shadow-sm"
                />
                <div>
                  <h4 className="text-body font-semibold text-gray-900 line-clamp-2 hover:text-red-600 transition-colors cursor-pointer font-inter">Exploring the Nightlife of Your City with a Dedicated Night Driver from Driveronhire.com</h4>
                </div>
              </div>
              <div className="flex gap-4">
                <img
                  src="https://images.unsplash.com/photo-1518770660439-4636190af475?w=80&h=80&fit=crop"
                  alt="Related blog"
                  className="w-20 h-20 object-cover rounded-lg shadow-sm"
                />
                <div>
                  <h4 className="text-body font-semibold text-gray-900 line-clamp-2 hover:text-red-600 transition-colors cursor-pointer font-inter">Top Destinations from Mumbai for a Relaxing Driver-Driven Experience</h4>
                </div>
              </div>
              <div className="flex gap-4">
                <img
                  src="https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=80&h=80&fit=crop"
                  alt="Related blog"
                  className="w-20 h-20 object-cover rounded-lg shadow-sm"
                />
                <div>
                  <h4 className="text-body font-semibold text-gray-900 line-clamp-2 hover:text-red-600 transition-colors cursor-pointer font-inter">Tips for a Comfortable Journey with Our Professional Long Distance Drivers</h4>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Comments Section */}
        <div className="mt-12">
          <Card className="border border-gray-200 shadow-sm">
            <CardHeader>
              <CardTitle className="heading-sm">Comments ({comments.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Existing Comments */}
              <div className="space-y-8 mb-10">
                {comments.map((comment) => (
                  <div key={comment.id}>
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center text-white font-bold text-lg font-playfair shadow-sm">
                        {comment.email.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <span className="text-body font-semibold text-gray-900 font-inter">{comment.email}</span>
                          <span className="text-body-sm text-gray-500 font-inter">
                            {formatCommentDate(comment.created_at)}
                          </span>
                        </div>
                        <p className="text-body text-gray-700 font-inter leading-relaxed">{comment.comment}</p>
                        <div className="mt-3 flex gap-4 text-body-sm">
                          <button className="text-red-500 hover:text-red-600 font-medium font-inter transition-colors">👍 Like</button>
                          <button className="text-gray-500 hover:text-gray-600 font-medium font-inter transition-colors">Reply</button>
                        </div>
                      </div>
                    </div>
                    {comment.id !== comments[comments.length - 1].id && (
                      <Separator className="mt-8" />
                    )}
                  </div>
                ))}
              </div>

              {/* Add Comment Form */}
              <div>
                <h3 className="heading-sm mb-6">Leave a Comment</h3>
                <form onSubmit={handleCommentSubmit} className="space-y-6">
                  <div>
                    <Label htmlFor="email" className="text-body font-medium text-gray-700 font-inter">Your Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newComment.email}
                      onChange={(e) => setNewComment({ ...newComment, email: e.target.value })}
                      placeholder="Enter your email"
                      required
                      className="mt-2 font-inter text-body"
                    />
                  </div>
                  <div>
                    <Label htmlFor="comment" className="text-body font-medium text-gray-700 font-inter">Write your comment... *</Label>
                    <Textarea
                      id="comment"
                      value={newComment.comment}
                      onChange={(e) => setNewComment({ ...newComment, comment: e.target.value })}
                      placeholder="Share your thoughts..."
                      rows={4}
                      required
                      className="mt-2 font-inter text-body"
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={submitting}
                    className="bg-red-500 hover:bg-red-600 text-white font-inter font-medium px-8 py-3"
                  >
                    {submitting ? 'Submitting...' : 'Submit Comment'}
                  </Button>
                </form>
              </div>
            </CardContent>
          </Card>
        </div>
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

export default BlogDetail;
