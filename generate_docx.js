/**
 * DocForge AI — generate_docx.js
 * Usage: node generate_docx.js <input_json_path> <output_docx_path>
 *
 * input_json format:
 * {
 *   "doc_type": "Employee Offer Letter",
 *   "department": "HR",
 *   "company_name": "Turabit",
 *   "industry": "Technology / SaaS",
 *   "region": "India",
 *   "sections": [
 *     { "name": "Job Position Details", "content": "plain text content..." },
 *     ...
 *   ]
 * }
 */

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun,
  Table, TableRow, TableCell,
  Header, Footer,
  AlignmentType, HeadingLevel,
  BorderStyle, WidthType, ShadingType,
  PageNumber, NumberFormat,
  LevelFormat, TabStopType, TabStopPosition,
  PageBreak,
} = require('docx');

// ── Read input ─────────────────────────────────────────────────────────────
const [,, inputPath, outputPath] = process.argv;
if (!inputPath || !outputPath) {
  console.error('Usage: node generate_docx.js <input.json> <output.docx>');
  process.exit(1);
}

const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const { doc_type, department, company_name, industry, region, sections } = input;

// ── Helpers ────────────────────────────────────────────────────────────────

function textParagraph(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    ...opts,
    children: [new TextRun({ text, font: "Arial", size: opts.size || 22, ...opts.run })],
  });
}

function sectionHeading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: "2E4057" })],
  });
}

function metaRow(label, value) {
  const border = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new TableRow({
    children: [
      new TableCell({
        borders,
        width: { size: 2800, type: WidthType.DXA },
        children: [new Paragraph({
          spacing: { after: 60 },
          children: [new TextRun({ text: label, font: "Arial", size: 20, bold: true, color: "555555" })],
        })],
      }),
      new TableCell({
        borders,
        width: { size: 6560, type: WidthType.DXA },
        children: [new Paragraph({
          spacing: { after: 60 },
          children: [new TextRun({ text: value, font: "Arial", size: 20, color: "222222" })],
        })],
      }),
    ],
  });
}

// ── Content blocks from plain text ────────────────────────────────────────

function parsePlainTextToBlocks(text) {
  if (!text) return [textParagraph("")];
  const blocks = [];
  const lines = text.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      // blank line = spacing paragraph
      blocks.push(new Paragraph({ spacing: { after: 80 } }));
      continue;
    }

    // Numbered list line: "1. Item" or "1) Item"
    const numberedMatch = trimmed.match(/^(\d+)[.)]\s+(.+)$/);
    if (numberedMatch) {
      blocks.push(new Paragraph({
        spacing: { after: 80 },
        indent: { left: 360 },
        children: [new TextRun({
          text: `${numberedMatch[1]}. ${numberedMatch[2]}`,
          font: "Arial", size: 22,
        })],
      }));
      continue;
    }

    // Bullet line: "  - Item" or "- Item"
    const bulletMatch = trimmed.match(/^[-•]\s+(.+)$/);
    if (bulletMatch) {
      blocks.push(new Paragraph({
        spacing: { after: 80 },
        indent: { left: 360, hanging: 180 },
        children: [
          new TextRun({ text: "•  ", font: "Arial", size: 22 }),
          new TextRun({ text: bulletMatch[1], font: "Arial", size: 22 }),
        ],
      }));
      continue;
    }

    // Regular paragraph line
    blocks.push(new Paragraph({
      spacing: { after: 120 },
      children: [new TextRun({ text: trimmed, font: "Arial", size: 22 })],
    }));
  }

  return blocks;
}

// ── Build document ─────────────────────────────────────────────────────────

const children = [];

// ── Title block ────────────────────────────────────────────────────────────
children.push(
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { after: 200 },
    children: [new TextRun({
      text: doc_type,
      font: "Arial", size: 40, bold: true, color: "2E4057",
    })],
  })
);

// ── Meta table ─────────────────────────────────────────────────────────────
const metaBorder = { style: BorderStyle.SINGLE, size: 4, color: "E8E8E8" };
const metaBorders = { top: metaBorder, bottom: metaBorder, left: metaBorder, right: metaBorder };

children.push(
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: [
      metaRow("Organization:", company_name),
      metaRow("Department:", department),
      metaRow("Industry:", industry),
      metaRow("Region:", region),
      metaRow("Version:", "v1.0"),
      metaRow("Classification:", "Internal Use Only"),
      metaRow("Generated by:", "DocForge AI"),
    ],
  })
);

children.push(new Paragraph({ spacing: { after: 240 } }));

// ── Divider ────────────────────────────────────────────────────────────────
const divBorder = { style: BorderStyle.SINGLE, size: 6, color: "2E4057" };
children.push(
  new Paragraph({
    border: { bottom: divBorder },
    spacing: { after: 280 },
    children: [new TextRun({ text: "" })],
  })
);

// ── Sections ───────────────────────────────────────────────────────────────
sections.forEach((sec, idx) => {
  if (idx > 0) {
    // Small visual separator between sections
    children.push(new Paragraph({ spacing: { after: 160 } }));
  }
  children.push(sectionHeading(sec.name));
  const contentBlocks = parsePlainTextToBlocks(sec.content);
  children.push(...contentBlocks);
});

// ── Footer spacer ──────────────────────────────────────────────────────────
children.push(new Paragraph({ spacing: { after: 400 } }));
children.push(
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200 },
    children: [
      new TextRun({ text: `${doc_type}  ·  Generated by DocForge AI  ·  Confidential`, font: "Arial", size: 16, color: "AAAAAA" }),
    ],
  })
);

// ── Build doc ─────────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 40, bold: true, font: "Arial", color: "2E4057" },
        paragraph: { spacing: { before: 0, after: 200 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E4057" },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            spacing: { after: 0 },
            children: [
              new TextRun({ text: `${company_name}  |  ${doc_type}`, font: "Arial", size: 16, color: "888888" }),
            ],
          }),
        ],
      }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 0 },
            children: [
              new TextRun({ text: "Page ", font: "Arial", size: 16, color: "888888" }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "888888" }),
              new TextRun({ text: " of ", font: "Arial", size: 16, color: "888888" }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], font: "Arial", size: 16, color: "888888" }),
            ],
          }),
        ],
      }),
    },
    children,
  }],
});

// ── Write file ─────────────────────────────────────────────────────────────
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`OK:${outputPath}`);
}).catch(err => {
  console.error('DOCX error:', err.message);
  process.exit(1);
});
