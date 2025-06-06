
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Facebook, Twitter, Instagram, Linkedin, Mail, Phone, MapPin } from 'lucide-react';

const ModernFooter = () => {
  return (
    <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,0.15)_1px,transparent_0)] bg-[length:20px_20px]"></div>
      </div>
      
      <div className="relative">
        {/* Main Footer Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
            {/* Brand Section */}
            <div className="lg:col-span-1">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-lg">VB</span>
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                  Vacation BNA
                </span>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed mb-6">
                Discover amazing destinations and create unforgettable memories with our premium vacation rental services. Your perfect getaway awaits.
              </p>
              {/* Social Links */}
              <div className="flex space-x-4">
                <Button size="sm" variant="outline" className="border-gray-600 text-gray-300 hover:bg-red-500 hover:border-red-500 hover:text-white transition-all duration-300">
                  <Facebook size={16} />
                </Button>
                <Button size="sm" variant="outline" className="border-gray-600 text-gray-300 hover:bg-red-500 hover:border-red-500 hover:text-white transition-all duration-300">
                  <Twitter size={16} />
                </Button>
                <Button size="sm" variant="outline" className="border-gray-600 text-gray-300 hover:bg-red-500 hover:border-red-500 hover:text-white transition-all duration-300">
                  <Instagram size={16} />
                </Button>
                <Button size="sm" variant="outline" className="border-gray-600 text-gray-300 hover:bg-red-500 hover:border-red-500 hover:text-white transition-all duration-300">
                  <Linkedin size={16} />
                </Button>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-6 text-white">Quick Links</h3>
              <ul className="space-y-3">
                {['Home', 'Properties', 'Blogs', 'About Us', 'Contact Us', 'Privacy Policy'].map((link) => (
                  <li key={link}>
                    <Link 
                      to={link === 'Home' ? '/' : `/${link.toLowerCase().replace(' ', '-')}`}
                      className="text-gray-300 hover:text-red-400 transition-colors duration-300 text-sm flex items-center group"
                    >
                      <span className="w-1 h-1 bg-red-500 rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Top Destinations */}
            <div>
              <h3 className="text-lg font-semibold mb-6 text-white">Top Destinations</h3>
              <ul className="space-y-3">
                {['The Luxury Private Villa', 'Mountain Retreat', 'Beachfront Paradise', 'Urban Loft', 'Country Estate', 'Lakeside Cabin'].map((destination) => (
                  <li key={destination}>
                    <span className="text-gray-300 hover:text-red-400 transition-colors duration-300 text-sm cursor-pointer flex items-center group">
                      <span className="w-1 h-1 bg-red-500 rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                      {destination}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Newsletter & Contact */}
            <div>
              <h3 className="text-lg font-semibold mb-6 text-white">Stay Connected</h3>
              <p className="text-gray-300 text-sm mb-4">
                Subscribe to our newsletter for the latest updates and exclusive offers.
              </p>
              <div className="flex gap-2 mb-6">
                <Input 
                  placeholder="Enter your email" 
                  className="bg-gray-800 border-gray-600 text-white placeholder-gray-400 focus:border-red-500"
                />
                <Button className="bg-red-500 hover:bg-red-600 px-4">
                  <Mail size={16} />
                </Button>
              </div>
              
              {/* Contact Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <MapPin size={16} className="text-red-500 flex-shrink-0" />
                  <span>William Industry Estate, Nashville</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <Mail size={16} className="text-red-500 flex-shrink-0" />
                  <span>info@vacationbna.com</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <Phone size={16} className="text-red-500 flex-shrink-0" />
                  <span>+01 234 567 88</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-gray-400 text-sm">
                © 2025 Vacation BNA. All rights reserved. Made with ❤️ for travelers.
              </p>
              <div className="flex gap-6 text-sm text-gray-400">
                <span className="hover:text-red-400 cursor-pointer transition-colors duration-300">Terms of Service</span>
                <span className="hover:text-red-400 cursor-pointer transition-colors duration-300">Privacy Policy</span>
                <span className="hover:text-red-400 cursor-pointer transition-colors duration-300">Cookies</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default ModernFooter;
