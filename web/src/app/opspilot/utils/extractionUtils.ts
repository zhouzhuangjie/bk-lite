export const getDefaultExtractionMethod = (extension: string): string => {
  const extensionMapping: Record<string, string> = {
    docx: 'chapter',
    pdf: 'fullText',
    xlsx: 'worksheet',
    csv: 'worksheet',
    txt: 'fullText',
    md: 'fullText',
    link: 'fullText',
    text: 'fullText',
  };
  return extensionMapping[extension] || 'fullText';
};


export const getExtractionMethodMap = (extension: string): string => {
  const extensionMapping: Record<string, string> = {
    fullText: 'full',
    chapter: 'paragraph',
    worksheet: 'excel_full_content_parse',
    row: 'excel_header_row_parse',
  };
  return extensionMapping[extension] || 'full';
};
