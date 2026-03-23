import api from '@/lib/axios';

export const questionService = {
  getAllQuestions: async (search = '', tag = '') => {
    const params = {};
    if (search) params.search = search;
    if (tag)    params.tag    = tag;
    const response = await api.get('/questions/', { params });
    return response.data;
  },

  getQuestionDetail: async (id) => {
    const response = await api.get(`/questions/${id}/`);
    return response.data;
  },

  createQuestion: async (data) => {
    const response = await api.post('/questions/', data);
    return response.data;
  },

  getAllTags: async () => {
    const response = await api.get('/questions/tags/');
    return response.data;
  },
};