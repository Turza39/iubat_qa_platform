'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { questionService } from '@/services/questionService';
import { answerService } from '@/services/answerService';
import { voteService } from '@/services/voteService';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Spinner from '@/components/ui/Spinner';
import VerificationBadge from '@/components/common/VerificationBadge';
import {
  ChevronUp,
  MessageSquare,
  Clock,
  ArrowLeft,
  ShieldCheck,
  ShieldX,
  Send,
  Tag,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function QuestionDetailPage() {
  const { id }        = useParams();
  const router        = useRouter();
  const { user }      = useAuth();

  const [question, setQuestion]         = useState(null);
  const [answers, setAnswers]           = useState([]);
  const [loading, setLoading]           = useState(true);
  const [answerBody, setAnswerBody]     = useState('');
  const [answerError, setAnswerError]   = useState('');
  const [submitting, setSubmitting]     = useState(false);
  const [votingId, setVotingId]         = useState(null);
  const [votingType, setVotingType]     = useState(null);

  useEffect(() => {
    fetchQuestionDetail();
  }, [id]);

  const fetchQuestionDetail = async () => {
    try {
      setLoading(true);
      const data = await questionService.getQuestionDetail(id);
      setQuestion(data.question);
      setAnswers(data.answers);
    } catch (error) {
      toast.error('Failed to load question.');
      router.push('/');
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionVote = async () => {
    if (!user) {
      toast.error('Please login to vote.');
      return;
    }
    try {
      setVotingId('question');
      setVotingType('question');
      const data = await voteService.toggleQuestionVote(id);
      setQuestion(prev => ({ ...prev, upvote_count: data.upvote_count }));
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to vote.';
      toast.error(message);
    } finally {
      setVotingId(null);
      setVotingType(null);
    }
  };

  const handleAnswerVote = async (answerId) => {
    if (!user) {
      toast.error('Please login to vote.');
      return;
    }
    try {
      setVotingId(answerId);
      setVotingType('answer');
      const data = await voteService.toggleAnswerVote(answerId);
      setAnswers(prev =>
        prev.map(a =>
          a.id === answerId ? { ...a, upvote_count: data.upvote_count } : a
        )
      );
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to vote.';
      toast.error(message);
    } finally {
      setVotingId(null);
      setVotingType(null);
    }
  };

  const handleAnswerSubmit = async (e) => {
    e.preventDefault();

    if (!answerBody.trim()) {
      setAnswerError('Answer cannot be empty.');
      return;
    }
    if (answerBody.trim().length < 10) {
      setAnswerError('Answer must be at least 10 characters.');
      return;
    }
    if (answerBody.length > 5000) {
      setAnswerError('Answer must not exceed 5000 characters.');
      return;
    }

    try {
      setSubmitting(true);
      const newAnswer = await answerService.postAnswer(id, { body: answerBody });
      setAnswers(prev => [newAnswer, ...prev]);
      setAnswerBody('');
      setAnswerError('');
      setQuestion(prev => ({ ...prev, answer_count: prev.answer_count + 1 }));
      toast.success('Answer posted successfully!');
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to post answer.';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    const date  = new Date(dateString);
    const now   = new Date();
    const diff  = Math.floor((now - date) / 1000);

    if (diff < 60)      return 'just now';
    if (diff < 3600)    return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)   return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800)  return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!question) return null;

  const sortedAnswers = [...answers].sort((a, b) => b.upvote_count - a.upvote_count);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 py-8">

        {/* Back Button */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-6 transition-colors"
        >
          <ArrowLeft size={16} />
          Back to questions
        </button>

        {/* Question Card */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 mb-4">
          <div className="flex gap-4">

            {/* Vote Column */}
            <div className="flex flex-col items-center gap-1 shrink-0">
              <button
                onClick={handleQuestionVote}
                disabled={votingId === 'question'}
                className="flex flex-col items-center gap-1 p-2 rounded-xl hover:bg-slate-100 transition-colors disabled:opacity-50 group"
              >
                {votingId === 'question' ? (
                  <Spinner size="sm" />
                ) : (
                  <ChevronUp
                    size={22}
                    className="text-slate-400 group-hover:text-blue-600 transition-colors"
                  />
                )}
                <span className="text-sm font-bold text-slate-600">
                  {question.upvote_count}
                </span>
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold text-slate-800 mb-3 leading-snug">
                {question.title}
              </h1>

              {/* Tags */}
              {question.tags?.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap mb-4">
                  <Tag size={13} className="text-slate-400" />
                  {question.tags.map(tag => (
                    <Badge key={tag.id} variant="tag">
                      {tag.name}
                    </Badge>
                  ))}
                </div>
              )}

              {/* Body */}
              <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap mb-4">
                {question.body}
              </p>

              {/* Meta */}
              <div className="flex items-center gap-2 text-xs text-slate-400 pt-3 border-t border-slate-100">
                <span className="flex items-center gap-1">
                  <Clock size={11} />
                  {formatDate(question.created_at)}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1.5">
                  Asked by
                  <span className="font-medium text-slate-600">
                    {question.author.username}
                  </span>
                  <VerificationBadge status={question.author.verification_status} />
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <MessageSquare size={11} />
                  {question.answer_count} answers
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Answers Section */}
        <div className="mb-4">
          <h2 className="text-base font-semibold text-slate-700 mb-3 flex items-center gap-2">
            <MessageSquare size={16} className="text-slate-500" />
            {sortedAnswers.length} Answer{sortedAnswers.length !== 1 ? 's' : ''}
          </h2>

          {sortedAnswers.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <MessageSquare size={32} className="mx-auto text-slate-300 mb-2" />
              <p className="text-slate-500 text-sm font-medium">No answers yet</p>
              <p className="text-slate-400 text-xs mt-1">
                Be the first verified student to answer this question
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {sortedAnswers.map((answer, index) => (
                <div
                  key={answer.id}
                  className={`bg-white border rounded-xl p-5 ${
                    index === 0 && answer.upvote_count > 0
                      ? 'border-emerald-200 bg-emerald-50/30'
                      : 'border-slate-200'
                  }`}
                >
                  <div className="flex gap-4">

                    {/* Vote */}
                    <div className="flex flex-col items-center gap-1 shrink-0">
                      <button
                        onClick={() => handleAnswerVote(answer.id)}
                        disabled={votingId === answer.id}
                        className="flex flex-col items-center gap-1 p-1.5 rounded-lg hover:bg-slate-100 transition-colors disabled:opacity-50 group"
                      >
                        {votingId === answer.id ? (
                          <Spinner size="sm" />
                        ) : (
                          <ChevronUp
                            size={18}
                            className="text-slate-400 group-hover:text-blue-600 transition-colors"
                          />
                        )}
                        <span className="text-xs font-bold text-slate-600">
                          {answer.upvote_count}
                        </span>
                      </button>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {index === 0 && answer.upvote_count > 0 && (
                        <div className="flex items-center gap-1.5 mb-2">
                          <ShieldCheck size={13} className="text-emerald-600" />
                          <span className="text-xs font-medium text-emerald-700">
                            Top Answer
                          </span>
                        </div>
                      )}
                      <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap mb-3">
                        {answer.body}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <span className="flex items-center gap-1">
                          <Clock size={11} />
                          {formatDate(answer.created_at)}
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1.5">
                          Answered by
                          <span className="font-medium text-slate-600">
                            {answer.author.username}
                          </span>
                          <VerificationBadge status={answer.author.verification_status} />
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Answer Input Section */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
          <h3 className="text-base font-semibold text-slate-700 mb-4">
            Your Answer
          </h3>

          {/* Not logged in */}
          {!user && (
            <div className="text-center py-6 bg-slate-50 rounded-xl border border-slate-200">
              <p className="text-slate-500 text-sm mb-3">
                You must be logged in to answer
              </p>
              <div className="flex items-center justify-center gap-3">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => router.push('/login')}
                >
                  Login
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push('/register')}
                >
                  Register
                </Button>
              </div>
            </div>
          )}

          {/* Logged in but not verified */}
          {user && user.verification_status !== 'verified' &&  (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
              <ShieldX size={18} className="text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-800 mb-1">
                  Verification required to answer
                </p>
                <p className="text-xs text-amber-700 mb-3">
                  Only verified IUBAT students can post answers. Submit your
                  student ID to get verified.
                </p>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => router.push('/verify')}
                >
                  <ShieldCheck size={14} />
                  Get Verified
                </Button>
              </div>
            </div>
          )}

          {/* Verified - show answer form */}
          {user && user.verification_status === 'verified' && (
            <form onSubmit={handleAnswerSubmit} className="flex flex-col gap-3">
              <textarea
                value={answerBody}
                onChange={(e) => {
                  setAnswerBody(e.target.value);
                  if (answerError) setAnswerError('');
                }}
                placeholder="Write your answer here. Be clear and helpful..."
                rows={5}
                className={`
                  w-full px-3 py-2.5 text-sm rounded-lg border transition-colors duration-200
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                  resize-none
                  ${answerError
                    ? 'border-red-400 bg-red-50'
                    : 'border-slate-300 bg-white hover:border-slate-400'
                  }
                `}
              />
              <div className="flex items-center justify-between">
                <div>
                  {answerError && (
                    <p className="text-xs text-red-500">{answerError}</p>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs ${
                    answerBody.length > 4500 ? 'text-red-500' : 'text-slate-400'
                  }`}>
                    {answerBody.length}/5000
                  </span>
                  <Button
                    type="submit"
                    variant="primary"
                    size="md"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <Spinner size="sm" />
                        Posting...
                      </>
                    ) : (
                      <>
                        <Send size={14} />
                        Post Answer
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </form>
          )}
        </div>

      </div>
    </div>
  );
}