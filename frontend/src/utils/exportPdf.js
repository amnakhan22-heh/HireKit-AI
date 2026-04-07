export function exportKitAsPdf(elementId) {
  const element = document.getElementById(elementId);
  if (!element) {
    throw new Error(`Element with id "${elementId}" not found`);
  }

  const originalTitle = document.title;
  document.title = 'HireKit AI';
  window.print();
  document.title = originalTitle;
}
