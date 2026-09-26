# MS6-I01: Low-fidelity wireframes

All sheets are deliberately low-fidelity. Boxes indicate information hierarchy, controls, state messages and transitions; they do not specify visual style, design tokens, icons, colours, fonts, spacing scale, final wording, or runtime behavior. Implementation verification uses 360, 768, and 1440 px viewports. A separate 768 px sheet is not required for I01; mobile and desktop sheets define the two compositions, and the intermediate viewport must be checked during implementation.

| Surface | Desktop | Mobile | Scenario coverage |
| --- | --- | --- | --- |
| Onboarding | [SVG](wireframes/onboarding-desktop.svg) | [SVG](wireframes/onboarding-mobile.svg) | SC-01 |
| Exercise | [SVG](wireframes/exercise-desktop.svg) | [SVG](wireframes/exercise-mobile.svg) | SC-03--SC-06, SC-08 |
| Progress | [SVG](wireframes/progress-desktop.svg) | [SVG](wireframes/progress-mobile.svg) | SC-02, SC-04, SC-08 |
| Practice | [SVG](wireframes/practice-desktop.svg) | [SVG](wireframes/practice-mobile.svg) | SC-04, SC-07, SC-08 |

## Reading rule

Bracketed English state names, where present, are developer annotations rather than learner-visible copy. Learner-visible strings inside the interface are Russian. Arrows identify a user action or a server-confirmed transition. Any actual UI implementation must reconcile its labels and state machine with accepted R02/R03 fixtures and the API-needs review.
