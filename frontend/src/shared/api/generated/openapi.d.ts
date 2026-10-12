// Generated from frozen canonical OpenAPI; do not edit.
export interface paths {
    "/api/v1/auth/csrf/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get csrf
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["get_csrf"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/register/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * register
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["register"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/login/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * login
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data.
         */
        post: operations["login"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/logout/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * logout
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data.
         */
        post: operations["logout"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/users/me/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get me
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["get_me"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * update me
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data.
         */
        patch: operations["update_me"];
        trace?: never;
    };
    "/api/v1/onboarding/complete/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * complete onboarding
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["complete_onboarding"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/grades/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list grades
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["list_grades"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/topics/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list topics
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["list_topics"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/topics/{slug}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get topic
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["get_topic"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/topics/{slug}/exercises/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list topic exercises
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["list_topic_exercises"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/exercises/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get exercise
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["get_exercise"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list attempts
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["list_attempts"];
        put?: never;
        /**
         * create attempt
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["create_attempt"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get attempt
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["get_attempt"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/{id}/draft/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /**
         * update draft
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        put: operations["update_draft"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/{id}/submit/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * submit attempt
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["submit_attempt"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/{id}/hints/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * request hint
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["request_hint"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/{id}/reveal/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * reveal attempt
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["reveal_attempt"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/attempts/{id}/abandon/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * abandon attempt
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["abandon_attempt"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/diagnostics/sessions/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * create diagnostics session
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["create_diagnostics_session"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/diagnostics/sessions/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get diagnostics session
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["get_diagnostics_session"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/diagnostics/sessions/{id}/next/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * next diagnostics session
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["next_diagnostics_session"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/diagnostics/sessions/{id}/finish/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * finish diagnostics session
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["finish_diagnostics_session"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/practice/sessions/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * create practice session
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["create_practice_session"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/practice/sessions/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * get practice session
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["get_practice_session"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/practice/sessions/{id}/next/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * next practice session
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["next_practice_session"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/practice/sessions/{id}/finish/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * finish practice session
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["finish_practice_session"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/progress/skills/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list progress skills
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["list_progress_skills"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/progress/topics/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list progress topics
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["list_progress_topics"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/progress/events/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list progress events
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["list_progress_events"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/progress/self-reports/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * create self report
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["create_self_report"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/ai/conversations/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * create conversation
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["create_conversation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/ai/conversations/{id}/messages/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * list messages
         * @description GET is read-only and creates no attempt/item/evidence. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers.
         */
        get: operations["list_messages"];
        put?: never;
        /**
         * create message
         * @description Authenticate as applicable, validate CSRF and public schema before acting. Raw text is untrusted data. Scope query to session owner; foreign/missing returns identical 404 with no current revision or identifiers. Replay persisted response before checking current revision/state for exact retry.
         */
        post: operations["create_message"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health/live/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * health live
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["health_live"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health/ready/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * health ready
         * @description GET is read-only and creates no attempt/item/evidence.
         */
        get: operations["health_ready"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        TopicReference: {
            id: string | number;
            slug: string;
        };
        ExerciseVersionIdentity: {
            /** Format: uuid */
            id: string;
            /** Format: uuid */
            exercise_id: string;
            version: number;
            contract_version: number;
            /** @enum {string} */
            status: "PUBLISHED" | "ARCHIVED";
        };
        InputField: {
            name: string;
            /** @enum {string} */
            input_type: "math_text" | "text" | "positive_integer" | "enum" | "object";
            required: boolean;
            label?: string;
        };
        InputSchema: {
            /** @constant */
            type: "object";
            fields: components["schemas"]["InputField"][];
        };
        StepSchema: {
            /** @constant */
            type: "ordered_steps";
            allowed_step_types: ("MATH_EXPRESSION" | "EQUATION_STATE" | "STRUCTURED_FIELDS" | "FINAL_STATEMENT")[];
            step_fields?: components["schemas"]["InputField"][];
            ordering?: {
                /** @constant */
                field: "step_no";
                /** @constant */
                direction: "ascending";
            };
            serialization?: {
                /** @enum {string} */
                step_type: "MATH_EXPRESSION" | "EQUATION_STATE" | "STRUCTURED_FIELDS" | "FINAL_STATEMENT";
                payload_fields: string[];
            }[];
        };
        RevealPolicy: {
            allowed: boolean;
            confirmation_required: boolean;
        };
        HintPolicy: {
            allowed: boolean;
            levels: number[];
        };
        PublicExerciseDTO: {
            /** Format: uuid */
            id: string;
            code: string;
            topic: components["schemas"]["TopicReference"];
            statement: string;
            /** @enum {string} */
            interaction_mode: "SELF_CHECK" | "FINAL_ANSWER" | "STEP_BY_STEP" | "STRUCTURED_SOLUTION";
            input_schema: components["schemas"]["InputSchema"] | null;
            step_schema: components["schemas"]["StepSchema"] | null;
            parser_profile: string | null;
            /** @enum {string} */
            difficulty: "easy" | "medium" | "hard";
            reveal_policy: components["schemas"]["RevealPolicy"];
            contract_version: number;
            version: number;
            exercise_version: components["schemas"]["ExerciseVersionIdentity"];
            difficulty_level: number;
            skill_codes: string[];
            allowed_help_actions: ("HINT" | "REVEAL")[];
            hint_policy?: components["schemas"]["HintPolicy"];
            presentation?: {
                submit_label?: string;
                submit_control?: boolean;
                reveal_control?: boolean;
                add_step_label?: string;
            };
        } & (unknown & unknown & unknown);
        /** @description Raw student data, never trusted instructions or correctness facts. Runtime validates against the frozen public input/step shape; no eval/exec. Dynamic subject fields are intentionally extensible. */
        UntrustedPayload: {
            [key: string]: unknown;
        };
        SolutionStepSubmission: {
            step_no: number;
            /** @enum {string} */
            step_type: "MATH_EXPRESSION" | "EQUATION_STATE" | "STRUCTURED_FIELDS" | "FINAL_STATEMENT";
            payload: components["schemas"]["UntrustedPayload"];
            raw_text: string | null;
        };
        SolutionStep: {
            step_no: number;
            /** @enum {string} */
            step_type: "MATH_EXPRESSION" | "EQUATION_STATE" | "STRUCTURED_FIELDS" | "FINAL_STATEMENT";
            payload: components["schemas"]["UntrustedPayload"];
            raw_text: string | null;
            /** Format: uuid */
            step_id: string;
            normalized_repr: string | null;
            /** @enum {string} */
            parse_status: "OK" | "UNSUPPORTED" | "INVALID" | "NOT_REQUIRED";
        };
        AttemptDraft: {
            payload: components["schemas"]["UntrustedPayload"];
            steps: components["schemas"]["SolutionStepSubmission"][];
        };
        Exposure: {
            /** Format: uuid */
            exercise_version_id: string;
            max_help_level: number;
            revealed_at: string | null;
            positive_credit_used: boolean;
        };
        Eligibility: {
            independent: boolean;
            positive_credit_eligible: boolean;
            /** @enum {string} */
            reason: "ELIGIBLE" | "HINT_EXPOSURE" | "REVEAL_EXPOSURE" | "ALREADY_CREDITED" | "UNSUPPORTED_INPUT" | "NOT_CORRECT" | "SELF_CHECK" | "PENDING";
        };
        AssessmentResult: {
            /** @enum {string} */
            outcome: "CORRECT" | "WRONG" | "UNSUPPORTED" | "INDETERMINATE";
            safe_feedback: string;
            first_error_step_id: string | null;
            misconception_code: string | null;
            /** @enum {string} */
            service_state: "NORMAL" | "DEGRADED";
            positive_credit_awarded: boolean;
        };
        Attempt: {
            /** Format: uuid */
            id: string;
            exercise_version: components["schemas"]["ExerciseVersionIdentity"];
            previous_attempt_id: string | null;
            /** @enum {string} */
            interaction_mode: "SELF_CHECK" | "FINAL_ANSWER" | "STEP_BY_STEP" | "STRUCTURED_SOLUTION";
            revision: number;
            /** @enum {string} */
            state: "STARTED" | "SUBMITTED" | "COMPLETED" | "REVIEWED" | "ABANDONED";
            draft: components["schemas"]["AttemptDraft"];
            steps: components["schemas"]["SolutionStep"][];
            snapshot_digest: string | null;
            operation_id: string | null;
            result: components["schemas"]["AssessmentResult"] | null;
            exposure: components["schemas"]["Exposure"];
            eligibility: components["schemas"]["Eligibility"];
            /** Format: date-time */
            created_at: string;
            submitted_at: string | null;
            completed_at: string | null;
        } & (unknown & unknown & unknown & unknown & unknown);
        CreateAttemptRequest: {
            /** Format: uuid */
            exercise_id: string;
            contract_version: number;
            version: number;
            previous_attempt_id?: string | null;
        };
        DraftUpdateRequest: {
            expected_revision: number;
            contract_version: number;
            draft: components["schemas"]["AttemptDraft"];
        };
        SubmitRequest: {
            expected_revision: number;
            contract_version: number;
        };
        HintRequest: {
            contract_version: number;
            level: number;
        };
        RevealRequest: {
            contract_version: number;
            /** @constant */
            confirm: true;
        };
        AbandonRequest: {
            expected_revision: number;
            contract_version: number;
        };
        HintResult: {
            /** Format: uuid */
            action_id: string;
            level: number;
            text: string;
            exposure: components["schemas"]["Exposure"];
            /** @enum {string} */
            service_state: "NORMAL" | "DEGRADED";
        };
        RevealResult: {
            /** Format: uuid */
            action_id: string;
            /** Format: date-time */
            reveal_recorded_at: string;
            revealed_content: {
                answer: string;
                steps: string[];
            };
            exposure: components["schemas"]["Exposure"];
            attempt: components["schemas"]["Attempt"];
        };
        Pagination: {
            next_cursor: string | null;
            page_size: number;
            has_more: boolean;
        };
        Meta: {
            /** Format: uuid */
            request_id: string;
            version?: string;
            pagination?: components["schemas"]["Pagination"];
        };
        SuccessEnvelope: {
            data: unknown;
            meta: components["schemas"]["Meta"];
        };
        ErrorEnvelope: {
            error: {
                /** @enum {string} */
                code: "INVALID_REQUEST" | "LIMIT_EXCEEDED" | "AUTHENTICATION_REQUIRED" | "CSRF_FAILED" | "FORBIDDEN" | "NOT_FOUND" | "REVISION_CONFLICT" | "IDEMPOTENCY_CONFLICT" | "VERSION_CONFLICT" | "STATE_CONFLICT" | "RATE_LIMITED" | "SERVICE_UNAVAILABLE";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        RevisionConflict: {
            error: {
                /** @constant */
                code: "REVISION_CONFLICT";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
                current_revision: number;
                reload_url: string;
            };
        };
        IdempotencyConflict: {
            error: {
                /** @constant */
                code: "IDEMPOTENCY_CONFLICT";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        ConflictEnvelope: components["schemas"]["RevisionConflict"] | components["schemas"]["IdempotencyConflict"] | {
            error: {
                /** @enum {string} */
                code: "VERSION_CONFLICT" | "STATE_CONFLICT";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        BadRequestError: {
            error: {
                /** @enum {string} */
                code: "INVALID_REQUEST" | "LIMIT_EXCEEDED";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        AuthenticationError: {
            error: {
                /** @enum {string} */
                code: "AUTHENTICATION_REQUIRED";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        ForbiddenError: {
            error: {
                /** @enum {string} */
                code: "CSRF_FAILED" | "FORBIDDEN";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        NotFoundError: {
            error: {
                /** @enum {string} */
                code: "NOT_FOUND";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        RateLimitError: {
            error: {
                /** @enum {string} */
                code: "RATE_LIMITED";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        UnavailableError: {
            error: {
                /** @enum {string} */
                code: "SERVICE_UNAVAILABLE";
                message: string;
                field_errors: {
                    [key: string]: string[];
                };
                retryable: boolean;
                /** Format: uuid */
                request_id: string;
            };
        };
        Grade: {
            id: number | string;
            number: number;
            title: string;
        };
        Topic: {
            id: string | number;
            slug: string;
            title: string;
            parent: components["schemas"]["TopicReference"] | null;
            theory: string;
        };
        User: {
            id: number | string;
            username: string;
            selected_grade_id: (number | string) | null;
            onboarding_mode: ("START_ZERO" | "DIAGNOSTIC" | "SELF_REPORT") | null;
            onboarding_complete: boolean;
        };
        CsrfToken: {
            csrf_token: string;
        };
        RegisterRequest: {
            username: string;
            password: string;
            /** Format: email */
            email?: string;
        };
        LoginRequest: {
            username: string;
            password: string;
        };
        EmptyRequest: Record<string, never>;
        Acknowledgement: {
            completed: boolean;
        };
        ProfileUpdateRequest: {
            selected_grade_id?: number | string;
        };
        OnboardingRequest: {
            selected_grade_id: number | string;
            /** @enum {string} */
            mode: "START_ZERO" | "DIAGNOSTIC" | "SELF_REPORT";
        };
        DiagnosticCreateRequest: {
            skill_codes: string[];
        };
        PracticeCreateRequest: {
            target_skill_code: string;
            origin_topic: components["schemas"]["TopicReference"];
        };
        NextRequest: {
            current_item_id: string | null;
            /** @enum {string} */
            action: "ADVANCE" | "SKIP";
        };
        FinishRequest: {
            /** @enum {string} */
            reason: "SUCCESS" | "LIMIT_REACHED" | "NO_CANDIDATE" | "ABANDONED";
        };
        SessionItem: {
            /** Format: uuid */
            id: string;
            position: number;
            exercise: components["schemas"]["PublicExerciseDTO"];
            /** Format: uuid */
            attempt_id: string;
        };
        ReturnRoute: {
            topic: components["schemas"]["TopicReference"] | null;
            url: string;
            /** @enum {string} */
            reason: "ORIGIN" | "PUBLISHED_PARENT" | "CATALOGUE";
        };
        DiagnosticSession: {
            /** Format: uuid */
            id: string;
            /** @enum {string} */
            state: "ACTIVE" | "COMPLETED" | "ABANDONED";
            policy_version: string;
            current_item: components["schemas"]["SessionItem"] | null;
            item_count: number;
            exit_reason: ("SUCCESS" | "LIMIT_REACHED" | "NO_CANDIDATE" | "ABANDONED") | null;
            operation_id: string | null;
            /** Format: date-time */
            created_at: string;
            skill_itinerary: string[];
            start_zero_available: boolean;
        };
        PracticeSession: {
            /** Format: uuid */
            id: string;
            /** @enum {string} */
            state: "ACTIVE" | "COMPLETED" | "ABANDONED";
            policy_version: string;
            current_item: components["schemas"]["SessionItem"] | null;
            item_count: number;
            exit_reason: ("SUCCESS" | "LIMIT_REACHED" | "NO_CANDIDATE" | "ABANDONED") | null;
            operation_id: string | null;
            /** Format: date-time */
            created_at: string;
            target_skill_code: string;
            origin_topic: components["schemas"]["TopicReference"];
            return_route: components["schemas"]["ReturnRoute"];
            /** @enum {string} */
            selection_reason: "WEAK_PREREQUISITE" | "LOW_CONFIDENCE_DIAGNOSTIC" | "TARGET" | "REPEAT_POOL_EXHAUSTED" | "NO_CANDIDATE";
            independent_correct_streak: number;
        };
        SkillProgress: {
            skill_code: string;
            mastery: number;
            confidence: number;
            evidence_count: number;
            /** @enum {string} */
            status: "NOT_STARTED" | "LEARNING" | "WEAK" | "MASTERED";
            last_updated: string | null;
            reducer_version: string;
            self_reported: boolean;
        };
        TopicProgress: {
            topic: components["schemas"]["TopicReference"];
            mastery: number;
            confidence: number;
            assessed_skill_count: number;
            total_skill_count: number;
        };
        ProgressEvent: {
            /** Format: uuid */
            event_id: string;
            skill_code: string;
            /** @enum {string} */
            event_kind: "SELF_REPORTED_KNOWN" | "CORRECT_FIRST_TRY" | "CORRECT_AFTER_HINT" | "WRONG_ATTEMPT" | "MISCONCEPTION_DETECTED" | "ANSWER_REVEALED" | "DIAGNOSTIC_CORRECT" | "DIAGNOSTIC_WRONG";
            /** Format: date-time */
            occurred_at: string;
            attempt_id: string | null;
            evidence_ref: string;
            policy_version: string;
        };
        SelfReportRequest: {
            skill_codes: string[];
        };
        SelfReportResult: {
            accepted_skill_codes: string[];
            already_reported_skill_codes: string[];
        };
        ConversationRequest: {
            topic: components["schemas"]["TopicReference"];
            exercise_version_id: string | null;
            attempt_id: string | null;
        };
        Conversation: {
            /** Format: uuid */
            id: string;
            topic: components["schemas"]["TopicReference"];
            exercise_version_id: string | null;
            /** Format: date-time */
            created_at: string;
        };
        MessageRequest: {
            text: string;
        };
        TutorMessage: {
            /** Format: uuid */
            id: string;
            /** Format: uuid */
            conversation_id: string;
            /** @enum {string} */
            role: "USER" | "ASSISTANT";
            text: string;
            /** Format: date-time */
            created_at: string;
            /** @enum {string} */
            service_state: "NORMAL" | "DEGRADED";
            help_action_id: string | null;
            allowed_followup_ids: string[];
        };
        HealthLive: {
            /** @constant */
            status: "LIVE";
        };
        HealthReady: {
            /** @enum {string} */
            status: "READY" | "NOT_READY";
            /** @enum {string} */
            database: "AVAILABLE" | "UNAVAILABLE";
            /** @enum {string} */
            configuration: "VALID" | "INVALID";
            /** @enum {string} */
            provider: "AVAILABLE" | "DEGRADED" | "UNAVAILABLE";
        };
        PublicExerciseDTOResponse: {
            data: components["schemas"]["PublicExerciseDTO"];
            meta: components["schemas"]["Meta"];
        };
        AttemptResponse: {
            data: components["schemas"]["Attempt"];
            meta: components["schemas"]["Meta"];
        };
        HintResultResponse: {
            data: components["schemas"]["HintResult"];
            meta: components["schemas"]["Meta"];
        };
        RevealResultResponse: {
            data: components["schemas"]["RevealResult"];
            meta: components["schemas"]["Meta"];
        };
        UserResponse: {
            data: components["schemas"]["User"];
            meta: components["schemas"]["Meta"];
        };
        CsrfTokenResponse: {
            data: components["schemas"]["CsrfToken"];
            meta: components["schemas"]["Meta"];
        };
        AcknowledgementResponse: {
            data: components["schemas"]["Acknowledgement"];
            meta: components["schemas"]["Meta"];
        };
        DiagnosticSessionResponse: {
            data: components["schemas"]["DiagnosticSession"];
            meta: components["schemas"]["Meta"];
        };
        PracticeSessionResponse: {
            data: components["schemas"]["PracticeSession"];
            meta: components["schemas"]["Meta"];
        };
        SelfReportResultResponse: {
            data: components["schemas"]["SelfReportResult"];
            meta: components["schemas"]["Meta"];
        };
        ConversationResponse: {
            data: components["schemas"]["Conversation"];
            meta: components["schemas"]["Meta"];
        };
        TutorMessageResponse: {
            data: components["schemas"]["TutorMessage"];
            meta: components["schemas"]["Meta"];
        };
        HealthLiveResponse: {
            data: components["schemas"]["HealthLive"];
            meta: components["schemas"]["Meta"];
        };
        HealthReadyResponse: {
            data: components["schemas"]["HealthReady"];
            meta: components["schemas"]["Meta"];
        };
        TopicResponse: {
            data: components["schemas"]["Topic"];
            meta: components["schemas"]["Meta"];
        };
        GradeListResponse: {
            data: components["schemas"]["Grade"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        TopicListResponse: {
            data: components["schemas"]["Topic"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        PublicExerciseDTOListResponse: {
            data: components["schemas"]["PublicExerciseDTO"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        AttemptListResponse: {
            data: components["schemas"]["Attempt"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        SkillProgressListResponse: {
            data: components["schemas"]["SkillProgress"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        TopicProgressListResponse: {
            data: components["schemas"]["TopicProgress"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        ProgressEventListResponse: {
            data: components["schemas"]["ProgressEvent"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        TutorMessageListResponse: {
            data: components["schemas"]["TutorMessage"][];
            meta: {
                /** Format: uuid */
                request_id: string;
                version?: string;
                pagination: components["schemas"]["Pagination"];
            };
        };
        PendingAttemptResponse: components["schemas"]["AttemptResponse"] & {
            data?: {
                /** @constant */
                state?: "SUBMITTED";
                /** Format: uuid */
                operation_id?: string;
            };
        };
    };
    responses: {
        /** @description Malformed/schema/limit error; never strong misconception evidence. */
        400: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["BadRequestError"];
            };
        };
        /** @description Authentication required, independent of object existence. */
        401: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["AuthenticationError"];
            };
        };
        /** @description CSRF failed or forbidden role; no owner-secret details. */
        403: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["ForbiddenError"];
            };
        };
        /** @description Missing OR foreign owned object: identical generic response. */
        404: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["NotFoundError"];
            };
        };
        /** @description Revision, version, idempotency or state conflict. */
        409: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["ConflictEnvelope"];
            };
        };
        /** @description Rate limited. */
        429: {
            headers: {
                /** @description Seconds until safe retry. */
                "Retry-After": number;
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["RateLimitError"];
            };
        };
        /** @description Operation cannot safely finish; reconcile canonical state before retry. */
        503: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/json": components["schemas"]["UnavailableError"];
            };
        };
    };
    parameters: {
        ResourceId: string;
        TopicSlug: string;
        /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
        Cursor: string;
        PageSize: number;
        /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
        Csrf: string;
        /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
        IdempotencyKey: string;
    };
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    get_csrf: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CsrfTokenResponse"];
                };
            };
            400: components["responses"]["400"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    register: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RegisterRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
            400: components["responses"]["400"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    login: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LoginRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    logout: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EmptyRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AcknowledgementResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    get_me: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    update_me: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProfileUpdateRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    complete_onboarding: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OnboardingRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_grades: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GradeListResponse"];
                };
            };
            400: components["responses"]["400"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_topics: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TopicListResponse"];
                };
            };
            400: components["responses"]["400"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    get_topic: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                slug: components["parameters"]["TopicSlug"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TopicResponse"];
                };
            };
            400: components["responses"]["400"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_topic_exercises: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path: {
                slug: components["parameters"]["TopicSlug"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PublicExerciseDTOListResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    get_exercise: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PublicExerciseDTOResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_attempts: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttemptListResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    create_attempt: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CreateAttemptRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttemptResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    get_attempt: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttemptResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    update_draft: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DraftUpdateRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttemptResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    submit_attempt: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SubmitRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttemptResponse"];
                };
            };
            /** @description Immutable SUBMITTED operation; poll canonical GET attempt at 1/2/4 seconds then manual retry with original key. No queue promised. */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PendingAttemptResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    request_hint: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HintRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HintResultResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    reveal_attempt: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RevealRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RevealResultResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    abandon_attempt: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AbandonRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttemptResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    create_diagnostics_session: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DiagnosticCreateRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DiagnosticSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    get_diagnostics_session: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DiagnosticSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    next_diagnostics_session: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["NextRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DiagnosticSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    finish_diagnostics_session: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["FinishRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DiagnosticSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    create_practice_session: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PracticeCreateRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PracticeSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    get_practice_session: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PracticeSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    next_practice_session: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["NextRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PracticeSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    finish_practice_session: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["FinishRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PracticeSessionResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_progress_skills: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SkillProgressListResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_progress_topics: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TopicProgressListResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_progress_events: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProgressEventListResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    create_self_report: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SelfReportRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SelfReportResultResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    create_conversation: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationRequest"];
            };
        };
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    list_messages: {
        parameters: {
            query?: {
                /** @description Opaque owner/filter-bound cursor; stable ascending (created_at,id), no offset. */
                cursor?: components["parameters"]["Cursor"];
                page_size?: components["parameters"]["PageSize"];
            };
            header?: never;
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TutorMessageListResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    create_message: {
        parameters: {
            query?: never;
            header: {
                /** @description Get token using auth/csrf/; cookie/token match required on every mutation, including login/register. Session rotates at login. */
                "X-CSRFToken": components["parameters"]["Csrf"];
                /** @description Owner + operation + key scopes a receipt >=7 days. Same digest replays persisted status/body/operation; different digest returns 409. Permanent domain uniqueness survives expiry. */
                "Idempotency-Key": components["parameters"]["IdempotencyKey"];
            };
            path: {
                id: components["parameters"]["ResourceId"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MessageRequest"];
            };
        };
        responses: {
            /** @description Safe persisted fallback message with service_state DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TutorMessageResponse"];
                };
            };
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TutorMessageResponse"];
                };
            };
            400: components["responses"]["400"];
            401: components["responses"]["401"];
            403: components["responses"]["403"];
            404: components["responses"]["404"];
            409: components["responses"]["409"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    health_live: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HealthLiveResponse"];
                };
            };
            400: components["responses"]["400"];
            429: components["responses"]["429"];
            503: components["responses"]["503"];
        };
    };
    health_ready: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Persisted successful result; UNSUPPORTED remains business data and safe fallback is DEGRADED. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HealthReadyResponse"];
                };
            };
            400: components["responses"]["400"];
            429: components["responses"]["429"];
            /** @description Necessary DB/config unavailable; safe health fields only. Provider failure with functioning core fallback returns READY/DEGRADED 200. */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HealthReadyResponse"];
                };
            };
        };
    };
}
