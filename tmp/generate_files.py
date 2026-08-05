from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from fpdf import FPDF
import os

output_dir = os.path.dirname(os.path.abspath(__file__))

# Color scheme
DARK_BLUE = RGBColor(0x1e, 0x3a, 0x5f)
MED_BLUE = RGBColor(0x2d, 0x5a, 0x87)
WHITE = RGBColor(0xff, 0xff, 0xff)

def create_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6]
    
    def add_title_slide(title, subtitle, sub2=None):
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK_BLUE
        bg.line.fill.background()
        
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
        sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4), Inches(12.333), Inches(0.8))
        tf = sub_box.text_frame
        p = tf.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(22)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
        if sub2:
            sub2_box = slide.shapes.add_textbox(Inches(0.5), Inches(5), Inches(12.333), Inches(0.5))
            tf = sub2_box.text_frame
            p = tf.paragraphs[0]
            p.text = sub2
            p.font.size = Pt(16)
            p.font.color.rgb = RGBColor(0xcc, 0xcc, 0xcc)
            p.alignment = PP_ALIGN.CENTER
        return slide
    
    def add_content_slide(title, bullets):
        slide = prs.slides.add_slide(blank_layout)
        title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE
        
        content_box = slide.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(12), Inches(5.5))
        tf = content_box.text_frame
        tf.word_wrap = True
        
        for i, bullet in enumerate(bullets):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = "• " + bullet
            p.font.size = Pt(18)
            p.space_after = Pt(12)
        return slide
    
    # Slide 1: Title
    add_title_slide("OutSystems to FullStack Migration", "AI-Powered Application Modernization", "Approach Document")
    
    # Slide 2: The Challenge
    add_content_slide("The Challenge", [
        "High licensing costs that scale with usage and users",
        "Vendor lock-in limiting technology choices and flexibility",
        "Talent constraints with limited OutSystems developer availability",
        "Scalability concerns for growing business needs",
        "Integration complexity with modern cloud-native architectures"
    ])
    
    # Slide 3: Our Solution
    add_content_slide("Our Solution: AI-Accelerated Migration", [
        "Automated Code Generation - AI analyzes OML metadata and generates equivalent Java/.NET code",
        "Pattern Recognition - Intelligent mapping of OutSystems patterns to standard frameworks",
        "Accelerated Timeline - 60-70% faster than manual rewrite",
        "Risk Mitigation - Incremental migration with validation at each phase"
    ])
    
    # Slide 4: Target Stack Options
    add_content_slide("Target Stack Options", [
        "Java Stack: Spring Boot, React/Angular, PostgreSQL/MySQL, Docker + Kubernetes",
        "Best for: Organizations with Java expertise or cloud-native focus",
        "",
        ".NET Stack: ASP.NET Core, Blazor/React, SQL Server/PostgreSQL, Azure/AWS",
        "Best for: Microsoft ecosystem organizations or existing .NET teams"
    ])
    
    # Slide 5: OutSystems Export Formats
    add_content_slide("OutSystems Export Formats - What We Analyze", [
        "OAP (Application Pack) - ZIP archive containing OML files for complete applications",
        "OML (Module) - XML-based file with all application metadata (key for migration)",
        "",
        "OML Contains: Entities (data models), Screens (UI), Server/Client Actions (logic),",
        "Aggregates (queries), Integrations (APIs), Roles/Permissions, Site Properties",
        "",
        "Fully parseable with standard XML tools - enables automated analysis and code generation"
    ])
    
    # Slide 6: Migration Approach
    add_content_slide("Migration Approach", [
        "Phase 1: Discovery & Analysis - Extract and analyze OML files, map data models",
        "Phase 2: Architecture Design - Define target architecture, plan database migration",
        "Phase 3: AI-Assisted Code Generation - Generate backend, frontend, and schemas",
        "Phase 4: Validation & Refinement - Test, validate, performance tuning, UAT"
    ])
    
    # Slide 7: Cost Benefits
    add_content_slide("Cost Reduction Benefits", [
        "60-80% Licensing Cost Reduction",
        "3-5x Larger Talent Pool of Java/.NET developers",
        "100% Code Ownership",
        "Eliminate recurring platform fees (typically $50K-$500K+ annually)",
        "Flexible scaling without per-user licensing constraints"
    ])
    
    # Slide 8: POC Scope
    add_content_slide("Proof of Concept Scope", [
        "Included: 1 representative module, 5-10 entities, 3-5 workflows, auth flow, 1-2 API integrations",
        "",
        "Deliverables:",
        "Working application in target stack",
        "Migration assessment report and full roadmap",
        "Effort estimation and ROI projection"
    ])
    
    # Slide 9: POC Timeline
    add_content_slide("POC Timeline: 4-6 Weeks", [
        "Week 1 - Discovery: Extract OML, analyze structure, document current state",
        "Week 2 - Design: Define architecture, map data models, plan approach",
        "Week 3-4 - Development: AI-assisted code generation, implementation",
        "Week 5 - Testing: Functional validation, data migration verification",
        "Week 6 - Delivery: Demo, documentation, roadmap presentation"
    ])
    
    # Slide 10: Why Partner
    add_content_slide("Why Partner With Us", [
        "Proven AI-assisted migration methodology refined across engagements",
        "Deep OutSystems expertise understanding OML internals",
        "Full-stack development capability in both Java and .NET",
        "Risk-managed approach with incremental delivery",
        "Knowledge transfer ensuring your team can maintain applications",
        "Post-migration support available"
    ])
    
    # Slide 11: Next Steps
    add_content_slide("Next Steps", [
        "1. Share your OutSystems application portfolio overview",
        "2. Joint discovery call to assess complexity and priorities",
        "3. Select a pilot application for POC",
        "4. Agree on target stack and timeline",
        "5. Kick off the POC engagement"
    ])
    
    # Slide 12: Thank You
    add_title_slide("Thank You", "Let's modernize your applications together", "Questions?")
    
    prs.save(os.path.join(output_dir, "outsystems-migration-approach.pptx"))
    print("Created: outsystems-migration-approach.pptx")


