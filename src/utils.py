from langchain.schema import Document

# Teeme ridadest etteantud pikkusega tekstijupid, koos lehekülje ja reanumbritega
def parse_lines_to_chunks(lines: list[str], page_num: int, chunk_size: int) -> list[Document]:
    current_chunk = []
    current_lines = []
    current_text_length = 0
    chunks = []

    # Kui väga vähe ridu leheküljel, siis ilmselt tegu pealkirja vms.-ga, jätame vahele
    # Vajalik, sest kippus just neid vastustena andma
    non_short_lines = [line for line in lines if len(line.split()) > 3]
    if len(non_short_lines) < 3:
        return []

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        line_length = len(line)
        
        # Tükeldame käistsi
        if current_text_length + line_length > chunk_size and current_chunk:
            chunks.append(Document(
                page_content='\n'.join(current_chunk),
                metadata={
                    'page': page_num,
                    'start_line': current_lines[0],
                    'end_line': current_lines[-1],
                }
            ))
            current_chunk = []
            current_lines = []
            current_text_length = 0
        
        current_chunk.append(line.strip())
        current_lines.append(line_num)
        current_text_length += line_length
    
    # Et viimast ära ei unusta
    if current_chunk:
        chunks.append(Document(
            page_content='\n'.join(current_chunk),
            metadata={
                'page': page_num,
                'start_line': current_lines[0],
                'end_line': current_lines[-1],
            }
        ))
    return chunks
