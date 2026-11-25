import os
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output

def convert_pdf_to_markdown(pdf_path: str, output_dir: str):
    model_dict = create_model_dict()
    
    converter = PdfConverter(
        artifact_dict=model_dict,
    )
    
    rendered = converter(pdf_path)
    
    subfolder_name = os.path.basename(pdf_path).replace(".pdf", "")
    save_path = os.path.join(output_dir, subfolder_name)
    
    save_output(rendered, save_path)
    
    print(f"Result in: {save_path}")
    
    markdown_text = rendered.markdown
    print("\Md fragment:")
    print("=" * 40)
    print(markdown_text[:500])
    print("=" * 40)

if __name__ == "__main__":
    PDF_FILE = "/content/Matematyka_dlia_ekonomistiv_Chastyna_2_Intehralne_chyslennia_ta_riady.pdf"
    OUTPUT_FOLDER = "./parsed_output"
    
    if os.path.exists(PDF_FILE):
        convert_pdf_to_markdown(PDF_FILE, OUTPUT_FOLDER)
    else:
        print(f"File {PDF_FILE} not found.")