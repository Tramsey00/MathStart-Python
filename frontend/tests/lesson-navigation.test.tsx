import { render, screen, cleanup } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import { LessonNavigation } from '../src/shared/lesson/lesson-components';

afterEach(cleanup);
const topic = { slug: 'topic', title: 'Тема', order: 1 };
it.each([
  [null, topic, null, 'Следующая тема'],
  [topic, null, 'Предыдущая тема', null],
  [topic, { ...topic, boundary: 'section' as const }, 'Предыдущая тема', 'Следующий раздел'],
  [{ ...topic, boundary: 'section' as const }, topic, 'Предыдущий раздел', 'Следующая тема'],
])('uses the requested section/subject boundary labels', (previous, next, left, right) => {
  render(<LessonNavigation previous={previous} next={next} href={() => '/topic/'} catalogueHref="/section/"/>);
  if (left) expect(screen.getByRole('link', { name: `${left}: Тема` })).toBeTruthy();
  else expect(document.querySelector('.lesson-previous')).toBeNull();
  if (right) expect(screen.getByRole('link', { name: `${right}: Тема` })).toBeTruthy();
  else expect(document.querySelector('.lesson-next')).toBeNull();
  expect(screen.getByRole('link', { name: 'Все темы раздела' }).getAttribute('href')).toBe('/section/');
});
