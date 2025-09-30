'use client';

import { useState, useEffect } from 'react';
import { RecommendationCard } from './RecommendationCard';

interface Book {
  id: number;
  product_name: string;
  product_description: string;
  category: string;
  price: string;
  rating: string;
  image_url: string;
  product_page_url: string;
  scraped_at: string;
}

interface RecommendedBook {
  id: number;
  product_name: string;
  product_description?: string;
  category?: string;
  price: number;
  rating?: string;
  image_url?: string;
  product_page_url?: string;
  similarity_score: number;
  recommendation_type: string;
}

interface RecommendationsResponse {
  product_id: number;
  product_name: string;
  recommendation_type: string;
  recommendations: RecommendedBook[];
  total_found: number;
}

interface RecommendationsProps {
  book: Book;
  onBookClick: (book: Book) => void;
}

type RecommendationType = 'hybrid' | 'price' | 'category' | 'description';

export function Recommendations({ book, onBookClick }: RecommendationsProps) {
  const [recommendations, setRecommendations] = useState<RecommendedBook[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendationType, setRecommendationType] = useState<RecommendationType>('hybrid');
  const [limit, setLimit] = useState(8);
  const [expanded, setExpanded] = useState(false);

  const fetchRecommendations = async () => {
    if (!book.id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      let url = `http://localhost:8000/api/v1/recommendations/${book.id}?recommendation_type=${recommendationType}&limit=${limit}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
      }
      
      const data: RecommendationsResponse = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [book.id, recommendationType, limit]);

  const handleRecommendedBookClick = (recommendedBook: RecommendedBook) => {
    // Convert RecommendedBook to Book format
    const bookData: Book = {
      id: recommendedBook.id,
      product_name: recommendedBook.product_name,
      product_description: recommendedBook.product_description || '',
      category: recommendedBook.category || '',
      price: recommendedBook.price?.toString() || '0',
      rating: recommendedBook.rating || '',
      image_url: recommendedBook.image_url || '',
      product_page_url: recommendedBook.product_page_url || '',
      scraped_at: ''
    };
    onBookClick(bookData);
  };

  const getRecommendationTypeIcon = (type: RecommendationType) => {
    switch (type) {
      case 'price':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
        );
      case 'category':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        );
      case 'description':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case 'hybrid':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
    }
  };

  const getRecommendationTypeDescription = (type: RecommendationType) => {
    switch (type) {
      case 'price':
        return 'Find books with similar prices';
      case 'category':
        return 'Find books in the same category';
      case 'description':
        return 'AI-powered content similarity';
      case 'hybrid':
        return 'Best of all recommendation types';
    }
  };

  if (!expanded) {
    return (
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl sm:rounded-2xl p-3 sm:p-6">
        <button
          onClick={() => setExpanded(true)}
          className="w-full flex items-center justify-between text-left hover:bg-white/50 rounded-xl p-3 sm:p-4 transition-all duration-200"
        >
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-bold text-gray-900">
                You Might Also Like
              </h3>
              <p className="text-gray-600 text-xs sm:text-sm">
                AI-powered book recommendations based on this book
              </p>
            </div>
          </div>
          <svg className="w-5 h-5 sm:w-6 sm:h-6 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl sm:rounded-2xl p-3 sm:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg sm:text-xl font-bold text-gray-900">
              You Might Also Like
            </h3>
            <p className="text-gray-600 text-xs sm:text-sm">
              {recommendations.length} recommendations found
            </p>
          </div>
        </div>
        <button
          onClick={() => setExpanded(false)}
          className="text-gray-400 hover:text-gray-600 transition-colors p-1"
        >
          <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7" />
          </svg>
        </button>
      </div>

      {/* Controls */}
      <div className="mb-4 sm:mb-6 space-y-3 sm:space-y-4">
        {/* Recommendation Type Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Recommendation Type
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
            {(['hybrid', 'description', 'category', 'price'] as RecommendationType[]).map((type) => (
              <button
                key={type}
                onClick={() => setRecommendationType(type)}
                className={`p-3 sm:p-3 rounded-lg border-2 transition-all duration-200 ${
                  recommendationType === type
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 active:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2 mb-1">
                  {getRecommendationTypeIcon(type)}
                  <span className="text-sm sm:text-sm font-medium capitalize">{type}</span>
                </div>
                <div className="text-xs text-gray-500">
                  {getRecommendationTypeDescription(type)}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Number of Results */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of recommendations:
          </label>
          <select
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="w-full border-2 border-gray-300 rounded-lg px-4 py-3 text-base font-medium bg-white text-gray-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 appearance-none"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e")`,
              backgroundPosition: 'right 0.5rem center',
              backgroundRepeat: 'no-repeat',
              backgroundSize: '1.5em 1.5em'
            }}
          >
            <option value={4}>Show 4 recommendations</option>
            <option value={8}>Show 8 recommendations</option>
            <option value={12}>Show 12 recommendations</option>
            <option value={16}>Show 16 recommendations</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-8 sm:py-12">
          <div className="animate-spin rounded-full h-8 w-8 sm:h-8 sm:w-8 border-b-2 border-indigo-600"></div>
          <span className="text-gray-600 text-sm sm:text-base mt-3">Finding similar books...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4 mb-4 sm:mb-6">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-red-700">{error}</span>
          </div>
          <button
            onClick={fetchRecommendations}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Recommendations Grid */}
      {!loading && !error && recommendations.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {recommendations.map((rec) => (
            <RecommendationCard
              key={rec.id}
              book={rec}
              onClick={handleRecommendedBookClick}
            />
          ))}
        </div>
      )}

      {/* No Results */}
      {!loading && !error && recommendations.length === 0 && (
        <div className="text-center py-8 sm:py-12">
          <svg className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-3 sm:mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
          <p className="text-gray-600 text-sm px-4">
            Try a different recommendation type or check back later as we add more books.
          </p>
        </div>
      )}
    </div>
  );
}