def create_pdf():
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def title_slide(title, subtitle, sub2=None):
        pdf.add_page()
        pdf.set_fill_color(30, 58, 95)
        pdf.rect(0, 0, 297, 210, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 36)
        pdf.set_y(70)
        pdf.cell(0, 20, title, align='C')
        pdf.set_font('Helvetica', '', 18)
        pdf.set_y(95)
        pdf.cell(0, 10, subtitle, align='C')
        if sub2:
            pdf.set_font('Helvetica', '', 14)
            pdf.set_text_color(200, 200, 200)
            pdf.set_y(115)
            pdf.cell(0, 10, sub2, align='C')
    
    def content_slide(title, bullets):
        pdf.add_page()
        pdf.set_text_color(30, 58, 95)
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_xy(15, 15)
        pdf.cell(0, 12, title)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', '', 14)
        y = 35
        for bullet in bullets:
            if bullet:
                pdf.set_xy(20, y)
                pdf.multi_cell(260, 8, f"* {bullet}")
                y = pdf.get_y() + 3
            else:
                y += 5
    
    # Slide 1
    title_slide("OutSystems to FullStack Migration", "AI-Powered Application Modernization", "Approach Document")
    
    # Slide 2
    content_slide("The Challenge", [
        "High licensing costs that scale with usage and users",
        "Vendor lock-in limiting technology choices and flexibility",
        "Talent constraints with limited OutSystems developer availability",
        "Scalability concerns for growing business needs",
        "Integration complexity with modern cloud-native architectures"
    ])
    
    # Slide 3
    content_slide("Our Solution: AI-Accelerated Migration", [
        "Automated Code Generation - AI analyzes OML metadata and generates equivalent Java/.NET code",
        "Pattern Recognition - Intelligent mapping of OutSystems patterns to standard frameworks",
        "Accelerated Timeline - 60-70% faster than manual rewrite",
        "Risk Mitigation - Incremental migration with validation at each phase"
    ])
    
    # Slide 4
    content_slide("Target Stack Options", [
        "Java Stack: Spring Boot, React/Angular, PostgreSQL/MySQL, Docker + Kubernetes",
        "Best for: Organizations with Java expertise or cloud-native focus",
        "",
        ".NET Stack: ASP.NET Core, Blazor/React, SQL Server/PostgreSQL, Azure/AWS",
        "Best for: Microsoft ecosystem organizations or existing .NET teams"
    ])
    
    # Slide 5
    content_slide("OutSystems Export Formats - What We Analyze", [
        "OAP (Application Pack) - ZIP archive containing OML files for complete applications",
        "OML (Module) - XML-based file with all application metadata (key for migration)",
        "",
        "OML Contains: Entities (data models), Screens (UI), Server/Client Actions (logic),",
        "Aggregates (queries), Integrations (APIs), Roles/Permissions, Site Properties",
        "",
        "Fully parseable with standard XML tools - enables automated analysis and code generation"
    ])
    
    # Slide 6
    content_slide("Migration Approach", [
        "Phase 1: Discovery & Analysis - Extract and analyze OML files, map data models",
        "Phase 2: Architecture Design - Define target architecture, plan database migration",
        "Phase 3: AI-Assisted Code Generation - Generate backend, frontend, and schemas",
        "Phase 4: Validation & Refinement - Test, validate, performance tuning, UAT"
    ])
    
    # Slide 6
    content_slide("Cost Reduction Benefits", [
        "60-80% Licensing Cost Reduction",
        "3-5x Larger Talent Pool of Java/.NET developers",
        "100% Code Ownership",
        "Eliminate recurring platform fees (typically $50K-$500K+ annually)",
        "Flexible scaling without per-user licensing constraints"
    ])
    
    # Slide 7
    content_slide("Proof of Concept Scope", [
        "Included: 1 representative module, 5-10 entities, 3-5 workflows, auth flow, 1-2 API integrations",
        "",
        "Deliverables:",
        "Working application in target stack",
        "Migration assessment report and full roadmap",
        "Effort estimation and ROI projection"
    ])
    
    # Slide 8
    content_slide("POC Timeline: 4-6 Weeks", [
        "Week 1 - Discovery: Extract OML, analyze structure, document current state",
        "Week 2 - Design: Define architecture, map data models, plan approach",
        "Week 3-4 - Development: AI-assisted code generation, implementation",
        "Week 5 - Testing: Functional validation, data migration verification",
        "Week 6 - Delivery: Demo, documentation, roadmap presentation"
    ])
    
    # Slide 9
    content_slide("Why Partner With Us", [
        "Proven AI-assisted migration methodology refined across engagements",
        "Deep OutSystems expertise understanding OML internals",
        "Full-stack development capability in both Java and .NET",
        "Risk-managed approach with incremental delivery",
        "Knowledge transfer ensuring your team can maintain applications",
        "Post-migration support available"
    ])
    
    # Slide 10
    content_slide("Next Steps", [
        "1. Share your OutSystems application portfolio overview",
        "2. Joint discovery call to assess complexity and priorities",
        "3. Select a pilot application for POC",
        "4. Agree on target stack and timeline",
        "5. Kick off the POC engagement"
    ])
    
    # Slide 11
    title_slide("Thank You", "Let's modernize your applications together", "Questions?")
    
    pdf.output(os.path.join(output_dir, "outsystems-migration-approach.pdf"))
    print("Created: outsystems-migration-approach.pdf")


if __name__ == "__main__":
    create_pptx()
    create_pdf()
