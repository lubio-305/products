// 自架的極簡線條圖示組，20x20 viewBox，用 currentColor 繼承文字顏色，
// 用法：icon("plus", {size: 16})

const ICON_PATHS = {
  plus: '<line x1="10" y1="4" x2="10" y2="16"/><line x1="4" y1="10" x2="16" y2="10"/>',
  edit: '<path d="M4 16l1-4 9-9 3 3-9 9z"/><line x1="12.5" y1="4.5" x2="15.5" y2="7.5"/>',
  upload:
    '<polyline points="6,9 10,5 14,9"/><line x1="10" y1="5" x2="10" y2="15"/><path d="M4 15v2a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-2"/>',
  download:
    '<polyline points="6,10 10,14 14,10"/><line x1="10" y1="4" x2="10" y2="14"/><path d="M4 15v2a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-2"/>',
  user: '<circle cx="10" cy="7" r="3"/><path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6"/>',
  bell: '<path d="M6 8a4 4 0 0 1 8 0c0 4 1.5 5 1.5 5h-11S6 12 6 8z"/><path d="M8.5 16a1.5 1.5 0 0 0 3 0"/>',
  handover:
    '<polyline points="6,5 3,8 6,11"/><line x1="3" y1="8" x2="15" y2="8"/><polyline points="14,9 17,12 14,15"/><line x1="5" y1="12" x2="17" y2="12"/>',
  history: '<circle cx="10" cy="10" r="7"/><polyline points="10,6 10,10 13,12"/>',
  filter: '<path d="M3 4h14l-5 6v5l-4 2v-7z"/>',
  logout:
    '<path d="M8 4H4v12h4"/><line x1="17" y1="10" x2="8" y2="10"/><polyline points="13,6 17,10 13,14"/>',
  folder: '<path d="M3 6a1 1 0 0 1 1-1h4l2 2h6a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>',
  check: '<polyline points="4,10 8,14 16,5"/>',
  doc: '<path d="M6 3h6l3 3v11H6z"/><line x1="8" y1="9" x2="14" y2="9"/><line x1="8" y1="12" x2="14" y2="12"/>',
  warning:
    '<path d="M10 3l8 14H2z"/><line x1="10" y1="8" x2="10" y2="12"/><circle cx="10" cy="14.5" r="0.75" fill="currentColor" stroke="none"/>',
  users:
    '<circle cx="7" cy="7" r="2.5"/><path d="M2.5 17c0-2.8 2-5 4.5-5s4.5 2.2 4.5 5"/><circle cx="14" cy="8" r="2"/><path d="M11.5 17c0-2.3 1.6-4 3.5-4s3.5 1.7 3.5 4"/>',
};

function icon(name, { size = 16, className = "" } = {}) {
  const paths = ICON_PATHS[name];
  if (!paths) return "";
  return `<svg class="icon ${className}" width="${size}" height="${size}" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;
}
