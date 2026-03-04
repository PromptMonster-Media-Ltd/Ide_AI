/**
 * export.ts — Export format type definitions.
 * @module types/export
 */

export const ExportFormat = {
  Markdown: 'md',
  Text: 'txt',
  PDF: 'pdf',
  DOCX: 'docx',
  ZIP: 'zip',
} as const

export type ExportFormat = (typeof ExportFormat)[keyof typeof ExportFormat]
