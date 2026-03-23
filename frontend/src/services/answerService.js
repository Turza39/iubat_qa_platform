import api from '@/lib/axios';

export const answerService = {
  postAnswer: async (questionId, data) => {
    const response = await api.post(`/answers/questions/${questionId}/`, data);
    return response.data;
  },
};