"""Read-only, database-independent search over the published topic catalogue."""

from content.models import ContentPage


def catalogue_context(params):
    # Avoid retrieving lesson HTML/CSS/JS for this small title catalogue.
    topics = list(ContentPage.objects.filter(
        is_published=True, page_type=ContentPage.PageType.TOPIC,
    ).select_related("grade", "subject", "section").only(
        "title", "slug", "page_type", "grade", "subject", "section",
    ).order_by(
        "grade__order", "grade_id", "subject__order", "subject_id",
        "section__order", "section_id", "order", "title", "pk",
    ))
    grades = {topic.grade.slug: topic.grade for topic in topics if topic.grade}
    grade = params.get("grade", "")
    if grade not in grades:
        grade = ""
    available = [topic for topic in topics
                 if not grade or (topic.grade and topic.grade.slug == grade)]
    # A subject slug denotes the same subject across grades; IDs are grade-local.
    subjects = {}
    for topic in available:
        if topic.subject:
            subjects.setdefault(topic.subject.slug, topic.subject)
    subject = params.get("subject", "")
    if subject not in subjects:
        subject = ""
    query = params.get("q", "").strip()
    needle = query.casefold()
    matches = [topic for topic in available
               if (not subject or (topic.subject and topic.subject.slug == subject))
               and needle in topic.title.casefold()]
    return {
        "catalogue_topics": matches,
        "catalogue_grades": list(grades.values()),
        "catalogue_subjects": list(subjects.values()),
        "catalogue_grade": grade,
        "catalogue_subject": subject,
        "catalogue_query": query,
        "catalogue_count": len(matches),
    }
