from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, BaseDocTemplate, NextPageTemplate, PageBreak, FrameBreak, Paragraph, Spacer, Image, Table, TableStyle, Image, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.staticfiles.templatetags.staticfiles import static


class PdfPrint():
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        self.pageSize = letter
        self.width, self.height = self.pageSize

    def planReport(self, table_data, title, plan):
        styles = getSampleStyleSheet()
        Elements = []
        doc = BaseDocTemplate(self.buffer)
        column_gap = 1 * inch
        templates = []
        top = Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        rightPadding=column_gap / 2,
                        showBoundary=0)
        left = Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height - ((plan.designs.count() * inch)),
                        showBoundary=0)
        designs = Frame(
                        doc.leftMargin + doc.width / 2,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height - .5 * inch,
                        showBoundary=0)
        columns = []
        # tops = []
        columns.append(top)
        columns.append(designs)
        columns.append(left)
        # templates.append(PageTemplate(frames=tops, id="top"))
        templates.append(PageTemplate(frames=columns, id="columns"))
        doc.addPageTemplates(templates)

        styles.add(ParagraphStyle(name='line', parent=styles['BodyText'], spaceBefore=0))
        styles.add(ParagraphStyle(name='campaign-name', parent=styles['h4'], spaceBefore=0, spaceAfter=0, fontName='Helvetica-Bold'))
        image = Image('/Users/estyrosenberg/Desktop/MediaPlan/mediaPlan/mediaPlan/static/img/mediaotg-small.png', 122.25, 31.75)
        image.hAlign = 'LEFT'
        Elements.append(Spacer(width=0, height=.25*inch))
        Elements.append(image)
        Elements.append(Spacer(width=0, height=.5*inch))
        Elements.append(Paragraph('Plan no: ' + str(plan.pk), styles['line']))
        Elements.append(Paragraph(str(plan.name), styles['campaign-name']))
        client = plan.client
        if plan.client.parent != None:
            client += ' - ' + plan.client.parent
        Elements.append(Paragraph(str(client), styles['line']))
        Elements.append(Paragraph('Created: ' + f'{plan.created_at:%b %d, %Y}', styles['line']))
        Elements.append(FrameBreak())

        designList = []
        for design in plan.designs.all():
            tempImage = ''
            if design.thumbnail is not None:
                print('WIDTH: ' + str(design.thumbnail.image.width))
                tempImage = Image("/Users/estyrosenberg/Desktop/MediaPlan/mediaPlan/mediaPlan/" + design.thumbnail.image.url, design.thumbnail.image.width / 20, design.thumbnail.image.height / 20)
            designList.append([design.name, tempImage])
        Elements.append(Spacer(width=0, height=.25*inch))
        designList.insert(0, ['Designs', ''])
        wh_table = Table(designList, colWidths=[1.25*inch] * 5)
        wh_table.setStyle(TableStyle(
            [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
             ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
             ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
             ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
        Elements.append(wh_table)

        
        Elements.append(FrameBreak())
        for table in table_data:
            Elements.append(Spacer(width=0, height=.25*inch))
            wh_table = Table(table['table'], colWidths=[1.25*inch] * 5)
            wh_table.setStyle(TableStyle(
                [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
                 ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
                 ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
                 ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
                 ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
            Elements.append(wh_table)

        if plan.full_ads.count() > 0:
            fullList = []
            fullTotal = 0
            for ad in plan.full_ads.all():
                fullList.append([ad.rate.publication.name, ad.rate.rateName, ad.deadline, ad.design, '$' + ('%.2f' % int(ad.rate.price))])
                fullTotal += int(ad.rate.price)
            Elements.append(Spacer(width=0, height=.25*inch))
            fullList.insert(0, ['Full Campaign', '', '', '', '$' + ('%.2f' % int(fullTotal))])
            wh_table = Table(fullList, colWidths=[1.25*inch] * 5)
            wh_table.setStyle(TableStyle(
                [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
                 ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
                 ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
                 ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
                 ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
            Elements.append(wh_table)

        if plan.expenses.count() > 0:
            extraList = []
            extraTotal = 0
            for ad in plan.expenses.all():
                extraList.append([ad.name, '', ad.deadline, '', '$' + ('%.2f' % int(ad.total))])
                extraTotal += int(ad.total)
            Elements.append(Spacer(width=0, height=.25*inch))
            extraList.insert(0, ['Additional Expenses', '', '', '', '$' + ('%.2f' % int(extraTotal))])
            wh_table = Table(extraList, colWidths=[1.25*inch] * 5)
            wh_table.setStyle(TableStyle(
                [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
                 ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
                 ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
                 ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
                 ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
            Elements.append(wh_table)

        Elements.append(Spacer(width=0, height=.25*inch))
        totals = [['Totals']]
        weekly = 0
        for ad in plan.weekly_ads.all():
            weekly += int(ad.rate.price)
        totals.append(['Weeklys', '$' + ('%.2f' % int(weekly))])
        wh_table = Table(totals, colWidths=[1.25*inch] * 5)
        wh_table.setStyle(TableStyle(
            [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
             ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
             ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
             ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
        wh_table.hAlign = 'RIGHT'
        Elements.append(wh_table)

        doc.build(Elements)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def designReport(self, plan):
        styles = getSampleStyleSheet()
        Elements = []
        doc = BaseDocTemplate(self.buffer)
        column_gap = 1 * inch
        templates = []
        top = Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        rightPadding=column_gap / 2,
                        showBoundary=0)
        left = Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height - ((plan.designs.count() * inch)),
                        showBoundary=0)
        designs = Frame(
                        doc.leftMargin + doc.width / 2,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height - .5 * inch,
                        showBoundary=0)
        columns = []
        columns.append(top)
        columns.append(designs)
        columns.append(left)
        templates.append(PageTemplate(frames=columns, id="columns"))
        doc.addPageTemplates(templates)

        styles.add(ParagraphStyle(name='line', parent=styles['BodyText'], spaceBefore=0))
        styles.add(ParagraphStyle(name='campaign-name', parent=styles['h4'], spaceBefore=0, spaceAfter=0, fontName='Helvetica-Bold'))
        image = Image('/Users/estyrosenberg/Desktop/MediaPlan/mediaPlan/mediaPlan/static/img/mediaotg-small.png', 122.25, 31.75)
        image.hAlign = 'LEFT'
        Elements.append(Spacer(width=0, height=.25*inch))
        Elements.append(image)
        Elements.append(Spacer(width=0, height=.5*inch))
        Elements.append(Paragraph('Plan no: ' + str(plan.pk), styles['line']))
        Elements.append(Paragraph(str(plan.name), styles['campaign-name']))
        client = plan.client
        if plan.client.parent != None:
            client += ' - ' + plan.client.parent
        Elements.append(Paragraph(str(client), styles['line']))
        Elements.append(Paragraph('Created: ' + f'{plan.created_at:%b %d, %Y}', styles['line']))
        Elements.append(FrameBreak())

        designList = []
        for design in plan.designs.all():
            tempImage = ''
            if design.thumbnail is not None:
                print('WIDTH: ' + str(design.thumbnail.image.width))
                tempImage = Image("/Users/estyrosenberg/Desktop/MediaPlan/mediaPlan/mediaPlan/" + design.thumbnail.image.url, design.thumbnail.image.width / 20, design.thumbnail.image.height / 20)
            designList.append([design.name, tempImage])
        Elements.append(Spacer(width=0, height=.25*inch))
        designList.insert(0, ['Designs', ''])
        wh_table = Table(designList, colWidths=[1.25*inch] * 5)
        wh_table.setStyle(TableStyle(
            [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
             ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
             ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
             ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
        Elements.append(wh_table)
        Elements.append(FrameBreak())

        ads = []
        publications = []
        for ad in plan.weekly_ads.all():
            index = next((index for (index, d) in enumerate(publications) if d["name"] == ad.rate.publication.name), None)
            if index is None:
                publications.append({'name': ad.rate.publication.name, 'ads': []})
            else:
                publications[index]['ads'].append(ad)

        for pub in publications:
            adsList = [[pub['name'],'', '']]
            for ad in pub['ads']:
                adsList.append([ad.rate.rateName, ad.rate.bleed, ad.rate.dimensions])
            Elements.append(Spacer(width=0, height=.25*inch))
            wh_table = Table(adsList, colWidths=[2*inch] * 5)
            wh_table.setStyle(TableStyle(
                [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
                 ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
                 ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
                 ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
                 ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
            Elements.append(wh_table)

        doc.build(Elements)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def publicationReport(self, plan, publication, ads):
        styles = getSampleStyleSheet()
        Elements = []
        doc = BaseDocTemplate(self.buffer)
        column_gap = 1 * inch
        templates = []
        top = Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        rightPadding=column_gap / 2,
                        showBoundary=0)
        left = Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height - ((plan.designs.count() * inch) + 1*inch),
                        showBoundary=0)
        designs = Frame(
                        doc.leftMargin + doc.width / 2,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height - .5 * inch,
                        showBoundary=0)
        columns = []
        columns.append(top)
        columns.append(designs)
        columns.append(left)
        templates.append(PageTemplate(frames=columns, id="columns"))
        doc.addPageTemplates(templates)

        styles.add(ParagraphStyle(name='line', parent=styles['BodyText'], spaceBefore=0))
        styles.add(ParagraphStyle(name='campaign-name', parent=styles['h4'], spaceBefore=0, spaceAfter=0, fontName='Helvetica-Bold'))


        image = Image('/Users/estyrosenberg/Desktop/MediaPlan/mediaPlan/mediaPlan/static/img/mediaotg-small.png', 122.25, 31.75)
        image.hAlign = 'LEFT'
        Elements.append(Spacer(width=0, height=.25*inch))
        Elements.append(image)
        Elements.append(Spacer(width=0, height=.5*inch))

        Elements.append(Paragraph(str(publication.name), styles['line']))
        Elements.append(Paragraph(str(publication.contactName), styles['line']))
        Elements.append(Spacer(width=0, height=.25*inch))

        Elements.append(Paragraph('Plan no: ' + str(plan.pk), styles['line']))
        Elements.append(Paragraph(str(plan.name), styles['campaign-name']))
        client = plan.client
        if plan.client.parent != None:
            client += ' - ' + plan.client.parent
        Elements.append(Paragraph(str(client), styles['line']))
        Elements.append(Paragraph('Created: ' + f'{plan.created_at:%b %d, %Y}', styles['line']))
        Elements.append(FrameBreak())

        designList = []
        for design in plan.designs.all():
            tempImage = ''
            if design.thumbnail is not None:
                print('WIDTH: ' + str(design.thumbnail.image.width))
                tempImage = Image("/Users/estyrosenberg/Desktop/MediaPlan/mediaPlan/mediaPlan/" + design.thumbnail.image.url, design.thumbnail.image.width / 20, design.thumbnail.image.height / 20)
            designList.append([design.name, tempImage])
        Elements.append(Spacer(width=0, height=.25*inch))
        designList.insert(0, ['Designs', ''])
        wh_table = Table(designList, colWidths=[1.25*inch] * 5)
        wh_table.setStyle(TableStyle(
            [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
             ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
             ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
             ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
        Elements.append(wh_table)
        Elements.append(FrameBreak())

        adsList = []
        for ad in ads:
            deadline = ''
            if hasattr(ad, 'week'):
                deadline = str(ad.week.start) + ' - ' + str(ad.week.end)
            else:
                deadline = ad.deadline
            adsList.append([ad.rate.rateName, deadline, ad.design, '$' + ('%.2f' % int(ad.rate.price))])
        Elements.append(Spacer(width=0, height=.25*inch))
        adsList.insert(0, ['Ads', '', '', ''])
        wh_table = Table(adsList, colWidths=[1.05*inch])
        wh_table._argW[1] = 3*inch

        wh_table.setStyle(TableStyle(
            [('INNERGRID', (0,1), (-1, -1), 0.25, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.Color(red=(200.0/255),green=(200.0/255),blue=(200.0/255))), 
             ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), 
             ('BACKGROUND', (0,0), (-1, 0), colors.Color(red=(230.0/255),green=(230.0/255),blue=(230.0/255))),
             ('TEXTCOLOR', (0,0), (-1,-1), colors.Color(red=(50.0/255),green=(50.0/255),blue=(50.0/255)))]))
        Elements.append(wh_table)

        doc.build(Elements)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf
