// Generated from canonical OpenAPI + R02 inventory. Only eight baseline operations.
import PublicExerciseDTO from "./PublicExerciseDTO.mjs";
import CsrfTokenResponse from "./CsrfTokenResponse.mjs";
import BadRequestError from "./BadRequestError.mjs";
import RateLimitError from "./RateLimitError.mjs";
import UnavailableError from "./UnavailableError.mjs";
import RegisterRequest from "./RegisterRequest.mjs";
import UserResponse from "./UserResponse.mjs";
import ForbiddenError from "./ForbiddenError.mjs";
import ConflictEnvelope from "./ConflictEnvelope.mjs";
import LoginRequest from "./LoginRequest.mjs";
import AuthenticationError from "./AuthenticationError.mjs";
import EmptyRequest from "./EmptyRequest.mjs";
import AcknowledgementResponse from "./AcknowledgementResponse.mjs";
import ProfileUpdateRequest from "./ProfileUpdateRequest.mjs";
import OnboardingRequest from "./OnboardingRequest.mjs";
import GradeListResponse from "./GradeListResponse.mjs";
export const identityOperations = {
  "get_csrf": {
    "path": "/api/v1/auth/csrf/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "success": 200,
    "responses": {
      "200": CsrfTokenResponse,
      "400": BadRequestError,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "register": {
    "path": "/api/v1/auth/register/",
    "method": "POST",
    "receipt": true,
    "request": RegisterRequest,
    "success": 201,
    "responses": {
      "201": UserResponse,
      "400": BadRequestError,
      "403": ForbiddenError,
      "409": ConflictEnvelope,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "login": {
    "path": "/api/v1/auth/login/",
    "method": "POST",
    "receipt": false,
    "request": LoginRequest,
    "success": 200,
    "responses": {
      "200": UserResponse,
      "400": BadRequestError,
      "401": AuthenticationError,
      "403": ForbiddenError,
      "409": ConflictEnvelope,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "logout": {
    "path": "/api/v1/auth/logout/",
    "method": "POST",
    "receipt": false,
    "request": EmptyRequest,
    "success": 200,
    "responses": {
      "200": AcknowledgementResponse,
      "400": BadRequestError,
      "401": AuthenticationError,
      "403": ForbiddenError,
      "409": ConflictEnvelope,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "get_me": {
    "path": "/api/v1/users/me/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "success": 200,
    "responses": {
      "200": UserResponse,
      "400": BadRequestError,
      "401": AuthenticationError,
      "403": ForbiddenError,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "update_me": {
    "path": "/api/v1/users/me/",
    "method": "PATCH",
    "receipt": false,
    "request": ProfileUpdateRequest,
    "success": 200,
    "responses": {
      "200": UserResponse,
      "400": BadRequestError,
      "401": AuthenticationError,
      "403": ForbiddenError,
      "409": ConflictEnvelope,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "complete_onboarding": {
    "path": "/api/v1/onboarding/complete/",
    "method": "POST",
    "receipt": true,
    "request": OnboardingRequest,
    "success": 200,
    "responses": {
      "200": UserResponse,
      "400": BadRequestError,
      "401": AuthenticationError,
      "403": ForbiddenError,
      "409": ConflictEnvelope,
      "429": RateLimitError,
      "503": UnavailableError
    }
  },
  "list_grades": {
    "path": "/api/v1/grades/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "success": 200,
    "responses": {
      "200": GradeListResponse,
      "400": BadRequestError,
      "429": RateLimitError,
      "503": UnavailableError
    }
  }
} as const;
