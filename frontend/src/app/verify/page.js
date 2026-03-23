'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { authService } from '@/services/authService';
import Button from '@/components/ui/Button';
import Spinner from '@/components/ui/Spinner';
import Badge from '@/components/ui/Badge';
import {
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Upload,
  ImageIcon,
  X,
  CheckCircle2,
  AlertCircle,
  Info,
  ArrowLeft,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function VerifyPage() {
  const router = useRouter();
  const { user, loading, refreshUser } = useAuth();
  const fileInputRef = useRef(null);

  // Page state
  const [pageLoading, setPageLoading] = useState(true);
  const [verifyStatus, setVerifyStatus] = useState(null);

  // Upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [fileError, setFileError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // ── Auth guard ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (loading) return;       // ← wait for auth to initialize
    if (!user) {
      router.push('/login');
    }
  }, [user, loading, router]);
  // ── Load verification status ──────────────────────────────────────────────
  useEffect(() => {
    if (user) {
      fetchVerificationStatus();
    }
  }, [user]);

  const fetchVerificationStatus = async () => {
    try {
      setPageLoading(true);
      const data = await authService.getVerificationStatus();
      setVerifyStatus(data);
    } catch (error) {
      toast.error('Failed to load verification status.');
    } finally {
      setPageLoading(false);
    }
  };

  // ── File handling ─────────────────────────────────────────────────────────
  const validateFile = (file) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      return 'Only JPG, JPEG and PNG files are allowed.';
    }
    if (file.size > 5 * 1024 * 1024) {
      return 'File size must not exceed 5MB.';
    }
    return '';
  };

  const handleFileSelect = (file) => {
    if (!file) return;

    const error = validateFile(file);
    if (error) {
      setFileError(error);
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    setFileError('');
    setSelectedFile(file);

    // Generate preview
    const reader = new FileReader();
    reader.onloadend = () => setPreviewUrl(reader.result);
    reader.readAsDataURL(file);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setFileError('');
    // Reset file input so same file can be reselected
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // ── Submit ────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setFileError('Please select your student ID card image.');
      return;
    }

    try {
      setSubmitting(true);
      const formData = new FormData();
      formData.append('id_card_image', selectedFile);
      await authService.submitVerification(formData);
      toast.success('Verification request submitted successfully!');
      // Refresh status from backend
      await fetchVerificationStatus();
      await refreshUser();
      setSelectedFile(null);
      setPreviewUrl(null);
    } catch (error) {
      const data = error.response?.data;
      if (data?.id_card_image) {
        setFileError(data.id_card_image[0]);
      } else if (data?.message) {
        toast.error(data.message);
      } else {
        toast.error('Failed to submit verification. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // ── Format file size ──────────────────────────────────────────────────────
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // ── Loading state ─────────────────────────────────────────────────────────
  if (loading || !user || pageLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  // ── Already verified ──────────────────────────────────────────────────────
  if (user.verification_status === 'verified') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-10 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-full mb-4">
            <ShieldCheck size={32} className="text-emerald-600" />
          </div>
          <h1 className="text-xl font-bold text-slate-800 mb-2">
            You&apos;re Already Verified!
          </h1>
          <p className="text-slate-500 text-sm mb-6">
            Your student ID has been verified. You can now post answers
            and participate fully in the IUBAT Q&amp;A community.
          </p>
          <div className="flex flex-col gap-2">
            <Button
              variant="primary"
              size="md"
              fullWidth
              onClick={() => router.push('/')}
            >
              Browse Questions
            </Button>
            <Button
              variant="ghost"
              size="md"
              fullWidth
              onClick={() => router.push('/profile')}
            >
              Go to Profile
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // ── Pending state ─────────────────────────────────────────────────────────
  if (user.verification_status === 'pending') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-10 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-amber-100 rounded-full mb-4">
            <ShieldAlert size={32} className="text-amber-600" />
          </div>
          <h1 className="text-xl font-bold text-slate-800 mb-2">
            Verification Under Review
          </h1>
          <p className="text-slate-500 text-sm mb-2">
            Your student ID card has been submitted and is currently
            being reviewed by our team.
          </p>
          <p className="text-slate-400 text-xs mb-6">
            This usually takes up to 24 hours. You&apos;ll be able to
            post answers once approved.
          </p>

          {/* Submitted at */}
          {verifyStatus?.submitted_at && (
            <div className="bg-amber-50 border border-amber-100 rounded-xl px-4 py-3 mb-6">
              <p className="text-xs text-amber-700">
                Submitted on{' '}
                <span className="font-medium">
                  {new Date(verifyStatus.submitted_at).toLocaleDateString(
                    'en-US',
                    { year: 'numeric', month: 'long', day: 'numeric' }
                  )}
                </span>
              </p>
            </div>
          )}

          <div className="flex flex-col gap-2">
            <Button
              variant="primary"
              size="md"
              fullWidth
              onClick={() => router.push('/')}
            >
              Browse Questions
            </Button>
            <Button
              variant="ghost"
              size="md"
              fullWidth
              onClick={() => router.push('/profile')}
            >
              <ArrowLeft size={15} />
              Back to Profile
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // ── Main form (not_submitted or rejected) ─────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-2xl mx-auto px-4 py-8">

        {/* Back Button */}
        <button
          onClick={() => router.push('/profile')}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition-colors mb-6"
        >
          <ArrowLeft size={15} />
          Back to Profile
        </button>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800 mb-1">
            Student Verification
          </h1>
          <p className="text-slate-500 text-sm">
            Submit your IUBAT student ID card to get verified and unlock
            full access to the platform.
          </p>
        </div>

        {/* Rejected Banner */}
        {user.verification_status === 'rejected' && (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-5">
            <ShieldX size={18} className="text-red-500 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-700">
                Previous request was rejected
              </p>
              <p className="text-xs text-red-500 mt-0.5">
                Please upload a clearer image of your student ID and resubmit.
              </p>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-5">

          {/* Upload Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6">
            <h2 className="font-semibold text-slate-800 mb-1">
              Upload Student ID Card
            </h2>
            <p className="text-xs text-slate-500 mb-5">
              Upload a clear photo of your IUBAT student ID card.
              JPG or PNG only, maximum 5MB.
            </p>

            {/* Drop Zone */}
            {!previewUrl ? (
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
                className={`
                  border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                  transition-colors duration-200
                  ${fileError
                    ? 'border-red-300 bg-red-50'
                    : 'border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50'
                  }
                `}
              >
                <div className="flex flex-col items-center gap-3">
                  <div className={`
                    w-12 h-12 rounded-full flex items-center justify-center
                    ${fileError ? 'bg-red-100' : 'bg-slate-200'}
                  `}>
                    <ImageIcon
                      size={22}
                      className={fileError ? 'text-red-400' : 'text-slate-400'}
                    />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-700 mb-1">
                      Drag & drop your ID card here
                    </p>
                    <p className="text-xs text-slate-400">
                      or{' '}
                      <span className="text-blue-600 font-medium">
                        click to browse
                      </span>
                    </p>
                  </div>
                  <p className="text-xs text-slate-400">
                    JPG, JPEG, PNG • Max 5MB
                  </p>
                </div>
              </div>
            ) : (
              /* Image Preview */
              <div className="relative rounded-xl overflow-hidden border border-slate-200">
                <img
                  src={previewUrl}
                  alt="ID card preview"
                  className="w-full max-h-64 object-contain bg-slate-100"
                />
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="absolute top-2 right-2 w-7 h-7 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors shadow-md"
                >
                  <X size={14} />
                </button>
                {/* File info */}
                <div className="px-4 py-2.5 bg-white border-t border-slate-100 flex items-center gap-2">
                  <ImageIcon size={14} className="text-slate-400 shrink-0" />
                  <span className="text-xs text-slate-600 truncate flex-1">
                    {selectedFile?.name}
                  </span>
                  <span className="text-xs text-slate-400 shrink-0">
                    {selectedFile && formatFileSize(selectedFile.size)}
                  </span>
                </div>
              </div>
            )}

            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/jpg,image/png"
              onChange={handleFileInputChange}
              className="hidden"
            />

            {/* File Error */}
            {fileError && (
              <div className="flex items-center gap-2 mt-3">
                <AlertCircle size={14} className="text-red-500 shrink-0" />
                <p className="text-xs text-red-500">{fileError}</p>
              </div>
            )}

            {/* Change file button */}
            {previewUrl && (
              <Button
                variant="ghost"
                size="sm"
                className="mt-3"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload size={13} />
                Change Image
              </Button>
            )}
          </div>

          {/* Guidelines Card */}
          <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Info size={15} className="text-blue-600 shrink-0" />
              <h3 className="text-sm font-semibold text-blue-800">
                Photo Guidelines
              </h3>
            </div>
            <ul className="flex flex-col gap-2">
              {[
                'Make sure your full name and student ID number are clearly visible',
                'Use good lighting — avoid shadows or glare on the card',
                'The entire card should fit within the photo frame',
                'JPG or PNG format only, file size must be under 5MB',
                'Do not crop or edit the image in any way',
              ].map((tip, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2
                    size={13}
                    className="text-blue-500 mt-0.5 shrink-0"
                  />
                  <span className="text-xs text-blue-700">{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* What happens next */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">
              What happens after submission?
            </h3>
            <ol className="flex flex-col gap-3">
              {[
                {
                  step: '1',
                  title: 'Under Review',
                  desc: 'Our team reviews your ID card within 24 hours',
                },
                {
                  step: '2',
                  title: 'Get Verified',
                  desc: 'Your account gets a verified badge visible to all users',
                },
                {
                  step: '3',
                  title: 'Full Access',
                  desc: 'Post answers and participate fully in the community',
                },
              ].map((item) => (
                <li key={item.step} className="flex items-start gap-3">
                  <span className="shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center mt-0.5">
                    {item.step}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-slate-700">
                      {item.title}
                    </p>
                    <p className="text-xs text-slate-500">{item.desc}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            disabled={submitting || !selectedFile}
            onClick={handleSubmit}
          >
            {submitting ? (
              <>
                <Spinner size="sm" />
                Submitting...
              </>
            ) : (
              <>
                <ShieldCheck size={17} />
                {user.verification_status === 'rejected'
                  ? 'Resubmit Verification'
                  : 'Submit for Verification'
                }
              </>
            )}
          </Button>

        </div>
      </div>
    </div>
  );
}