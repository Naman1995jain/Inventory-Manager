'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Recommendations } from './Recommendations';

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

interface BookDetailModalProps {
  book: Book;
  onClose: () => void;
}

export function BookDetailModal({ book, onClose }: BookDetailModalProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [showFullDescription, setShowFullDescription] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'auto';
    };
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  const getRatingStars = (rating: string) => {
    const ratingMap: { [key: string]: number } = {
      'One': 1,
      'Two': 2,
      'Three': 3,
      'Four': 4,
      'Five': 5
    };
    
    const numStars = ratingMap[rating] || 0;
    
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-6 h-6 ${star <= numStars ? 'text-amber-400' : 'text-gray-300'}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-2 text-base text-gray-700 font-semibold">
          {numStars}.0
        </span>
        <span className="text-sm text-gray-500 ml-1">({rating})</span>
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const truncateDescription = (description: string, maxLength: number = 200) => {
    if (description.length <= maxLength) return description;
    return description.substring(0, maxLength) + '...';
  };

  return (
    <div 
      className={`fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 transition-all duration-300 ${
        isVisible ? 'opacity-100' : 'opacity-0'
      }`}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          handleClose();
        }
      }}
    >
      <div className={`bg-white rounded-xl sm:rounded-3xl shadow-2xl max-w-7xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-hidden transition-all duration-300 mx-2 sm:mx-4 ${
        isVisible ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4'
      }`}>
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-600 px-4 sm:px-6 py-4 sm:py-5 flex items-center justify-between z-10">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-lg sm:text-xl font-bold text-white">
              Book Details
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="text-white/80 hover:text-white hover:bg-white/20 transition-all rounded-full p-1.5 sm:p-2"
          >
            <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(95vh-72px)] sm:max-h-[calc(90vh-80px)]">
          <div className="p-4 sm:p-6 lg:p-8">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 sm:gap-6 lg:gap-8">
              {/* Book Image */}
              <div className="lg:col-span-2">
                <div className="sticky top-8">
                  <div className="relative w-full aspect-[3/4] bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl overflow-hidden shadow-2xl group">
                    <Image
                      src={book.image_url}
                      alt={book.product_name}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-500"
                      sizes="(max-width: 1024px) 100vw, 40vw"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = '/images/book-placeholder.jpg';
                      }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </div>
                  
                  {/* Quick Stats */}
                  <div className="mt-6 grid grid-cols-2 gap-4">
                    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                        £{book.price}
                      </div>
                      <div className="text-xs text-gray-600 mt-1 font-medium">Price</div>
                    </div>
                    <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-amber-600">
                        {(() => {
                          const ratingMap: { [key: string]: number } = {
                            'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
                          };
                          return ratingMap[book.rating] || 0;
                        })()}.0
                      </div>
                      <div className="text-xs text-gray-600 mt-1 font-medium">Rating</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Book Information */}
              <div className="lg:col-span-3 space-y-6">
                {/* Title & Category */}
                <div>
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <h3 className="text-3xl font-bold text-gray-900 leading-tight">
                      {book.product_name}
                    </h3>
                  </div>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 text-sm font-semibold rounded-full">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                      </svg>
                      {book.category}
                    </span>
                  </div>
                  <div className="mb-4">
                    {getRatingStars(book.rating)}
                  </div>
                </div>

                {/* Description */}
                <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h4 className="text-lg font-bold text-gray-900">Description</h4>
                  </div>
                  {book.product_description ? (
                    <div>
                      <p className="text-gray-700 leading-relaxed">
                        {showFullDescription || book.product_description.length <= 200
                          ? book.product_description
                          : truncateDescription(book.product_description, 200)}
                      </p>
                      {book.product_description.length > 200 && (
                        <button
                          onClick={() => setShowFullDescription(!showFullDescription)}
                          className="mt-3 text-indigo-600 hover:text-indigo-700 font-semibold text-sm flex items-center gap-1"
                        >
                          {showFullDescription ? (
                            <>
                              Show Less
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7" />
                              </svg>
                            </>
                          ) : (
                            <>
                              Read More
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                              </svg>
                            </>
                          )}
                        </button>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No description available</p>
                  )}
                </div>

                {/* Additional Info */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="bg-white border-2 border-gray-100 rounded-xl p-4 hover:border-indigo-200 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Price</div>
                        <div className="text-2xl font-bold text-gray-900">£{book.price}</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border-2 border-gray-100 rounded-xl p-4 hover:border-purple-200 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Added On</div>
                        <div className="text-sm font-semibold text-gray-900">{formatDate(book.scraped_at)}</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <a
                    href={book.product_page_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 inline-flex items-center justify-center px-6 py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    View on Store
                  </a>
                  
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(book.product_page_url);
                      alert('Link copied to clipboard!');
                    }}
                    className="inline-flex items-center justify-center px-6 py-3.5 bg-white border-2 border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy Link
                  </button>
                </div>

                {/* Additional Features */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100">
                  <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Why Buy This Book?
                  </h4>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-3">
                      <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">Highly rated by readers</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">Part of our curated collection</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">Available for immediate purchase</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            
            {/* Recommendations Section */}
            <div className="mt-6 sm:mt-8">
              <Recommendations book={book} onBookClick={(recommendedBook) => {
                // Close current modal and open new one with recommended book
                handleClose();
                // Small delay to allow modal to close before opening new one
                setTimeout(() => {
                  // This will be handled by the parent component
                  window.dispatchEvent(new CustomEvent('openBookModal', { detail: recommendedBook }));
                }, 300);
              }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}