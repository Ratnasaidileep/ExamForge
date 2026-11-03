import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from app.core.config import settings

def generate_question_paper_pdf(paper_dict: Dict[str, Any], sections_list: List[Dict[str, Any]]) -> str:
    """
    Generates an official examination question paper PDF without answers.
    Returns the file path.
    """
    export_filename = f"question_paper_{paper_dict.get('id', 'paper')}_{uuid.uuid4().hex[:6]}.pdf"
    file_path = settings.STORAGE_EXPORTS_DIR / export_filename
    
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        alignment=1, # Centered
        spaceAfter=4,
        textColor=colors.HexColor('#1E293B')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        alignment=1,
        spaceAfter=8,
        textColor=colors.HexColor('#475569')
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=colors.HexColor('#0F172A')
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        textColor=colors.HexColor('#1E1B4B'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    q_num_style = ParagraphStyle(
        'QuestionNum',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1E293B')
    )
    
    q_text_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0F172A')
    )
    
    marks_style = ParagraphStyle(
        'MarksStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        alignment=2, # Right
        textColor=colors.HexColor('#3730A3')
    )
    
    option_style = ParagraphStyle(
        'OptionStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    elements = []
    
    # 1. Header Box
    elements.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", subtitle_style))
    elements.append(Paragraph("COLLEGE OF ENGINEERING & TECHNOLOGY", subtitle_style))
    elements.append(Paragraph(paper_dict.get('title', 'EXAMINATION QUESTION PAPER').upper(), title_style))
    elements.append(Spacer(1, 6))
    
    # Metadata Table
    subject_code = paper_dict.get('subject_id') or "ITS-401"
    duration = f"{paper_dict.get('duration_minutes', 60)} Minutes"
    total_marks = f"{paper_dict.get('total_marks', 50):g} Marks"
    
    meta_data = [
        [
            Paragraph(f"<b>Subject Code:</b> {subject_code}", meta_style),
            Paragraph(f"<b>Duration:</b> {duration}", meta_style),
            Paragraph(f"<b>Max Marks:</b> {total_marks}", meta_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[180, 170, 160])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#3730A3')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))
    
    # Instructions
    instructions_text = paper_dict.get('instructions') or (
        "1. All questions are compulsory unless specified otherwise.\n"
        "2. Marks for each question are indicated in brackets [ ] on the right.\n"
        "3. Scientific calculators and drawing instruments are permitted.\n"
        "4. Write legibly and illustrate your answers with neat diagrams wherever required."
    )
    inst_paragraphs = [Paragraph(f"<b>General Instructions:</b>", meta_style)]
    for line in instructions_text.split("\n"):
        if line.strip():
            inst_paragraphs.append(Paragraph(line.strip(), option_style))
            
    inst_table = Table([[inst_paragraphs]], colWidths=[510])
    inst_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(inst_table)
    elements.append(Spacer(1, 12))
    
    # 2. Sections and Questions
    q_global_counter = 1
    
    for sec in sections_list:
        sec_name = sec.get('name', 'Section')
        sec_marks = sec.get('total_marks', 0)
        sec_inst = sec.get('instructions')
        
        elements.append(Paragraph(f"{sec_name.upper()} ({sec_marks:g} Marks)", section_title_style))
        if sec_inst:
            elements.append(Paragraph(f"<i>{sec_inst}</i>", option_style))
            elements.append(Spacer(1, 4))
            
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=8))
        
        sec_items = sec.get('items', [])
        for item in sec_items:
            rev = item.get('revision') or {}
            q_text = rev.get('question_text') or item.get('question_text') or "Question Text"
            marks = item.get('marks') or rev.get('marks', 2.0)
            q_type = rev.get('question_type') or "short_answer"
            options = rev.get('options_json') or []
            
            # Format Question Row: [Q# | Text | Marks]
            q_row = [
                Paragraph(f"Q{q_global_counter}.", q_num_style),
                Paragraph(q_text, q_text_style),
                Paragraph(f"[{marks:g}]", marks_style)
            ]
            
            q_table = Table([q_row], colWidths=[30, 435, 45])
            q_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            q_elements = [q_table]
            
            # If MCQ, render options
            if q_type == 'mcq' and options:
                opt_rows = []
                letters = ["A", "B", "C", "D", "E"]
                for i, opt in enumerate(options):
                    letter_str = letters[i] if i < len(letters) else f"({i+1})"
                    opt_rows.append([
                        Paragraph("", q_num_style),
                        Paragraph(f"<b>({letter_str})</b> {opt}", option_style),
                        Paragraph("", marks_style)
                    ])
                opt_table = Table(opt_rows, colWidths=[30, 435, 45])
                opt_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                q_elements.append(opt_table)
                
            q_elements.append(Spacer(1, 8))
            elements.append(KeepTogether(q_elements))
            q_global_counter += 1
            
        elements.append(Spacer(1, 10))
        
    doc.build(elements)
    return str(file_path)

def generate_answer_key_pdf(paper_dict: Dict[str, Any], sections_list: List[Dict[str, Any]]) -> str:
    """
    Generates a confidential faculty answer key and scoring rubric PDF.
    Returns the file path.
    """
    export_filename = f"answer_key_{paper_dict.get('id', 'paper')}_{uuid.uuid4().hex[:6]}.pdf"
    file_path = settings.STORAGE_EXPORTS_DIR / export_filename
    
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'KeyTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,
        spaceAfter=4,
        textColor=colors.HexColor('#B91C1C')
    )
    
    subtitle_style = ParagraphStyle(
        'KeySubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1,
        spaceAfter=8,
        textColor=colors.HexColor('#1E293B')
    )
    
    body_style = ParagraphStyle(
        'KeyBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0F172A')
    )
    
    bold_style = ParagraphStyle(
        'KeyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=colors.HexColor('#0F172A')
    )
    
    answer_box_style = ParagraphStyle(
        'AnswerBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#15803D')
    )
    
    elements = []
    
    elements.append(Paragraph("CONFIDENTIAL — FACULTY ANSWER KEY & EVALUATION RUBRIC", title_style))
    elements.append(Paragraph(f"Paper: {paper_dict.get('title', 'Examination')} (Subject: {paper_dict.get('subject_id', 'ITS-401')})", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#B91C1C'), spaceAfter=12))
    
    q_global_counter = 1
    
    for sec in sections_list:
        sec_name = sec.get('name', 'Section')
        elements.append(Paragraph(f"<b>{sec_name.upper()}</b>", bold_style))
        elements.append(Spacer(1, 6))
        
        for item in sec.get('items', []):
            rev = item.get('revision') or {}
            q_text = rev.get('question_text') or "Question Text"
            marks = item.get('marks') or rev.get('marks', 2.0)
            q_type = rev.get('question_type') or "short_answer"
            correct_ans = rev.get('correct_answer') or "N/A"
            model_ans = rev.get('model_answer') or ""
            rubric = rev.get('rubric_json') or []
            explanation = rev.get('explanation') or ""
            excerpt = rev.get('supporting_excerpt') or ""
            
            box_content = [
                Paragraph(f"<b>Question {q_global_counter}:</b> {q_text} <i>[{marks:g} Marks]</i>", bold_style),
                Spacer(1, 4)
            ]
            
            if q_type == 'mcq':
                box_content.append(Paragraph(f"<b>Correct Answer:</b> {correct_ans}", answer_box_style))
                if explanation:
                    box_content.append(Paragraph(f"<b>Explanation:</b> {explanation}", body_style))
            else:
                if model_ans:
                    box_content.append(Paragraph(f"<b>Model Answer:</b><br/>{model_ans}", body_style))
                if rubric:
                    rubric_text = "<br/>".join([f"• {r.get('criteria') or r.get('criterion')}: <b>{r.get('marks', 0)}M</b>" for r in rubric if isinstance(r, dict)])
                    if rubric_text:
                        box_content.append(Spacer(1, 3))
                        box_content.append(Paragraph(f"<b>Grading Rubric:</b><br/>{rubric_text}", body_style))
            
            if excerpt:
                box_content.append(Spacer(1, 3))
                box_content.append(Paragraph(f"<b>Source Evidence Excerpt:</b> <i>\"{excerpt}\"</i>", ParagraphStyle('Exc', parent=body_style, textColor=colors.HexColor('#475569'))))
                
            q_box = Table([[box_content]], colWidths=[510])
            q_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E2E8F0')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(KeepTogether([q_box, Spacer(1, 8)]))
            q_global_counter += 1
            
        elements.append(Spacer(1, 10))
        
    doc.build(elements)
    return str(file_path)
