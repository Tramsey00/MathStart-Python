// Generated canonical wire types. No fixtures.
import type {components} from './openapi';
export interface IdentityContracts {
get_csrf: {request: never; response: components['schemas']['CsrfTokenResponse']};
register: {request: components['schemas']['RegisterRequest']; response: components['schemas']['UserResponse']};
login: {request: components['schemas']['LoginRequest']; response: components['schemas']['UserResponse']};
logout: {request: components['schemas']['EmptyRequest']; response: components['schemas']['AcknowledgementResponse']};
get_me: {request: never; response: components['schemas']['UserResponse']};
update_me: {request: components['schemas']['ProfileUpdateRequest']; response: components['schemas']['UserResponse']};
complete_onboarding: {request: components['schemas']['OnboardingRequest']; response: components['schemas']['UserResponse']};
list_grades: {request: never; response: components['schemas']['GradeListResponse']};
}
