'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { questionService } from '@/services/questionService';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Spinner from '@/components/ui/Spinner';
import { PenSquare, Tag, X, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AskPage() {
  const router      = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [formData, setFormData] = useState({
    title   : '',
    body    : '',
    tag_ids : [],
  });

  const [tags, setTags]         = useState([]);
  const [errors, setErrors]     = useState({});
  const [loading, setLoading]   = useState(false);
  const [tagsLoading, setTagsLoading] = useState(true);

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      toast.error('Please login to ask a question.');
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      const data = await questionService.getAllTags();
      setTags(data);
    } catch (error) {
      toast.error('Failed to load tags.');
    } finally {
      setTagsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleTagToggle = (tagId) => {
    setFormData(prev => {
      const already = prev.tag_ids.includes(tagId);
      if (already) {
        return { ...prev, tag_ids: prev.tag_ids.filter(id => id !== tagId) };
      }
      if (prev.tag_ids.length >= 5) {
        toast.error('You can select a maximum of 5 tags.');
        return prev;
      }
      return { ...prev, tag_ids: [...prev.tag_ids, tagId] };
    });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required.';
    } else if (formData.title.trim().length < 10) {
      newErrors.title = 'Title must be at least 10 characters.';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must not exceed 200 characters.';
    }

    if (!formData.body.trim()) {
      newErrors.body = 'Question body is required.';
    } else if (formData.body.trim().length < 20) {
      newErrors.body = 'Please provide more detail (at least 20 characters).';
    } else if (formData.body.length > 5000) {
      newErrors.body = 'Body must not exceed 5000 characters.';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      setLoading(true);
      const data = await questionService.createQuestion(formData);
      toast.success('Question posted successfully!');
      router.push(`/questions/${data.id}`);
    } catch (error) {
      const responseData = error.response?.data;
      if (responseData) {
        const backendErrors = {};
        if (responseData.title) backendErrors.title = responseData.title[0];
        if (responseData.body)  backendErrors.body  = responseData.body[0];
        if (Object.keys(backendErrors).length > 0) {
          setErrors(backendErrors);
        } else {
          toast.error('Failed to post question. Please try again.');
        }
      } else {
        toast.error('Something went wrong. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-3xl mx-auto px-4 py-8">

        {/* Page Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 bg-blue-100 rounded-lg flex items-center justify-center">
              <PenSquare size={18} className="text-blue-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-800">Ask a Question</h1>
          </div>
          <p className="text-slate-500 text-sm ml-12">
            Get answers from verified IUBAT students
          </p>
        </div>

        {/* Tips Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex gap-3">
          <AlertCircle size={18} className="text-blue-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-800 mb-1">
              Tips for a good question
            </p>
            <ul className="text-xs text-blue-700 space-y-0.5 list-disc list-inside">
              <li>Be specific and clear about what you want to know</li>
              <li>Include relevant details about your situation</li>
              <li>Choose appropriate tags to reach the right audience</li>
            </ul>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">

            {/* Title */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-slate-700">
                Question Title <span className="text-red-500">*</span>
              </label>
              <input
                name="title"
                type="text"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g. What are the admission requirements for CSE department?"
                className={`
                  w-full px-3 py-2.5 text-sm rounded-lg border transition-colors duration-200
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                  ${errors.title
                    ? 'border-red-400 bg-red-50'
                    : 'border-slate-300 bg-white hover:border-slate-400'
                  }
                `}
              />
              <div className="flex items-center justify-between">
                {errors.title
                  ? <p className="text-xs text-red-500">{errors.title}</p>
                  : <span />
                }
                <span className={`text-xs ml-auto ${
                  formData.title.length > 180 ? 'text-red-500' : 'text-slate-400'
                }`}>
                  {formData.title.length}/200
                </span>
              </div>
            </div>

            {/* Body */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-slate-700">
                Question Details <span className="text-red-500">*</span>
              </label>
              <textarea
                name="body"
                value={formData.body}
                onChange={handleChange}
                placeholder="Describe your question in detail. Include any relevant context, what you've already tried, or specific information you need..."
                rows={7}
                className={`
                  w-full px-3 py-2.5 text-sm rounded-lg border transition-colors duration-200
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                  resize-none
                  ${errors.body
                    ? 'border-red-400 bg-red-50'
                    : 'border-slate-300 bg-white hover:border-slate-400'
                  }
                `}
              />
              <div className="flex items-center justify-between">
                {errors.body
                  ? <p className="text-xs text-red-500">{errors.body}</p>
                  : <span />
                }
                <span className={`text-xs ml-auto ${
                  formData.body.length > 4500 ? 'text-red-500' : 'text-slate-400'
                }`}>
                  {formData.body.length}/5000
                </span>
              </div>
            </div>

            {/* Tags */}
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-700 flex items-center gap-1.5">
                  <Tag size={14} className="text-slate-500" />
                  Tags
                  <span className="text-xs font-normal text-slate-400">(optional, max 5)</span>
                </label>
                {formData.tag_ids.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, tag_ids: [] }))}
                    className="text-xs text-slate-400 hover:text-red-500 transition-colors"
                  >
                    Clear all
                  </button>
                )}
              </div>

              {tagsLoading ? (
                <div className="flex items-center gap-2 py-2">
                  <Spinner size="sm" />
                  <span className="text-xs text-slate-400">Loading tags...</span>
                </div>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => {
                    const isSelected = formData.tag_ids.includes(tag.id);
                    return (
                      <button
                        key={tag.id}
                        type="button"
                        onClick={() => handleTagToggle(tag.id)}
                        className={`
                          flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                          border transition-all duration-150
                          ${isSelected
                            ? 'bg-blue-600 text-white border-blue-600'
                            : 'bg-white text-slate-600 border-slate-300 hover:border-blue-400 hover:text-blue-600'
                          }
                        `}
                      >
                        {tag.name}
                        {isSelected && <X size={11} />}
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Selected Tags Preview */}
              {formData.tag_ids.length > 0 && (
                <p className="text-xs text-slate-400">
                  {formData.tag_ids.length} tag{formData.tag_ids.length > 1 ? 's' : ''} selected
                </p>
              )}
            </div>

            {/* Submit */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => router.back()}
                className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
              >
                Cancel
              </button>
              <Button
                type="submit"
                variant="primary"
                size="md"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Spinner size="sm" />
                    Posting...
                  </>
                ) : (
                  <>
                    <PenSquare size={15} />
                    Post Question
                  </>
                )}
              </Button>
            </div>

          </form>
        </div>

      </div>
    </div>
  );
}