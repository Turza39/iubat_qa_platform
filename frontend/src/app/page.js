'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { questionService } from '@/services/questionService';
import { voteService } from '@/services/voteService';
import { useAuth } from '@/context/AuthContext';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Spinner from '@/components/ui/Spinner';
import VerificationBadge from '@/components/common/VerificationBadge';
import {
  Search,
  MessageSquare,
  ChevronUp,
  PenSquare,
  Tag,
  Clock,
  TrendingUp,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function Home() {
  const { user }                          = useAuth();
  const router                            = useRouter();
  const [questions, setQuestions]         = useState([]);
  const [tags, setTags]                   = useState([]);
  const [loading, setLoading]             = useState(true);
  const [searchInput, setSearchInput]     = useState('');
  const [searchQuery, setSearchQuery]     = useState('');
  const [selectedTag, setSelectedTag]     = useState('');
  const [sortBy, setSortBy]               = useState('newest');
  const [votingId, setVotingId]           = useState(null);

  useEffect(() => {
    fetchTags();
  }, []);

  useEffect(() => {
    fetchQuestions();
  }, [searchQuery, selectedTag]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const data = await questionService.getAllQuestions(searchQuery, selectedTag);
      setQuestions(data);
    } catch (error) {
      toast.error('Failed to load questions.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const data = await questionService.getAllTags();
      setTags(data);
    } catch (error) {
      console.error('Failed to load tags.');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchQuery(searchInput.trim());
    setSelectedTag('');
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setSearchQuery('');
  };

  const handleTagClick = (slug) => {
    setSelectedTag(prev => prev === slug ? '' : slug);
    setSearchInput('');
    setSearchQuery('');
  };

  const handleVote = async (e, questionId) => {
    e.stopPropagation();
    if (!user) {
      toast.error('Please login to vote.');
      return;
    }
    try {
      setVotingId(questionId);
      const data = await voteService.toggleQuestionVote(questionId);
      setQuestions(prev =>
        prev.map(q =>
          q.id === questionId ? { ...q, upvote_count: data.upvote_count } : q
        )
      );
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to vote.';
      toast.error(message);
    } finally {
      setVotingId(null);
    }
  };

  const getSortedQuestions = () => {
    const sorted = [...questions];
    if (sortBy === 'popular') {
      sorted.sort((a, b) => b.upvote_count - a.upvote_count);
    }
    return sorted;
  };

  const formatDate = (dateString) => {
    const date    = new Date(dateString);
    const now     = new Date();
    const diff    = Math.floor((now - date) / 1000);

    if (diff < 60)                    return 'just now';
    if (diff < 3600)                  return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)                 return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800)                return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const sortedQuestions = getSortedQuestions();

  return (
    <div className="min-h-screen bg-slate-50">

      {/* Hero Section */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 py-10 text-center">
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            IUBAT Campus Q&A
          </h1>
          <p className="text-slate-500 mb-6 text-sm">
            Ask questions, get answers from verified IUBAT students.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-xl mx-auto">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                />
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search questions..."
                  className="w-full pl-9 pr-9 py-2.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                />
                {searchInput && (
                  <button
                    type="button"
                    onClick={handleClearSearch}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>
              <Button type="submit" variant="primary" size="md">
                Search
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-6">

          {/* Questions Feed */}
          <div className="flex-1 min-w-0">

            {/* Feed Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-slate-700 text-sm">
                  {searchQuery
                    ? `Results for "${searchQuery}"`
                    : selectedTag
                    ? `Tagged: ${tags.find(t => t.slug === selectedTag)?.name || selectedTag}`
                    : 'All Questions'
                  }
                </h2>
                {!loading && (
                  <span className="text-xs text-slate-400">
                    ({sortedQuestions.length})
                  </span>
                )}
              </div>

              {/* Sort Buttons */}
              <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-1">
                <button
                  onClick={() => setSortBy('newest')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    sortBy === 'newest'
                      ? 'bg-white text-slate-700 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  <Clock size={12} />
                  Newest
                </button>
                <button
                  onClick={() => setSortBy('popular')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    sortBy === 'popular'
                      ? 'bg-white text-slate-700 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  <TrendingUp size={12} />
                  Popular
                </button>
              </div>
            </div>

            {/* Active Filter Pills */}
            {(searchQuery || selectedTag) && (
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs text-slate-500">Active filter:</span>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSearchInput('');
                    setSelectedTag('');
                  }}
                  className="flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full hover:bg-blue-100 transition-colors"
                >
                  {searchQuery ? `"${searchQuery}"` : tags.find(t => t.slug === selectedTag)?.name}
                  <X size={11} />
                </button>
              </div>
            )}

            {/* Questions List */}
            {loading ? (
              <div className="flex justify-center py-16">
                <Spinner size="lg" />
              </div>
            ) : sortedQuestions.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
                <MessageSquare size={36} className="mx-auto text-slate-300 mb-3" />
                <p className="text-slate-500 font-medium mb-1">No questions found</p>
                <p className="text-slate-400 text-sm mb-4">
                  {searchQuery
                    ? 'Try different keywords'
                    : 'Be the first to ask a question!'
                  }
                </p>
                {user && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => router.push('/ask')}
                  >
                    <PenSquare size={14} />
                    Ask a Question
                  </Button>
                )}
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {sortedQuestions.map((question) => (
                  <div
                    key={question.id}
                    onClick={() => router.push(`/questions/${question.id}`)}
                    className="bg-white border border-slate-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer group"
                  >
                    <div className="flex gap-3">

                      {/* Vote Button */}
                      <div className="flex flex-col items-center gap-1 pt-0.5 shrink-0">
                        <button
                          onClick={(e) => handleVote(e, question.id)}
                          disabled={votingId === question.id}
                          className="flex flex-col items-center gap-0.5 p-1.5 rounded-lg hover:bg-slate-100 transition-colors disabled:opacity-50 text-slate-400 hover:text-blue-600"
                        >
                          {votingId === question.id ? (
                            <Spinner size="sm" />
                          ) : (
                            <ChevronUp size={18} />
                          )}
                          <span className="text-xs font-semibold text-slate-600">
                            {question.upvote_count}
                          </span>
                        </button>
                      </div>

                      {/* Question Content */}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-slate-800 text-sm mb-1.5 group-hover:text-blue-700 transition-colors leading-snug">
                          {question.title}
                        </h3>

                        {/* Tags */}
                        {question.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mb-2.5">
                            {question.tags.map((tag) => (
                              <button
                                key={tag.id}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleTagClick(tag.slug);
                                }}
                              >
                                <Badge variant="tag">
                                  {tag.name}
                                </Badge>
                              </button>
                            ))}
                          </div>
                        )}

                        {/* Meta */}
                        <div className="flex items-center gap-3 text-xs text-slate-400">
                          <span className="flex items-center gap-1">
                            <MessageSquare size={11} />
                            {question.answer_count} answers
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            asked by
                            <span className="font-medium text-slate-600">
                              {question.author.username}
                            </span>
                            <VerificationBadge status={question.author.verification_status} />
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Clock size={11} />
                            {formatDate(question.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:w-60 shrink-0 flex flex-col gap-4">

            {/* Ask Question CTA */}
            {user ? (
              <div className="bg-blue-600 rounded-xl p-4 text-white">
                <h3 className="font-semibold text-sm mb-1">Have a question?</h3>
                <p className="text-xs text-blue-100 mb-3">
                  Get answers from verified IUBAT students.
                </p>
                <Button
                  variant="secondary"
                  size="sm"
                  fullWidth
                  onClick={() => router.push('/ask')}
                >
                  <PenSquare size={14} />
                  Ask a Question
                </Button>
              </div>
            ) : (
              <div className="bg-blue-600 rounded-xl p-4 text-white">
                <h3 className="font-semibold text-sm mb-1">Join IUBAT Q&A</h3>
                <p className="text-xs text-blue-100 mb-3">
                  Register to ask questions and get answers from verified students.
                </p>
                <div className="flex flex-col gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    fullWidth
                    onClick={() => router.push('/register')}
                  >
                    Register
                  </Button>
                  <button
                    onClick={() => router.push('/login')}
                    className="text-xs text-blue-100 hover:text-white transition-colors text-center"
                  >
                    Already have an account? Login
                  </button>
                </div>
              </div>
            )}

            {/* Tags Widget */}
            <div className="bg-white border border-slate-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Tag size={14} className="text-slate-500" />
                <h3 className="font-semibold text-slate-700 text-sm">Browse by Tag</h3>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    onClick={() => handleTagClick(tag.slug)}
                  >
                    <Badge
                      variant={selectedTag === tag.slug ? 'verified' : 'tag'}
                    >
                      {tag.name}
                    </Badge>
                  </button>
                ))}
              </div>
            </div>

            {/* How it Works */}
            <div className="bg-white border border-slate-200 rounded-xl p-4">
              <h3 className="font-semibold text-slate-700 text-sm mb-3">
                How it works
              </h3>
              <ol className="flex flex-col gap-2.5">
                {[
                  { step: '1', text: 'Register for an account' },
                  { step: '2', text: 'Submit your student ID to get verified' },
                  { step: '3', text: 'Ask or answer questions' },
                ].map((item) => (
                  <li key={item.step} className="flex items-start gap-2.5">
                    <span className="shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center mt-0.5">
                      {item.step}
                    </span>
                    <span className="text-xs text-slate-600">{item.text}</span>
                  </li>
                ))}
              </ol>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}