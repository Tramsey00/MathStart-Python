// User policy: ordinary UI work does not start a verification cascade.
console.error('NOT_RUN: автоматические frontend-тесты временно отключены по решению пользователя от 25.10.2026.');
console.error('Отдельно порученный полный прогон: npm run test:full. Не запускать его без поручения.');
// A deferred run is not PASS and must not create a verification receipt.
process.exitCode = 2;
