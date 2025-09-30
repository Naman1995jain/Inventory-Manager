'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

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

interface RecommendationCardProps {
  book: RecommendedBook;
  onClick: (book: RecommendedBook) => void;
}

export function RecommendationCard({ book, onClick }: RecommendationCardProps) {
  const getRatingStars = (rating: string) => {
    const ratingMap: { [key: string]: number } = {
      'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
    };
    const numRating = ratingMap[rating] || 0;
    
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-3 h-3 ${
              star <= numRating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  const getSimilarityPercentage = () => {
    return Math.round(book.similarity_score * 100);
  };

  const getRecommendationTypeIcon = () => {
    switch (book.recommendation_type) {
      case 'price_based':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
        );
      case 'category_based':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        );
      case 'description_based':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case 'hybrid':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
    }
  };

  const getRecommendationTypeLabel = () => {
    switch (book.recommendation_type) {
      case 'price_based':
        return 'Similar Price';
      case 'category_based':
        return 'Same Category';
      case 'description_based':
        return 'AI Match';
      case 'hybrid':
        return 'Smart Match';
      default:
        return 'Recommended';
    }
  };

  const getRecommendationTypeColor = () => {
    switch (book.recommendation_type) {
      case 'price_based':
        return 'bg-green-100 text-green-700';
      case 'category_based':
        return 'bg-blue-100 text-blue-700';
      case 'description_based':
        return 'bg-purple-100 text-purple-700';
      case 'hybrid':
        return 'bg-indigo-100 text-indigo-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer group overflow-hidden border border-gray-200"
      onClick={() => onClick(book)}
    >
      {/* Image */}
      <div className="relative w-full h-32 sm:h-40 lg:h-48 bg-gradient-to-br from-gray-100 to-gray-200 overflow-hidden">
        <Image
          src={book.image_url || '/images/book-placeholder.jpg'}
          alt={book.product_name}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-300"
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/images/book-placeholder.jpg';
          }}
        />
        
        {/* Similarity Score Badge */}
        <div className="absolute top-1 sm:top-2 right-1 sm:right-2 bg-white/90 backdrop-blur-sm rounded-full px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs font-bold text-gray-700">
          {getSimilarityPercentage()}%
        </div>
        
        {/* Recommendation Type Badge */}
        <div className={`absolute top-1 sm:top-2 left-1 sm:left-2 ${getRecommendationTypeColor()} rounded-full px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs font-medium flex items-center gap-1`}>
          <div className="w-3 h-3 sm:w-4 sm:h-4">
            {getRecommendationTypeIcon()}
          </div>
          <span className="hidden sm:inline">{getRecommendationTypeLabel()}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-2 sm:p-3 lg:p-4">
        {/* Title */}
        <h4 className="font-semibold text-gray-900 text-xs sm:text-sm line-clamp-2 mb-1 sm:mb-2 group-hover:text-indigo-600 transition-colors leading-tight">
          {book.product_name}
        </h4>

        {/* Category */}
        {book.category && (
          <p className="text-xs text-gray-500 mb-1 sm:mb-2 truncate">
            {book.category}
          </p>
        )}

        {/* Rating and Price */}
        <div className="flex items-center justify-between mb-1 sm:mb-2">
          <div className="flex flex-col gap-1">
            {book.rating && (
              <div className="flex items-center gap-1">
                {getRatingStars(book.rating)}
                <span className="text-xs text-gray-500 ml-1 hidden sm:inline">{book.rating}</span>
              </div>
            )}
          </div>
          
          <div className="text-sm sm:text-base lg:text-lg font-bold text-indigo-600">
            £{book.price?.toFixed(2) || '0.00'}
          </div>
        </div>

        {/* Description Preview - Hidden on mobile */}
        {book.product_description && (
          <p className="text-xs text-gray-600 line-clamp-2 hidden sm:block">
            {book.product_description}
          </p>
        )}
      </div>
    </div>
  );
}