"""
URL routing configuration for FastAPI backend.

Unlike Django, FastAPI uses decorators and routers for URL routing.
This file serves as a reference documentation of all API endpoints.

All endpoints are registered in main.py via router.include_router()
"""

# API Route Prefixes
API_PREFIX = "/api"

# Endpoint Groups
USERS_PREFIX = f"{API_PREFIX}/users"
QUESTIONS_PREFIX = f"{API_PREFIX}/questions"
ANSWERS_PREFIX = f"{API_PREFIX}/answers"
VOTES_PREFIX = f"{API_PREFIX}/votes"

# Users Endpoints
# POST   /api/users/register/             - Register new user
# POST   /api/users/login/                - Login user
# POST   /api/users/logout/               - Logout user
# GET    /api/users/me/                   - Get current user
# GET    /api/users/{user_id}/            - Get user profile
# PUT    /api/users/{user_id}/            - Update user profile
# POST   /api/users/{user_id}/verify/     - Request verification
# GET    /api/users/{user_id}/verify/     - Check verification status

# Questions Endpoints
# GET    /api/questions/                  - List all questions
# POST   /api/questions/                  - Create new question
# GET    /api/questions/{question_id}/    - Get question details
# PUT    /api/questions/{question_id}/    - Update question
# DELETE /api/questions/{question_id}/    - Delete question

# Answers Endpoints
# GET    /api/answers/questions/{question_id}/       - Get answers for a question
# POST   /api/answers/questions/{question_id}/       - Create answer (verified users only)
# PUT    /api/answers/questions/{question_id}/       - Update answer (author only)
# DELETE /api/answers/questions/{question_id}/       - Delete answer (author only)

# Votes Endpoints
# POST   /api/votes/answers/{answer_id}/  - Upvote answer
# DELETE /api/votes/answers/{answer_id}/  - Remove vote on answer
# POST   /api/votes/questions/{question_id}/ - Upvote question
# DELETE /api/votes/questions/{question_id}/ - Remove vote on question


# Router imports (for reference)
# from routes.answers import router as answers_router
# from routes.users import router as users_router
# from routes.questions import router as questions_router
# from routes.votes import router as votes_router

# Include routers in main.py:
# app.include_router(users_router)
# app.include_router(questions_router)
# app.include_router(answers_router)
# app.include_router(votes_router)


"""
Authentication:
All endpoints requiring authentication use JWT tokens in the Authorization header:
    Authorization: Bearer <token>

Permission Classes (equivalent to Django):
- IsAuthenticated: User must be logged in
- IsVerified: User must be logged in AND verified
- IsAuthorOrReadOnly: Can read publicly, but must be author to edit
- IsAdminOrReadOnly: Can read publicly, but must be admin to edit

Error Responses:
401 Unauthorized: Missing or invalid authentication
403 Forbidden: Insufficient permissions
404 Not Found: Resource not found
400 Bad Request: Invalid request data
500 Internal Server Error: Server error

Response Format:
All endpoints return JSON responses with consistent structure:
    {
        "data": {...},      # Successful response data
        "error": null,      # Error message if any
        "status": "success" # "success" or "error"
    }
"""
