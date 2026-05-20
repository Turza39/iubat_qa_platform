import api from '@/lib/axios'

export const questionService = {
  getAllQuestions: async (search = '', tag = '', skip = 0, limit = 20) => {
    const params = { skip, limit }
    if (search) params.search = search
    if (tag) params.tag = tag
    const response = await api.get('/questions/', { params })
    return response.data
  },

  getQuestionDetail: async (id, skip = 0, limit = 5) => {
    const params = { skip, limit }
    const response = await api.get(`/questions/${id}/`, { params })
    return response.data
  },

  createQuestion: async (data) => {
    const response = await api.post('/questions/', data)
    return response.data
  },

  getAllTags: async () => {
    const response = await api.get('/questions/tags/')
    return response.data
  },
}
