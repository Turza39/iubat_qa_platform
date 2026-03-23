'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { authService } from '@/services/authService';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Spinner from '@/components/ui/Spinner';
import VerificationBadge from '@/components/common/VerificationBadge';
import {
  User,
  Mail,
  Calendar,
  ShieldCheck,
  ShieldX,
  Clock,
  MessageSquare,
  ChevronUp,
  PenSquare,
  Edit2,
  X,
  Check,
  ShieldAlert,
  Lock,                    
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function ProfilePage() {
  const router                          = useRouter();
  const { user, loading, refreshUser }  = useAuth();

  const [questions, setQuestions]               = useState([]);
  const [questionsLoading, setQuestionsLoading] = useState(true);
  const [isEditing, setIsEditing]               = useState(false);
  const [formData, setFormData]                 = useState({
    username        : '',
    email           : '',
    current_password: '',          // ← added
  });
  const [errors, setErrors]   = useState({});
  const [saving, setSaving]   = useState(false);

  // ── Redirect guest ────────────────────────────────────────────────────────
  useEffect(() => {
    if (loading) return;           // ← wait for auth
    if (!user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // ── Load questions ────────────────────────────────────────────────────────
  useEffect(() => {
    if (user) {
      fetchProfileData();
    }
  }, [user]);

  const fetchProfileData = async () => {
    try {
      setQuestionsLoading(true);
      const data = await authService.getProfile();
      setQuestions(data.questions || []);
    } catch (error) {
      toast.error('Failed to load profile data.');
    } finally {
      setQuestionsLoading(false);
    }
  };

  // ── Edit handlers ─────────────────────────────────────────────────────────
  const handleEditStart = () => {
    setFormData({
      username        : user.username,
      email           : user.email,
      current_password: '',        // ← always start empty
    });
    setErrors({});
    setIsEditing(true);
  };

  const handleEditCancel = () => {
    setIsEditing(false);
    setErrors({});
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required.';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address.';
    }
    return newErrors;
  };

  const handleSave = async () => {
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    // No changes made
    if (
      formData.username === user.username &&
      formData.email    === user.email
    ) {
      setIsEditing(false);
      return;
    }

    try {
      setSaving(true);
      await authService.updateProfile(formData);
      await refreshUser();
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      const data = error.response?.data;
      if (data?.username) {
        setErrors(prev => ({ ...prev, username: data.username[0] }));
      }
      if (data?.email) {
        setErrors(prev => ({ ...prev, email: data.email[0] }));
      }
      if (data?.current_password) {
        setErrors(prev => ({
          ...prev,
          current_password: data.current_password[0],   // ← map backend error
        }));
      }
      if (!data?.username && !data?.email && !data?.current_password) {
        toast.error('Failed to update profile. Please try again.');
      }
    } finally {
      setSaving(false);
    }
  };

  // ── Helpers ───────────────────────────────────────────────────────────────
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year : 'numeric',
      month: 'long',
      day  : 'numeric',
    });
  };

  const formatRelativeDate = (dateString) => {
    const date = new Date(dateString);
    const now  = new Date();
    const diff = Math.floor((now - date) / 1000);
    if (diff < 60)     return 'just now';
    if (diff < 3600)   return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)  return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    });
  };

  const getVerificationInfo = () => {
    switch (user?.verification_status) {
      case 'verified':
        return {
          icon   : <ShieldCheck size={16} className="text-emerald-600" />,
          label  : 'Verified Student',
          badge  : 'verified',
          message: 'Your student ID has been verified.',
        };
      case 'pending':
        return {
          icon   : <ShieldAlert size={16} className="text-amber-600" />,
          label  : 'Verification Pending',
          badge  : 'pending',
          message: 'Your verification request is under review.',
        };
      case 'rejected':
        return {
          icon   : <ShieldX size={16} className="text-red-500" />,
          label  : 'Verification Rejected',
          badge  : 'rejected',
          message: 'Your request was rejected. Please resubmit.',
        };
      default:
        return {
          icon   : <ShieldX size={16} className="text-slate-400" />,
          label  : 'Not Verified',
          badge  : 'default',
          message: 'Submit your student ID to get verified.',
        };
    }
  };

  // ── Loading ───────────────────────────────────────────────────────────────
  if (loading || !user) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  const verificationInfo = getVerificationInfo();

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-6">

          {/* ── Left Column ── */}
          <div className="flex flex-col gap-4 lg:w-72 shrink-0">

            {/* Profile Card */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6">
              <div className="flex flex-col items-center text-center mb-5">
                <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-3">
                  <span className="text-2xl font-bold text-blue-600">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                <h1 className="text-lg font-bold text-slate-800">
                  {user.username}
                </h1>
                <div className="mt-1">
                  <VerificationBadge status={user.verification_status} />
                </div>
              </div>

              <div className="flex flex-col gap-3 mb-5">
                <div className="flex items-center gap-2.5 text-sm text-slate-600">
                  <Mail size={14} className="text-slate-400 shrink-0" />
                  <span className="truncate">{user.email}</span>
                </div>
                <div className="flex items-center gap-2.5 text-sm text-slate-600">
                  <Calendar size={14} className="text-slate-400 shrink-0" />
                  <span>Joined {formatDate(user.date_joined)}</span>
                </div>
                <div className="flex items-center gap-2.5 text-sm text-slate-600">
                  <MessageSquare size={14} className="text-slate-400 shrink-0" />
                  <span>
                    {questions.length} question{questions.length !== 1 ? 's' : ''} asked
                  </span>
                </div>
              </div>

              {!isEditing && (
                <Button
                  variant="outline"
                  size="sm"
                  fullWidth
                  onClick={handleEditStart}
                >
                  <Edit2 size={14} />
                  Edit Profile
                </Button>
              )}
            </div>

            {/* Verification Card */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5">
              <h2 className="text-sm font-semibold text-slate-700 mb-3">
                Verification Status
              </h2>
              <div className="flex items-center gap-2 mb-2">
                {verificationInfo.icon}
                <Badge variant={verificationInfo.badge}>
                  {verificationInfo.label}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                {verificationInfo.message}
              </p>

              {user.verification_status !== 'verified' &&
               user.verification_status !== 'pending' && (
                <Button
                  variant="primary"
                  size="sm"
                  fullWidth
                  onClick={() => router.push('/verify')}
                >
                  <ShieldCheck size={14} />
                  {user.verification_status === 'rejected'
                    ? 'Resubmit Verification'
                    : 'Get Verified'
                  }
                </Button>
              )}

              {user.verification_status === 'pending' && (
                <div className="text-xs text-amber-600 bg-amber-50 rounded-lg px-3 py-2 text-center">
                  Usually reviewed within 24 hours
                </div>
              )}
            </div>

          </div>

          {/* ── Right Column ── */}
          <div className="flex-1 min-w-0 flex flex-col gap-4">

            {/* Edit Form */}
            {isEditing && (
              <div className="bg-white border border-blue-200 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-semibold text-slate-800">Edit Profile</h2>
                  <button
                    onClick={handleEditCancel}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div className="flex flex-col gap-4">
                  <Input
                    label="Username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter your username"
                    error={errors.username}
                    required
                  />
                  <Input
                    label="Email Address"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Enter your email"
                    error={errors.email}
                    required
                  />

                  {/* Divider */}
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-px bg-slate-100" />
                    <span className="text-xs text-slate-400">
                      Confirm identity to save
                    </span>
                    <div className="flex-1 h-px bg-slate-100" />
                  </div>

                  <Input
                    label="Current Password"
                    name="current_password"
                    type="password"
                    value={formData.current_password}
                    onChange={handleChange}
                    placeholder="Enter your current password"
                    error={errors.current_password}
                    required
                  />

                  {/* Security note */}
                  <div className="flex items-start gap-2 bg-slate-50 rounded-lg px-3 py-2.5">
                    <Lock size={13} className="text-slate-400 mt-0.5 shrink-0" />
                    <p className="text-xs text-slate-500">
                      Your current password is required to confirm any
                      changes to your profile.
                    </p>
                  </div>

                  <div className="flex gap-3 pt-1">
                    <Button
                      variant="primary"
                      size="md"
                      onClick={handleSave}
                      disabled={saving}
                    >
                      {saving ? (
                        <>
                          <Spinner size="sm" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Check size={15} />
                          Save Changes
                        </>
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="md"
                      onClick={handleEditCancel}
                      disabled={saving}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Questions History */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-5">
                <h2 className="font-semibold text-slate-800">
                  My Questions
                  {!questionsLoading && (
                    <span className="ml-2 text-xs font-normal text-slate-400">
                      ({questions.length})
                    </span>
                  )}
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push('/ask')}
                >
                  <PenSquare size={13} />
                  Ask Question
                </Button>
              </div>

              {questionsLoading ? (
                <div className="flex justify-center py-10">
                  <Spinner size="md" />
                </div>
              ) : questions.length === 0 ? (
                <div className="text-center py-10">
                  <MessageSquare size={32} className="mx-auto text-slate-300 mb-3" />
                  <p className="text-slate-500 text-sm font-medium mb-1">
                    No questions yet
                  </p>
                  <p className="text-slate-400 text-xs mb-4">
                    Ask your first question to the IUBAT community
                  </p>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => router.push('/ask')}
                  >
                    <PenSquare size={13} />
                    Ask a Question
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col divide-y divide-slate-100">
                  {questions.map((question) => (
                    <div
                      key={question.id}
                      onClick={() => router.push(`/questions/${question.id}`)}
                      className="py-4 first:pt-0 last:pb-0 cursor-pointer group"
                    >
                      <div className="flex gap-3">
                        <div className="shrink-0 flex flex-col items-center gap-1 pt-0.5">
                          <ChevronUp size={14} className="text-slate-300" />
                          <span className="text-xs font-semibold text-slate-500">
                            {question.upvote_count}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-slate-700 group-hover:text-blue-600 transition-colors leading-snug mb-2">
                            {question.title}
                          </h3>
                          {question.tags?.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {question.tags.map((tag) => (
                                <Badge key={tag.id} variant="tag">
                                  {tag.name}
                                </Badge>
                              ))}
                            </div>
                          )}
                          <div className="flex items-center gap-3 text-xs text-slate-400">
                            <span className="flex items-center gap-1">
                              <MessageSquare size={11} />
                              {question.answer_count} answer{question.answer_count !== 1 ? 's' : ''}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Clock size={11} />
                              {formatRelativeDate(question.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}