# MS6-I01: Screen map and transitions

```mermaid
flowchart TD
  subgraph ENTRY[Entry and onboarding]
    G[Guest catalogue / topic]
    A[Register or sign in]
    P[Profile and grade]
    O{Onboarding choice}
    Z[Start from beginning]
    D[Diagnostic]
    S[Familiar topics: self-assessment]
    C[Student catalogue]
    DASH[Student dashboard]
    RESUME[Continue learning]
    G --> A --> P --> O
    O --> Z --> C
    O --> D --> C
    O --> S --> C
    A -->|returning student| DASH
    C --> DASH
    DASH --> RESUME
  end

  subgraph WORK[Topic and personal exercise work]
    T[Topic theory]
    AG{Authenticated?}
    E{Exercise mode}
    SC[SELF_CHECK: unassessed view; no scored submit]
    FA[FINAL_ANSWER]
    SB[STEP_BY_STEP]
    SS[STRUCTURED_SOLUTION]
    R[Server result / safe feedback]
    G --> T
    C --> T
    RESUME -->|resume selected learning context| T
    T --> AG
    AG -->|no: sign in first| A
    AG -->|yes| E
    E --> SC
    SC -->|return without assessment| T
    E --> FA --> R
    E --> SB --> R
    E --> SS --> R
  end

  subgraph HELP[Help and reveal during work]
    H[Bounded hint]
    CONT[Continue solving]
    RC{Reveal separately selected and confirmed?}
    RV[Revealed for user + exercise version]
    E --> H
    H --> CONT --> E
    E --> RC
    H --> RC
    RC -->|yes; server records exposure| RV
    RC -->|cancel; assessed exercise source| E
    RC -->|cancel; self-check source| SC
    SC -->|explicit reveal if allowed| RC
    RV -->|return to self-check when that is the source| SC
    TU[Tutor panel]
    LH[Prepared local hint / retry state]
    E --> TU
    TU -->|provider outage| LH --> E
  end

  subgraph FOLLOWUP[Progress and follow-up]
    PR[Progress / history]
    SK[Skills list / map]
    AP{Practice or diagnostic needed?}
    PS[Practice session]
    RT[Return to origin topic]
    R --> PR
    DASH --> PR
    PR --> SK
    SK -->|selected topic| T
    R --> AP
    AP -->|practice| PS --> RT --> T
    AP -->|diagnostic| D
    AP -->|not needed| T
  end
```

## Transition rules

- `Topic -> Exercise` keeps the topic reference and exposes only the public exercise contract.
- `Topic -> personal Exercise` crosses an explicit auth gate. Guests keep catalogue/theory access but cannot start personal attempt flows.
- `Exercise -> Result` is server-authoritative; processing/retry never makes a second progress claim. A correction after completed evaluation starts a new attempt.
- `SELF_CHECK` is a separate unassessed view with no scored submit or assessment-result transition. Explicit reveal (when allowed) and return are available; neither viewing nor revealing it increases mastery. Cancelling reveal returns to the originating view.
- The authenticated dashboard provides a continue-learning entry and access to progress/history and the skills list/map. These are conceptual surfaces, not route or API names.
- `Hint -> Continue` is the ordinary path. Reveal remains a separately selected and confirmed action; exposure persists for the user + exercise version across attempts.
- `Result -> Practice` states a target/reason and preserves an origin-topic reference; student may leave at any time.
- `Result -> Topic` remains available when no practice or diagnostic is needed.
- `Tutor/help` is available while the learner works, and `Tutor outage -> Prepared hint` keeps deterministic validation available while clearly labelling the unavailable service.
- A guest may traverse catalogue/theory but cannot open personal progress, history, diagnostic, or persistent attempt flows.

## Existing versus future surfaces

Existing Content catalogue/topic routes remain the host for theory. The account, exercise, progress, diagnostic/practice and Tutor screens are future surfaces described here for I02--I14; their route names and API endpoints are intentionally not invented by I01.
