import os
import csv
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTLine, LTTextLine
from pdfminer.converter import PDFPageAggregator

#set the path for the pdf file of T2 sponsors list.
dir = os.path.dirname(os.path.realpath(__file__))
rel_path = "files/Tier_2_5_Register_of_Sponsors_2015-05-01.pdf"
pdfpath = os.path.join(dir,rel_path)

print pdfpath
field_names = ["Organisation Name","Town/City","Tier & Rating","Sub Tier"]

#open the pdf file of T2 sponsor list.
with open(pdfpath, "r") as pdf_file:
    #create a parser object of the file.
    parser = PDFParser(pdf_file)
    #create a PDF document object to store the document structure.
    doc = PDFDocument(parser)
    #check whether the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    #create a PDF resource manager object to store shared resources.
    rsrcmgr = PDFResourceManager()
    #set parameters for analysis.
    laparams = LAParams(line_margin=0.2)
    #create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr,laparams=laparams)
    #create a PDF intepreter object to process each page.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    page_dict = {}
    
    #set column locations of the table.
    col1 = 24.0
    col2 = 351.0
    col3 = 576.0
    col4 = 678.0
    #set top margin of the table.
    top_h1 = 396.0
    top_h2 = 568.0
    #set keys of each table column.
    col1_key = int(col1)
    col2_key = int(col2)
    col3_key = int(col3)
    col4_key = int(col4)
    #initialise page_dict that stores columns of a row in the table.
    page_dict[col1_key] = ""#field_names[0]
    page_dict[col2_key] = ""#field_names[1]
    page_dict[col3_key] = ""#field_names[2]
    page_dict[col4_key] = ""#field_names[3]
    
    #open and wrtie data.csv file.
    with open("data.csv","wb") as data:
        writer = csv.writer(data)
        #process each page contained in the PDF document.
        for i,page in enumerate(PDFPage.create_pages(doc)):
            #page_content that stores table elements in current page.
            page_content = []
            #process each page.
            interpreter.process_page(page)
            #receive the LTPage object for the page.
            layout = device.get_result()
            print "page {}".format(i+1)
            if i == 2: break
            #choose correct top margin for page 1.
            if i == 0:
                top_h = top_h1
            else:
                top_h = top_h2
            #process each child objects within LTPage object.
            for obj in layout:
                #select only LTTextBox and LTLine objects.
                if isinstance(obj,LTTextBox) or isinstance(obj,LTLine):
                    #get x0,y0 position.
                    x0 = obj.bbox[0]
                    y0 = obj.bbox[1]
                    #if col_key is table columns, store the object it in page_content.
                    col_key = int(x0)
                    if col_key in page_dict and y0 < top_h:
                        page_content.append(obj)
            #sort page_content by y0 position.
            page_content.sort(key=lambda x: x.bbox[1], reverse=True)
            #iterate sorted page_content.
            for obj in page_content:
                #if it is a LTLine object.
                if isinstance(obj,LTLine):
                    #combine columns into a row.
                    row=[page_dict[col1_key],page_dict[col2_key],
                         page_dict[col3_key],page_dict[col4_key]]
                    #write the row into csv file.
                    writer.writerow([s.encode("utf-8") for s in row])
#                    print "Line here {}".format(ob.bbox)
                    #reset page_dict to store columns of next row. 
                    page_dict[col1_key] = ""
                    page_dict[col2_key] = ""
                    page_dict[col3_key] = ""
                    page_dict[col4_key] = ""
                #if it is a LTTextBox object.
                else:
#                   #store it to corresponding column.
                    page_dict[int(obj.bbox[0])] += obj.get_text()
#                    print ob.get_text()


