import api from '@/lib/axios';

export const voteService = {
  toggleQuestionVote: async (questionId) => {
    const response = await api.post(`/votes/questions/${questionId}/`);
    return response.data;
  },

  toggleAnswerVote: async (answerId) => {
    const response = await api.post(`/votes/answers/${answerId}/`);
    return response.data;
  },
};